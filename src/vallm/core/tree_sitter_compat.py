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


def node_start_row(node) -> int:
    start_point = getattr(node, "start_point", None)
    if start_point is not None:
        if callable(start_point):
            start_point = start_point()
        if hasattr(start_point, "row"):
            row = start_point.row
            return row() if callable(row) else int(row)
        if isinstance(start_point, (tuple, list)) and start_point:
            return int(start_point[0]) + 1
    start_position = getattr(node, "start_position", None)
    if start_position is not None:
        if callable(start_position):
            start_position = start_position()
        row = start_position.row
        return (row() if callable(row) else int(row)) + 1
    return 1


def node_text(node, source: str) -> str:
    text = getattr(node, "text", None)
    if text is not None:
        if callable(text):
            raw = text()
        else:
            raw = text
        if isinstance(raw, bytes):
            return raw.decode("utf-8")
        return str(raw)
    byte_range = getattr(node, "byte_range", None)
    if byte_range is not None:
        if callable(byte_range):
            byte_range = byte_range()
        start = byte_range.start
        end = byte_range.end
        return source[start:end]
    start_byte = getattr(node, "start_byte", None)
    end_byte = getattr(node, "end_byte", None)
    if start_byte is not None and end_byte is not None:
        start = start_byte() if callable(start_byte) else start_byte
        end = end_byte() if callable(end_byte) else end_byte
        return source[start:end]
    return ""


def node_child_by_field_name(node, field_name: str):
    child_by_field = getattr(node, "child_by_field_name", None)
    if child_by_field is None:
        return None
    child = child_by_field(field_name)
    return child() if callable(child) else child
