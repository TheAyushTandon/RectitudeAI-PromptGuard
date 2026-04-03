"""
Orchestrator — risk-tiered request routing.

Tier 1 (<5ms):   Regex prefilter — blocks obvious attacks instantly
Tier 2 (<200ms): ML classifiers — runs in parallel, only for ambiguous requests
Tier 3:          Capability token check — only for requests with tool calls
Behavioral:      ASI score update — always, but non-blocking

Routing logic:
  prefilter score >= 0.85  → block immediately, skip ML
  prefilter score 0.50–0.84 → run ML classifiers
  prefilter score < 0.50   → fast-pass with light ML scan
  tool_calls present        → always run capability token check
  session has ASI alert     → force ML regardless of prefilter score

This means a clean "what is the capital of France?" goes through
in ~5ms (just regex). An ambiguous prompt goes through in ~150ms.
An obvious injection is blocked in <1ms.
"""

from __future__ import annotations
import asyncio
import time
import uuid
from dataclasses import dataclass, field
from typing import List, Optional

from backend.layer1_intent_security.regex_prefilter import prefilter, PrefilterResult
from backend.layer1_intent_security.injection_classifier import InjectionClassifier
from backend.layer1_intent_security.perplexity_detector import PerplexityDetector
from backend.layer1_intent_security.policy_engine import apply_policies
from backend.layer2_crypto.capability_tokens import CapabilityTokenService
from backend.layer3_behavior_monitor.asi_calculator import ASICalculator
from backend.gateway.security.output_mediator import mediate_output
from backend.models.requests import InferenceRequest
from backend.models.security import SecurityDecision
from backend.storage.audit_logs import AuditLogger
from backend.utils.logging import get_logger

logger = get_logger(__name__)

# Lazy-loaded singletons — initialised once on first request
_injection_clf: Optional[InjectionClassifier] = None
_perplexity_clf: Optional[PerplexityDetector] = None
_token_svc = CapabilityTokenService()
_asi_calc = ASICalculator()
_audit = AuditLogger()


def _get_injection_clf() -> InjectionClassifier:
    global _injection_clf
    if _injection_clf is None:
        _injection_clf = InjectionClassifier()
    return _injection_clf


def _get_perplexity_clf() -> PerplexityDetector:
    global _perplexity_clf
    if _perplexity_clf is None:
        _perplexity_clf = PerplexityDetector()
    return _perplexity_clf


@dataclass
class OrchestratorResult:
    decision: str               # "allow" | "block" | "escalate"
    risk_score: float
    reason: str
    request_id: str
    latency_ms: float
    tier_reached: int           # 1, 2, or 3
    capability_token: str = ""
    asi_score: float = 1.0
    asi_alert: bool = False
    output_safe: bool = True
    output_findings: list = field(default_factory=list)
    detector_signals: dict = field(default_factory=dict)


