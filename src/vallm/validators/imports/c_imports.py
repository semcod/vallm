"""C/C++ import validation."""

from typing import List, Dict, Any
from vallm.core.proposal import Proposal
from vallm.scoring import Issue, Severity, ValidationResult
from .base import BaseImportValidator


class CImportValidator(BaseImportValidator):
    """C/C++ import validator."""

    def __init__(self, language: str = "c"):
        self.language = language

    def validate(self, proposal: Proposal, context: dict) -> ValidationResult:
        """Validate C/C++ includes using tree-sitter."""
        issues = []
        includes = self.extract_imports(proposal.code)

        for include_info in includes:
            header_name = include_info["module"]
            line = include_info["line"]

            if not self.module_exists(header_name):
                issues.append(
                    Issue(
                        message=f"Header '{header_name}' not found",
                        severity=Severity.WARNING,
                        line=line,
                        rule="c.include.resolvable",
                    )
                )

        return self.create_validation_result(
            issues, len(includes), len(includes) - len(issues), self.language
        )

    def extract_imports(self, code: str) -> List[Dict[str, Any]]:
        """Extract #include statements from C/C++ using tree-sitter."""
        includes = []
        try:
            parser = get_parser(self.language)
            tree = parser.parse(code.encode("utf-8"))

            def walk(node):
                if node.type == "preproc_include":
                    for child in node.children:
                        if child.type == "string_literal":
                            header = child.text.decode("utf-8").strip('"<>')
                            includes.append({"module": header, "line": node.start_point[0] + 1})
                            break
                        elif child.type == "system_lib_string":
                            header = child.text.decode("utf-8").strip("<>")
                            includes.append({"module": header, "line": node.start_point[0] + 1})
                            break

                for child in node.children:
                    walk(child)

            walk(tree.root_node)
        except Exception:
            pass

        return includes

    def module_exists(self, header_name: str) -> bool:
        """Check if a C/C++ header is known."""
        # Standard C headers
        c_headers = {
            "stdio.h",
            "stdlib.h",
            "string.h",
            "math.h",
            "ctype.h",
            "assert.h",
            "errno.h",
            "float.h",
            "limits.h",
            "locale.h",
            "setjmp.h",
            "signal.h",
            "stdarg.h",
            "stddef.h",
            "stdint.h",
            "stdio.h",
            "stdlib.h",
            "string.h",
            "time.h",
            "wchar.h",
            "wctype.h",
            "complex.h",
            "fenv.h",
            "inttypes.h",
            "stdatomic.h",
            "stdnoreturn.h",
            "threads.h",
            "uchar.h",
        }
        # Standard C++ headers (without .h)
        cpp_headers = {
            "iostream",
            "vector",
            "string",
            "map",
            "set",
            "algorithm",
            "memory",
            "utility",
            "functional",
            "iterator",
            "array",
            "deque",
            "forward_list",
            "list",
            "queue",
            "stack",
            "unordered_map",
            "unordered_set",
            "bitset",
            "regex",
            "thread",
            "mutex",
            "condition_variable",
            "future",
            "atomic",
            "chrono",
            "filesystem",
            "optional",
            "variant",
            "any",
            "span",
            "ranges",
            "concepts",
            "coroutine",
            "format",
        }
        if header_name in c_headers or header_name in cpp_headers:
            return True
        if header_name.endswith(".h") and header_name[:-2] in cpp_headers:
            return True
        return False
