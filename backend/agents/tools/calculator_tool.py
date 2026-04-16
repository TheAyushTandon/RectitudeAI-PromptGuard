"""
Calculator Tool — safe math evaluator for the Financial Advisor Agent.

Uses ast.literal_eval for simple expressions and a custom parser
for mathematical operations. No eval() or exec() used.
"""

from __future__ import annotations
import ast
import math
import operator
from typing import Any, Optional

from backend.utils.logging import get_logger

logger = get_logger(__name__)

# Safe operators for expression evaluation
_SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

# Safe math functions
_SAFE_FUNCS = {
    "abs": abs,
    "round": round,
    "max": max,
    "min": min,
    "sum": sum,
    "sqrt": math.sqrt,
    "log": math.log,
    "log10": math.log10,
    "ceil": math.ceil,
    "floor": math.floor,
    "pow": math.pow,
    "pi": math.pi,
    "e": math.e,
}


class CalculatorTool:
    """Safe mathematical expression evaluator."""

    def evaluate(self, expression: str) -> dict:
        """
        Safely evaluate a mathematical expression.

        Args:
            expression: Mathematical expression string (e.g., "2 + 3 * 4")

        Returns:
            Dict with 'result', 'expression', and optionally 'error'
        """
        if not expression or not expression.strip():
            return {"error": "Empty expression", "expression": expression}

        # Clean up the expression
        clean = expression.strip()

        try:
            # Parse the expression into an AST
            tree = ast.parse(clean, mode="eval")
            result = self._eval_node(tree.body)

            logger.info("Calculator: %s = %s", clean, result)
            return {
                "result": result,
                "expression": clean,
                "formatted": f"{clean} = {result}",
            }

        except (ValueError, TypeError, ZeroDivisionError) as e:
            return {"error": str(e), "expression": clean}
        except Exception as e:
            logger.warning("Calculator rejected expression '%s': %s", clean, e)
            return {"error": f"Cannot evaluate: {e}", "expression": clean}

    def _eval_node(self, node: ast.AST) -> Any:
        """Recursively evaluate AST nodes with safety checks."""
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError(f"Unsupported constant type: {type(node.value)}")

        elif isinstance(node, ast.BinOp):
            op_func = _SAFE_OPS.get(type(node.op))
            if op_func is None:
                raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)

            # Safety: prevent extreme exponentiation
            if isinstance(node.op, ast.Pow) and abs(right) > 100:
                raise ValueError("Exponent too large (max 100)")

            return op_func(left, right)

        elif isinstance(node, ast.UnaryOp):
            op_func = _SAFE_OPS.get(type(node.op))
            if op_func is None:
                raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")
            return op_func(self._eval_node(node.operand))

        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                if func_name in _SAFE_FUNCS:
                    func = _SAFE_FUNCS[func_name]
                    if callable(func):
                        args = [self._eval_node(arg) for arg in node.args]
                        return func(*args)
                    else:
                        return func  # Constants like pi, e
                raise ValueError(f"Function '{func_name}' is not allowed")
            raise ValueError("Only named function calls are allowed")

        elif isinstance(node, ast.Name):
            if node.id in _SAFE_FUNCS:
                val = _SAFE_FUNCS[node.id]
                if not callable(val):
                    return val  # Constants
            raise ValueError(f"Unknown variable: {node.id}")

        else:
            raise ValueError(f"Unsupported expression type: {type(node).__name__}")
