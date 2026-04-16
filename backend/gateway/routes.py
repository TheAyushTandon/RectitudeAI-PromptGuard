"""
Inference routes — all security logic delegated to the orchestrator.
This file should stay thin.
"""

from fastapi import APIRouter, Depends, HTTPException
from backend.models.requests import InferenceRequest, AgentChatRequest
from backend.models.responses import InferenceResponse, AgentChatResponse
from backend.gateway.security.auth.jwt_handler import get_current_user
from backend.gateway.security.auth.rate_limiter import rate_limit_dependency
from backend.gateway.llm.client import get_llm_client
from backend.layer5_orchestration.orchestrator import orchestrator
from backend.utils.exceptions import SecurityBlockError
from backend.utils.logging import get_logger
import uuid
import time
from datetime import datetime

# ── Agent system imports ─────────────────────────────────────────────────
from backend.agents.registry import agent_registry
from backend.agents.router import agent_router
from backend.agents.hr_database_agent import HRDatabaseAgent
from backend.agents.email_agent import EmailAgent
from backend.agents.code_exec_agent import CodeExecAgent
from backend.agents.financial_advisor_agent import FinanceAuditAgent
from backend.agents.general_agent import GeneralAgent

# Register all agents on module load
for _AgentCls in [HRDatabaseAgent, EmailAgent, CodeExecAgent, FinanceAuditAgent, GeneralAgent]:
    _inst = _AgentCls()
    if _inst.name not in agent_registry:
        agent_registry.register(_inst)

router = APIRouter()
logger = get_logger(__name__)


