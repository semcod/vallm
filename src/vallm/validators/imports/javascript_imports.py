"""JavaScript/TypeScript import validation."""

from typing import List, Dict, Any
from vallm.core.proposal import Proposal
from vallm.scoring import Issue, Severity, ValidationResult
from vallm.core.tree_sitter_compat import (
    node_child_by_field_name,
    node_children,
    node_kind,
    node_start_row,
    node_text,
    tree_root,
)
from .base import BaseImportValidator

# Common JavaScript/Node.js built-in modules
_KNOWN_JS_MODULES = {
    "fs",
    "path",
    "http",
    "https",
    "url",
    "util",
    "events",
    "stream",
    "crypto",
    "os",
    "buffer",
    "querystring",
    "child_process",
    "cluster",
    "console",
    "dgram",
    "dns",
    "net",
    "readline",
    "repl",
    "tls",
    "tty",
    "v8",
    "vm",
    "zlib",
    "worker_threads",
    "perf_hooks",
    "async_hooks",
    "assert",
    "constants",
    "domain",
    "punycode",
    "string_decoder",
    "sys",
}


class JavaScriptImportValidator(BaseImportValidator):
    """JavaScript/TypeScript import validator."""

    def __init__(self, language: str = "javascript"):
        self.language = language

    def validate(self, proposal: Proposal, context: dict) -> ValidationResult:
        """Validate JavaScript/TypeScript imports using tree-sitter."""
        issues = []
        imports = self.extract_imports(proposal.code)

        for import_info in imports:
            module_name = import_info["module"]
            line = import_info["line"]

            if not self.module_exists(module_name):
                issues.append(
                    Issue(
                        message=f"Module '{module_name}' not found",
                        severity=Severity.WARNING,  # Less strict for JS
                        line=line,
                        rule="js.import.resolvable",
                    )
                )

        return self.create_validation_result(
            issues, len(imports), len(imports) - len(issues), self.language
        )

    def extract_imports(self, code: str) -> List[Dict[str, Any]]:
        """Extract import statements from JavaScript/TypeScript using tree-sitter."""
        imports = []
        try:
            from vallm.core.ast_compare import _cached_get_parser

            parser = _cached_get_parser(self.language)
            tree = parser.parse(code)

            def walk(node):
                if node_kind(node) == "import_statement":
                    source = None
                    for child in node_children(node):
                        if node_kind(child) == "string":
                            source = node_text(child, code).strip("'\"")
                            break
                    if source:
                        imports.append({"module": source, "line": node_start_row(node)})

                elif node_kind(node) == "call_expression":
                    func = node_child_by_field_name(node, "function")
                    if func and node_text(func, code) == "require":
                        for child in node_children(node):
                            if node_kind(child) == "string":
                                source = node_text(child, code).strip("'\"")
                                imports.append({"module": source, "line": node_start_row(node)})
                                break

                for child in node_children(node):
                    walk(child)

            walk(tree_root(tree))
        except Exception:
            import re

            patterns = [
                r"import.*?from\s*['\"]([^'\"]+)['\"]",
                r"import\s*['\"]([^'\"]+)['\"]",
                r"require\s*\(\s*['\"]([^'\"]+)['\"]\s*\)",
            ]
            for pattern in patterns:
                for match in re.finditer(pattern, code):
                    imports.append(
                        {"module": match.group(1), "line": code[: match.start()].count("\n") + 1}
                    )

        return imports

    def module_exists(self, module_name: str) -> bool:
        """Check if a JavaScript/TypeScript module is known."""
        if module_name.startswith("./") or module_name.startswith("../"):
            return True
        if module_name.split("/")[0] in _KNOWN_JS_MODULES:
            return True
        if module_name.startswith("@"):
            return True
        return False

    def get_language(self) -> str:
        """Get the language identifier."""
        return self.language

    def _get_error_message(self, module_name: str) -> str:
        """Get error message for missing module."""
        return f"Module '{module_name}' not found"

    def _get_rule_name(self) -> str:
        """Get rule name for validation errors."""
        return "js.import.resolvable"
