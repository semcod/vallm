"""Java import validation."""

from typing import List, Dict, Any

from vallm.core.tree_sitter_compat import node_children, node_kind, node_start_row, node_text, parse_source, tree_root
from .base import BaseImportValidator

# Common Java packages
_KNOWN_JAVA_MODULES = {
    "java.lang",
    "java.util",
    "java.io",
    "java.net",
    "java.time",
    "java.text",
    "java.math",
    "java.nio",
    "java.security",
    "java.sql",
    "javax.swing",
    "javax.servlet",
    "javax.persistence",
    "javax.annotation",
    "org.springframework",
    "org.junit",
    "org.apache",
    "com.google",
    "com.fasterxml",
    "org.slf4j",
    "lombok",
    "jakarta",
    "org.hibernate",
}


class JavaImportValidator(BaseImportValidator):
    """Java import validator."""

    def get_language(self) -> str:
        """Get language identifier."""
        return "java"

    def _get_error_message(self, module_name: str) -> str:
        """Get error message for missing package."""
        return f"Package '{module_name}' not found"

    def _get_rule_name(self) -> str:
        """Get rule name for validation errors."""
        return "java.import.resolvable"

    def extract_imports(self, code: str) -> List[Dict[str, Any]]:
        """Extract import statements from Java using tree-sitter."""
        imports = []
        try:
            from vallm.core.ast_compare import _cached_get_parser

            parser = _cached_get_parser("java")
            tree = parse_source(parser, code)

            def walk(node):
                if node_kind(node) == "import_declaration":
                    for child in node_children(node):
                        if node_kind(child) in {"scoped_identifier", "identifier"}:
                            module = node_text(child, code)
                            imports.append({"module": module, "line": node_start_row(node)})
                            break

                for child in node_children(node):
                    walk(child)

            walk(tree_root(tree))
        except Exception:
            pass

        return imports

    def module_exists(self, module_name: str) -> bool:
        """Check if a Java package is known."""
        top_level = module_name.rsplit(".", 1)[0] if "." in module_name else module_name
        for known in _KNOWN_JAVA_MODULES:
            if module_name.startswith(known) or known.startswith(top_level):
                return True
        if module_name.startswith("org.") or module_name.startswith("com."):
            return True
        return False
