"""Python import validation."""

import ast
import importlib.util
from typing import List, Dict, Any
from vallm.core.proposal import Proposal
from vallm.scoring import Issue, Severity, ValidationResult
from .base import BaseImportValidator

# Common stdlib/builtin modules that importlib.util.find_spec may not find
_KNOWN_PYTHON_MODULES = {
    "sys", "os", "re", "json", "math", "random", "datetime", "collections",
    "functools", "itertools", "pathlib", "typing", "dataclasses", "enum",
    "abc", "io", "string", "textwrap", "copy", "pprint", "warnings",
    "logging", "unittest", "contextlib", "operator", "hashlib", "hmac",
    "secrets", "struct", "time", "calendar", "locale", "decimal", "fractions",
    "statistics", "array", "bisect", "heapq", "queue", "types", "weakref",
    "inspect", "dis", "traceback", "gc", "argparse", "configparser", "csv",
    "sqlite3", "urllib", "http", "email", "html", "xml", "socket", "ssl",
    "select", "signal", "subprocess", "threading", "multiprocessing",
    "concurrent", "asyncio", "shutil", "tempfile", "glob", "fnmatch",
    "pickle", "shelve", "marshal", "dbm", "gzip", "bz2", "lzma", "zipfile",
    "tarfile", "zlib", "base64", "binascii", "codecs", "unicodedata",
    "difflib", "pdb", "profile", "timeit", "trace", "ast", "token",
    "tokenize", "importlib", "pkgutil", "platform", "errno", "ctypes",
}


class PythonImportValidator(BaseImportValidator):
    """Python-specific import validator."""
    
    def validate(self, proposal: Proposal, context: dict) -> ValidationResult:
        """Validate Python imports using AST."""
        issues = []
        try:
            tree = ast.parse(proposal.code)
            imports = self.extract_imports(proposal.code)
            
            for import_info in imports:
                module_name = import_info["module"]
                line = import_info["line"]
                
                if not self.module_exists(module_name):
                    issues.append(Issue(
                        message=f"Module '{module_name}' not found",
                        severity=Severity.ERROR,
                        line=line,
                        rule="python.import.resolvable"
                    ))
            
            return self.create_validation_result(
                issues, len(imports), len(imports) - len(issues), "python"
            )
            
        except SyntaxError as e:
            return ValidationResult(
                validator="imports.python",
                score=0.0,
                weight=self.weight,
                issues=[Issue(
                    message=f"Syntax error: {e}",
                    severity=Severity.ERROR,
                    line=e.lineno,
                    rule="python.syntax"
                )],
                details={"error": str(e), "language": "python"},
            )
    
    def extract_imports(self, code: str) -> List[Dict[str, Any]]:
        """Extract import statements from Python code using AST."""
        imports = []
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append({
                            "module": alias.name,
                            "line": node.lineno
                        })
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append({
                            "module": node.module,
                            "line": node.lineno
                        })
        except SyntaxError:
            pass
        
        return imports
    
    def module_exists(self, module_name: str) -> bool:
        """Check if a Python module exists in current environment."""
        top_level = module_name.split(".")[0]
        if top_level in _KNOWN_PYTHON_MODULES:
            return True
        try:
            return importlib.util.find_spec(top_level) is not None
        except (ModuleNotFoundError, ValueError):
            return False
