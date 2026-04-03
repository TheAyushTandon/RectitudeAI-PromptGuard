"""
RL Policy Updater — learns to improve the security policy from red team reports.

Architecture
────────────
  RedTeamEnv (gymnasium.Env)
      State  : [asr, fpr, n_patterns, block_thresh, escalate_thresh,
                bypass_override, bypass_exfil, bypass_extraction,
                bypass_persona, bypass_encoding, bypass_multi_turn]
      Actions: discrete 8
                0  no-op
                1  add_suggested_pattern   (from report.suggested_patterns)
                2  tighten_block_thresh    (-0.05)
                3  relax_block_thresh      (+0.05)
                4  tighten_escalate_thresh (-0.05)
                5  relax_escalate_thresh   (+0.05)
                6  remove_worst_pattern    (most recently added)
                7  reset_thresholds        (back to safe defaults)
      Reward :  +2 per ASR reduction (scaled)
                -1 per FPR increase (scaled)
                -0.1 per no-op
                +0.5 bonus for ASR < 10%

  RLPolicyUpdater
      .train(n_steps)       — train the PPO agent, save model to logs/
      .run_cycle()          — load latest report → propose updates → save JSON
      .apply_approved()     — write approved updates to PolicyStore (live)
      .interactive_review() — CLI human approve/reject of each proposal

Policy → Engine wiring
──────────────────────
  PolicyStore.get("block_threshold")    → read by policy_engine.py each request
  PolicyStore.get("escalate_threshold") → read by policy_engine.py each request
  PolicyStore.get("custom_patterns")    → merged into regex_prefilter at runtime
"""

from __future__ import annotations

import json
import os
import re
import time
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

try:
    import gymnasium as gym
    from gymnasium import spaces
    _GYM_OK = True
except ImportError:
    _GYM_OK = False

try:
    from stable_baselines3 import PPO
    from stable_baselines3.common.monitor import Monitor
    _SB3_OK = True
except ImportError:
    _SB3_OK = False

from backend.layer1_intent_security.regex_prefilter import prefilter
from backend.storage.policy_store import PolicyStore
from backend.utils.logging import get_logger

logger = get_logger(__name__)

# ── Paths ─────────────────────────────────────────────────────────────────────
REPORT_PATH   = "logs/vulnerability_report.json"
PROPOSAL_PATH = "logs/proposed_policy_updates.json"
MODEL_PATH    = "logs/rl_ppo_policy"
HISTORY_PATH  = "logs/rl_training_history.json"

# ── Operational bounds ────────────────────────────────────────────────────────
BLOCK_THRESH_MIN    = 0.60
BLOCK_THRESH_MAX    = 0.95
ESCALATE_THRESH_MIN = 0.30
ESCALATE_THRESH_MAX = 0.75
DEFAULT_BLOCK       = 0.80
DEFAULT_ESCALATE    = 0.50

ATTACK_CATEGORIES = [
    "override", "exfil", "extraction", "persona",
    "encoding", "multi_turn", "indirect", "privilege",
]


# ── Data classes ──────────────────────────────────────────────────────────────

@dataclass
class PolicyUpdate:
    action:     str    # "add_pattern" | "adjust_threshold" | "remove_pattern" | "no_op"
    target:     str    # threshold name or "regex_prefilter"
    value:      Any    # new value
    confidence: float
    reason:     str


@dataclass
class TrainingStep:
    episode:      int
    reward:       float
    asr_before:   float
    asr_after:    float
    fpr_before:   float
    fpr_after:    float
    action_taken: str
    timestamp:    float


# ── Helpers ───────────────────────────────────────────────────────────────────

def _load_report(path: str = REPORT_PATH) -> Optional[dict]:
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def _bypass_by_category(report: dict) -> Dict[str, float]:
    counts: Dict[str, int] = {c: 0 for c in ATTACK_CATEGORIES}
    totals: Dict[str, int] = {c: 0 for c in ATTACK_CATEGORIES}
    for r in report.get("results", []):
        cat = r.get("category", "")
        if cat in counts:
            totals[cat] += 1
            if not r.get("blocked", False):
                counts[cat] += 1
    return {c: counts[c] / max(totals[c], 1) for c in ATTACK_CATEGORIES}