@router.post("/v1/inference", response_model=InferenceResponse)
async def generate_response(
    req: InferenceRequest,
    # user=Depends(get_current_user),
    # _rl=Depends(rate_limit_dependency),
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
    #
    # FIX: Previously this called orchestrator.process() a SECOND time, which re-ran
    # the full security pipeline (regex prefilter, ML classifiers, ASI compute) on the
    # same prompt. This caused:
    #   (a) Every request to append TWO entries to the ASI session history, distorting
    #       drift scores and causing spurious ASI alerts after just 5 requests.
    #   (b) Redundant ML inference adding ~150ms of avoidable latency per request.
    #
    # Fixed: call only the output mediator and ASI updater directly. The orchestrator
    # result from Phase 1 already has all the security metadata we need.
    from backend.gateway.security.output_mediator import mediate_output
    from backend.layer3_behavior_monitor.asi_calculator import ASICalculator
    _post_asi = ASICalculator()

    med = mediate_output(llm_response.response)
    asi_snap = _post_asi.compute(
        prompt=req.prompt,
        session_id=pre_result.request_id,  # use same session key
        tool_invoked=tool_names[0] if tool_names else None,
        response_token_count=len(llm_response.response.split()),
        blocked=False,
    )

    if not med.safe:
        logger.warning(
            "Output mediation blocked leakage for request %s: %s",
            pre_result.request_id,
            med.findings,
        )
        return InferenceResponse(
            response="[Response redacted by security mediator — potential data leakage detected]",
            tool_calls=[],
            metadata={
                "request_id": pre_result.request_id,
                "redacted": True,
                "findings_count": len(med.findings),
                "latency_ms": pre_result.latency_ms,
                "asi_score": asi_snap.asi,
            },
            request_id=pre_result.request_id,
            timestamp=datetime.utcnow(),
        )

    return InferenceResponse(
        response=llm_response.response,
        tool_calls=[],
        metadata={
            "request_id": pre_result.request_id,
            "latency_ms": pre_result.latency_ms,
            "tier_reached": pre_result.tier_reached,
            "risk_score": pre_result.risk_score,
            "asi_score": asi_snap.asi,
            "asi_alert": asi_snap.alert,
            "capability_token_issued": bool(pre_result.capability_token),
        },
        request_id=pre_result.request_id,
        timestamp=datetime.utcnow(),
    )


# ── Agent Chat Endpoint ──────────────────────────────────────────────────
@router.get("/chat", include_in_schema=False)
async def chat_get_info():
    """Information about the chat endpoint for accidental GET requests."""
    return {
        "status": "API active",
        "message": "This is a REST API endpoint. For the Chat UI, please visit http://localhost:3000/chat",
        "backend_version": settings.app_version,
        "endpoint": "/v1/agent/chat (POST)"
    }

@router.post("/chat", response_model=AgentChatResponse)
@router.post("/v1/chat", response_model=AgentChatResponse)
@router.post("/v1/agent/chat", response_model=AgentChatResponse)
async def agent_chat(
    req: AgentChatRequest,
    # user=Depends(get_current_user),
    # _rl=Depends(rate_limit_dependency),
):
    """
    Agent-routed chat endpoint.
    
    Flow:
      1. Security pipeline screens the prompt (L1 → L2 → L3)
      2. Agent Router classifies intent → selects agent
      3. Selected agent processes the request with capability tokens
      4. Output passes through the Output Mediator
      5. Response returned with full security metadata
    """
    t0 = time.monotonic()
    session_id = req.session_id or f"sess_{uuid.uuid4().hex[:8]}"

    # Phase 1: Pre-agent security screening
    inference_req = InferenceRequest(
        user_id=req.user_id,
        prompt=req.prompt,
        conversation_id=session_id,
        is_security_enabled=req.is_security_enabled,
    )
    pre_result = await orchestrator.process(inference_req)

    if pre_result.decision == "block":
        return AgentChatResponse(
            response=f"[BLOCKED] Your request was flagged by our security system. Reason: {pre_result.reason}",
            agent_used="security_gateway",
            request_id=pre_result.request_id,
            session_id=session_id,
            security_metadata={
                "decision": "block",
                "risk_score": pre_result.risk_score,
                "reason": pre_result.reason,
                "tier_reached": pre_result.tier_reached,
                "asi_score": pre_result.asi_score,
            },
            execution_time_ms=round((time.monotonic() - t0) * 1000, 2),
        )

    # Phase 2: Route to agent (Detect slash commands first)
    target_agent = None
    prompt_to_process = req.prompt.strip()

    # Priority 1: Explicit agent_name in request
    logger.info("Routing request: agent_name='%s', registry=%s", req.agent_name, agent_registry.agent_names)
    if req.agent_name and req.agent_name in agent_registry:
        target_agent = agent_registry.get_agent(req.agent_name)
    
    # Priority 2: Slash command prefix in prompt (e.g. /hr_database hello)
    elif prompt_to_process.startswith("/"):
        import re
        cmd_match = re.match(r"^/(\w+)\s*(.*)", prompt_to_process)
        if cmd_match:
            cmd_name = cmd_match.group(1)
            # Try to match cmd_name directly or with agent_registry keys
            if cmd_name in agent_registry:
                target_agent = agent_registry.get_agent(cmd_name)
                prompt_to_process = cmd_match.group(2) # Strip the command
            else:
                # Special cases for commands if names differ
                found = False
                for a in agent_registry.list_agents():
                    if a["name"] == cmd_name:
                        target_agent = agent_registry.get_agent(a["name"])
                        prompt_to_process = cmd_match.group(2)
                        found = True
                        break
    
    # Priority 3: Auto-classify intent
    if not target_agent:
        agent_name = await agent_router.classify(prompt_to_process)
        target_agent = agent_registry.get_agent(agent_name) if agent_name else None

    if target_agent is None:
        return AgentChatResponse(
            response="I'm not sure which department can help with that. Available agents: " +
                     ", ".join(a["name"] for a in agent_registry.list_agents()),
            agent_used="router",
            request_id=pre_result.request_id,
            session_id=session_id,
            security_metadata={
                "decision": pre_result.decision,
                "risk_score": pre_result.risk_score,
            },
            execution_time_ms=round((time.monotonic() - t0) * 1000, 2),
        )

    # Phase 3: Agent processes the request
    agent_response = await target_agent.process(
        prompt=prompt_to_process,
        session_id=session_id,
        risk_score=pre_result.risk_score,
        model=req.model,
        is_security_enabled=req.is_security_enabled,
    )

    # Phase 4: Post-agent output mediation
    from backend.gateway.security.output_mediator import mediate_output
    output_check = mediate_output(agent_response.response, enabled=req.is_security_enabled)

    if not output_check.safe:
        logger.warning(
            "Agent '%s' output caught by mediator: %s",
            target_agent.name, output_check.findings,
        )
        final_response = output_check.redacted_text
    else:
        final_response = agent_response.response

    elapsed_ms = round((time.monotonic() - t0) * 1000, 2)

    # Final Audit Log (Optional but helpful for Dashboard complete view)
    from backend.layer5_orchestration.orchestrator import _audit
    _audit.log_event({
        "request_id": agent_response.request_id,
        "user_id": req.user_id,
        "session_id": session_id,
        "agent_used": agent_response.agent_name,
        "decision": "allow", # If we reached here, it was allowed
        "risk_score": pre_result.risk_score,
        "latency_ms": elapsed_ms,
        "status": "completed",
        "output_safe": output_check.safe
    })

    return AgentChatResponse(
        response=final_response,
        agent_used=agent_response.agent_name,
        request_id=agent_response.request_id,
        session_id=session_id,
        tools_invoked=[t.tool_name for t in agent_response.tools_invoked],
        capability_token_issued=bool(agent_response.capability_token),
        security_metadata={
            "decision": pre_result.decision,
            "risk_score": pre_result.risk_score,
            "asi_score": pre_result.asi_score,
            "asi_alert": pre_result.asi_alert,
            "output_safe": output_check.safe,
            "output_findings_count": len(output_check.findings),
            "tier_reached": pre_result.tier_reached,
            "effective_scope": agent_response.metadata.get("effective_scope", []),
        },
        execution_time_ms=elapsed_ms,
    )


@router.get("/v1/agents")
async def list_agents():
    """List all available agents and their capabilities."""
    return {
        "agents": agent_registry.list_agents(),
        "total": len(agent_registry),
    }


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


@router.get("/v1/sessions")
async def list_sessions():
    """List all active chat sessions and their titles."""
    from backend.storage.chat_history import chat_memory
    return {"sessions": chat_memory.list_sessions()}


@router.get("/v1/history/{session_id}")
async def get_history(session_id: str):
    """Retrieve full message history for a specific session."""
    from backend.storage.chat_history import chat_memory
    return {"messages": chat_memory.get_history(session_id)}

@router.delete("/v1/history/{session_id}")
async def delete_history(session_id: str):
    """Permanently delete a session and its history."""
    from backend.storage.chat_history import chat_memory
    chat_memory.delete_session(session_id)
    return {"status": "success", "session_id": session_id}


@router.get("/v1/models")
async def list_models():
    """List all available local LLM models (via Ollama)."""
    client = get_llm_client()
    if hasattr(client, "list_models"):
        models = await client.list_models()
        return {"models": models}
    return {"models": []}



