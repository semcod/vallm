"""Batch processing utilities for vallm CLI."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from rich.console import Console

from vallm.cli.batch_filter import filter_files
from vallm.cli.batch_process import (
    handle_no_files_found,
    output_batch_results,
    process_files,
    show_validation_start,
)
from vallm.cli.batch_processor_files import build_file_list
from vallm.config import VallmSettings
from vallm.core.gitignore import load_gitignore


class BatchProcessor:
    """Handles batch validation of multiple files."""

    def __init__(self, console: Console):
        self.console = console

    def process_batch(
        self,
        paths: list[Path],
        recursive: bool,
        include: Optional[str],
        exclude: Optional[str],
        use_gitignore: bool,
        settings: VallmSettings,
        output_format: str,
        fail_fast: bool,
        verbose: bool,
        show_issues: bool,
    ) -> tuple[dict, list, int, list]:
        """Process a batch of files for validation."""
        gitignore_parser = self._load_gitignore_parser(use_gitignore)
        files_to_validate = self._build_file_list(paths, recursive)
        filtered_files = filter_files(
            files_to_validate,
            include,
            exclude,
            gitignore_parser,
            use_gitignore,
            self.console,
        )

        if not filtered_files:
            handle_no_files_found(output_format)
            return {}, [], 0, []

        show_validation_start(filtered_files, output_format, self.console)
        results_by_language, failed_files, passed_count, _ = process_files(
            filtered_files,
            settings,
            output_format,
            fail_fast,
            verbose,
            show_issues,
            self.console,
        )

        return results_by_language, failed_files, passed_count, filtered_files

    def output_batch_results(
        self,
        results_by_language: dict,
        passed_count: int,
        failed_files: list,
        output_format: str,
        filtered_files: list,
    ) -> None:
        """Output batch validation results."""
        output_batch_results(
            results_by_language,
            filtered_files,
            passed_count,
            failed_files,
            output_format,
        )

    def _load_gitignore_parser(self, use_gitignore: bool):
        """Load gitignore parser if enabled."""
        if not use_gitignore:
            return None

        gitignore_parser = load_gitignore()
        if gitignore_parser.root.exists():
            self.console.print(f"[dim]Using .gitignore from {gitignore_parser.root}[/dim]")
        else:
            self.console.print("[dim]No .gitignore found, using default excludes[/dim]")
        return gitignore_parser

    def _build_file_list(self, paths: list[Path], recursive: bool) -> list[Path]:
        """Build list of files from input paths."""
        return build_file_list(paths, recursive)