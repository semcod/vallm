"""Code graph analysis: import and call graph construction."""

from __future__ import annotations

import ast
from dataclasses import dataclass, field


@dataclass
class ImportEdge:
    """Represents an import dependency."""

    source_module: str
    imported_name: str
    alias: str | None = None
    line: int = 0


@dataclass
class CallEdge:
    """Represents a function call relationship."""

    caller: str
    callee: str
    line: int = 0


@dataclass
class CodeGraph:
    """A graph of code relationships (imports and calls)."""

    imports: list[ImportEdge] = field(default_factory=list)
    calls: list[CallEdge] = field(default_factory=list)
    functions: list[str] = field(default_factory=list)
    classes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Serialize to dict for comparison."""
        return {
            "imports": [(e.source_module, e.imported_name) for e in self.imports],
            "calls": [(e.caller, e.callee) for e in self.calls],
            "functions": sorted(self.functions),
            "classes": sorted(self.classes),
        }


def build_python_graph(code: str, module_name: str = "<module>") -> CodeGraph:
    """Build an import/call graph from Python source code."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return CodeGraph()

    graph = CodeGraph()
    current_scope = module_name

    class GraphVisitor(ast.NodeVisitor):
        def visit_Import(self, node):
            for alias in node.names:
                graph.imports.append(
                    ImportEdge(
                        source_module=alias.name,
                        imported_name=alias.name,
                        alias=alias.asname,
                        line=node.lineno,
                    )
                )
            self.generic_visit(node)

        def visit_ImportFrom(self, node):
            module = node.module or ""
            for alias in node.names:
                graph.imports.append(
                    ImportEdge(
                        source_module=module,
                        imported_name=alias.name,
                        alias=alias.asname,
                        line=node.lineno,
                    )
                )
            self.generic_visit(node)

        def visit_FunctionDef(self, node):
            nonlocal current_scope
            graph.functions.append(node.name)
            old_scope = current_scope
            current_scope = node.name
            self.generic_visit(node)
            current_scope = old_scope

        def visit_AsyncFunctionDef(self, node):
            self.visit_FunctionDef(node)

        def visit_ClassDef(self, node):
            graph.classes.append(node.name)
            self.generic_visit(node)

        def visit_Call(self, node):
            callee = _get_call_name(node.func)
            if callee:
                graph.calls.append(
                    CallEdge(caller=current_scope, callee=callee, line=node.lineno)
                )
            self.generic_visit(node)

    def _get_call_name(node) -> str | None:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            prefix = _get_call_name(node.value)
            if prefix:
                return f"{prefix}.{node.attr}"
            return node.attr
        return None

    GraphVisitor().visit(tree)
    return graph
