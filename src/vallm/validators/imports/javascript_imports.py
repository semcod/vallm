"""JavaScript/TypeScript import validation."""

from typing import List, Dict, Any
from vallm.core.proposal import Proposal
from vallm.scoring import Issue, Severity, ValidationResult
from .base import BaseImportValidator

# Common JavaScript/Node.js built-in modules
_KNOWN_JS_MODULES = {
    "fs", "path", "http", "https", "url", "util", "events", "stream",
    "crypto", "os", "buffer", "querystring", "child_process", "cluster",
    "console", "dgram", "dns", "net", "readline", "repl", "tls", "tty",
    "v8", "vm", "zlib", "worker_threads", "perf_hooks", "async_hooks",
    "assert", "constants", "domain", "punycode", "string_decoder", "sys",
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
                issues.append(Issue(
                    message=f"Module '{module_name}' not found",
                    severity=Severity.WARNING,  # Less strict for JS
                    line=line,
                    rule="js.import.resolvable"
                ))
        
        return self.create_validation_result(
            issues, len(imports), len(imports) - len(issues), self.language
        )
    
    def extract_imports(self, code: str) -> List[Dict[str, Any]]:
        """Extract import statements from JavaScript/TypeScript using tree-sitter."""
        imports = []
        try:
            from tree_sitter_language_pack import get_parser
            parser = get_parser(self.language)
            tree = parser.parse(code.encode("utf-8"))

            def walk(node):
                # import x from 'module'
                # import { x } from 'module'
                # import 'module'
                if node.type == "import_statement":
                    source = None
                    for child in node.children:
                        if child.type == "string":
                            source = child.text.decode("utf-8").strip("'\"")
                            break
                    if source:
                        imports.append({"module": source, "line": node.start_point[0] + 1})

                # require('module')
                elif node.type == "call_expression":
                    func = node.child_by_field_name("function")
                    if func and func.text.decode("utf-8") == "require":
                        for child in node.children:
                            if child.type == "string":
                                source = child.text.decode("utf-8").strip("'\"")
                                imports.append({"module": source, "line": node.start_point[0] + 1})
                                break

                for child in node.children:
                    walk(child)

            walk(tree.root_node)
        except Exception:
            # Fallback: simple regex-based extraction
            import re
            # Match import statements and require calls
            patterns = [
                r"import.*?from\s*['\"]([^'\"]+)['\"]",
                r"import\s*['\"]([^'\"]+)['\"]",
                r"require\s*\(\s*['\"]([^'\"]+)['\"]\s*\)"
            ]
            for i, pattern in enumerate(patterns):
                for match in re.finditer(pattern, code):
                    imports.append({"module": match.group(1), "line": code[:match.start()].count('\n') + 1})

        return imports
    
    def module_exists(self, module_name: str) -> bool:
        """Check if a JavaScript/TypeScript module is known."""
        # Relative imports (start with ./ or ../)
        if module_name.startswith("./") or module_name.startswith("../"):
            return True
        # Node.js built-ins
        if module_name.split("/")[0] in _KNOWN_JS_MODULES:
            return True
        # @scoped packages - assume exists (can't verify without package.json)
        if module_name.startswith("@"):
            return True
        return False
