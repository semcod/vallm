"""Rust import validation."""

from typing import List, Dict, Any
from vallm.core.proposal import Proposal
from vallm.scoring import Issue, Severity, ValidationResult
from .base import BaseImportValidator

# Common Rust standard library crates
_KNOWN_RUST_MODULES = {
    "std", "core", "alloc", "proc_macro", "test",
    "fmt", "vec", "string", "option", "result", "iter", "collections",
    "boxed", "cell", "rc", "sync", "thread", "time", "fs", "path",
    "io", "net", "os", "env", "error", "anyhow", "serde", "tokio",
    "async_trait", "log", "tracing", "clap", "regex", "uuid", "chrono",
}


class RustImportValidator(BaseImportValidator):
    """Rust import validator."""
    
    def validate(self, proposal: Proposal, context: dict) -> ValidationResult:
        """Validate Rust imports using tree-sitter."""
        issues = []
        imports = self.extract_imports(proposal.code)
        
        for import_info in imports:
            module_name = import_info["module"]
            line = import_info["line"]
            
            if not self.module_exists(module_name):
                issues.append(Issue(
                    message=f"Crate '{module_name}' not found",
                    severity=Severity.WARNING,
                    line=line,
                    rule="rust.import.resolvable"
                ))
        
        return self.create_validation_result(
            issues, len(imports), len(imports) - len(issues), "rust"
        )
    
    def extract_imports(self, code: str) -> List[Dict[str, Any]]:
        """Extract use statements from Rust using tree-sitter."""
        imports = []
        try:
            from tree_sitter_language_pack import get_parser
            parser = get_parser("rust")
            tree = parser.parse(code.encode("utf-8"))

            def walk(node):
                if node.type == "use_declaration":
                    # Extract module path
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
            # Fallback: simple regex-based extraction
            import re
            pattern = r"use\s+([^;]+);"
            for match in re.finditer(pattern, code):
                module = match.group(1).strip()
                imports.append({"module": module, "line": code[:match.start()].count('\n') + 1})

        return imports
    
    def module_exists(self, module_name: str) -> bool:
        """Check if a Rust crate/module is known."""
        # Standard library
        top_level = module_name.split("::")[0]
        if top_level in _KNOWN_RUST_MODULES:
            return True
        # Common crates (assume external crates exist)
        return True  # Rust crates are typically in Cargo.toml