class Orchestrator:

    async def process(
        self,
        req: InferenceRequest,
        llm_response: Optional[str] = None,
        tool_calls: Optional[List[str]] = None,
    ) -> OrchestratorResult:
        """
        Full pipeline. Call this from routes.py.

        If llm_response is provided, the output mediator runs too.
        tool_calls is a list of tool names the LLM wants to invoke.
        """
        t0 = time.monotonic()
        request_id = str(uuid.uuid4())[:12]
        session_id = req.conversation_id or req.user_id
        signals: dict = {}

        # ── Tier 1: Regex prefilter ─────────────────────────────────────────
        pre: PrefilterResult = prefilter(req.prompt)
        signals["regex_prefilter"] = {
            "decision": pre.decision,
            "risk_score": pre.risk_score,
            "triggered": pre.triggered,
        }
        logger.info("[%s] T1 regex: %s score=%.3f", request_id, pre.decision, pre.risk_score)

        if pre.decision == "block" and pre.risk_score >= 1.0:
            return self._finalise(
                OrchestratorResult(
                    decision="block", risk_score=1.0,
                    reason=f"Tier-1 instant block: {pre.reason}",
                    request_id=request_id,
                    latency_ms=self._ms(t0),
                    tier_reached=1,
                    detector_signals=signals,
                ),
                req, session_id, blocked=True,
            )

        # Check ASI for this session — if alert, force ML regardless
        asi_risk = _asi_calc.get_risk_score(session_id)
        force_ml = asi_risk >= 0.45 or pre.risk_score >= 0.50

        tier_reached = 1

        # ── Tier 2: ML classifiers (parallel) ──────────────────────────────
        ml_decisions: List[SecurityDecision] = []

        if force_ml:
            tier_reached = 2
            injection_task = asyncio.create_task(
                _get_injection_clf().classify(req.prompt)
            )
            perplexity_task = asyncio.create_task(
                _get_perplexity_clf().classify(req.prompt)
            )
            injection_dec, perplexity_dec = await asyncio.gather(
                injection_task, perplexity_task
            )
            ml_decisions = [injection_dec, perplexity_dec]
            signals["injection_ml"] = {
                "decision": injection_dec.decision,
                "risk_score": injection_dec.risk_score,
            }
            signals["perplexity"] = {
                "decision": perplexity_dec.decision,
                "risk_score": perplexity_dec.risk_score,
            }
            logger.info(
                "[%s] T2 ML: inj=%.3f perp=%.3f",
                request_id, injection_dec.risk_score, perplexity_dec.risk_score,
            )

        # Add regex as a SecurityDecision for policy fusion
        regex_sd = SecurityDecision(
            decision=pre.decision,
            risk_score=pre.risk_score,
            reason=pre.reason,
            metadata={"classifier": "regex_prefilter"},
        )

        # Add ASI as a SecurityDecision
        asi_sd = SecurityDecision(
            decision="escalate" if asi_risk >= 0.45 else "allow",
            risk_score=asi_risk,
            reason=f"ASI drift risk {asi_risk:.2%}",
            metadata={"classifier": "behavioral_asi"},
        )

        all_decisions = [regex_sd, *ml_decisions, asi_sd]
        final_decision = apply_policies(req, all_decisions)

        if final_decision.decision == "block":
            return self._finalise(
                OrchestratorResult(
                    decision="block",
                    risk_score=final_decision.risk_score,
                    reason=final_decision.reason,
                    request_id=request_id,
                    latency_ms=self._ms(t0),
                    tier_reached=tier_reached,
                    asi_score=round(1.0 - asi_risk, 4),
                    asi_alert=asi_risk >= 0.45,
                    detector_signals=signals,
                ),
                req, session_id, blocked=True,
            )

        # ── Tier 3: Capability token ────────────────────────────────────────
        capability_token = ""
        if tool_calls:
            tier_reached = 3
            allowed_tools = _token_svc.get_default_scope(final_decision.risk_score)
            capability_token = _token_svc.issue_token(session_id, allowed_tools)

            # Verify each requested tool call
            for tool_name in tool_calls:
                ok, reason = _token_svc.verify_tool_call(capability_token, tool_name)
                if not ok:
                    return self._finalise(
                        OrchestratorResult(
                            decision="block",
                            risk_score=0.95,
                            reason=f"Capability token denied tool '{tool_name}': {reason}",
                            request_id=request_id,
                            latency_ms=self._ms(t0),
                            tier_reached=3,
                            capability_token=capability_token,
                            detector_signals=signals,
                        ),
                        req, session_id, blocked=True,
                    )

        # ── Output mediation (if LLM has already responded) ─────────────────
        output_safe = True
        output_findings: list = []
        if llm_response:
            med = mediate_output(llm_response)
            output_safe = med.safe
            output_findings = med.findings
            if not med.safe:
                logger.warning(
                    "[%s] Output mediator caught %d findings (severity=%s)",
                    request_id, len(med.findings), med.severity,
                )

        # ── ASI update (always, non-blocking) ───────────────────────────────
        snap = _asi_calc.compute(
            prompt=req.prompt,
            session_id=session_id,
            tool_invoked=tool_calls[0] if tool_calls else None,
            response_token_count=len(llm_response.split()) if llm_response else 0,
            blocked=False,
        )

        result = OrchestratorResult(
            decision=final_decision.decision,
            risk_score=final_decision.risk_score,
            reason=final_decision.reason,
            request_id=request_id,
            latency_ms=self._ms(t0),
            tier_reached=tier_reached,
            capability_token=capability_token,
            asi_score=snap.asi,
            asi_alert=snap.alert,
            output_safe=output_safe,
            output_findings=output_findings,
            detector_signals=signals,
        )
        return self._finalise(result, req, session_id, blocked=False)

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _ms(self, t0: float) -> float:
        return round((time.monotonic() - t0) * 1000, 2)

    def _finalise(
        self,
        result: OrchestratorResult,
        req: InferenceRequest,
        session_id: str,
        blocked: bool,
    ) -> OrchestratorResult:
        # Update ASI on blocks too (persistence-after-block is a signal)
        if blocked:
            _asi_calc.compute(
                prompt=req.prompt,
                session_id=session_id,
                blocked=True,
            )

        # Audit log
        _audit.log_event({
            "request_id": result.request_id,
            "user_id": req.user_id,
            "session_id": session_id,
            "decision": result.decision,
            "risk_score": result.risk_score,
            "tier_reached": result.tier_reached,
            "latency_ms": result.latency_ms,
            "asi_score": result.asi_score,
            "asi_alert": result.asi_alert,
            "reason": result.reason,
            "signals": result.detector_signals,
        })

        logger.info(
            "[%s] FINAL %s score=%.3f tier=%d latency=%.1fms ASI=%.3f%s",
            result.request_id,
            result.decision.upper(),
            result.risk_score,
            result.tier_reached,
            result.latency_ms,
            result.asi_score,
            " ⚠ ASI ALERT" if result.asi_alert else "",
        )
        return result


# Module-level singleton
orchestrator = Orchestrator()
