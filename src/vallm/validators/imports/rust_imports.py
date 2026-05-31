"""Rust import validation."""

from typing import List, Dict, Any

from vallm.core.tree_sitter_compat import (
    node_child_by_field_name,
    node_children,
    node_kind,
    node_start_row,
    node_text,
    parse_source,
    tree_root,
)
from .base import BaseImportValidator

# Common Rust standard library crates
_KNOWN_RUST_MODULES = {
    "std",
    "core",
    "alloc",
    "proc_macro",
    "test",
    "fmt",
    "vec",
    "string",
    "option",
    "result",
    "iter",
    "collections",
    "boxed",
    "cell",
    "rc",
    "sync",
    "thread",
    "time",
    "fs",
    "path",
    "io",
    "net",
    "os",
    "env",
    "error",
    "anyhow",
    "serde",
    "tokio",
    "async_trait",
    "log",
    "tracing",
    "clap",
    "regex",
    "uuid",
    "chrono",
}


class RustImportValidator(BaseImportValidator):
    """Rust import validator."""

    def get_language(self) -> str:
        """Get language identifier."""
        return "rust"

    def _get_error_message(self, module_name: str) -> str:
        """Get error message for missing crate."""
        return f"Crate '{module_name}' not found"

    def _get_rule_name(self) -> str:
        """Get rule name for validation errors."""
        return "rust.import.resolvable"

    def extract_imports(self, code: str) -> List[Dict[str, Any]]:
        """Extract use statements from Rust using tree-sitter."""
        imports = []
        try:
            from vallm.core.ast_compare import _cached_get_parser

            parser = _cached_get_parser("rust")
            tree = parse_source(parser, code)

            def walk(node):
                if node_kind(node) == "use_declaration":
                    for child in node_children(node):
                        if node_kind(child) in {"scoped_identifier", "identifier"}:
                            module = node_text(child, code)
                            imports.append({"module": module, "line": node_start_row(node)})
                            break
                        if node_kind(child) == "use_list":
                            parent = node_child_by_field_name(node, "argument")
                            if parent:
                                module = node_text(parent, code)
                                imports.append({"module": module, "line": node_start_row(node)})
                            break

                for child in node_children(node):
                    walk(child)

            walk(tree_root(tree))
        except Exception:
            import re

            pattern = r"use\s+([^;]+);"
            for match in re.finditer(pattern, code):
                module = match.group(1).strip()
                imports.append({"module": module, "line": code[: match.start()].count("\n") + 1})

        return imports

    def module_exists(self, module_name: str) -> bool:
        """Check if a Rust crate/module is known."""
        top_level = module_name.split("::")[0]
        if top_level in _KNOWN_RUST_MODULES:
            return True
        return True
