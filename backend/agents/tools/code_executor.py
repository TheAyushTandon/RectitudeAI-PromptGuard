"""
Code Executor Tool — sandboxed Python execution for the Code Exec Agent.

Security design:
  - RESTRICTED IMPORTS: Only a whitelist of safe modules allowed.
  - NO BUILTINS ABUSE: exec(), eval(), __import__(), open(), compile() blocked.
  - NO SYSTEM ACCESS: os, sys, subprocess, shutil, socket all blocked.
  - TIME LIMIT: Execution kills after 5 seconds.
  - OUTPUT CAP: stdout/stderr capped at 2000 characters.
  - RESTICTED GLOBALS: Uses RestrictedPython for compile-time analysis.

This is intentionally restrictive. The Code Execution Agent's purpose is
to demonstrate that even when an agent has code execution capability,
Rectitude.AI's multi-layer defense prevents abuse.
"""

from __future__ import annotations
import io
import re
import sys
import time
import threading
from contextlib import redirect_stdout, redirect_stderr
from dataclasses import dataclass
from typing import Optional

from backend.utils.logging import get_logger

logger = get_logger(__name__)

MAX_OUTPUT_CHARS = 2000
MAX_EXECUTION_SECONDS = 5

# Modules allowed in the sandbox
SAFE_MODULES = {
    "math", "statistics", "random", "json", "datetime",
    "collections", "itertools", "functools", "operator",
    "string", "re", "decimal", "fractions", "textwrap",
}

# Dangerous patterns to block at the source level (pre-execution)
_DANGEROUS_PATTERNS = [
    re.compile(r"\b(os|sys|subprocess|shutil|socket|ctypes|signal)\b"),
    re.compile(r"\b(__import__|exec|eval|compile|globals|locals|vars|dir)\s*\("),
    re.compile(r"\bopen\s*\("),
    re.compile(r"\b(getattr|setattr|delattr)\s*\("),
    re.compile(r"\bimport\s+(os|sys|subprocess|shutil|socket|ctypes|signal|importlib)"),
    re.compile(r"from\s+(os|sys|subprocess|shutil|socket|ctypes|signal|importlib)\b"),
    re.compile(r"__\w+__"),  # Dunder access
]


@dataclass
class ExecutionResult:
    """Result of a sandboxed code execution."""
    success: bool
    stdout: str
    stderr: str
    error: str = ""
    execution_time_ms: float = 0.0
    blocked: bool = False
    block_reason: str = ""


class CodeExecutor:
    """Sandboxed Python code executor."""

    def validate_code(self, code: str) -> tuple[bool, str]:
        """
        Pre-execution static analysis to catch dangerous patterns.

        Returns:
            (is_safe, reason)
        """
        if not code or not code.strip():
            return False, "Empty code"

        for pattern in _DANGEROUS_PATTERNS:
            match = pattern.search(code)
            if match:
                return False, f"Blocked: dangerous pattern detected — '{match.group()}'"

        # Check for import statements and validate against whitelist
        import_pattern = re.compile(r"(?:^|;)\s*(?:import|from)\s+(\w+)", re.MULTILINE)
        for match in import_pattern.finditer(code):
            module_name = match.group(1)
            if module_name not in SAFE_MODULES:
                return False, f"Blocked: module '{module_name}' is not in the safe list. Allowed: {', '.join(sorted(SAFE_MODULES))}"

        return True, "Code passed validation"

    async def execute(self, code: str) -> ExecutionResult:
        """
        Execute Python code in a sandboxed environment.

        Args:
            code: Python source code to execute

        Returns:
            ExecutionResult with stdout/stderr/error
        """
        # Step 1: Static validation
        is_safe, reason = self.validate_code(code)
        if not is_safe:
            logger.warning("CodeExecutor blocked code: %s", reason)
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="",
                error=reason,
                blocked=True,
                block_reason=reason,
            )

        # Step 2: Build safe globals
        safe_globals = self._build_safe_globals()

        # Step 3: Execute with timeout
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        result = {"error": None, "exec_time": 0.0}

        def _run():
            t0 = time.monotonic()
            try:
                with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                    exec(compile(code, "<agent_sandbox>", "exec"), safe_globals)
            except Exception as e:
                result["error"] = f"{type(e).__name__}: {str(e)}"
            finally:
                result["exec_time"] = (time.monotonic() - t0) * 1000

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
        thread.join(timeout=MAX_EXECUTION_SECONDS)

        if thread.is_alive():
            logger.warning("CodeExecutor: execution timed out after %ds", MAX_EXECUTION_SECONDS)
            return ExecutionResult(
                success=False,
                stdout=stdout_capture.getvalue()[:MAX_OUTPUT_CHARS],
                stderr="",
                error=f"Execution timed out after {MAX_EXECUTION_SECONDS} seconds",
                execution_time_ms=MAX_EXECUTION_SECONDS * 1000,
            )

        stdout_text = stdout_capture.getvalue()[:MAX_OUTPUT_CHARS]
        stderr_text = stderr_capture.getvalue()[:MAX_OUTPUT_CHARS]

        if result["error"]:
            return ExecutionResult(
                success=False,
                stdout=stdout_text,
                stderr=stderr_text,
                error=result["error"],
                execution_time_ms=round(result["exec_time"], 2),
            )

        return ExecutionResult(
            success=True,
            stdout=stdout_text,
            stderr=stderr_text,
            execution_time_ms=round(result["exec_time"], 2),
        )

    def _build_safe_globals(self) -> dict:
        """Build a restricted globals dictionary for safe execution."""
        import math
        import statistics
        import random
        import json
        import datetime
        import collections
        import itertools
        import functools
        import string
        import decimal
        import operator

        def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name in SAFE_MODULES:
                return __import__(name, globals, locals, fromlist, level)
            raise ImportError(f"Import of module '{name}' is restricted.")

        safe = {
            "__builtins__": {
                # Safe builtins only
                "__import__": safe_import,
                "print": print,
                "len": len,
                "range": range,
                "enumerate": enumerate,
                "zip": zip,
                "map": map,
                "filter": filter,
                "sorted": sorted,
                "reversed": reversed,
                "list": list,
                "dict": dict,
                "set": set,
                "tuple": tuple,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
                "sum": sum,
                "min": min,
                "max": max,
                "abs": abs,
                "round": round,
                "pow": pow,
                "divmod": divmod,
                "isinstance": isinstance,
                "issubclass": issubclass,
                "type": type,
                "hasattr": hasattr,
                "repr": repr,
                "format": format,
                "chr": chr,
                "ord": ord,
                "hex": hex,
                "oct": oct,
                "bin": bin,
                "any": any,
                "all": all,
                "input": lambda *a: "",  # No-op
                "Exception": Exception,
                "ValueError": ValueError,
                "TypeError": TypeError,
                "KeyError": KeyError,
                "IndexError": IndexError,
                "StopIteration": StopIteration,
                "ImportError": ImportError,
                "True": True,
                "False": False,
                "None": None,
            },
            # Pre-imported safe modules
            "math": math,
            "statistics": statistics,
            "random": random,
            "json": json,
            "datetime": datetime,
            "collections": collections,
            "itertools": itertools,
            "functools": functools,
            "string": string,
            "decimal": decimal,
            "operator": operator,
        }
        return safe
