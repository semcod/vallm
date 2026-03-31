"""Go import validation."""

from typing import List, Dict, Any
from vallm.core.proposal import Proposal
from vallm.scoring import Issue, Severity, ValidationResult
from .base import BaseImportValidator

# Common Go standard library packages
_KNOWN_GO_MODULES = {
    "fmt", "os", "io", "strings", "strconv", "math", "time", "net",
    "http", "json", "log", "errors", "context", "sync", "bufio", "filepath",
    "runtime", "reflect", "sort", "bytes", "regexp", "encoding", "base64",
    "hex", "binary", "json", "xml", "gob", "csv", "syscall", "unsafe",
    "testing", "template", "html", "database", "sql", "crypto", "hash",
    "md5", "sha1", "sha256", "sha512", "aes", "cipher", "rand", "rsa",
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
            tree = parser.parse(code.encode("utf-8"))

            def walk(node):
                if node.type == "import_declaration":
                    for child in node.children:
                        if child.type == "import_spec":
                            path_node = child.child_by_field_name("path")
                            if path_node:
                                path = path_node.text.decode("utf-8").strip('"')
                                imports.append({"module": path, "line": node.start_point[0] + 1})
                        elif child.type == "import_spec_list":
                            for spec in child.children:
                                if spec.type == "import_spec":
                                    path_node = spec.child_by_field_name("path")
                                    if path_node:
                                        path = path_node.text.decode("utf-8").strip('"')
                                        imports.append({"module": path, "line": node.start_point[0] + 1})

                for child in node.children:
                    walk(child)

            walk(tree.root_node)
        except Exception:
            # Fallback: simple regex-based extraction
            import re
            pattern = r"import\s*\(?\s*\"([^\"]+)\""
            for match in re.finditer(pattern, code):
                imports.append({"module": match.group(1), "line": code[:match.start()].count('\n') + 1})

        return imports
    
    def module_exists(self, module_name: str) -> bool:
        """Check if a Go package is known."""
        # Standard library
        top_level = module_name.split("/")[0]
        if top_level in _KNOWN_GO_MODULES:
            return True
        # Common external packages (GitHub, etc.)
        if module_name.startswith("github.com/"):
            return True
        if module_name.startswith("golang.org/"):
            return True
        if module_name.startswith("google.golang.org/"):
            return True
        return False