def _run_quick_redteam(
    custom_patterns: List[str],
    block_thresh: float,
    escalate_thresh: float,
) -> Tuple[float, float]:
    """Score the current policy against the built-in attack catalogue."""
    from backend.layer4_red_teaming.attack_runner import BUILTIN_ATTACKS

    compiled_custom = []
    for p in custom_patterns:
        try:
            compiled_custom.append(re.compile(p, re.IGNORECASE | re.DOTALL))
        except re.error:
            pass

    attack_results = [a for a in BUILTIN_ATTACKS if a["category"] != "legitimate"]
    legit_results  = [a for a in BUILTIN_ATTACKS if a["category"] == "legitimate"]

    def _classify(prompt: str) -> str:
        result = prefilter(prompt)
        if result.decision == "allow" and compiled_custom:
            for cp in compiled_custom:
                if cp.search(prompt):
                    return "escalate"
        return result.decision

    blocked  = sum(1 for a in attack_results if _classify(a["prompt"]) != "allow")
    bypassed = len(attack_results) - blocked
    fp       = sum(1 for a in legit_results  if _classify(a["prompt"]) != "allow")

    asr = bypassed / max(len(attack_results), 1)
    fpr = fp       / max(len(legit_results),  1)
    return round(asr, 4), round(fpr, 4)


def _validate_pattern(pattern: str) -> Tuple[bool, str]:
    if not pattern or len(pattern.strip()) < 4:
        return False, "Pattern too short"
    try:
        compiled = re.compile(pattern, re.IGNORECASE)
    except re.error as e:
        return False, f"Invalid regex: {e}"
    trivial = ["ok", "hi", "a", "yes", "no"]
    for s in trivial:
        if compiled.fullmatch(s):
            return False, f"Matches trivially short string '{s}'"
    if len(pattern) < 8 and not pattern.startswith(r"\b"):
        return False, "Short pattern must use \\b word-boundary anchor"
    return True, "OK"


# ── Gymnasium Environment ─────────────────────────────────────────────────────

if _GYM_OK:
    _GymBase = gym.Env
else:
    _GymBase = object


