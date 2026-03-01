"""Import validation: checks that all imported modules are resolvable."""

from __future__ import annotations

import ast
import importlib.util

from vallm.core.proposal import Proposal
from vallm.scoring import Issue, Severity, ValidationResult
from vallm.validators.base import BaseValidator

# Common stdlib/builtin modules that importlib.util.find_spec may not find
_KNOWN_MODULES = {
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


class ImportValidator(BaseValidator):
    """Tier 1: Validate that imports are resolvable."""

    tier = 1
    name = "imports"
    weight = 1.5

    def validate(self, proposal: Proposal, context: dict) -> ValidationResult:
        if proposal.language != "python":
            return ValidationResult(
                validator=self.name,
                score=1.0,
                weight=self.weight,
                confidence=0.5,
                details={"skipped": "non-python"},
            )

        issues = []
        try:
            tree = ast.parse(proposal.code)
        except SyntaxError:
            return ValidationResult(
                validator=self.name,
                score=0.0,
                weight=self.weight,
                confidence=1.0,
                issues=[Issue("Cannot parse code for import checking", Severity.ERROR)],
            )

        modules_checked = 0
        modules_found = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    modules_checked += 1
                    if self._module_exists(alias.name):
                        modules_found += 1
                    else:
                        issues.append(
                            Issue(
                                message=f"Module not found: {alias.name}",
                                severity=Severity.WARNING,
                                line=node.lineno,
                                rule="imports.missing",
                            )
                        )
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    modules_checked += 1
                    if self._module_exists(node.module):
                        modules_found += 1
                    else:
                        issues.append(
                            Issue(
                                message=f"Module not found: {node.module}",
                                severity=Severity.WARNING,
                                line=node.lineno,
                                rule="imports.missing",
                            )
                        )

        if modules_checked == 0:
            score = 1.0
        else:
            score = modules_found / modules_checked

        return ValidationResult(
            validator=self.name,
            score=score,
            weight=self.weight,
            confidence=0.8,
            issues=issues,
            details={"checked": modules_checked, "found": modules_found},
        )

    @staticmethod
    def _module_exists(module_name: str) -> bool:
        """Check if a module exists in the current environment."""
        top_level = module_name.split(".")[0]
        if top_level in _KNOWN_MODULES:
            return True
        try:
            return importlib.util.find_spec(top_level) is not None
        except (ModuleNotFoundError, ValueError):
            return False
