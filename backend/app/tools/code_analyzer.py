"""
Safe static code analyzer for Athena's Coding Agent.
Performs AST parsing, complexity estimation, and security linting WITHOUT executing user code on the host machine.
"""
import ast
import logging
from typing import Dict, Any, List
from app.models.schemas import CodeAnalysisResult

logger = logging.getLogger(__name__)

DANGEROUS_CALLS = {
    "eval", "exec", "compile", "__import__", "globals", "locals"
}

DANGEROUS_MODULES = {
    "os", "sys", "subprocess", "shutil", "socket", "pty", "commands", "pickle"
}

class StaticVisitor(ast.NodeVisitor):
    def __init__(self):
        self.loops = 0
        self.max_loop_depth = 0
        self._current_depth = 0
        self.has_recursion = False
        self.function_names = set()
        self.dangerous_found = []
        self.issues = []

    def visit_FunctionDef(self, node):
        self.function_names.add(node.name)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self.function_names.add(node.name)
        self.generic_visit(node)

    def visit_For(self, node):
        self.loops += 1
        self._current_depth += 1
        if self._current_depth > self.max_loop_depth:
            self.max_loop_depth = self._current_depth
        self.generic_visit(node)
        self._current_depth -= 1

    def visit_While(self, node):
        self.loops += 1
        self._current_depth += 1
        if self._current_depth > self.max_loop_depth:
            self.max_loop_depth = self._current_depth
        self.generic_visit(node)
        self._current_depth -= 1

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name in self.function_names:
                self.has_recursion = True
            if func_name in DANGEROUS_CALLS:
                self.dangerous_found.append(f"Dangerous builtin function call: '{func_name}'")
        elif isinstance(node.func, ast.Attribute):
            attr_name = node.func.attr
            if attr_name in ("system", "popen", "spawn"):
                self.dangerous_found.append(f"Potentially unsafe shell execution method: '{attr_name}'")
        self.generic_visit(node)

    def visit_Import(self, node):
        for alias in node.names:
            if alias.name.split('.')[0] in DANGEROUS_MODULES:
                self.dangerous_found.append(f"Restricted system module import: '{alias.name}'")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module and node.module.split('.')[0] in DANGEROUS_MODULES:
            self.dangerous_found.append(f"Restricted system module import from: '{node.module}'")
        self.generic_visit(node)

def analyze_python_code(code: str) -> CodeAnalysisResult:
    """
    Statically analyzes Python code.
    Guarantees:
    - Never executes arbitrary user code on the host machine.
    - Sets has_executed = False.
    - Provides AST-grounded complexity and security analysis.
    """
    clean_code = code.strip()
    if not clean_code:
        return CodeAnalysisResult(
            language="python",
            is_safe=True,
            static_summary="Empty code snippet provided.",
            ast_valid=True,
            complexity="O(1)",
            suggested_fixes=[],
            has_executed=False
        )

    try:
        tree = ast.parse(clean_code)
    except SyntaxError as se:
        return CodeAnalysisResult(
            language="python",
            is_safe=True,
            static_summary=f"Syntax Error at line {se.lineno}: {se.msg}",
            ast_valid=False,
            complexity="Undefined (invalid syntax)",
            suggested_fixes=[f"Correct syntax at line {se.lineno}, col {se.offset}: '{se.text.strip() if se.text else ''}'"],
            has_executed=False
        )

    visitor = StaticVisitor()
    visitor.visit(tree)

    # Complexity heuristic
    if visitor.max_loop_depth >= 3:
        complexity = f"O(n^{visitor.max_loop_depth}) polynomial time"
    elif visitor.max_loop_depth == 2:
        complexity = "O(n^2) quadratic time (nested loops detected)"
    elif visitor.max_loop_depth == 1:
        complexity = "O(n) linear time (single loop detected)"
    elif visitor.has_recursion:
        complexity = "O(2^n) or O(n) recursive branching (inspect base cases and memoization)"
    else:
        complexity = "O(1) constant time"

    is_safe = len(visitor.dangerous_found) == 0
    suggested_fixes = []

    if visitor.dangerous_found:
        suggested_fixes.extend([f"Review security notice: {item}" for item in visitor.dangerous_found])
        summary = f"Code parsed with AST. Security Notice: {len(visitor.dangerous_found)} sensitive calls or imports detected. Code was NOT executed."
    else:
        summary = f"Valid Python syntax. Estimated time complexity: {complexity}. Static analysis completed without host execution."

    return CodeAnalysisResult(
        language="python",
        is_safe=is_safe,
        static_summary=summary,
        ast_valid=True,
        complexity=complexity,
        suggested_fixes=suggested_fixes,
        has_executed=False
    )