class RedTeamEnv(_GymBase):
    """
    Gymnasium environment for RL-based policy optimisation.

    Observation (11 floats, all in [0,1]):
        asr, fpr, n_custom_patterns_norm, block_thresh_norm, escalate_thresh_norm,
        bypass_override, bypass_exfil, bypass_extraction, bypass_persona,
        bypass_encoding, bypass_multi_turn

    Actions (discrete 8): see module docstring.
    """

    metadata = {"render_modes": []}

    def __init__(self, initial_report: Optional[dict] = None):
        if not _GYM_OK:
            raise ImportError("pip install gymnasium")
        super().__init__()

        self.action_space      = spaces.Discrete(8)
        self.observation_space = spaces.Box(
            low=0.0, high=1.0, shape=(11,), dtype=np.float32
        )

        self._report       = initial_report or _load_report() or {}
        self._store        = PolicyStore()
        self._block        = float(self._store.get("block_threshold",    DEFAULT_BLOCK))
        self._escalate     = float(self._store.get("escalate_threshold", DEFAULT_ESCALATE))
        self._patterns: List[str] = list(self._store.get("custom_patterns", []))

        self._episode    = 0
        self._step_count = 0
        self._history: List[TrainingStep] = []
        self._prev_asr, self._prev_fpr = _run_quick_redteam(
            self._patterns, self._block, self._escalate
        )

        self._action_names = {
            0: "no_op",
            1: "add_suggested_pattern",
            2: "tighten_block_thresh",
            3: "relax_block_thresh",
            4: "tighten_escalate_thresh",
            5: "relax_escalate_thresh",
            6: "remove_worst_pattern",
            7: "reset_thresholds",
        }

    def _get_obs(self) -> np.ndarray:
        cat = _bypass_by_category(self._report)
        obs = np.array([
            self._prev_asr,
            self._prev_fpr,
            min(len(self._patterns) / 20.0, 1.0),
            (self._block    - BLOCK_THRESH_MIN)    / (BLOCK_THRESH_MAX    - BLOCK_THRESH_MIN),
            (self._escalate - ESCALATE_THRESH_MIN) / (ESCALATE_THRESH_MAX - ESCALATE_THRESH_MIN),
            cat.get("override",   0.0),
            cat.get("exfil",      0.0),
            cat.get("extraction", 0.0),
            cat.get("persona",    0.0),
            cat.get("encoding",   0.0),
            cat.get("multi_turn", 0.0),
        ], dtype=np.float32)
        return np.clip(obs, 0.0, 1.0)

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self._episode    += 1
        self._step_count  = 0
        fresh = _load_report()
        if fresh:
            self._report = fresh
        self._prev_asr, self._prev_fpr = _run_quick_redteam(
            self._patterns, self._block, self._escalate
        )
        return self._get_obs(), {}

    def step(self, action: int):
        self._step_count += 1
        action_name = self._action_names.get(int(action), "unknown")
        applied     = False

        if action == 0:
            pass

        elif action == 1:
            for candidate in self._report.get("suggested_patterns", []):
                if candidate not in self._patterns:
                    ok, _ = _validate_pattern(candidate)
                    if ok:
                        self._patterns.append(candidate)
                        applied = True
                        break

        elif action == 2:
            new = round(self._block - 0.05, 2)
            if new >= BLOCK_THRESH_MIN:
                self._block = new; applied = True

        elif action == 3:
            new = round(self._block + 0.05, 2)
            if new <= BLOCK_THRESH_MAX:
                self._block = new; applied = True

        elif action == 4:
            new = round(self._escalate - 0.05, 2)
            if new >= ESCALATE_THRESH_MIN and new < self._block:
                self._escalate = new; applied = True

        elif action == 5:
            new = round(self._escalate + 0.05, 2)
            if new <= ESCALATE_THRESH_MAX and new < self._block:
                self._escalate = new; applied = True

        elif action == 6:
            if self._patterns:
                self._patterns.pop(); applied = True

        elif action == 7:
            if self._block != DEFAULT_BLOCK or self._escalate != DEFAULT_ESCALATE:
                self._block    = DEFAULT_BLOCK
                self._escalate = DEFAULT_ESCALATE
                applied = True

        new_asr, new_fpr = _run_quick_redteam(
            self._patterns, self._block, self._escalate
        )

        reward  = (self._prev_asr - new_asr) * 2.0
        reward -= (new_fpr - self._prev_fpr) * 1.0
        if action == 0:
            reward -= 0.1
        if not applied and action != 0:
            reward -= 0.05
        if new_asr < 0.10:
            reward += 0.5
        if new_fpr < 0.05:
            reward += 0.2

        self._history.append(TrainingStep(
            episode=self._episode, reward=round(reward, 4),
            asr_before=self._prev_asr, asr_after=new_asr,
            fpr_before=self._prev_fpr, fpr_after=new_fpr,
            action_taken=action_name, timestamp=time.time(),
        ))

        self._prev_asr = new_asr
        self._prev_fpr = new_fpr

        terminated = new_asr < 0.10 and new_fpr < 0.05
        truncated  = self._step_count >= 20

        return self._get_obs(), reward, terminated, truncated, {
            "asr": new_asr, "fpr": new_fpr,
            "action": action_name, "applied": applied,
        }

    def render(self):
        print(f"  ASR={self._prev_asr:.1%}  FPR={self._prev_fpr:.1%}  "
              f"thresholds=({self._block}/{self._escalate})  "
              f"custom_patterns={len(self._patterns)}")

    def get_best_policy(self) -> dict:
        return {
            "block_threshold":    self._block,
            "escalate_threshold": self._escalate,
            "custom_patterns":    list(self._patterns),
            "asr":                self._prev_asr,
            "fpr":                self._prev_fpr,
        }


# ── RL Policy Updater ─────────────────────────────────────────────────────────

