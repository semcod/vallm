"""Go import validation."""

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

# Common Go standard library packages
_KNOWN_GO_MODULES = {
    "fmt",
    "os",
    "io",
    "strings",
    "strconv",
    "math",
    "time",
    "net",
    "http",
    "json",
    "log",
    "errors",
    "context",
    "sync",
    "bufio",
    "filepath",
    "runtime",
    "reflect",
    "sort",
    "bytes",
    "regexp",
    "encoding",
    "base64",
    "hex",
    "binary",
    "json",
    "xml",
    "gob",
    "csv",
    "syscall",
    "unsafe",
    "testing",
    "template",
    "html",
    "database",
    "sql",
    "crypto",
    "hash",
    "md5",
    "sha1",
    "sha256",
    "sha512",
    "aes",
    "cipher",
    "rand",
    "rsa",
}


class GoImportValidator(BaseImportValidator):
    """Go import validator."""

    def get_language(self) -> str:
        """Get language identifier."""
        return "go"

    def _get_error_message(self, module_name: str) -> str:
        """Get error message for missing package."""
        return f"Package '{module_name}' not found"

    def _get_rule_name(self) -> str:
        """Get rule name for validation errors."""
        return "go.import.resolvable"

    def extract_imports(self, code: str) -> List[Dict[str, Any]]:
        """Extract import statements from Go using tree-sitter."""
        imports = []
        try:
            from vallm.core.ast_compare import _cached_get_parser

            parser = _cached_get_parser("go")
            tree = parse_source(parser, code)

            def walk(node):
                if node_kind(node) == "import_declaration":
                    for child in node_children(node):
                        if node_kind(child) == "import_spec":
                            path_node = node_child_by_field_name(child, "path")
                            if path_node:
                                path = node_text(path_node, code).strip('"')
                                imports.append({"module": path, "line": node_start_row(node)})
                        elif node_kind(child) == "import_spec_list":
                            for spec in node_children(child):
                                if node_kind(spec) == "import_spec":
                                    path_node = node_child_by_field_name(spec, "path")
                                    if path_node:
                                        path = node_text(path_node, code).strip('"')
                                        imports.append(
                                            {"module": path, "line": node_start_row(node)}
                                        )

                for child in node_children(node):
                    walk(child)

            walk(tree_root(tree))
        except Exception:
            import re

            pattern = r"import\s*\(?\s*\"([^\"]+)\""
            for match in re.finditer(pattern, code):
                imports.append(
                    {"module": match.group(1), "line": code[: match.start()].count("\n") + 1}
                )

        return imports

    def module_exists(self, module_name: str) -> bool:
        """Check if a Go package is known."""
        top_level = module_name.split("/")[0]
        if top_level in _KNOWN_GO_MODULES:
            return True
        if module_name.startswith("github.com/"):
            return True
        if module_name.startswith("golang.org/"):
            return True
        if module_name.startswith("google.golang.org/"):
            return True
        return False
