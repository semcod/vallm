"""Java import validation."""

from typing import List, Dict, Any
from vallm.core.proposal import Proposal
from vallm.scoring import Issue, Severity, ValidationResult
from .base import BaseImportValidator

# Common Java packages
_KNOWN_JAVA_MODULES = {
    "java.lang", "java.util", "java.io", "java.net", "java.time",
    "java.text", "java.math", "java.nio", "java.security", "java.sql",
    "javax.swing", "javax.servlet", "javax.persistence", "javax.annotation",
    "org.springframework", "org.junit", "org.apache", "com.google",
    "com.fasterxml", "org.slf4j", "lombok", "jakarta", "org.hibernate",
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
            parser = get_parser("java")
            tree = parser.parse(code.encode("utf-8"))

            def walk(node):
                if node.type == "import_declaration":
                    # Get full package path
                    for child in node.children:
                        if child.type == "scoped_identifier" or child.type == "identifier":
                            module = child.text.decode("utf-8")
                            imports.append({"module": module, "line": node.start_point[0] + 1})
                            break

                for child in node.children:
                    walk(child)

            walk(tree.root_node)
        except Exception:
            pass

        return imports
    
    def module_exists(self, module_name: str) -> bool:
        """Check if a Java package is known."""
        # Standard library packages
        top_level = module_name.rsplit(".", 1)[0] if "." in module_name else module_name
        for known in _KNOWN_JAVA_MODULES:
            if module_name.startswith(known) or known.startswith(top_level):
                return True
        # Common external packages
        if module_name.startswith("org.") or module_name.startswith("com."):
            return True
        return False
