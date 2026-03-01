"""Tests for AST comparison utilities."""

from vallm.core.ast_compare import (
    parse_code,
    parse_python_ast,
    python_ast_similarity,
    tree_sitter_node_count,
    tree_sitter_error_count,
)


def test_parse_code_python():
    tree = parse_code("def foo(): pass", "python")
    assert tree.root_node.type == "module"


def test_parse_code_javascript():
    tree = parse_code("const x = 1;", "javascript")
    assert tree.root_node is not None


def test_parse_python_ast_valid():
    result = parse_python_ast("x = 1")
    assert result is not None


def test_parse_python_ast_invalid():
    result = parse_python_ast("def foo(:")
    assert result is None


def test_similarity_identical():
    code = "def add(a, b): return a + b"
    assert python_ast_similarity(code, code) == 1.0


def test_similarity_renamed():
    code1 = "def add(a, b): return a + b"
    code2 = "def sum_vals(x, y): return x + y"
    sim = python_ast_similarity(code1, code2)
    assert sim > 0.8  # Structurally identical after normalization


def test_similarity_different():
    code1 = "def add(a, b): return a + b"
    code2 = "class Foo:\n    def __init__(self):\n        self.x = [1, 2, 3]"
    sim = python_ast_similarity(code1, code2)
    assert sim < 0.6


def test_node_count():
    count = tree_sitter_node_count("x = 1", "python")
    assert count > 0


def test_error_count_valid():
    errors = tree_sitter_error_count("x = 1", "python")
    assert errors == 0


def test_error_count_invalid():
    errors = tree_sitter_error_count("def foo(:", "python")
    assert errors > 0
