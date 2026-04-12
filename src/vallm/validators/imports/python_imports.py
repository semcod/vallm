def _is_import_error_handler(handler: ast.ExceptHandler) -> bool:
    handler_type = handler.type
    if handler_type is None:
        return True

    if isinstance(handler_type, ast.Name):
        return handler_type.id in _IMPORT_ERROR_NAMES

    if isinstance(handler_type, ast.Tuple):
        return any(
            isinstance(element, ast.Name) and element.id in _IMPORT_ERROR_NAMES
            for element in handler_type.elts
        )

    return False


def _has_import_error_handler(handlers: list[ast.ExceptHandler]) -> bool:
    return any(_is_import_error_handler(handler) for handler in handlers)


def _collect_guarded_lines(tree: ast.AST) -> Set[int]:
    """Return line numbers of imports guarded by try/except ImportError."""
    guarded: Set[int] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Try):
            continue

        if not _has_import_error_handler(node.handlers):
            continue

        for stmt in node.body:
            for n in ast.walk(stmt):
                if isinstance(n, (ast.Import, ast.ImportFrom)):
                    guarded.add(n.lineno)
    return guarded
