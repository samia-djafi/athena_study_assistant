"""
Safe mathematical calculator tool for CS/AI calculations.
Evaluates math expressions safely using AST validation without eval() vulnerabilities.
"""
import ast
import operator
import math
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Allowed operators
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

# Allowed math functions
SAFE_FUNCTIONS = {
    "sqrt": math.sqrt,
    "log": math.log,
    "log2": math.log2,
    "log10": math.log10,
    "exp": math.exp,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "ceil": math.ceil,
    "floor": math.floor,
    "comb": math.comb,
    "perm": math.perm,
    "factorial": math.factorial,
}

SAFE_CONSTANTS = {
    "pi": math.pi,
    "e": math.e,
}

class SafeEvaluator(ast.NodeVisitor):
    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise ValueError(f"Unsupported expression syntax: {type(node).__name__}")

    def visit_Expression(self, node):
        return self.visit(node.body)

    def visit_Constant(self, node):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Disallowed constant type: {type(node.value).__name__}")

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op_type = type(node.op)
        if op_type in SAFE_OPERATORS:
            if op_type == ast.Pow and (isinstance(right, (int, float)) and right > 1000):
                raise ValueError("Exponent too large to evaluate safely.")
            return SAFE_OPERATORS[op_type](left, right)
        raise ValueError(f"Disallowed binary operator: {op_type.__name__}")

    def visit_UnaryOp(self, node):
        operand = self.visit(node.operand)
        op_type = type(node.op)
        if op_type in SAFE_OPERATORS:
            return SAFE_OPERATORS[op_type](operand)
        raise ValueError(f"Disallowed unary operator: {op_type.__name__}")

    def visit_Name(self, node):
        if node.id in SAFE_CONSTANTS:
            return SAFE_CONSTANTS[node.id]
        raise ValueError(f"Undefined or restricted identifier: {node.id}")

    def visit_Call(self, node):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Only standard function calls are permitted.")
        func_name = node.func.id
        if func_name not in SAFE_FUNCTIONS:
            raise ValueError(f"Function '{func_name}' is not in the safe calculation whitelist.")
        args = [self.visit(arg) for arg in node.args]
        return SAFE_FUNCTIONS[func_name](*args)

def safe_calculate(expression: str) -> Dict[str, Any]:
    """
    Safely evaluate a mathematical expression.
    Returns: {"success": bool, "result": float/int or None, "error": str or None}
    """
    clean_expr = expression.strip()
    # Normalize common symbols
    clean_expr = clean_expr.replace("^", "**")
    try:
        tree = ast.parse(clean_expr, mode='eval')
        evaluator = SafeEvaluator()
        result = evaluator.visit(tree)
        return {
            "success": True,
            "expression": expression,
            "result": result,
            "formatted": f"{result:.6g}" if isinstance(result, float) else str(result),
            "error": None
        }
    except Exception as e:
        logger.warning(f"Safe calculator rejected '{expression}': {e}")
        return {
            "success": False,
            "expression": expression,
            "result": None,
            "formatted": None,
            "error": str(e)
        }
