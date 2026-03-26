"""Output formatting functions for vallm CLI."""

from __future__ import annotations

import json
from collections import Counter
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

if TYPE_CHECKING:
    from vallm.scoring import PipelineResult, ValidationResult

console = Console()

TOON_ISSUE_LABELS = {
    "error": "[err]",
    "warning": "[warn]",
    "info": "[info]",
}
TOON_UNSUPPORTED_ORDER = ("*.md", "Dockerfile*", "*.txt", "*.yml", "*.example", "other")


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
        print(f"# vallm batch | 0f | 0✓ 0⚠ 0✗ | {_toon_today()}")
        print()
        print("SUMMARY:")
        print("  scanned: 0  passed: 0 (0.0%)  warnings: 0  errors: 0  unsupported: 0")
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


def format_error_message(error: str) -> str:
    """Format error messages consistently across all output formats."""
    if "NoneType" in str(error):
        return "Unable to process file (unsupported format or binary)"
    elif "binary" in str(error).lower():
        return "Binary file (skipped)"
    else:
        return str(error)


def build_files_data(results_by_language: dict) -> list:
    """Build standardized files data structure for all output formats."""
    files_details = []
    for lang, results in results_by_language.items():
        for r in results:
            filename = getattr(r, 'filename', None) or 'unknown'
            
            # Build issues list with consistent structure
            issues = []
            for issue in r.all_issues:
                issue_data = {
                    "rule": issue.rule or "unknown",
                    "severity": issue.severity.value,
                    "message": issue.message,
                }
                if issue.line is not None:
                    issue_data["line"] = issue.line
                if issue.column is not None:
                    issue_data["column"] = issue.column
                issues.append(issue_data)
            
            files_details.append({
                "path": filename,
                "language": lang,
                "verdict": r.verdict.value,
                "score": round(r.weighted_score, 2),
                "issues": issues,
                "issues_count": len(issues),
            })
    return files_details


def build_failed_files_data(failed_files: list) -> list:
    """Build standardized failed files data structure for all output formats."""
    return [
        {
            "path": str(file_path),
            "error": format_error_message(error)
        }
        for file_path, error in failed_files
    ]


def _toon_today() -> str:
    return date.today().isoformat()


def _split_toon_results(files_details: list[dict]) -> tuple[list[dict], list[dict]]:
    warnings = []
    errors = []

    for file_data in files_details:
        verdict = file_data["verdict"]
        score = file_data["score"]
        if verdict == "review" or (verdict == "pass" and score < 1.0):
            warnings.append(file_data)
        elif verdict == "fail":
            errors.append(file_data)

    warnings.sort(key=lambda item: (item["score"], item["path"]))
    errors.sort(key=lambda item: (item["score"], item["path"]))
    return warnings, errors


def _format_toon_issue(issue: dict) -> str:
    severity = issue.get("severity", "info")
    label = TOON_ISSUE_LABELS.get(severity, f"[{severity}]")
    location = ""
    line = issue.get("line")
    column = issue.get("column")
    if line is not None:
        location = f"@{line}"
        if column is not None:
            location += f":{column}"
    return f"    {label} {issue.get('rule', 'unknown')}: {issue.get('message', '')}{location}"


def _unsupported_bucket(file_path: str) -> str:
    name = Path(file_path).name.lower()
    if name.startswith("dockerfile"):
        return "Dockerfile*"
    if name.endswith(".md"):
        return "*.md"
    if name.endswith(".txt"):
        return "*.txt"
    if name.endswith(".yml"):
        return "*.yml"
    if name.endswith(".example"):
        return "*.example"
    return "other"


def _build_unsupported_summary(failed_files: list) -> Counter[str]:
    unsupported = Counter()
    for file_path, error in failed_files:
        if str(error).startswith("Validation "):
            continue
        unsupported[_unsupported_bucket(str(file_path))] += 1
    return unsupported


def _format_unsupported_summary(unsupported_counts: Counter[str]) -> str:
    ordered: list[str] = []
    for bucket in TOON_UNSUPPORTED_ORDER:
        if unsupported_counts.get(bucket):
            ordered.append(f"{bucket} ({unsupported_counts[bucket]})")

    for bucket in sorted(bucket for bucket in unsupported_counts if bucket not in TOON_UNSUPPORTED_ORDER):
        ordered.append(f"{bucket} ({unsupported_counts[bucket]})")

    return "  ".join(ordered)


