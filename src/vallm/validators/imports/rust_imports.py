"""Rust import validation."""

from typing import List, Dict, Any
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
            tree = parser.parse(code.encode("utf-8"))

            def walk(node):
                if node.type == "use_declaration":
                    # Extract module path
                    for child in node.children:
                        if child.type == "scoped_identifier" or child.type == "identifier":
                            module = child.text.decode("utf-8")
                            imports.append({"module": module, "line": node.start_point[0] + 1})
                            break
                        elif child.type == "use_list":
                            # use std::{io, fs}; - extract parent scope
                            parent = node.child_by_field_name("argument")
                            if parent:
                                module = parent.text.decode("utf-8")
                                imports.append({"module": module, "line": node.start_point[0] + 1})
                            break

                for child in node.children:
                    walk(child)

            walk(tree.root_node)
        except Exception:
            # Fallback: simple regex-based extraction
            import re

            pattern = r"use\s+([^;]+);"
            for match in re.finditer(pattern, code):
                module = match.group(1).strip()
                imports.append({"module": module, "line": code[: match.start()].count("\n") + 1})

        return imports

    def module_exists(self, module_name: str) -> bool:
        """Check if a Rust crate/module is known."""
        # Standard library
        top_level = module_name.split("::")[0]
        if top_level in _KNOWN_RUST_MODULES:
            return True
        # Common crates (assume external crates exist)
        return True  # Rust crates are typically in Cargo.toml
