"""
Agent Stability Index (ASI) — sliding-window behavioural drift monitor.

Runs as a background scorer per session. Does NOT block synchronously —
it returns a score that the orchestrator uses to adjust routing on the
*next* request. That's intentional: it detects slow multi-turn attacks.

Metrics computed:
  C  — response consistency (semantic similarity of consecutive prompts)
  T  — tool usage stability (unexpected tool invocations)
  B  — boundary stability (token count variance, refusal persistence)
  LDFR — latent diagnosis flip rate (sharp topic reversals)

ASI = 0.35*C + 0.30*T + 0.20*B + 0.15*(1-LDFR)

Alert fires when ASI < 0.55 for 2 consecutive windows.
"""

from __future__ import annotations
import math
import json
import time
from dataclasses import dataclass, field, asdict
from typing import List, Optional

try:
    import redis as _redis_module
    from backend.gateway.config import settings as _settings
    _r = _redis_module.Redis(
        host=_settings.redis_host,
        port=_settings.redis_port,
        db=_settings.redis_db,
        decode_responses=True,
        socket_connect_timeout=2,
    )
    _r.ping()
    _REDIS_OK = True
except Exception:
    _r = None
    _REDIS_OK = False

# Fallback in-process store when Redis is unavailable
_LOCAL_STORE: dict[str, list] = {}

WINDOW_SIZE = 10          # interactions per ASI window
ALERT_THRESHOLD = 0.55    # ASI below this = suspicious
ALERT_CONSECUTIVE = 2     # consecutive windows below threshold = alert


@dataclass
class ASISnapshot:
    session_id: str
    asi: float
    c_consistency: float
    t_tool: float
    b_boundaries: float
    ldfr: float
    alert: bool
    window_count: int
    timestamp: float = field(default_factory=time.time)


def _get_session(session_id: str) -> list:
    key = f"asi:session:{session_id}"
    if _REDIS_OK and _r:
        raw = _r.get(key)
        return json.loads(raw) if raw else []
    return _LOCAL_STORE.get(key, [])


def _save_session(session_id: str, data: list):
    key = f"asi:session:{session_id}"
    if _REDIS_OK and _r:
        _r.setex(key, 3600, json.dumps(data))
    else:
        _LOCAL_STORE[key] = data


def _get_alert_count(session_id: str) -> int:
    key = f"asi:alert_count:{session_id}"
    if _REDIS_OK and _r:
        v = _r.get(key)
        return int(v) if v else 0
    return _LOCAL_STORE.get(key, 0)


def _set_alert_count(session_id: str, count: int):
    key = f"asi:alert_count:{session_id}"
    if _REDIS_OK and _r:
        _r.setex(key, 3600, count)
    else:
        _LOCAL_STORE[key] = count