class RLPolicyUpdater:
    """
    Full RL-based policy update pipeline.

    Quick-start:
        updater = RLPolicyUpdater()
        updater.train(n_steps=10_000)   # one-time
        updates = updater.run_cycle()
        updater.interactive_review(updates)
    """

    def __init__(self):
        self._store = PolicyStore()

    # ── Training ──────────────────────────────────────────────────────────

    def train(self, n_steps: int = 10_000, verbose: int = 1) -> None:
        """Train (or resume) the PPO agent. Saves to logs/rl_ppo_policy.zip."""
        if not (_SB3_OK and _GYM_OK):
            raise ImportError("pip install gymnasium stable-baselines3")

        os.makedirs("logs", exist_ok=True)
        report = _load_report()
        if not report:
            print("[RL] Run the red team first: python scripts/run_redteam.py")
            return

        env = Monitor(RedTeamEnv(initial_report=report))

        if os.path.exists(MODEL_PATH + ".zip"):
            logger.info("Resuming from %s", MODEL_PATH)
            model = PPO.load(MODEL_PATH, env=env)
            model.set_env(env)
        else:
            logger.info("Fresh PPO training")
            model = PPO(
                "MlpPolicy", env,
                verbose=verbose,
                learning_rate=3e-4,
                n_steps=256,
                batch_size=64,
                n_epochs=10,
                gamma=0.99,
                gae_lambda=0.95,
                clip_range=0.2,
                ent_coef=0.01,
            )

        model.learn(total_timesteps=n_steps)
        model.save(MODEL_PATH)
        logger.info("Saved PPO model → %s.zip", MODEL_PATH)

        history = [asdict(s) for s in env.env._history]
        with open(HISTORY_PATH, "w") as f:
            json.dump(history, f, indent=2)

        if history:
            rewards = [s["reward"] for s in history]
            print(f"\n[RL Training complete]"
                  f"  steps={len(history)}"
                  f"  mean_reward={sum(rewards)/len(rewards):.3f}"
                  f"  final_ASR={history[-1]['asr_after']:.1%}"
                  f"  final_FPR={history[-1]['fpr_after']:.1%}")
            best = min(history, key=lambda s: s["asr_after"])
            print(f"  best_ASR={best['asr_after']:.1%}  "
                  f"(episode {best['episode']}, action={best['action_taken']})")

    # ── Proposal generation ───────────────────────────────────────────────

    def propose_updates(self, report: dict) -> List[PolicyUpdate]:
        """Generate proposals. Uses PPO agent if trained, else heuristics."""
        if _SB3_OK and _GYM_OK and os.path.exists(MODEL_PATH + ".zip"):
            try:
                return self._propose_from_agent(report)
            except Exception as e:
                logger.warning("Agent inference failed (%s) — falling back to heuristics", e)
        logger.info("Using heuristic proposals (train for PPO-based proposals)")
        return self._propose_heuristic(report)

    def _propose_from_agent(self, report: dict) -> List[PolicyUpdate]:
        env   = RedTeamEnv(initial_report=report)
        model = PPO.load(MODEL_PATH, env=env)
        obs, _ = env.reset()

        updates: List[PolicyUpdate] = []
        seen: set = set()

        for _ in range(20):
            action, _ = model.predict(obs, deterministic=True)
            action    = int(action)
            obs, reward, terminated, truncated, info = env.step(action)
            name = env._action_names[action]

            if action != 0 and info.get("applied") and name not in seen:
                seen.add(name)
                u = self._action_to_proposal(action, env, report,
                                              confidence=min(0.5 + reward * 0.2, 0.95))
                if u:
                    updates.append(u)

            if terminated or truncated:
                break

        asr_start = report.get("attack_success_rate", 0)
        logger.info("Agent proposed %d updates  ASR: %.1f%% → %.1f%%",
                    len(updates), asr_start * 100, env._prev_asr * 100)
        return updates

    def _propose_heuristic(self, report: dict) -> List[PolicyUpdate]:
        updates: List[PolicyUpdate] = []
        asr = report.get("attack_success_rate", 0.0)
        fpr = report.get("false_positive_rate", 0.0)

        if asr > 0.20 and fpr < 0.10:
            updates.append(PolicyUpdate(
                action="adjust_threshold", target="escalate_threshold",
                value=max(DEFAULT_ESCALATE - 0.05, ESCALATE_THRESH_MIN),
                confidence=0.70,
                reason=f"ASR {asr:.1%} > 20% with FPR headroom — tighten escalate",
            ))
        if asr > 0.40:
            updates.append(PolicyUpdate(
                action="adjust_threshold", target="block_threshold",
                value=max(DEFAULT_BLOCK - 0.05, BLOCK_THRESH_MIN),
                confidence=0.65,
                reason=f"High ASR {asr:.1%} — tighten block threshold",
            ))
        if fpr > 0.15:
            updates.append(PolicyUpdate(
                action="adjust_threshold", target="block_threshold",
                value=min(DEFAULT_BLOCK + 0.05, BLOCK_THRESH_MAX),
                confidence=0.60,
                reason=f"FPR {fpr:.1%} too high — relax block threshold",
            ))

        existing = set(self._store.get("custom_patterns", []))
        for candidate in report.get("suggested_patterns", []):
            if candidate in existing:
                continue
            ok, reason = _validate_pattern(candidate)
            if ok:
                updates.append(PolicyUpdate(
                    action="add_pattern", target="regex_prefilter",
                    value=candidate, confidence=0.55,
                    reason="Validated pattern from red team bypass analysis",
                ))
        return updates

    def _action_to_proposal(self, action: int, env: RedTeamEnv,
                             report: dict, confidence: float) -> Optional[PolicyUpdate]:
        if action == 1:
            for c in report.get("suggested_patterns", []):
                if c not in self._store.get("custom_patterns", []):
                    ok, _ = _validate_pattern(c)
                    if ok:
                        return PolicyUpdate(
                            action="add_pattern", target="regex_prefilter",
                            value=c, confidence=confidence,
                            reason="Agent identified regex gap for bypassed attacks",
                        )
        elif action in (2, 3):
            return PolicyUpdate(
                action="adjust_threshold", target="block_threshold",
                value=env._block, confidence=confidence,
                reason=f"Agent {'tightened' if action==2 else 'relaxed'} "
                       f"block threshold to {env._block}",
            )
        elif action in (4, 5):
            return PolicyUpdate(
                action="adjust_threshold", target="escalate_threshold",
                value=env._escalate, confidence=confidence,
                reason=f"Agent {'tightened' if action==4 else 'relaxed'} "
                       f"escalate threshold to {env._escalate}",
            )
        elif action == 6:
            p = env._patterns[-1] if env._patterns else ""
            return PolicyUpdate(
                action="remove_pattern", target="regex_prefilter",
                value=p, confidence=confidence,
                reason="Agent removed lowest-evidence custom pattern",
            )
        elif action == 7:
            return PolicyUpdate(
                action="adjust_threshold", target="block_threshold",
                value=DEFAULT_BLOCK, confidence=confidence,
                reason=f"Agent reset thresholds to defaults ({DEFAULT_BLOCK}/{DEFAULT_ESCALATE})",
            )
        return None

    # ── Persistence ───────────────────────────────────────────────────────

    def save_proposals(self, updates: List[PolicyUpdate]):
        os.makedirs("logs", exist_ok=True)
        data = [
            {
                "action": u.action, "target": u.target,
                "value": u.value, "confidence": round(u.confidence, 3),
                "reason": u.reason, "approved": None,
            }
            for u in updates
        ]
        with open(PROPOSAL_PATH, "w") as f:
            json.dump(data, f, indent=2)
        logger.info("Saved %d proposals → %s", len(updates), PROPOSAL_PATH)

    # ── Apply updates to live PolicyStore ────────────────────────────────

    def apply_approved(self, updates: List[PolicyUpdate]):
        """
        Write approved updates to PolicyStore.
        Changes are persisted to logs/active_policy.json and take effect
        on the next request — no server restart required.
        """
        applied = 0
        for u in updates:
            try:
                if u.action == "adjust_threshold":
                    key = u.target
                    val = float(u.value)
                    if key == "block_threshold":
                        val = float(np.clip(val, BLOCK_THRESH_MIN, BLOCK_THRESH_MAX))
                    elif key == "escalate_threshold":
                        val = float(np.clip(val, ESCALATE_THRESH_MIN, ESCALATE_THRESH_MAX))
                        val = min(val, float(self._store.get("block_threshold", DEFAULT_BLOCK)) - 0.05)
                    self._store.set(key, round(val, 2))
                    logger.info("Applied: %s = %s", key, val)
                    applied += 1

                elif u.action == "add_pattern":
                    ok, reason = _validate_pattern(str(u.value))
                    if not ok:
                        logger.warning("Rejected pattern '%s': %s", u.value, reason)
                        continue
                    self._store.add_custom_pattern(str(u.value))
                    logger.info("Added pattern: %s", u.value)
                    applied += 1

                elif u.action == "remove_pattern":
                    patterns = list(self._store.get("custom_patterns", []))
                    if str(u.value) in patterns:
                        patterns.remove(str(u.value))
                        self._store.set("custom_patterns", patterns)
                        logger.info("Removed pattern: %s", u.value)
                        applied += 1

            except Exception as e:
                logger.error("Failed to apply %s: %s", u, e)

        print(f"\n[RL] Applied {applied}/{len(updates)} updates → live immediately (no restart needed)")

    # ── Interactive CLI review ────────────────────────────────────────────

    def interactive_review(self, updates: List[PolicyUpdate]):
        """Interactive terminal approval of proposals."""
        if not updates:
            print("\n[RL] No proposals to review.")
            return

        print("\n" + "═" * 65)
        print("  RL Policy Update Review")
        print("═" * 65)

        approved: List[PolicyUpdate] = []
        for i, u in enumerate(updates, 1):
            print(f"\n  [{i}/{len(updates)}]  {u.action.upper()}  →  {u.target}")
            print(f"        value      : {u.value}")
            print(f"        confidence : {u.confidence:.0%}")
            print(f"        reason     : {u.reason}")

            if u.action == "add_pattern":
                ok, msg = _validate_pattern(str(u.value))
                status = "✓ valid" if ok else f"✗ {msg}"
                print(f"        validation : {status}")
            elif u.action == "adjust_threshold":
                current = self._store.get(u.target, "?")
                print(f"        current    : {current}  →  {u.value}")

            while True:
                choice = input("\n        approve? [y/n/q=quit] ").strip().lower()
                if choice in ("y", "n", "q"):
                    break
            if choice == "q":
                print("\n[RL] Review aborted.")
                break
            if choice == "y":
                approved.append(u)
                print("        → approved")
            else:
                print("        → skipped")

        if approved:
            self.apply_approved(approved)
        else:
            print("\n[RL] No updates applied.")

        custom   = self._store.get("custom_patterns", [])
        b_thresh = self._store.get("block_threshold",    DEFAULT_BLOCK)
        e_thresh = self._store.get("escalate_threshold", DEFAULT_ESCALATE)
        new_asr, new_fpr = _run_quick_redteam(custom, b_thresh, e_thresh)
        print(f"\n[RL] Post-update built-in ASR={new_asr:.1%}  FPR={new_fpr:.1%}")
        print("═" * 65 + "\n")

    # ── Full cycle ────────────────────────────────────────────────────────

    def run_cycle(self, auto_approve_above: float = 0.0) -> List[PolicyUpdate]:
        """
        Full pipeline: load report → propose → save → optional auto-approve.
        Set auto_approve_above=0.85 for CI pipelines.
        """
        report = _load_report()
        if not report:
            print("[RL] No vulnerability report. Run: python scripts/run_redteam.py")
            return []

        asr = report.get("attack_success_rate", 0)
        fpr = report.get("false_positive_rate", 0)
        print(f"\n[RL] Report: ASR={asr:.1%}  FPR={fpr:.1%}  "
              f"bypassed={report.get('attacks_bypassed','?')}")

        updates = self.propose_updates(report)
        self.save_proposals(updates)
        print(f"[RL] {len(updates)} proposals → {PROPOSAL_PATH}")

        if auto_approve_above > 0.0:
            auto = [u for u in updates if u.confidence >= auto_approve_above]
            if auto:
                print(f"[RL] Auto-approving {len(auto)} proposals "
                      f"(confidence ≥ {auto_approve_above:.0%})")
                self.apply_approved(auto)

        return updates


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="RectitudeAI RL Policy Updater")
    sub = parser.add_subparsers(dest="cmd")

    pt = sub.add_parser("train", help="Train the PPO agent")
    pt.add_argument("--steps",   type=int, default=10_000)
    pt.add_argument("--verbose", type=int, default=1)

    pr = sub.add_parser("run", help="Propose updates from latest report")
    pr.add_argument("--auto-approve", type=float, default=0.0,
                    help="Auto-approve proposals above this confidence (0-1)")
    pr.add_argument("--interactive", action="store_true",
                    help="Interactively approve/reject in terminal")

    sub.add_parser("status", help="Show current PolicyStore state")

    args = parser.parse_args()
    updater = RLPolicyUpdater()

    if args.cmd == "train":
        updater.train(n_steps=args.steps, verbose=args.verbose)

    elif args.cmd == "run":
        updates = updater.run_cycle(auto_approve_above=args.auto_approve)
        if args.interactive and updates:
            updater.interactive_review(updates)

    elif args.cmd == "status":
        store = PolicyStore()
        print("\n[PolicyStore] Current state:")
        for k, v in store.get_all().items():
            print(f"  {k:<30} = {v}")
        print()

    else:
        parser.print_help()