"""File processing utilities for batch validation."""

from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional

from rich.console import Console

from vallm.cli.batch_constants import _MAX_WORKERS
from vallm.cli.output_formatters import (
    output_batch_empty as render_batch_empty,
    output_batch_results as render_batch_results,
    output_validate_result as render_validate_result,
)
from vallm.config import VallmSettings
from vallm.core.languages import detect_language
from vallm.core.proposal import Proposal
from vallm.scoring import validate


if _MAX_WORKERS <= 0:
    _MAX_WORKERS = min(os.cpu_count() or 1, 8)


def read_file_text(file_path: Path) -> Optional[str]:
    """Read file as text; return None on encoding error."""
    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def detect_file_language(file_path: Path):
    """Detect language object or return None for unsupported files."""
    return detect_language(file_path)


def show_progress(i: int, total: int, file_path: Path, output_format: str, console: Console) -> None:
    """Print per-file progress line in rich mode."""
    if output_format == "rich":
        console.print(f"[dim]Processing {i}/{total}: {file_path}[/dim]")


def handle_validation_result(
    result, file_path: Path, output_format: str, verbose: bool, show_issues: bool, console: Console
):
    """Handle the result of validating a single file."""
    if result is None:
        return None, None

    if output_format == "rich" and verbose:
        render_validate_result(result, file_path, show_issues)

    return result, file_path


def process_single_file(
    file_path: Path,
    settings: VallmSettings,
    output_format: str,
    verbose: bool,
    show_issues: bool,
    console: Console,
    i: int,
    total: int,
):
    """Process a single file for validation."""
    show_progress(i, total, file_path, output_format, console)

    text = read_file_text(file_path)
    if text is None:
        return None, None, None

    language = detect_file_language(file_path)
    if language is None:
        return None, None, None

    proposal = Proposal(file_path, text, language, settings)
    result = validate(proposal, settings=settings)

    result, file_path = handle_validation_result(result, file_path, output_format, verbose, show_issues, console)
    return result, file_path, language


def process_files(
    filtered_files: list[Path],
    settings: VallmSettings,
    output_format: str,
    fail_fast: bool,
    verbose: bool,
    show_issues: bool,
    console: Console,
) -> tuple[dict, list, int, list]:
    """Process multiple files using thread pool."""
    results_by_language = {}
    failed_files = []
    passed_count = 0
    processed_files = []

    with ThreadPoolExecutor(max_workers=_MAX_WORKERS) as executor:
        futures = [
            executor.submit(
                process_single_file,
                f,
                settings,
                output_format,
                verbose,
                show_issues,
                console,
                i + 1,
                len(filtered_files),
            )
            for i, f in enumerate(filtered_files)
        ]

        for future in as_completed(futures):
            result, file_path, language = future.result()
            if result is None:
                continue

            processed_files.append(file_path)
            language_name = language.name if language is not None else "unknown"
            if language_name not in results_by_language:
                results_by_language[language_name] = []
            results_by_language[language_name].append(result)

            if result.all_issues:
                failed_files.append((file_path, f"Validation {result.verdict.value}: {len(result.all_issues)} issue(s)"))
                if fail_fast:
                    break
            else:
                passed_count += 1

    return results_by_language, failed_files, passed_count, processed_files


def handle_no_files_found(output_format: str) -> None:
    """Handle case when no files are found to validate."""
    render_batch_empty(output_format)


def show_validation_start(filtered_files: list[Path], output_format: str, console: Console) -> None:
    """Show validation start message."""
    if output_format == "rich":
        console.print(f"[bold]Validating {len(filtered_files)} files...[/bold]")


def output_batch_results(
    results_by_language: dict,
    filtered_files: list,
    passed_count: int,
    failed_files: list,
    output_format: str,
) -> None:
    """Output batch validation results."""
    render_batch_results(
        results_by_language,
        filtered_files,
        passed_count,
        failed_files,
        output_format,
    )