"""Output formatting functions for vallm CLI."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

if TYPE_CHECKING:
    from vallm.scoring import PipelineResult, ValidationResult

console = Console()


def output_validate_result(result: "ValidationResult", output_format: str, verbose: bool) -> None:
    """Output validation result in the specified format."""
    if output_format == "json":
        output_json(result)
    elif output_format == "text":
        output_text(result)
    else:
        output_rich(result, verbose)


def output_batch_results(
    results_by_language: dict,
    filtered_files: list,
    passed_count: int,
    failed_files: list,
    output_format: str,
) -> None:
    """Output batch validation results in the specified format."""
    if output_format == "json":
        output_batch_json(results_by_language, filtered_files, passed_count, failed_files)
    elif output_format == "yaml":
        output_batch_yaml(results_by_language, filtered_files, passed_count, failed_files)
    elif output_format == "toon":
        output_batch_toon(results_by_language, filtered_files, passed_count, failed_files)
    else:
        output_batch_rich(results_by_language, filtered_files, passed_count, failed_files)


def output_batch_empty(output_format: str) -> None:
    """Output empty results."""
    if output_format == "json":
        print(json.dumps({"summary": {"total_files": 0}, "files": []}))
    elif output_format == "yaml":
        print("# vallm batch validation results")
        print("---")
        print("summary:")
        print("  total_files: 0")
        print("  passed: 0")
        print("  failed: 0")
        print("files: []")
    elif output_format == "toon":
        print("# vallm batch | 0f | 0✓ 0✗")
        print()
        print("SUMMARY:")
        print("  total: 0")
        print("  passed: 0")
        print("  failed: 0")
        print("FILES: []")
    else:
        console.print("[yellow]No files found to validate.[/yellow]")


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

    # Verdict banner
    verdict_colors = {
        Verdict.PASS: "green",
        Verdict.REVIEW: "yellow", 
        Verdict.FAIL: "red",
    }
    
    verdict_color = verdict_colors.get(result.verdict, "white")
    console.print(Panel(
        f"[{verdict_color} bold]{result.verdict.value.upper()}[/{verdict_color} bold]",
        title="Validation Result",
        border_style=verdict_color,
    ))
    
    # Score
    console.print(f"Score: [bold]{result.weighted_score:.2f}[/bold]")
    
    # Issues (if any)
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
    
    # Detailed validator results (if verbose)
    if verbose:
        console.print("\n[bold]Validator Details:[/bold]")
        for validator_result in result.results:
            console.print(f"  {validator_result.validator}: {validator_result.score:.2f}")


def output_batch_rich(
    results_by_language: dict,
    filtered_files: list,
    passed_count: int,
    failed_files: list,
) -> None:
    """Output rich formatted batch summary."""
    print_summary_header()
    table = build_results_table(results_by_language)
    console.print(table)
    console.print(f"\nTotal: {len(filtered_files)} files, {passed_count} passed, {len(failed_files)} failed")
    
    if failed_files:
        console.print("\n[red]Failed Files:[/red]")
        for file_path, error in failed_files:
            console.print(f"  [red]•[/red] {file_path}: {error}")


def output_batch_text(
    results_by_language: dict,
    filtered_files: list,
    passed_count: int,
    failed_files: list,
) -> None:
    """Output plain text batch summary."""
    print("\n" + "="*60)
    print("BATCH VALIDATION SUMMARY")
    print("="*60)
    
    print(f"Total files: {len(filtered_files)}")
    print(f"Passed: {passed_count}")
    print(f"Failed: {len(failed_files)}")
    print()
    
    if results_by_language:
        print("Results by language:")
        for lang, results in results_by_language.items():
            passed = sum(1 for r in results if r.verdict.value == "pass")
            total = len(results)
            print(f"  {lang}: {passed}/{total} passed")
    
    if failed_files:
        print("\nFailed files:")
        for file_path, error in failed_files:
            print(f"  {file_path}: {error}")


def output_batch_json(
    results_by_language: dict,
    filtered_files: list,
    passed_count: int,
    failed_files: list,
) -> None:
    """Output JSON batch summary with detailed per-file results."""
    # Build detailed files list with path and full details
    files_details = []
    for lang, results in results_by_language.items():
        for r in results:
            # Get filename from result if available
            filename = getattr(r, 'filename', None) or 'unknown'
            files_details.append({
                "path": filename,
                "language": lang,
                "verdict": r.verdict.value,
                "score": r.weighted_score,
                "issues": [
                    {
                        "rule": issue.rule,
                        "severity": issue.severity.value,
                        "message": issue.message,
                        "line": issue.line,
                        "column": issue.column,
                    }
                    for issue in r.all_issues
                ],
                "issues_count": len(r.all_issues),
            })

    data = {
        "summary": {
            "total_files": len(filtered_files),
            "passed": passed_count,
            "failed": len(failed_files),
        },
        "files": files_details,
        "failed_files": [
            {"path": str(file_path), "error": error}
            for file_path, error in failed_files
        ],
    }

    print(json.dumps(data, indent=2))


def output_batch_yaml(
    results_by_language: dict,
    filtered_files: list,
    passed_count: int,
    failed_files: list,
) -> None:
    """Output YAML batch summary with detailed per-file results."""
    print("# vallm batch validation results")
    print("---")
    print(f"summary:")
    print(f"  total_files: {len(filtered_files)}")
    print(f"  passed: {passed_count}")
    print(f"  failed: {len(failed_files)}")
    print()

    # Detailed per-file results
    if results_by_language:
        print("files:")
        for lang, results in results_by_language.items():
            for r in results:
                filename = getattr(r, 'filename', None) or 'unknown'
                print(f"  - path: {filename}")
                print(f"    language: {lang}")
                print(f"    verdict: {r.verdict.value}")
                print(f"    score: {r.weighted_score:.2f}")
                print(f"    issues_count: {len(r.all_issues)}")
                if r.all_issues:
                    print(f"    issues:")
                    for issue in r.all_issues:
                        line_info = f", line: {issue.line}" if issue.line else ""
                        col_info = f", column: {issue.column}" if issue.column else ""
                        print(f"      - rule: {issue.rule}")
                        print(f"        severity: {issue.severity.value}")
                        print(f"        message: \"{issue.message}\"{line_info}{col_info}")
        print()

    if failed_files:
        print("failed_files:")
        for file_path, error in failed_files:
            print(f"  - path: {file_path}")
            print(f"    error: {error}")


def output_batch_toon(
    results_by_language: dict,
    filtered_files: list,
    passed_count: int,
    failed_files: list,
) -> None:
    """Output TOON format batch summary with detailed per-file results."""
    print(f"# vallm batch | {len(filtered_files)}f | {passed_count}✓ {len(failed_files)}✗")
    print()
    print("SUMMARY:")
    print(f"  total: {len(filtered_files)}")
    print(f"  passed: {passed_count}")
    print(f"  failed: {len(failed_files)}")
    print()

    # Detailed per-file results
    if results_by_language:
        print("FILES:")
        for lang, results in results_by_language.items():
            print(f"  [{lang}]")
            for r in results:
                filename = getattr(r, 'filename', None) or 'unknown'
                status_icon = "✓" if r.verdict.value == "pass" else "✗"
                print(f"    {status_icon} {filename}")
                print(f"      verdict: {r.verdict.value}")
                print(f"      score: {r.weighted_score:.2f}")
                if r.all_issues:
                    print(f"      issues: {len(r.all_issues)}")
                    for issue in r.all_issues:
                        location = f"@{issue.line}" if issue.line else ""
                        # Use rule instead of validator since Issue doesn't have validator attribute
                        validator_name = issue.rule or "unknown"
                        print(f"        [{issue.severity.value}] {validator_name}: {issue.message}{location}")
        print()

    if failed_files:
        print("FAILED:")
        for file_path, error in failed_files:
            print(f"  ✗ {file_path}: {error}")


def print_summary_header() -> None:
    """Print summary header for batch results."""
    console.print("[bold blue]VALLM BATCH VALIDATION RESULTS[/bold blue]")


def build_results_table(results_by_language: dict) -> Table:
    """Build results table for rich output."""
    table = Table(title="Results by Language")
    table.add_column("Language", style="cyan", no_wrap=True)
    table.add_column("Total", justify="right")
    table.add_column("Passed", justify="right", style="green")
    table.add_column("Failed", justify="right", style="red")
    table.add_column("Avg Score", justify="right")
    
    for lang, results in results_by_language.items():
        passed = sum(1 for r in results if r.verdict.value == "pass")
        failed = len(results) - passed
        avg_score = sum(r.weighted_score for r in results) / len(results) if results else 0
        
        table.add_row(
            lang,
            str(len(results)),
            str(passed),
            str(failed),
            f"{avg_score:.2f}",
        )
    
    return table