def _print_toon_file_section(title: str, files: list[dict]) -> None:
    print(f"{title}[{len(files)}]:")
    width = min(max(len(file_data["path"]) for file_data in files), 48)
    for file_data in files:
        print(f"  {file_data['path']:<{width}}  {file_data['score']:.2f}")
        for issue in file_data["issues"]:
            print(_format_toon_issue(issue))


def output_batch_json(
    results_by_language: dict,
    filtered_files: list,
    passed_count: int,
    failed_files: list,
) -> None:
    """Output JSON batch summary with detailed per-file results."""
    total_files = len(filtered_files)
    failed_count = len(failed_files)
    
    # Build standardized data structures
    files_details = build_files_data(results_by_language)
    failed_files_data = build_failed_files_data(failed_files)
    
    # Calculate success rate
    success_rate = round((passed_count / total_files) * 100, 1) if total_files > 0 else 0.0
    
    data = {
        "summary": {
            "total_files": total_files,
            "passed": passed_count,
            "failed": failed_count,
            "success_rate": success_rate,
        },
        "files": files_details,
        "failed_files": failed_files_data,
    }

    print(json.dumps(data, indent=2))


def output_batch_yaml(
    results_by_language: dict,
    filtered_files: list,
    passed_count: int,
    failed_files: list,
) -> None:
    """Output YAML batch summary with detailed per-file results."""
    total_files = len(filtered_files)
    failed_count = len(failed_files)
    
    # Build standardized data structures
    files_details = build_files_data(results_by_language)
    failed_files_data = build_failed_files_data(failed_files)
    
    # Calculate success rate
    success_rate = round((passed_count / total_files) * 100, 1) if total_files > 0 else 0.0
    
    print("# vallm batch validation results")
    print("---")
    print(f"summary:")
    print(f"  total_files: {total_files}")
    print(f"  passed: {passed_count}")
    print(f"  failed: {failed_count}")
    print(f"  success_rate: {success_rate}%")
    print()

    # Detailed per-file results
    if files_details:
        print("files:")
        for file_data in files_details:
            print(f"  - path: {file_data['path']}")
            print(f"    language: {file_data['language']}")
            print(f"    verdict: {file_data['verdict']}")
            print(f"    score: {file_data['score']:.2f}")
            print(f"    issues_count: {file_data['issues_count']}")
            if file_data['issues']:
                print(f"    issues:")
                for issue in file_data['issues']:
                    print(f"      - rule: {issue['rule']}")
                    print(f"        severity: {issue['severity']}")
                    print(f"        message: \"{issue['message']}\"")
                    if 'line' in issue:
                        print(f"        line: {issue['line']}")
                    if 'column' in issue:
                        print(f"        column: {issue['column']}")
        print()

    if failed_files_data:
        print("failed_files:")
        for file_data in failed_files_data:
            print(f"  - path: {file_data['path']}")
            print(f"    error: {file_data['error']}")


def output_batch_toon(
    results_by_language: dict,
    filtered_files: list,
    passed_count: int,
    failed_files: list,
) -> None:
    """Output TOON format batch summary with detailed per-file results."""
    total_files = len(filtered_files)
    files_details = build_files_data(results_by_language)
    warnings, errors = _split_toon_results(files_details)
    unsupported_counts = _build_unsupported_summary(failed_files)
    unsupported_count = sum(unsupported_counts.values())
    success_rate = round((passed_count / total_files) * 100, 1) if total_files > 0 else 0.0

    print(f"# vallm batch | {total_files}f | {passed_count}✓ {len(warnings)}⚠ {len(errors)}✗ | {_toon_today()}")
    print()
    print("SUMMARY:")
    print(
        f"  scanned: {total_files}  passed: {passed_count} ({success_rate:.1f}%)  "
        f"warnings: {len(warnings)}  errors: {len(errors)}  unsupported: {unsupported_count}"
    )
    print()
    if warnings:
        _print_toon_file_section("WARNINGS", warnings)
        print()
    if errors:
        _print_toon_file_section("ERRORS", errors)
        print()
    if unsupported_count:
        print(f"UNSUPPORTED[{unsupported_count}]:")
        print(f"  {_format_unsupported_summary(unsupported_counts)}")


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
