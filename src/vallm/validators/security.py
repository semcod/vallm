"""Security validation using bandit (optional) and built-in pattern checks."""

from __future__ import annotations

import ast
import re

from vallm.core.proposal import Proposal
from vallm.scoring import Issue, Severity, ValidationResult
from vallm.validators.base import BaseValidator

# Built-in dangerous pattern checks (no external deps required)
# Python patterns
_PYTHON_PATTERNS = [
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

# JavaScript/TypeScript patterns
_JS_PATTERNS = [
    (r"\beval\s*\(", "Use of eval() is a security risk", "security.eval"),
    (r"Function\s*\(", "Dynamic Function constructor is dangerous", "security.dynamic_function"),
    (r"innerHTML\s*=", "innerHTML can lead to XSS vulnerabilities", "security.innerhtml"),
    (r"document\.write\s*\(", "document.write can lead to XSS", "security.document_write"),
    (r"\.src\s*=\s*['\"]javascript:", "javascript: URL is dangerous", "security.javascript_url"),
    (r"new\s+Function\s*\(", "Dynamic Function constructor is dangerous", "security.dynamic_function"),
    (r"password\s*[=:]\s*['\"]", "Hardcoded password detected", "security.hardcoded_password"),
    (r"(?:api[_-]?key|secret|token)\s*[=:]\s*['\"]", "Hardcoded secret", "security.hardcoded_secret"),
    (r"localStorage\.setItem.*password", "Storing password in localStorage is insecure", "security.localStorage_password"),
    (r"child_process\.exec\s*\(", "child_process.exec with shell execution", "security.child_process_exec"),
]

# Go patterns
_GO_PATTERNS = [
    (r"os\.Exec\s*\(", "os.Exec can be dangerous", "security.os_exec"),
    (r"exec\.Command\s*\(.*sh\s*-c", "Shell command execution with user input", "security.shell_exec"),
    (r"template\.HTML\s*\(", "Unescaped HTML template output", "security.unescaped_html"),
    (r"template\.JS\s*\(", "Unescaped JavaScript template output", "security.unescaped_js"),
    (r"password\s*:=\s*[\"']", "Hardcoded password detected", "security.hardcoded_password"),
    (r"(?:apiKey|secret|token)\s*:=\s*[\"']", "Hardcoded secret", "security.hardcoded_secret"),
    (r"sql\.Query\s*\(.*\+", "SQL query with string concatenation", "security.sql_injection"),
    (r"fmt\.Sprintf.*SELECT.*WHERE", "SQL query with Sprintf", "security.sql_sprintf"),
]

# Rust patterns
_RUST_PATTERNS = [
    (r"unsafe\s*\{", "Unsafe block - review carefully", "security.unsafe_block"),
    (r"std::mem::transmute", "transmute can lead to undefined behavior", "security.transmute"),
    (r"std::ptr::", "Raw pointer operations are dangerous", "security.raw_pointer"),
    (r"unwrap\s*\(\)", "unwrap() can panic - consider proper error handling", "security.unwrap"),
    (r"expect\s*\(\s*[\"']", "expect() with hardcoded message", "security.expect"),
    (r"password\s*=\s*[\"']", "Hardcoded password detected", "security.hardcoded_password"),
    (r"(?:api_key|secret|token)\s*=\s*[\"']", "Hardcoded secret", "security.hardcoded_secret"),
    (r"format!.*SELECT.*WHERE", "SQL query with format!", "security.sql_format"),
]

# Java patterns
_JAVA_PATTERNS = [
    (r"Runtime\.getRuntime\(\)\.exec", "Runtime.exec can be dangerous", "security.runtime_exec"),
    (r"ProcessBuilder.*sh\s+-c", "Shell command execution", "security.shell_exec"),
    (r"Class\.forName\s*\(", "Dynamic class loading", "security.dynamic_class"),
    (r"ScriptEngine\.eval\s*\(", "Script engine eval is dangerous", "security.script_eval"),
    (r"password\s*=\s*[\"']", "Hardcoded password detected", "security.hardcoded_password"),
    (r"(?:apiKey|secret|token)\s*=\s*[\"']", "Hardcoded secret", "security.hardcoded_secret"),
    (r"Statement\.executeQuery.*\+", "SQL query with string concatenation", "security.sql_injection"),
    (r"String\.format.*SELECT.*WHERE", "SQL query with String.format", "security.sql_format"),
    (r"ObjectInputStream", "ObjectInputStream can be dangerous for deserialization", "security.deserialization"),
]

# C/C++ patterns
_C_CPP_PATTERNS = [
    (r"\bsystem\s*\(", "system() call is dangerous", "security.system_call"),
    (r"\bpopen\s*\(", "popen() is dangerous", "security.popen"),
    (r"strcpy\s*\(", "strcpy is unsafe - use strncpy", "security.strcpy"),
    (r"strcat\s*\(", "strcat is unsafe - use strncat", "security.strcat"),
    (r"gets\s*\(", "gets() is extremely dangerous - use fgets", "security.gets"),
    (r"sprintf\s*\([^,]+,\s*[^\"]*%s", "sprintf with string format - potential buffer overflow", "security.sprintf"),
    (r"scanf\s*\(.*%s", "scanf with %s - potential buffer overflow", "security.scanf"),
    (r"printf\s*\(.*\+.*\)", "printf with variable format - potential format string vulnerability", "security.format_string"),
    (r"malloc\s*\([^)]*\*\s*[^)]*\)", "malloc with multiplication - potential integer overflow", "security.malloc_overflow"),
    (r"free\s*\([^)]*\)\s*;\s*free\s*\(", "Double free detected", "security.double_free"),
    (r"password\s*=\s*[\"']", "Hardcoded password detected", "security.hardcoded_password"),
    (r"(?:api_key|secret|token)\s*=\s*[\"']", "Hardcoded secret", "security.hardcoded_secret"),
]

# Language-agnostic patterns (apply to all languages)
_UNIVERSAL_PATTERNS = [
    (r"password\s*[=:]\s*['\"]", "Hardcoded password detected", "security.hardcoded_password"),
    (r"(?:api[_-]?key|secret[_-]?key|api[_-]?secret)\s*[=:]\s*['\"]", "Hardcoded API key", "security.hardcoded_apikey"),
    (r"private[_-]?key\s*[=:]\s*['\"]", "Hardcoded private key", "security.hardcoded_privatekey"),
    (r"aws[_-]?secret[_-]?access[_-]?key\s*[=:]\s*['\"]", "Hardcoded AWS secret", "security.hardcoded_aws"),
    (r"-----BEGIN.*PRIVATE KEY-----", "Private key in code", "security.private_key_in_code"),
]

# Mapping of language to patterns
_LANGUAGE_PATTERNS = {
    "python": _PYTHON_PATTERNS,
    "javascript": _JS_PATTERNS,
    "typescript": _JS_PATTERNS,
    "go": _GO_PATTERNS,
    "rust": _RUST_PATTERNS,
    "java": _JAVA_PATTERNS,
    "c": _C_CPP_PATTERNS,
    "cpp": _C_CPP_PATTERNS,
}


class SecurityValidator(BaseValidator):
    """Tier 2: Security analysis using built-in patterns and optionally bandit."""

    tier = 2
    name = "security"
    weight = 1.5

    def validate(self, proposal: Proposal, context: dict) -> ValidationResult:
        issues: list[Issue] = []

        # Universal pattern checks (apply to all languages)
        universal_issues = self._check_patterns(proposal.code, _UNIVERSAL_PATTERNS)
        issues.extend(universal_issues)

        # Language-specific pattern checks
        lang_patterns = _LANGUAGE_PATTERNS.get(proposal.language, [])
        if lang_patterns:
            lang_issues = self._check_patterns(proposal.code, lang_patterns)
            issues.extend(lang_issues)

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

    def _check_patterns(self, code: str, patterns: list) -> list[Issue]:
        """Check for dangerous patterns using regex."""
        issues = []
        for line_no, line in enumerate(code.splitlines(), 1):
            for pattern, message, rule in patterns:
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
