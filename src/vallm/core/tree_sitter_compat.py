"""Compatibility helpers for tree-sitter language-pack API changes."""

from __future__ import annotations


def tree_root(tree):
    root = tree.root_node
    return root() if callable(root) else root


def node_kind(node) -> str:
    if hasattr(node, "kind"):
        kind = node.kind
        return kind() if callable(kind) else kind
    type_attr = node.type
    return type_attr() if callable(type_attr) else type_attr


def node_child_count(node) -> int:
    count = node.child_count
    return count() if callable(count) else count


def node_child(node, index: int):
    return node.child(index)


def node_children(node):
    children = getattr(node, "children", None)
    if children is not None and not callable(children):
        return children
    return [node.child(index) for index in range(node_child_count(node))]


def node_is_error(node) -> bool:
    if hasattr(node, "is_error"):
        value = node.is_error
        if callable(value):
            return bool(value())
        return bool(value)
    return node_kind(node) == "ERROR"


def node_is_missing(node) -> bool:
    value = node.is_missing
    return value() if callable(value) else bool(value)
