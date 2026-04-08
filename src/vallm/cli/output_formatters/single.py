"""Single-result output formatters for vallm CLI."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from rich.console import Console
from rich.panel import Panel

if TYPE_CHECKING:
    from vallm.scoring import ValidationResult

console = Console()


def output_json(result: "ValidationResult") -> None:
    """Output single file validation result as JSON (used by validate command)."""
    data = {
        "verdict": result.verdict.value,
        "score": result.weighted_score,
        "issues": [
            {
                "rule": issue.rule,
                "severity": issue.severity.value,
                "message": issue.message,
                "line": issue.line,
                "column": issue.column,
            }
            for issue in result.all_issues
        ],
    }
    print(json.dumps(data, indent=2))


def output_text(result: "ValidationResult") -> None:
    """Output single file validation result as text (used by validate command)."""
    print(f"Verdict: {result.verdict.value}")
    print(f"Score: {result.weighted_score:.2f}")
    for r in result.results:
        print(f"  {r.validator}: {r.score:.2f} (weight={r.weight})")


def output_rich(result: "ValidationResult", verbose: bool) -> None:
    """Output rich formatted validation result."""
    from vallm.scoring import Verdict

    verdict_colors = {
        Verdict.PASS: "green",
        Verdict.REVIEW: "yellow",
        Verdict.FAIL: "red",
    }

    verdict_color = verdict_colors.get(result.verdict, "white")
    console.print(
        Panel(
            f"[{verdict_color} bold]{result.verdict.value.upper()}[/{verdict_color} bold]",
            title="Validation Result",
            border_style=verdict_color,
        )
    )

    console.print(f"Score: [bold]{result.weighted_score:.2f}[/bold]")

    if result.all_issues:
        console.print("\n[bold]Issues:[/bold]")
        for issue in result.all_issues:
            severity_colors = {
                "error": "red",
                "warning": "yellow",
                "info": "blue",
            }
            color = severity_colors.get(issue.severity.value, "white")
            location = f" (line {issue.line})" if issue.line else ""
            console.print(f"  [{color}]•[/{color}] {issue.message}{location}")

    if verbose:
        console.print("\n[bold]Validator Details:[/bold]")
        for validator_result in result.results:
            console.print(f"  {validator_result.validator}: {validator_result.score:.2f}")
