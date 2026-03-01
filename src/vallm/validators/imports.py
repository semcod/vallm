"""Import validation: checks that all imported modules are resolvable."""

from __future__ import annotations

import ast
import importlib.util
import re
from typing import Optional

from tree_sitter_language_pack import get_parser

from vallm.core.proposal import Proposal
from vallm.scoring import Issue, Severity, ValidationResult
from vallm.validators.base import BaseValidator

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

# Common JavaScript/Node.js built-in modules
_KNOWN_JS_MODULES = {
    "fs", "path", "http", "https", "url", "util", "events", "stream",
    "crypto", "os", "buffer", "querystring", "child_process", "cluster",
    "console", "dgram", "dns", "net", "readline", "repl", "tls", "tty",
    "v8", "vm", "zlib", "worker_threads", "perf_hooks", "async_hooks",
    "assert", "constants", "domain", "punycode", "string_decoder", "sys",
}

# Common Go standard library packages
_KNOWN_GO_MODULES = {
    "fmt", "os", "io", "strings", "strconv", "math", "time", "net",
    "http", "json", "log", "errors", "context", "sync", "bufio", "filepath",
    "runtime", "reflect", "sort", "bytes", "regexp", "encoding", "base64",
    "hex", "binary", "json", "xml", "gob", "csv", "syscall", "unsafe",
    "testing", "template", "html", "database", "sql", "crypto", "hash",
    "md5", "sha1", "sha256", "sha512", "aes", "cipher", "rand", "rsa",
    "dsa", "ecdsa", "ed25519", "x509", "tls", "archive", "zip", "tar",
    "gzip", "zlib", "compress", "flate", "lzw", "image", "color", "draw",
    "gif", "jpeg", "png", "debug", " dwarf", "elf", "gosym", "macho",
    "pe", "plan9obj", "plugin", "build", "constraint", "types", "scanner",
    "token", "ast", "parser", "printer", "doc", "comment", "go", "gccgo",
}

# Common Rust standard library crates
_KNOWN_RUST_MODULES = {
    "std", "core", "alloc", "proc_macro", "test", "bench", "proc_macro2",
    "quote", "syn", "serde", "serde_json", "serde_derive", "tokio", "futures",
    "async_std", "rayon", "crossbeam", "parking_lot", "log", "env_logger",
    "clap", "structopt", "anyhow", "thiserror", "uuid", "chrono", "time",
    "rand", "regex", "lazy_static", "once_cell", "itertools", "either",
    "option_ext", "num", "num_traits", "num_integer", "num_bigint",
    "num_complex", "num_rational", "hashbrown", "indexmap", "btree",
    "vec_map", "smallvec", "arrayvec", "smartstring", "bytes", "string",
    "http", "hyper", "reqwest", "actix_web", "warp", "tide", "rocket",
    "axum", "tower", "tonic", "prost", "capnp", "flatbuffers", "bincode",
    "rmp", "rmp_serde", "rmpv", "cbor", "toml", "yaml", "json5",
    "csv", "polars", "ndarray", "nalgebra", "cgmath", "glium", "wgpu",
    "vulkano", "ash", "gfx", "rendy", "glutin", "winit", "sdl2",
}

# Common Java standard library packages
_KNOWN_JAVA_MODULES = {
    "java.lang", "java.util", "java.io", "java.net", "java.nio",
    "java.time", "java.text", "java.math", "java.security", "java.crypto",
    "java.sql", "java.awt", "javax.swing", "javax.servlet", "javax.xml",
    "javax.json", "javax.ws.rs", "javax.persistence", "javax.annotation",
    "java.util.concurrent", "java.util.function", "java.util.stream",
    "java.util.regex", "java.util.logging", "java.util.prefs", "java.util.spi",
    "java.lang.reflect", "java.lang.invoke", "java.lang.management",
    "java.lang.annotation", "java.lang.ref", "java.lang.module",
    "java.io.file", "java.io.stream", "java.io.reader", "java.io.writer",
    "java.io.filter", "java.io.buffered", "java.io.data", "java.io.object",
    "java.io.random", "java.io.file", "java.io.piped", "java.io.bytearray",
    "java.io.stringreader", "java.io.stringwriter", "java.io.print",
    "java.io.pushback", "java.io.line", "java.io.console", "java.io.serial",
    "java.net.http", "java.net.uri", "java.net.url", "java.net.socket",
    "java.net.serversocket", "java.net.datagram", "java.net.inet",
    "java.net.proxy", "java.net.cookie", "java.net.cache",
}


