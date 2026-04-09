"""Example 4: Code graph analysis and structural regression detection.

Demonstrates: import/call graph building and diffing.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from examples.utils import save_analysis_data
from vallm.core.graph_builder import build_python_graph
from vallm.core.graph_diff import diff_python_code

# Original code
before_code = """
import os
import json
from pathlib import Path

def read_config(path: str) -> dict:
    with open(path) as f:
        return json.load(f)

def process_data(config: dict) -> list:
    items = config.get("items", [])
    return [item.upper() for item in items]

def main():
    config = read_config("config.json")
    result = process_data(config)
    print(result)
"""

# Modified code (with changes)
after_code = """
import json
import yaml
from pathlib import Path
from dataclasses import dataclass

@dataclass
class Config:
    items: list[str]
    debug: bool = False

def read_config(path: str) -> Config:
    with open(path) as f:
        data = yaml.safe_load(f)
    return Config(**data)

def process_data(config: Config) -> list:
    items = config.items
    return [item.upper() for item in items]

def validate_config(config: Config) -> bool:
    return len(config.items) > 0

def main():
    config = read_config("config.yaml")
    if validate_config(config):
        result = process_data(config)
        print(result)
"""


def main():
    all_results = {}
    print("=" * 60)
    print("Code Graph: BEFORE")
    print("=" * 60)
    graph_before = build_python_graph(before_code, "mymodule")
    imports_before = [(e.source_module, e.imported_name) for e in graph_before.imports]
    functions_before = graph_before.functions
    classes_before = graph_before.classes
    calls_before = [(e.caller, e.callee) for e in graph_before.calls]
    
    print(f"Imports: {imports_before}")
    print(f"Functions: {functions_before}")
    print(f"Classes: {classes_before}")
    print(f"Calls: {calls_before}")
    
    # Store before data
    all_results["before"] = {
        "imports": imports_before,
        "functions": functions_before,
        "classes": classes_before,
        "calls": calls_before
    }

    print("\n" + "=" * 60)
    print("Code Graph: AFTER")
    print("=" * 60)
    graph_after = build_python_graph(after_code, "mymodule")
    imports_after = [(e.source_module, e.imported_name) for e in graph_after.imports]
    functions_after = graph_after.functions
    classes_after = graph_after.classes
    calls_after = [(e.caller, e.callee) for e in graph_after.calls]
    
    print(f"Imports: {imports_after}")
    print(f"Functions: {functions_after}")
    print(f"Classes: {classes_after}")
    print(f"Calls: {calls_after}")
    
    # Store after data
    all_results["after"] = {
        "imports": imports_after,
        "functions": functions_after,
        "classes": classes_after,
        "calls": calls_after
    }

    print("\n" + "=" * 60)
    print("Structural Diff")
    print("=" * 60)
    diff = diff_python_code(before_code, after_code)

    print(f"Has changes: {diff.has_changes}")
    print(f"Added imports: {diff.added_imports}")
    print(f"Removed imports: {diff.removed_imports}")
    print(f"Added functions: {diff.added_functions}")
    print(f"Removed functions: {diff.removed_functions}")
    print(f"Added classes: {diff.added_classes}")

    # Store diff data
    all_results["diff"] = {
        "has_changes": diff.has_changes,
        "added_imports": diff.added_imports,
        "removed_imports": diff.removed_imports,
        "added_functions": diff.added_functions,
        "removed_functions": diff.removed_functions,
        "added_classes": diff.added_classes,
        "breaking_changes": diff.breaking_changes if diff.breaking_changes else []
    }

    if diff.breaking_changes:
        print(f"\n⚠️  Breaking changes detected:")
        for change in diff.breaking_changes:
            print(f"  - {change}")
    else:
        print("\n✓ No breaking changes detected")

    # Save all analysis data
    save_analysis_data("graph_analysis", all_results)
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Changes detected: {diff.has_changes}")
    print(f"Breaking changes: {len(diff.breaking_changes) if diff.breaking_changes else 0}")
    print(f"Functions added: {len(diff.added_functions)}")
    print(f"Classes added: {len(diff.added_classes)}")


if __name__ == "__main__":
    main()
