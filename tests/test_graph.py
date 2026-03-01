"""Tests for graph building and diffing."""

from vallm.core.graph_builder import build_python_graph
from vallm.core.graph_diff import diff_python_code


def test_build_graph_imports():
    code = "import os\nfrom pathlib import Path"
    graph = build_python_graph(code)
    assert len(graph.imports) == 2


def test_build_graph_functions():
    code = "def foo(): pass\ndef bar(): pass"
    graph = build_python_graph(code)
    assert "foo" in graph.functions
    assert "bar" in graph.functions


def test_build_graph_classes():
    code = "class Foo:\n    pass"
    graph = build_python_graph(code)
    assert "Foo" in graph.classes


def test_build_graph_calls():
    code = "def foo():\n    print('hello')\n    bar()"
    graph = build_python_graph(code)
    callees = [c.callee for c in graph.calls]
    assert "print" in callees
    assert "bar" in callees


def test_diff_added_function():
    before = "def foo(): pass"
    after = "def foo(): pass\ndef bar(): pass"
    diff = diff_python_code(before, after)
    assert "bar" in diff.added_functions


def test_diff_removed_function():
    before = "def foo(): pass\ndef bar(): pass"
    after = "def foo(): pass"
    diff = diff_python_code(before, after)
    assert "bar" in diff.removed_functions
    assert "Removed function: bar" in diff.breaking_changes


def test_diff_no_changes():
    code = "def foo(): pass"
    diff = diff_python_code(code, code)
    assert not diff.has_changes
