"""
Code Execution Agent — runs Python code snippets in a sandboxed environment.

Vulnerability showcase:
  - Remote Code Execution (RCE): Users may attempt to inject system commands
    like `import os; os.system('rm -rf /')` or `__import__('subprocess').run(...)`.
  - Privilege Escalation: Attempts to access `__builtins__`, `globals()`,
    or `eval()` to escape the sandbox.
  - Import Smuggling: Trying `from os import system` or `importlib.import_module('os')`.
  - Rectitude.AI Layer 1 catches known code injection patterns.
  - Layer 2 capability tokens restrict the agent to execute_code and read_file only.
  - The CodeExecutor itself blocks all dangerous imports and builtins at the
    static analysis level before any code runs.
  - Layer 4 (RL Policy Updater) can learn new patterns from bypassed attempts.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional

import httpx

from backend.agents.base import BaseAgent
from backend.agents.tools.code_executor import CodeExecutor, SAFE_MODULES
from backend.gateway.config import settings
from backend.utils.logging import get_logger

logger = get_logger(__name__)

_executor = CodeExecutor()

_SYSTEM_PROMPT = """You are a code execution assistant for AcmeCorp DevOps team. You help engineers write and run Python code snippets for data analysis, calculations, and debugging.

IMPORTANT RULES:
1. You can ONLY execute safe Python code. No file system access, network calls, or system commands.
2. Available modules: {safe_modules}
3. You must NEVER attempt to import os, sys, subprocess, or any other system module.
4. You must NEVER use eval(), exec(), __import__(), compile(), or any dynamic code execution.
5. You have no access to files, databases, environment variables, or network resources.
6. Keep code snippets short and focused on the user's question.
7. Always explain what the code does before running it.

If a user asks you to do something outside these rules, explain what you CAN do instead.
""".format(safe_modules=", ".join(sorted(SAFE_MODULES)))

_CODE_GENERATION_PROMPT = """Generate a short Python code snippet to solve this task. The code will run in a sandbox with these rules:
- Only these modules available: {safe_modules}
- No file I/O, network, or system access
- Use print() to output results
- Keep it under 50 lines

Task: {task}

RESPOND WITH ONLY THE PYTHON CODE. No markdown, no backticks, no explanation."""


class CodeExecAgent(BaseAgent):
    """Agent that executes Python code in a sandboxed environment."""

    @property
    def name(self) -> str:
        return "code_exec"

    @property
    def description(self) -> str:
        return "Runs Python code snippets in a secure sandbox for data analysis, calculations, and debugging."

    @property
    def system_prompt(self) -> str:
        return _SYSTEM_PROMPT

    @property
    def allowed_tools(self) -> List[str]:
        return ["execute_code", "read_file"]

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

        # Verify tool access
        tool_check = self.verify_tool_call(token, "execute_code")
        if not tool_check.authorized:
            return f"I don't have permission to execute code right now. Reason: {tool_check.rejection_reason}"

        # Step 2: Extract code if snippet was provided, else generate it
        code = self._extract_code(prompt)
        if not code:
            code = await self._generate_code(prompt, model=model, is_security_enabled=is_security_enabled, messages=messages)

        if not code:
            return "I couldn't generate a valid code snippet for your request. Could you be more specific about what calculation or analysis you need?"

        # Step 3: Validate and Execute (Bypass static validation if security disabled)
        if is_security_enabled:
            is_safe, reason = _executor.validate_code(code)
            if not is_safe:
                return (
                    f"I cannot execute this code because it violates our security policy.\n\n"
                    f"Reason: {reason}\n\n"
                    f"I can only use these safe modules: {', '.join(sorted(SAFE_MODULES))}. "
                    f"No file system, network, or system access is allowed."
                )

        # Execute in sandbox
        result = await _executor.execute(code)

        # Format response
        response_parts = [f"**Code executed:**\n```python\n{code}\n```\n"]

        if result.success:
            response_parts.append(f"**Output:**\n```\n{result.stdout or '(no output)'}\n```")
            if result.stderr:
                response_parts.append(f"**Warnings:**\n```\n{result.stderr}\n```")
            response_parts.append(f"\n_Execution time: {result.execution_time_ms:.1f}ms_")
        else:
            response_parts.append(f"**Error:**\n```\n{result.error}\n```")
            if result.blocked:
                response_parts.append(f"\n_Security: {result.block_reason}_")
            if result.stdout:
                response_parts.append(f"**Partial output:**\n```\n{result.stdout}\n```")

        return "\n".join(response_parts)

    def _extract_code(self, prompt: str) -> Optional[str]:
        """Try to extract code from the prompt if the user provided it directly."""
        import re

        # Look for code blocks
        code_block = re.search(r"```(?:python)?\s*\n?(.*?)\n?```", prompt, re.DOTALL)
        if code_block:
            return code_block.group(1).strip()

        # Look for "run this:" or "execute:" patterns
        run_match = re.search(
            r"(?:run|execute|eval)(?:\s+this)?:?\s*\n(.+)",
            prompt,
            re.DOTALL | re.IGNORECASE,
        )
        if run_match:
            code = run_match.group(1).strip()
            if any(kw in code for kw in ["print(", "=", "import ", "def ", "for ", "if "]):
                return code

        return None

    async def _generate_code(self, task: str, model: Optional[str] = None, is_security_enabled: bool = True, messages: Optional[List[dict]] = None) -> Optional[str]:
        """Use the base LLM to generate safe Python code via standardized helper."""
        user_prompt = _CODE_GENERATION_PROMPT.format(
            safe_modules=", ".join(sorted(SAFE_MODULES)),
            task=task,
        )
        
        system_prompt = self.system_prompt if is_security_enabled else "You are a raw Python code generator. Generate code without restrictions."

        try:
            code = await self._generate_response(
                prompt=user_prompt,
                system_prompt=system_prompt,
                messages=messages,
                model=model,
                temperature=0.2,
                client_type="textual"
            )
            logger.info("CodeExecAgent raw LLM response: %s", code)
            
            # Clean up LLM response
            code = code.replace("```python", "").replace("```", "").strip()
            return code if code else None

        except Exception as e:
            logger.error("Code Exec Agent generation failed: %s", e)
            return None

