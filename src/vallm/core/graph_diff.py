"""Graph comparison for detecting structural regressions."""

from __future__ import annotations

from dataclasses import dataclass, field

from vallm.core.graph_builder import CodeGraph, build_python_graph


@dataclass
class GraphDiffResult:
    """Result of comparing two code graphs."""

    added_imports: list[tuple[str, str]] = field(default_factory=list)
    removed_imports: list[tuple[str, str]] = field(default_factory=list)
    added_functions: list[str] = field(default_factory=list)
    removed_functions: list[str] = field(default_factory=list)
    added_classes: list[str] = field(default_factory=list)
    removed_classes: list[str] = field(default_factory=list)
    added_calls: list[tuple[str, str]] = field(default_factory=list)
    removed_calls: list[tuple[str, str]] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(
            self.added_imports
            or self.removed_imports
            or self.added_functions
            or self.removed_functions
            or self.added_classes
            or self.removed_classes
            or self.added_calls
            or self.removed_calls
        )

    @property
    def breaking_changes(self) -> list[str]:
        """Identify potentially breaking changes."""
        issues = []
        for fn in self.removed_functions:
            issues.append(f"Removed function: {fn}")
        for cls in self.removed_classes:
            issues.append(f"Removed class: {cls}")
        for mod, name in self.removed_imports:
            issues.append(f"Removed import: {name} from {mod}")
        return issues


def diff_graphs(before: CodeGraph, after: CodeGraph) -> GraphDiffResult:
    """Compare two CodeGraphs and return the diff."""
    before_d = before.to_dict()
    after_d = after.to_dict()

    return GraphDiffResult(
        added_imports=_diff_list(before_d["imports"], after_d["imports"], added=True),
        removed_imports=_diff_list(before_d["imports"], after_d["imports"], added=False),
        added_functions=_diff_list(before_d["functions"], after_d["functions"], added=True),
        removed_functions=_diff_list(before_d["functions"], after_d["functions"], added=False),
        added_classes=_diff_list(before_d["classes"], after_d["classes"], added=True),
        removed_classes=_diff_list(before_d["classes"], after_d["classes"], added=False),
        added_calls=_diff_list(
            [(c.caller, c.callee) for c in before.calls],
            [(c.caller, c.callee) for c in after.calls],
            added=True,
        ),
        removed_calls=_diff_list(
            [(c.caller, c.callee) for c in before.calls],
            [(c.caller, c.callee) for c in after.calls],
            added=False,
        ),
    )


def diff_python_code(before_code: str, after_code: str) -> GraphDiffResult:
    """Convenience function: build graphs from code strings and diff them."""
    before_graph = build_python_graph(before_code, "before")
    after_graph = build_python_graph(after_code, "after")
    return diff_graphs(before_graph, after_graph)


def _diff_list(before, after, added: bool):
    set_before = set(before) if not isinstance(before[0] if before else "", tuple) else set(before)
    set_after = set(after) if not isinstance(after[0] if after else "", tuple) else set(after)
    if added:
        return sorted(set_after - set_before)
    return sorted(set_before - set_after)
