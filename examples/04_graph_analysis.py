"""Example 4: Code graph analysis and structural regression detection.

Demonstrates: import/call graph building and diffing.
"""

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
    print("=" * 60)
    print("Code Graph: BEFORE")
    print("=" * 60)
    graph_before = build_python_graph(before_code, "mymodule")
    print(f"Imports: {[(e.source_module, e.imported_name) for e in graph_before.imports]}")
    print(f"Functions: {graph_before.functions}")
    print(f"Classes: {graph_before.classes}")
    print(f"Calls: {[(e.caller, e.callee) for e in graph_before.calls]}")

    print("\n" + "=" * 60)
    print("Code Graph: AFTER")
    print("=" * 60)
    graph_after = build_python_graph(after_code, "mymodule")
    print(f"Imports: {[(e.source_module, e.imported_name) for e in graph_after.imports]}")
    print(f"Functions: {graph_after.functions}")
    print(f"Classes: {graph_after.classes}")
    print(f"Calls: {[(e.caller, e.callee) for e in graph_after.calls]}")

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

    if diff.breaking_changes:
        print(f"\n⚠️  Breaking changes detected:")
        for change in diff.breaking_changes:
            print(f"  - {change}")
    else:
        print("\n✓ No breaking changes detected")


if __name__ == "__main__":
    main()
