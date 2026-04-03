"""
Inference routes — all security logic delegated to the orchestrator.
This file should stay thin.
"""

from fastapi import APIRouter, Depends, HTTPException
from backend.models.requests import InferenceRequest
from backend.models.responses import InferenceResponse
from backend.gateway.security.auth.jwt_handler import get_current_user
from backend.gateway.security.auth.rate_limiter import rate_limit_dependency
from backend.gateway.llm.client import get_llm_client
from backend.layer5_orchestration.orchestrator import orchestrator
from backend.utils.exceptions import SecurityBlockError
from backend.utils.logging import get_logger
import uuid
from datetime import datetime

router = APIRouter()
logger = get_logger(__name__)


@router.post("/v1/inference", response_model=InferenceResponse)
async def generate_response(
    req: InferenceRequest,
    user=Depends(get_current_user),
    _rl=Depends(rate_limit_dependency),
):
    # Phase 1: Pre-LLM security check
    pre_result = await orchestrator.process(req)

    if pre_result.decision == "block":
        raise SecurityBlockError(
            pre_result.reason,
            pre_result.risk_score,
            {
                "request_id": pre_result.request_id,
                "tier_reached": pre_result.tier_reached,
                "asi_score": pre_result.asi_score,
                "signals": pre_result.detector_signals,
            },
        )

    if pre_result.decision == "escalate":
        # For demo purposes escalate still allows through but logs prominently.
        # In production this would queue for human review.
        logger.warning(
            "ESCALATED request %s — proceeding with elevated monitoring",
            pre_result.request_id,
        )

    # Phase 2: LLM call
    try:
        tool_names = [tc.name for tc in req.tool_calls] if req.tool_calls else []
        client = get_llm_client()
        llm_response = await client.generate(
            prompt=req.prompt,
            max_tokens=req.max_tokens,
            temperature=req.temperature,
        )
    except Exception as e:
        logger.error("LLM call failed: %s", e)
        raise HTTPException(status_code=500, detail="LLM inference failed")

    # Phase 3: Post-LLM output mediation + ASI update
    post_result = await orchestrator.process(
        req,
        llm_response=llm_response.response,
        tool_calls=tool_names or None,
    )

    if not post_result.output_safe:
        # Output had PII or credential leakage — return redacted version
        logger.warning(
            "Output mediation blocked leakage for request %s: %s",
            post_result.request_id,
            post_result.output_findings,
        )
        return InferenceResponse(
            response="[Response redacted by security mediator — potential data leakage detected]",
            tool_calls=[],
            metadata={
                "request_id": post_result.request_id,
                "redacted": True,
                "findings_count": len(post_result.output_findings),
                "latency_ms": post_result.latency_ms,
                "asi_score": post_result.asi_score,
            },
            request_id=post_result.request_id,
            timestamp=datetime.utcnow(),
        )

    return InferenceResponse(
        response=llm_response.response,
        tool_calls=[],
        metadata={
            "request_id": post_result.request_id,
            "latency_ms": post_result.latency_ms,
            "tier_reached": post_result.tier_reached,
            "risk_score": post_result.risk_score,
            "asi_score": post_result.asi_score,
            "asi_alert": post_result.asi_alert,
            "capability_token_issued": bool(post_result.capability_token),
        },
        request_id=post_result.request_id,
        timestamp=datetime.utcnow(),
    )


@router.get("/v1/session/{session_id}/asi")
async def get_session_asi(
    session_id: str,
    user=Depends(get_current_user),
):
    """Return current ASI score for a session. Used by the dashboard."""
    from backend.layer3_behavior_monitor.asi_calculator import ASICalculator
    calc = ASICalculator()
    risk = calc.get_risk_score(session_id)
    return {
        "session_id": session_id,
        "asi_score": round(1.0 - risk, 4),
        "risk_score": risk,
        "alert": risk >= 0.45,
    }


@router.post("/v1/session/{session_id}/reset")
async def reset_session(
    session_id: str,
    user=Depends(get_current_user),
):
    """Admin: reset a session's ASI history."""
    from backend.layer3_behavior_monitor.asi_calculator import ASICalculator
    ASICalculator().reset_session(session_id)
    return {"status": "reset", "session_id": session_id}
