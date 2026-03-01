"""Security validation using bandit (optional) and built-in pattern checks."""

from __future__ import annotations

import ast
import re

from vallm.core.proposal import Proposal
from vallm.scoring import Issue, Severity, ValidationResult
from vallm.validators.base import BaseValidator

# Built-in dangerous pattern checks (no external deps required)
_DANGEROUS_PATTERNS = [
    (r"\beval\s*\(", "Use of eval() is a security risk", "security.eval"),
    (r"\bexec\s*\(", "Use of exec() is a security risk", "security.exec"),
    (r"\b__import__\s*\(", "Use of __import__() is suspicious", "security.dynamic_import"),
    (r"\bos\.system\s*\(", "Use of os.system() — prefer subprocess", "security.os_system"),
    (r"\bpickle\.loads?\s*\(", "Unpickling untrusted data is dangerous", "security.pickle"),
    (r"\byaml\.load\s*\((?!.*Loader)", "yaml.load() without Loader is unsafe", "security.yaml"),
    (r"\bsubprocess\.\w+\(.*shell\s*=\s*True", "subprocess with shell=True", "security.shell"),
    (r"password\s*=\s*['\"]", "Hardcoded password detected", "security.hardcoded_password"),
    (r"(?:api[_-]?key|secret[_-]?key|token)\s*=\s*['\"]", "Hardcoded secret", "security.hardcoded_secret"),
]


class SecurityValidator(BaseValidator):
    """Tier 2: Security analysis using built-in patterns and optionally bandit."""

    tier = 2
    name = "security"
    weight = 1.5

    def validate(self, proposal: Proposal, context: dict) -> ValidationResult:
        issues: list[Issue] = []

        # Built-in pattern checks (work for any language)
        pattern_issues = self._check_patterns(proposal.code)
        issues.extend(pattern_issues)

        # Python-specific: AST-based checks
        if proposal.language == "python":
            ast_issues = self._check_python_ast(proposal.code)
            issues.extend(ast_issues)

        # Try bandit if available (Python only)
        if proposal.language == "python":
            bandit_issues = self._try_bandit(proposal.code)
            issues.extend(bandit_issues)

        if not issues:
            score = 1.0
        else:
            error_count = sum(1 for i in issues if i.severity == Severity.ERROR)
            warning_count = sum(1 for i in issues if i.severity == Severity.WARNING)
            score = max(0.0, 1.0 - error_count * 0.3 - warning_count * 0.1)

        return ValidationResult(
            validator=self.name,
            score=score,
            weight=self.weight,
            confidence=0.9,
            issues=issues,
        )

    def _check_patterns(self, code: str) -> list[Issue]:
        """Check for dangerous patterns using regex."""
        issues = []
        for line_no, line in enumerate(code.splitlines(), 1):
            for pattern, message, rule in _DANGEROUS_PATTERNS:
                if re.search(pattern, line):
                    issues.append(
                        Issue(
                            message=message,
                            severity=Severity.WARNING,
                            line=line_no,
                            rule=rule,
                        )
                    )
        return issues

    def _check_python_ast(self, code: str) -> list[Issue]:
        """AST-based security checks for Python."""
        issues = []
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return issues

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = self._get_func_name(node.func)
                if func_name == "eval":
                    issues.append(
                        Issue(
                            message="Direct eval() call detected",
                            severity=Severity.ERROR,
                            line=node.lineno,
                            rule="security.eval_ast",
                        )
                    )
                elif func_name == "exec":
                    issues.append(
                        Issue(
                            message="Direct exec() call detected",
                            severity=Severity.ERROR,
                            line=node.lineno,
                            rule="security.exec_ast",
                        )
                    )
        return issues

    @staticmethod
    def _get_func_name(node) -> str | None:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return node.attr
        return None

    @staticmethod
    def _try_bandit(code: str) -> list[Issue]:
        """Try to run bandit if installed."""
        try:
            from bandit.core.manager import BanditManager
            from bandit.core.config import BanditConfig
            import tempfile
            import os

            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(code)
                tmp_path = f.name

            try:
                b_conf = BanditConfig()
                b_mgr = BanditManager(b_conf, "file", False)
                b_mgr.discover_files([tmp_path])
                b_mgr.run_tests()

                issues = []
                for item in b_mgr.get_issue_list():
                    severity = Severity.WARNING
                    if item.severity == "HIGH":
                        severity = Severity.ERROR
                    issues.append(
                        Issue(
                            message=f"[bandit {item.test_id}] {item.text}",
                            severity=severity,
                            line=item.lineno,
                            rule=f"security.bandit.{item.test_id}",
                        )
                    )
                return issues
            finally:
                os.unlink(tmp_path)
        except ImportError:
            return []
        except Exception:
            return []