class ImportValidator(BaseValidator):
    """Tier 1: Validate that imports are resolvable."""

    tier = 1
    name = "imports"
    weight = 1.5

    def validate(self, proposal: Proposal, context: dict) -> ValidationResult:
        # Dispatch to language-specific validation
        language_handlers = {
            "python": self._validate_python,
            "javascript": self._validate_javascript,
            "typescript": self._validate_typescript,
            "go": self._validate_go,
            "rust": self._validate_rust,
            "java": self._validate_java,
            "c": self._validate_c,
            "cpp": self._validate_cpp,
        }

        handler = language_handlers.get(proposal.language)
        if handler:
            return handler(proposal)

        # Unknown language - skip with low confidence
        return ValidationResult(
            validator=self.name,
            score=1.0,
            weight=self.weight,
            confidence=0.3,
            details={"skipped": f"unsupported language: {proposal.language}"},
        )

    def _validate_python(self, proposal: Proposal) -> ValidationResult:
        """Validate Python imports using AST."""
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
                    if self._python_module_exists(alias.name):
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
                    if self._python_module_exists(node.module):
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
            details={"checked": modules_checked, "found": modules_found, "language": "python"},
        )

    def _validate_javascript(self, proposal: Proposal) -> ValidationResult:
        """Validate JavaScript/Node.js imports using tree-sitter."""
        return self._validate_js_ts(proposal, "javascript", _KNOWN_JS_MODULES)

    def _validate_typescript(self, proposal: Proposal) -> ValidationResult:
        """Validate TypeScript imports using tree-sitter."""
        return self._validate_js_ts(proposal, "typescript", _KNOWN_JS_MODULES)

    def _validate_js_ts(
        self, proposal: Proposal, language: str, known_modules: set
    ) -> ValidationResult:
        """Common validation for JavaScript/TypeScript."""
        issues = []
        imports = self._extract_js_imports(proposal.code, language)

        modules_checked = 0
        modules_found = 0

        for imp in imports:
            module_name = imp["module"]
            line_no = imp["line"]
            modules_checked += 1

            # Check if it's a known built-in or relative import
            if self._js_module_exists(module_name, known_modules):
                modules_found += 1
            else:
                issues.append(
                    Issue(
                        message=f"Unknown module: {module_name}",
                        severity=Severity.WARNING,
                        line=line_no,
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
            confidence=0.7,
            issues=issues,
            details={"checked": modules_checked, "found": modules_found, "language": language},
        )

    def _validate_go(self, proposal: Proposal) -> ValidationResult:
        """Validate Go imports using tree-sitter."""
        issues = []
        imports = self._extract_go_imports(proposal.code)

        modules_checked = 0
        modules_found = 0

        for imp in imports:
            module_name = imp["module"]
            line_no = imp["line"]
            modules_checked += 1

            if self._go_module_exists(module_name):
                modules_found += 1
            else:
                issues.append(
                    Issue(
                        message=f"Unknown Go package: {module_name}",
                        severity=Severity.WARNING,
                        line=line_no,
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
            confidence=0.7,
            issues=issues,
            details={"checked": modules_checked, "found": modules_found, "language": "go"},
        )

    def _validate_rust(self, proposal: Proposal) -> ValidationResult:
        """Validate Rust imports using tree-sitter."""
        issues = []
        imports = self._extract_rust_imports(proposal.code)

        modules_checked = 0
        modules_found = 0

        for imp in imports:
            module_name = imp["module"]
            line_no = imp["line"]
            modules_checked += 1

            if self._rust_module_exists(module_name):
                modules_found += 1
            else:
                issues.append(
                    Issue(
                        message=f"Unknown Rust crate/module: {module_name}",
                        severity=Severity.WARNING,
                        line=line_no,
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
            confidence=0.7,
            issues=issues,
            details={"checked": modules_checked, "found": modules_found, "language": "rust"},
        )

    def _validate_java(self, proposal: Proposal) -> ValidationResult:
        """Validate Java imports using tree-sitter."""
        issues = []
        imports = self._extract_java_imports(proposal.code)

        modules_checked = 0
        modules_found = 0

        for imp in imports:
            module_name = imp["module"]
            line_no = imp["line"]
            modules_checked += 1

            if self._java_module_exists(module_name):
                modules_found += 1
            else:
                issues.append(
                    Issue(
                        message=f"Unknown Java package: {module_name}",
                        severity=Severity.WARNING,
                        line=line_no,
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
            confidence=0.7,
            issues=issues,
            details={"checked": modules_checked, "found": modules_found, "language": "java"},
        )

    def _validate_c(self, proposal: Proposal) -> ValidationResult:
        """Validate C includes."""
        return self._validate_c_cpp(proposal, "c")

    def _validate_cpp(self, proposal: Proposal) -> ValidationResult:
        """Validate C++ includes."""
        return self._validate_c_cpp(proposal, "cpp")

    def _validate_c_cpp(self, proposal: Proposal, language: str) -> ValidationResult:
        """Common validation for C/C++ includes."""
        issues = []
        includes = self._extract_c_includes(proposal.code, language)

        modules_checked = 0
        modules_found = 0

        for inc in includes:
            header_name = inc["module"]
            line_no = inc["line"]
            modules_checked += 1

            if self._c_header_exists(header_name):
                modules_found += 1
            else:
                issues.append(
                    Issue(
                        message=f"Unknown header: {header_name}",
                        severity=Severity.WARNING,
                        line=line_no,
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
            confidence=0.6,
            issues=issues,
            details={"checked": modules_checked, "found": modules_found, "language": language},
        )

    # ==================== Tree-sitter extraction methods ====================

    def _extract_js_imports(self, code: str, language: str) -> list[dict]:
        """Extract import statements from JavaScript/TypeScript using tree-sitter."""
        imports = []
        try:
            parser = get_parser(language)
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
            pass

        return imports

    def _extract_go_imports(self, code: str) -> list[dict]:
        """Extract import statements from Go using tree-sitter."""
        imports = []
        try:
            parser = get_parser("go")
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
            pass

        return imports

    def _extract_rust_imports(self, code: str) -> list[dict]:
        """Extract use statements from Rust using tree-sitter."""
        imports = []
        try:
            parser = get_parser("rust")
            tree = parser.parse(code.encode("utf-8"))

            def walk(node):
                if node.type == "use_declaration":
                    # Extract the module path
                    for child in node.children:
                        if child.type == "scoped_identifier" or child.type == "identifier":
                            module = child.text.decode("utf-8")
                            imports.append({"module": module, "line": node.start_point[0] + 1})
                            break
                        elif child.type == "use_list":
                            # use std::{io, fs}; - extract parent scope
                            parent = node.child_by_field_name("argument")
                            if parent:
                                module = parent.text.decode("utf-8")
                                imports.append({"module": module, "line": node.start_point[0] + 1})
                            break

                for child in node.children:
                    walk(child)

            walk(tree.root_node)
        except Exception:
            pass

        return imports

    def _extract_java_imports(self, code: str) -> list[dict]:
        """Extract import statements from Java using tree-sitter."""
        imports = []
        try:
            parser = get_parser("java")
            tree = parser.parse(code.encode("utf-8"))

            def walk(node):
                if node.type == "import_declaration":
                    # Get the full package path
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

    def _extract_c_includes(self, code: str, language: str) -> list[dict]:
        """Extract #include statements from C/C++ using tree-sitter."""
        includes = []
        try:
            parser = get_parser(language)
            tree = parser.parse(code.encode("utf-8"))

            def walk(node):
                if node.type == "preproc_include":
                    for child in node.children:
                        if child.type == "string_literal":
                            header = child.text.decode("utf-8").strip('"<>')
                            includes.append({"module": header, "line": node.start_point[0] + 1})
                            break
                        elif child.type == "system_lib_string":
                            header = child.text.decode("utf-8").strip('<>')
                            includes.append({"module": header, "line": node.start_point[0] + 1})
                            break

                for child in node.children:
                    walk(child)

            walk(tree.root_node)
        except Exception:
            pass

        return includes

    # ==================== Module existence checks ====================

    @staticmethod
    def _python_module_exists(module_name: str) -> bool:
        """Check if a Python module exists in the current environment."""
        top_level = module_name.split(".")[0]
        if top_level in _KNOWN_PYTHON_MODULES:
            return True
        try:
            return importlib.util.find_spec(top_level) is not None
        except (ModuleNotFoundError, ValueError):
            return False

    @staticmethod
    def _js_module_exists(module_name: str, known_modules: set) -> bool:
        """Check if a JavaScript/TypeScript module is known."""
        # Relative imports (start with ./ or ../)
        if module_name.startswith("./") or module_name.startswith("../"):
            return True
        # Node.js built-ins
        if module_name.split("/")[0] in known_modules:
            return True
        # @scoped packages - assume exists (can't verify without package.json)
        if module_name.startswith("@"):
            return True
        return False

    @staticmethod
    def _go_module_exists(module_name: str) -> bool:
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

    @staticmethod
    def _rust_module_exists(module_name: str) -> bool:
        """Check if a Rust crate/module is known."""
        # Standard library
        top_level = module_name.split("::")[0]
        if top_level in _KNOWN_RUST_MODULES:
            return True
        # Common crates (assume external crates exist)
        return True  # Rust crates are typically in Cargo.toml

    @staticmethod
    def _java_module_exists(module_name: str) -> bool:
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

    @staticmethod
    def _c_header_exists(header_name: str) -> bool:
        """Check if a C/C++ header is known."""
        # Standard C headers
        c_headers = {
            "stdio.h", "stdlib.h", "string.h", "math.h", "ctype.h",
            "assert.h", "errno.h", "float.h", "limits.h", "locale.h",
            "setjmp.h", "signal.h", "stdarg.h", "stddef.h", "stdint.h",
            "stdio.h", "stdlib.h", "string.h", "time.h", "wchar.h",
            "wctype.h", "complex.h", "fenv.h", "inttypes.h", "stdatomic.h",
            "stdnoreturn.h", "threads.h", "uchar.h",
        }
        # Standard C++ headers (without .h)
        cpp_headers = {
            "iostream", "vector", "string", "map", "set", "algorithm",
            "memory", "utility", "functional", "iterator", "array",
            "deque", "forward_list", "list", "queue", "stack", "unordered_map",
            "unordered_set", "bitset", "regex", "thread", "mutex", "condition_variable",
            "future", "atomic", "chrono", "filesystem", "optional", "variant",
            "any", "span", "ranges", "concepts", "coroutine", "format",
        }
        if header_name in c_headers or header_name in cpp_headers:
            return True
        if header_name.endswith(".h") and header_name[:-2] in cpp_headers:
            return True
        return False