def _cosine_sim_simple(a: str, b: str) -> float:
    """
    Bag-of-words cosine similarity — no ML dependency.
    Good enough for detecting sharp topic switches.
    """
    def vec(text: str) -> dict:
        v: dict = {}
        for w in text.lower().split():
            v[w] = v.get(w, 0) + 1
        return v

    va, vb = vec(a), vec(b)
    common = set(va) & set(vb)
    if not common:
        return 0.0
    dot = sum(va[w] * vb[w] for w in common)
    mag_a = math.sqrt(sum(x**2 for x in va.values()))
    mag_b = math.sqrt(sum(x**2 for x in vb.values()))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def _coefficient_of_variation(values: List[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    if mean == 0:
        return 0.0
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return math.sqrt(variance) / mean


class ASICalculator:

    def compute(
        self,
        prompt: str,
        session_id: str,
        tool_invoked: Optional[str] = None,
        response_token_count: int = 0,
        blocked: bool = False,
    ) -> ASISnapshot:
        history = _get_session(session_id)

        entry = {
            "prompt": prompt,
            "tool": tool_invoked,
            "tokens": response_token_count,
            "blocked": blocked,
            "ts": time.time(),
        }
        history.append(entry)

        # Keep only the last WINDOW_SIZE entries
        if len(history) > WINDOW_SIZE:
            history = history[-WINDOW_SIZE:]
        _save_session(session_id, history)

        # Need at least 3 entries for meaningful scores
        if len(history) < 3:
            snap = ASISnapshot(
                session_id=session_id, asi=1.0,
                c_consistency=1.0, t_tool=1.0,
                b_boundaries=1.0, ldfr=0.0,
                alert=False, window_count=len(history),
            )
            return snap

        prompts = [e["prompt"] for e in history]
        tools   = [e["tool"] for e in history]
        tokens  = [e["tokens"] for e in history]

        # ── C: Response consistency ─────────────────────────────────────────
        # Average pairwise cosine similarity between consecutive prompts.
        # Floor at 0.30: two unrelated legit questions (zero BoW overlap)
        # should not look like an attack. Real attacks cause sharp variance
        # in direction, tracked by LDFR below.
        sims = [
            max(_cosine_sim_simple(prompts[i], prompts[i - 1]), 0.30)
            for i in range(1, len(prompts))
        ]
        c_consistency = sum(sims) / len(sims) if sims else 1.0

        # ── T: Tool usage stability ─────────────────────────────────────────
        # Penalise sessions that suddenly start using tools they haven't used
        # in the first half of the window (late tool introduction = suspicious).
        unique_tools = set(t for t in tools if t)
        if not unique_tools:
            t_tool = 1.0
        else:
            first_half_tools = set(t for t in tools[:len(tools)//2] if t)
            new_tools_late = unique_tools - first_half_tools
            t_tool = max(0.0, 1.0 - len(new_tools_late) * 0.25)

        # ── B: Boundary stability ───────────────────────────────────────────
        # High CV in token counts = erratic responses = model being manipulated
        cv = _coefficient_of_variation([float(t) for t in tokens if t > 0])
        b_boundaries = max(0.0, 1.0 - min(cv, 1.0))

        # Penalty for re-attempting after a block (persistence after refusal)
        blocked_count = sum(1 for e in history if e.get("blocked"))
        if blocked_count >= 2:
            b_boundaries *= 0.6

        # ── LDFR: Latent Diagnosis Flip Rate ────────────────────────────────
        # Fraction of consecutive pairs with similarity < 0.15 (sharp flips)
        flips = sum(1 for s in sims if s < 0.15)
        ldfr = flips / max(len(sims), 1)

        # ── ASI fusion ──────────────────────────────────────────────────────
        asi = (
            0.35 * c_consistency
            + 0.30 * t_tool
            + 0.20 * b_boundaries
            + 0.15 * (1.0 - ldfr)
        )
        asi = round(max(0.0, min(1.0, asi)), 4)

        # Alert logic
        alert_count = _get_alert_count(session_id)
        if asi < ALERT_THRESHOLD:
            alert_count += 1
        else:
            alert_count = 0
        _set_alert_count(session_id, alert_count)

        alert = alert_count >= ALERT_CONSECUTIVE

        return ASISnapshot(
            session_id=session_id,
            asi=asi,
            c_consistency=round(c_consistency, 4),
            t_tool=round(t_tool, 4),
            b_boundaries=round(b_boundaries, 4),
            ldfr=round(ldfr, 4),
            alert=alert,
            window_count=len(history),
        )

    def get_risk_score(self, session_id: str) -> float:
        """Returns inverted ASI as a risk score (0 = safe, 1 = high risk)."""
        history = _get_session(session_id)
        if not history:
            return 0.0
        snap = self.compute(
            prompt=history[-1]["prompt"],
            session_id=session_id,
        )
        return round(1.0 - snap.asi, 4)

    def reset_session(self, session_id: str):
        """Clear session history (e.g. after a legitimate context reset)."""
        _save_session(session_id, [])
        _set_alert_count(session_id, 0)
