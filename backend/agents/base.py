"""
BaseAgent — abstract base class for all Rectitude.AI agents.

Every agent in the system inherits from this class. It defines the contract:
  - name, description, system_prompt: identity
  - allowed_tools: list of tool names this agent may invoke
  - process(): the main execution method

Security integration:
  - Before process() runs, the security orchestrator has already screened
    the user prompt (L1 regex, L2 ML, L3 ASI).
  - Tool calls from the agent are verified via CapabilityTokenService (L2)
    before actual execution.
  - Agent responses pass through the OutputMediator (post-LLM) for
    PII/credential leakage scanning.
  - The DatabaseTool itself masks sensitive columns by default.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import time
import uuid

from backend.layer2_crypto.capability_tokens import CapabilityTokenService
from backend.storage.chat_history import chat_memory
from backend.utils.logging import get_logger

logger = get_logger(__name__)

_token_svc = CapabilityTokenService()

class AgentTool(ABC):
    """
    Base class for all tools that agents can use.
    Provides a name, description, and an execute() method.
    """
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the tool logic with given parameters."""
        ...


@dataclass
class ToolInvocation:
    """Record of a single tool call made by an agent."""
    tool_name: str
    parameters: Dict[str, Any]
    result: Any = None
    authorized: bool = False
    rejection_reason: str = ""
    execution_time_ms: float = 0.0


@dataclass
class ToolCheck:
    """Result of a tool verification check."""
    authorized: bool
    rejection_reason: str = ""


@dataclass
class AgentResponse:
    """Standardized response from any agent."""
    agent_name: str
    response: str
    tools_invoked: List[ToolInvocation] = field(default_factory=list)
    session_id: str = ""
    request_id: str = ""
    execution_time_ms: float = 0.0
    capability_token: str = ""
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the Rectitude.AI system.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name for this agent (e.g. 'hr_database')."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of this agent's purpose."""
        ...

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """System prompt that constrains this agent's LLM instance."""
        ...

    @property
    @abstractmethod
    def allowed_tools(self) -> List[str]:
        """List of tool names this agent is authorized to use."""
        ...

    def __init__(self):
        self._tools: Dict[str, AgentTool] = {}

    def register_tool(self, tool: AgentTool):
        """Register a tool instance with this agent."""
        self._tools[tool.name] = tool

    async def call_tool(self, tool_name: str, session_id: str, **kwargs) -> Any:
        """Execute a tool logic."""
        if tool_name not in self._tools:
            raise ValueError(f"Tool {tool_name} not found for agent {self.name}")
        return await self._tools[tool_name].execute(**kwargs)

    def verify_tool_call(self, token: str, tool_name: str) -> ToolCheck:
        """
        Standardized tool verification for any agent.
        Checks the capability token against the requested tool name.
        """
        allowed, reason = _token_svc.verify_tool_call(token, tool_name)
        return ToolCheck(authorized=allowed, rejection_reason=reason)

    @abstractmethod
    async def _execute(
        self,
        prompt: str,
        session_id: str,
        context: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None,
        is_security_enabled: bool = True,
        messages: Optional[List[dict]] = None,
    ) -> str:
        ...

    async def process(
        self,
        prompt: str,
        session_id: str,
        risk_score: float = 0.0,
        context: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None,
        is_security_enabled: bool = True,
    ) -> AgentResponse:
        t0 = time.monotonic()
        request_id = str(uuid.uuid4())[:12]

        # Issue a scoped capability token
        scope = _token_svc.get_default_scope(risk_score)
        effective_scope = [t for t in scope if t in self.allowed_tools]
        capability_token = _token_svc.issue_token(session_id, effective_scope)

        logger.info(
            "[%s] Agent '%s' processing | session=%s risk=%.2f scope=%s",
            request_id, self.name, session_id, risk_score, effective_scope,
        )

        try:
            # Fetch history and add current user prompt
            history = chat_memory.get_history(session_id)
            chat_memory.add_message(session_id, "user", prompt)
            
            ctx = dict(context or {})
            ctx["_capability_token"] = capability_token
            ctx["_request_id"] = request_id
            ctx["_history"] = history # Formatted history for agent specific logic

            response_text = await self._execute(
                prompt=prompt, 
                session_id=session_id, 
                context=ctx, 
                model=model, 
                is_security_enabled=is_security_enabled,
                messages=chat_memory.get_history(session_id) # Direct message list
            )
            
            # Store assistant response in history
            chat_memory.add_message(session_id, "assistant", response_text)
            
            elapsed_ms = round((time.monotonic() - t0) * 1000, 2)

            return AgentResponse(
                agent_name=self.name,
                response=response_text,
                session_id=session_id,
                request_id=request_id,
                execution_time_ms=elapsed_ms,
                capability_token=capability_token,
                metadata={
                    "effective_scope": effective_scope,
                    "risk_score": risk_score,
                },
            )

        except Exception as e:
            elapsed_ms = round((time.monotonic() - t0) * 1000, 2)
            logger.error("[%s] Agent '%s' failed: %s", request_id, self.name, e)
            return AgentResponse(
                agent_name=self.name,
                response="I encountered an error processing your request.",
                session_id=session_id,
                request_id=request_id,
                execution_time_ms=elapsed_ms,
                capability_token=capability_token,
                error=str(e),
            )

    async def _generate_response(
        self,
        prompt: Optional[str] = None,
        system_prompt: Optional[str] = None,
        messages: Optional[List[dict]] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        client_type: str = "default"
    ) -> str:
        """Standardized helper for generating LLM responses with explicit system prompts and history."""
        from backend.gateway.llm.client import get_llm_client
        
        # Use agent's default system prompt if none provided
        effective_system = system_prompt or self.system_prompt
        
        try:
            client = get_llm_client(client_type=client_type, model_name=model)
            result = await client.generate(
                prompt=prompt,
                system_prompt=effective_system,
                messages=messages,
                temperature=temperature,
            )
            return result.response.strip()
        except Exception as e:
            logger.error("Agent '%s' LLM generation failed: %s", self.name, e)
            raise e

