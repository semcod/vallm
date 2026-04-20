"""Batch output formatters for vallm CLI."""

from __future__ import annotations

import csv
import io
import json
from collections import Counter
from pathlib import Path
from typing import TYPE_CHECKING, Any

from rich.console import Console

from .shared import (
    _toon_today,
    build_failed_files_data,
    build_files_data,
)

if TYPE_CHECKING:
    pass


class VallmJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles non-serializable vallm objects."""

    def default(self, obj: Any) -> Any:
        # Handle VallmSettings and other config objects
        if hasattr(obj, "__class__") and "Settings" in obj.__class__.__name__:
            return f"<{obj.__class__.__name__} object>"
        # Handle Path objects
        if isinstance(obj, Path):
            return str(obj)
        # Handle enum objects
        if hasattr(obj, "value"):
            return obj.value
        return super().default(obj)


console = Console()
TOON_UNSUPPORTED_ORDER = ("*.md", "Dockerfile*", "*.txt", "*.yml", "*.example", "other")


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


def _toon_row(values: list[object]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["" if value is None else value for value in values])
    return buffer.getvalue().rstrip("\r\n")


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


def _ordered_unsupported_items(unsupported_counts: Counter[str]) -> list[tuple[str, int]]:
    ordered: list[tuple[str, int]] = []
    for bucket in TOON_UNSUPPORTED_ORDER:
        count = unsupported_counts.get(bucket)
        if count:
            ordered.append((bucket, count))

    for bucket in sorted(bucket for bucket in unsupported_counts if bucket not in TOON_UNSUPPORTED_ORDER):
        ordered.append((bucket, unsupported_counts[bucket]))

    return ordered


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


def _print_toon_file_section(title: str, files: list[dict]) -> None:
    print(f"{title}[{len(files)}]{{path,score}}:")
    for file_data in files:
        score = f"{file_data['score']:.2f}"
        print(f"  {_toon_row([file_data['path'], score])}")
        issues = file_data["issues"]
        if issues:
            print(f"    issues[{len(issues)}]{{rule,severity,message,line}}:")
            for issue in issues:
                print(
                    f"      {_toon_row([
                        issue.get('rule', 'unknown'),
                        issue.get('severity', 'info'),
                        issue.get('message', ''),
                        issue.get('line'),
                    ])}"
                )


def _print_toon_unsupported_section(unsupported_counts: Counter[str]) -> None:
    ordered = _ordered_unsupported_items(unsupported_counts)
    print(f"UNSUPPORTED[{len(ordered)}]{{bucket,count}}:")
    for bucket, count in ordered:
        print(f"  {_toon_row([bucket, count])}")


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
    print("\n" + "=" * 60)
    print("BATCH VALIDATION SUMMARY")
    print("=" * 60)

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


def output_batch_json(results_by_language: dict, filtered_files: list, passed_count: int, failed_files: list) -> None:
    """Output batch results as JSON."""
    total_files = len(filtered_files)
    failed_count = len(failed_files)

    files_details = build_files_data(results_by_language)
    failed_files_data = build_failed_files_data(failed_files)
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
    print(json.dumps(data, indent=2, cls=VallmJSONEncoder))


def output_batch_yaml(results_by_language: dict, filtered_files: list, passed_count: int, failed_files: list) -> None:
    """Output batch results as YAML-like text."""
    total_files = len(filtered_files)
    failed_count = len(failed_files)

    files_details = build_files_data(results_by_language)
    failed_files_data = build_failed_files_data(failed_files)
    success_rate = round((passed_count / total_files) * 100, 1) if total_files > 0 else 0.0

    print("# vallm batch validation results")
    print("---")
    print("summary:")
    print(f"  total_files: {total_files}")
    print(f"  passed: {passed_count}")
    print(f"  failed: {failed_count}")
    print(f"  success_rate: {success_rate}%")
    print()

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


def output_batch_toon(results_by_language: dict, filtered_files: list, passed_count: int, failed_files: list) -> None:
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
        _print_toon_unsupported_section(unsupported_counts)


def print_summary_header() -> None:
    """Print a standard header for batch summaries."""
    print("\n" + "=" * 60)
    print("BATCH VALIDATION SUMMARY")
    print("=" * 60)


def build_results_table(results_by_language: dict):
    """Build a rich table for batch results."""
    from rich.table import Table

    table = Table(title="Results by Language")
    table.add_column("Language")
    table.add_column("Passed")
    table.add_column("Total")
    table.add_column("Score")
    for lang, results in results_by_language.items():
        passed = sum(1 for r in results if r.verdict.value == "pass")
        total = len(results)
        avg_score = sum(r.weighted_score for r in results) / total if total else 0.0
        table.add_row(lang, str(passed), str(total), f"{avg_score:.2f}")
    return table
