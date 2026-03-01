"""AST comparison utilities using tree-sitter and edit distance."""

from __future__ import annotations

import ast
from typing import Optional

from tree_sitter_language_pack import get_parser


def parse_code(code: str, language: str = "python"):
    """Parse code using tree-sitter and return the tree."""
    parser = get_parser(language)
    return parser.parse(code.encode("utf-8"))


def parse_python_ast(code: str) -> Optional[ast.AST]:
    """Parse Python code using the built-in ast module. Returns None on failure."""
    try:
        return ast.parse(code)
    except SyntaxError:
        return None


def normalize_python_ast(tree: ast.AST) -> str:
    """Normalize a Python AST by replacing identifiers with canonical names.

    This enables fingerprint-based comparison that ignores variable naming.
    """
    class Normalizer(ast.NodeTransformer):
        def __init__(self):
            self._name_map: dict[str, str] = {}
            self._counter = 0

        def _canonical(self, name: str) -> str:
            if name not in self._name_map:
                self._name_map[name] = f"var_{self._counter}"
                self._counter += 1
            return self._name_map[name]

        def visit_Name(self, node):
            node.id = self._canonical(node.id)
            return self.generic_visit(node)

        def visit_FunctionDef(self, node):
            node.name = self._canonical(node.name)
            return self.generic_visit(node)

        def visit_arg(self, node):
            node.arg = self._canonical(node.arg)
            return self.generic_visit(node)

    normalized = Normalizer().visit(ast.parse(ast.unparse(tree)))
    return ast.dump(normalized)


def python_ast_similarity(code1: str, code2: str) -> float:
    """Compute structural similarity between two Python code snippets.

    Returns a float between 0.0 and 1.0.
    """
    tree1 = parse_python_ast(code1)
    tree2 = parse_python_ast(code2)

    if tree1 is None or tree2 is None:
        return 0.0

    norm1 = normalize_python_ast(tree1)
    norm2 = normalize_python_ast(tree2)

    if norm1 == norm2:
        return 1.0

    # Use SequenceMatcher for similarity on AST dumps
    from difflib import SequenceMatcher

    return SequenceMatcher(None, norm1, norm2).ratio()


def tree_sitter_node_count(code: str, language: str = "python") -> int:
    """Count the number of nodes in a tree-sitter parse tree."""
    tree = parse_code(code, language)
    count = 0

    def _walk(node):
        nonlocal count
        count += 1
        for child in node.children:
            _walk(child)

    _walk(tree.root_node)
    return count


def tree_sitter_error_count(code: str, language: str = "python") -> int:
    """Count syntax errors reported by tree-sitter."""
    tree = parse_code(code, language)
    errors = 0

    def _walk(node):
        nonlocal errors
        if node.type == "ERROR" or node.is_missing:
            errors += 1
        for child in node.children:
            _walk(child)

    _walk(tree.root_node)
    return errors


def structural_diff_summary(code1: str, code2: str, language: str = "python") -> dict:
    """Return a summary of structural differences between two code snippets."""
    tree1 = parse_code(code1, language)
    tree2 = parse_code(code2, language)

    def _collect_types(node):
        types = []
        def _walk(n):
            types.append(n.type)
            for child in n.children:
                _walk(child)
        _walk(node)
        return types

    types1 = _collect_types(tree1.root_node)
    types2 = _collect_types(tree2.root_node)

    set1, set2 = set(types1), set(types2)
    return {
        "nodes_before": len(types1),
        "nodes_after": len(types2),
        "added_types": set2 - set1,
        "removed_types": set1 - set2,
        "common_types": set1 & set2,
    }
