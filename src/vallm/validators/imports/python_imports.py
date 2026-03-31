"""Python import validation."""

import ast
import importlib.util
from pathlib import Path
from typing import List, Dict, Any, Set
from vallm.core.proposal import Proposal
from vallm.scoring import Issue, Severity, ValidationResult
from .base import BaseImportValidator

_IMPORT_ERROR_NAMES = frozenset(("ImportError", "ModuleNotFoundError"))


def _collect_guarded_lines(tree: ast.AST) -> Set[int]:
    """Return line numbers of imports guarded by try/except ImportError."""
    guarded: Set[int] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Try):
            continue
        catches_import_error = any(
            h.type is None
            or (isinstance(h.type, ast.Name) and h.type.id in _IMPORT_ERROR_NAMES)
            or (
                isinstance(h.type, ast.Tuple)
                and any(
                    isinstance(e, ast.Name) and e.id in _IMPORT_ERROR_NAMES
                    for e in h.type.elts
                )
            )
            for h in node.handlers
        )
        if catches_import_error:
            for stmt in node.body:
                for n in ast.walk(stmt):
                    if isinstance(n, (ast.Import, ast.ImportFrom)):
                        guarded.add(n.lineno)
    return guarded

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


_module_exists_cache: dict[str, bool] = {}
_local_modules: frozenset[str] | None = None


def _get_local_modules() -> frozenset[str]:
    """Pre-scan cwd once for local packages/modules."""
    global _local_modules
    if _local_modules is None:
        cwd = Path.cwd()
        found: set[str] = set()
        for p in cwd.iterdir():
            if p.is_dir() and (p / "__init__.py").exists():
                found.add(p.name)
            elif p.is_file() and p.suffix == ".py" and p.stem != "__init__":
                found.add(p.stem)
        _local_modules = frozenset(found)
    return _local_modules


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
            guarded = _collect_guarded_lines(tree)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    if node.lineno in guarded:
                        continue
                    for alias in node.names:
                        imports.append({
                            "module": alias.name,
                            "line": node.lineno
                        })
                elif isinstance(node, ast.ImportFrom):
                    if node.level > 0 or node.lineno in guarded:
                        continue
                    if node.module:
                        imports.append({
                            "module": node.module,
                            "line": node.lineno
                        })
        except SyntaxError:
            pass

        return imports
    
    def module_exists(self, module_name: str) -> bool:
        """Check if a Python module exists in current environment (cached)."""
        top_level = module_name.split(".")[0]
        if top_level in _KNOWN_PYTHON_MODULES:
            return True

        cached = _module_exists_cache.get(top_level)
        if cached is not None:
            return cached

        found = False
        try:
            if importlib.util.find_spec(top_level) is not None:
                found = True
        except (ImportError, ValueError):
            pass

        if not found:
            found = top_level in _get_local_modules()

        _module_exists_cache[top_level] = found
        return found
    
    def get_language(self) -> str:
        """Get the language identifier."""
        return "python"
    
    def _get_error_message(self, module_name: str) -> str:
        """Get error message for missing module."""
        return f"Module '{module_name}' not found"
    
    def _get_rule_name(self) -> str:
        """Get rule name for validation errors."""
        return "python.import.resolvable"
