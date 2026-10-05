"""
Safe calculator tool for mathematical evaluations in study sessions.
Uses AST parsing to avoid unsafe eval execution.
"""
import ast
import operator
import math
from typing import Union, Dict, Any

from core.logging_config import get_logger

logger = get_logger("tools.calculator")

# Allowed operations
SAFE_OPERATORS = {
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

SAFE_FUNCTIONS = {
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "log10": math.log10,
    "exp": math.exp,
    "abs": abs,
    "round": round,
    "pi": math.pi,
    "e": math.e,
}


def _eval_ast(node: ast.AST) -> Union[int, float]:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Unsupported constant type: {type(node.value)}")

    if isinstance(node, ast.BinOp):
        left = _eval_ast(node.left)
        right = _eval_ast(node.right)
        op_type = type(node.op)
        if op_type in SAFE_OPERATORS:
            return SAFE_OPERATORS[op_type](left, right)
        raise ValueError(f"Unsupported operator: {op_type}")

    if isinstance(node, ast.UnaryOp):
        operand = _eval_ast(node.operand)
        op_type = type(node.op)
        if op_type in SAFE_OPERATORS:
            return SAFE_OPERATORS[op_type](operand)
        raise ValueError(f"Unsupported unary operator: {op_type}")

    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id in SAFE_FUNCTIONS:
            args = [_eval_ast(arg) for arg in node.args]
            return SAFE_FUNCTIONS[node.func.id](*args)
        raise ValueError(f"Unsupported function call in expression")

    if isinstance(node, ast.Name) and node.id in SAFE_FUNCTIONS:
        return SAFE_FUNCTIONS[node.id]

    raise ValueError(f"Unsupported syntax tree element: {type(node)}")


def calculate(expression: str) -> Dict[str, Any]:
    """
    Safely evaluates mathematical expressions like '2 * (3 + 4)' or 'sqrt(144)'.
    """
    try:
        clean_expr = expression.strip()
        tree = ast.parse(clean_expr, mode='eval')
        result = _eval_ast(tree.body)
        return {
            "success": True,
            "expression": clean_expr,
            "result": result,
            "error": None
        }
    except Exception as e:
        logger.warning(f"Calculator failed to evaluate '{expression}': {e}")
        return {
            "success": False,
            "expression": expression,
            "result": None,
            "error": str(e)
        }
