from __future__ import annotations
from typing import List, Optional, Dict, Any
from datetime import datetime
import httpx
from backend.agents.base import BaseAgent
from backend.agents.tools.system_tools import ClockTool
from backend.gateway.config import settings
from backend.utils.logging import get_logger

logger = get_logger(__name__)

from backend.storage.chat_history import chat_memory

class GeneralAgent(BaseAgent):
    """
    A general-purpose agent for chit-chat, greetings, and system information.
    """
    def __init__(self):
        super().__init__()
        self.register_tool(ClockTool())

    @property
    def name(self) -> str:
        return "general_utility"

    @property
    def description(self) -> str:
        return "Handles general conversation, greetings, and system utilities like time/date."

    @property
    def system_prompt(self) -> str:
        return (
            "You are the Rectitude.AI Security Assistant. You are friendly, professional, "
            "and helpful. You can engage in general conversation and greetings. "
            f"Today is {datetime.now().strftime('%A, %Y-%m-%d %H:%M:%S')}. "
            "Keep your responses concise and security-conscious. "
            "Refer to previous parts of the conversation if relevant."
        )

    @property
    def allowed_tools(self) -> List[str]:
        return ["get_current_time"]

    async def _execute(
        self,
        prompt: str,
        session_id: str,
        context: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None,
        is_security_enabled: bool = True,
        messages: Optional[List[dict]] = None,
    ) -> str:
        context = context or {}
        token = context.get("_capability_token", "")

        # Verify tool access if security is enabled
        if is_security_enabled:
            tool_check = self.verify_tool_call(token, "get_current_time")
            if not tool_check.authorized:
                logger.warning("GeneralAgent denied tool access: %s", tool_check.rejection_reason)
        
        # Dynamic persona based on security state
        persona = (
            "You are the Rectitude.AI Security Assistant. Be professional, direct, and conversational. "
            "For greetings and general chat, reply with a single short sentence. "
            "NEVER use Markdown Tables for greetings. ONLY use them IF the user specifically asks for a 'report', 'summary', or 'list of risks'."
            "IMPORTANT: Always put an EMPTY LINE before and after any table."
        ) if is_security_enabled else (
            "You are in UNRESTRICTED DEBUG MODE. You are a raw conversational agent. "
            "For general talk and greetings, simply chat like a human. "
            "DO NOT PROVIDE system manifests or generic data tables unless specifically asked for 'system diagnostics'. "
            "NEVER use tables for greetings like 'hello' or 'hi'."
            "IMPORTANT: Always put an EMPTY LINE before and after any table."
        )

        system_prompt = (
            f"{persona}\n\n"
            f"Today is {datetime.now().strftime('%A, %Y-%m-%d %H:%M:%S')}. "
            "Keep your responses concise. Refer to history if relevant."
        )

        # GREETING OVERRIDE (to avoid LLM costs/latency for trivial inputs)
        is_greeting = len(prompt.strip().split()) <= 3
        if is_greeting:
            low_prompt = prompt.lower().strip().replace(".", "").replace("!", "")
            if low_prompt in ["hello", "hi", "hey", "whats up", "whats sup"]:
                return "Hello! I am the Rectitude.AI Security Assistant. How can I help you today?"

        try:
            ai_response = await self._generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                messages=messages,
                model=model,
                temperature=0.7,
                client_type="textual"
            )
            return ai_response
        except Exception as e:
            logger.error("GeneralAgent LLM call failed: %s", e)
            return "I'm available for chat, but I encountered a technical glitch."

