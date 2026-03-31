"""Batch processing utilities for vallm CLI."""

from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional

from rich.console import Console

from vallm.cli.output_formatters import (
    output_batch_empty,
    output_batch_results,
)
from vallm.config import VallmSettings
from vallm.core.gitignore import load_gitignore
from vallm.core.languages import detect_language
from vallm.core.proposal import Proposal
from vallm.scoring import validate, Verdict

TOON_EXTENSIONS = {".toon.yaml", ".toon"}

_MAX_WORKERS = min(os.cpu_count() or 1, 8)


class _CompiledPatterns:
    """Pre-compiled pattern set: exact names in a frozenset, globs in one regex."""

    __slots__ = ("exact", "regex", "is_empty")

    def __init__(self, exact: frozenset[str], regex, is_empty: bool):
        self.exact = exact
        self.regex = regex
        self.is_empty = is_empty


def _compile_patterns(raw: list[str]) -> _CompiledPatterns:
    """Split *raw* glob strings into an exact-match set and a combined regex."""
    import fnmatch
    import re

    if not raw:
        return _CompiledPatterns(frozenset(), None, True)

    exact: set[str] = set()
    regex_parts: list[str] = []

    for pat in dict.fromkeys(raw):  # deduplicate, preserve order
        if any(c in pat for c in ("*", "?", "[", "]")):
            regex_parts.append(fnmatch.translate(pat))
        else:
            exact.add(pat)

    compiled_re = re.compile("|".join(regex_parts)) if regex_parts else None
    return _CompiledPatterns(frozenset(exact), compiled_re, False)


def _validate_single_file(file_path: Path, settings: VallmSettings):
    """Validate a single file (top-level for thread-pool compatibility).

    Returns (file_path, lang_obj, result, error_str) tuple.
    """
    from vallm.validators.file_cache import get_file_cache

    lang_obj = detect_language(file_path)
    if lang_obj is None:
        return file_path, None, None, "Unsupported file type"

    cache = get_file_cache()
    cached = cache.get(file_path)
    if cached is not None:
        return file_path, lang_obj, cached, None

    try:
        code = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return file_path, None, None, "Unable to read file (binary?)"

    proposal = Proposal(
        code=code,
        language=lang_obj.tree_sitter_id,
        filename=str(file_path),
    )
    result = validate(proposal, settings)
    cache.set(file_path, result)
    return file_path, lang_obj, result, None


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
    ) -> tuple[dict, list, int]:
        """Process a batch of files for validation."""
        gitignore_parser = self._load_gitignore_parser(use_gitignore)
        
        files_to_validate = self._build_file_list(paths, recursive)
        filtered_files = self._filter_files(
            files_to_validate, include, exclude, gitignore_parser, use_gitignore
        )
        
        if not filtered_files:
            self._handle_no_files_found(output_format)
            return {}, [], 0, []
        
        self._show_validation_start(filtered_files, output_format)
        
        results_by_language, failed_files, passed_count, _ = self._process_files(
            filtered_files, settings, output_format, fail_fast, verbose, show_issues
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
            results_by_language, filtered_files, passed_count, failed_files, output_format
        )
    
    def _load_gitignore_parser(self, use_gitignore: bool):
        """Load gitignore parser if enabled."""
        if not use_gitignore:
            return None
            
        gitignore_parser = load_gitignore()
        if gitignore_parser.root.exists():
            self.console.print(f"[dim]Using .gitignore from {gitignore_parser.root}[/dim]")
        else:
            self.console.print(f"[dim]No .gitignore found, using default excludes[/dim]")
        return gitignore_parser
    
    def _build_file_list(self, paths: list[Path], recursive: bool) -> list[Path]:
        """Build list of files from input paths."""
        files_to_validate: list[Path] = []
        
        for path in paths:
            if path.is_file():
                files_to_validate.append(path)
            elif path.is_dir():
                if recursive:
                    for file_path in path.rglob("*"):
                        if file_path.is_file():
                            files_to_validate.append(file_path)
                else:
                    for file_path in path.iterdir():
                        if file_path.is_file():
                            files_to_validate.append(file_path)
        
        return files_to_validate
    
    def _filter_files(
        self,
        files: list[Path],
        include: Optional[str],
        exclude: Optional[str],
        gitignore_parser,
        use_gitignore: bool,
    ) -> list[Path]:
        """Filter files based on patterns and gitignore."""
        filtered_files = []
        excluded_by_gitignore = 0
        
        patterns = self._parse_filter_patterns(include, exclude)
        
        for f in files:
            if use_gitignore and gitignore_parser and gitignore_parser.matches(f):
                excluded_by_gitignore += 1
                continue
                
            if self._should_exclude_file(f, patterns["exclude"]):
                continue
                
            if self._matches_include_pattern(f, patterns["include"]):
                filtered_files.append(f)
        
        if excluded_by_gitignore > 0:
            self.console.print(f"[dim]Excluded {excluded_by_gitignore} files by .gitignore[/dim]")
        
        return filtered_files
    
    def _parse_filter_patterns(self, include: Optional[str], exclude: Optional[str]) -> dict:
        """Parse include and exclude patterns into compiled matchers."""
        raw_exclude: list[str] = []
        if exclude:
            raw_exclude = exclude.split(",")

        raw_exclude.extend([
            # Python
            "*.pyc", "*.pyo", "*.pyd", "__pycache__", ".pytest_cache",
            "*.egg-info", "build", "dist", ".tox", ".coverage", "htmlcov",
            # Git
            ".git", ".gitignore", ".gitmodules", ".github",
            # IDE/Editor
            ".vscode", ".idea", "*.swp", "*.swo", "*~", ".DS_Store",
            # Virtual environments
            "venv", "env", ".venv", "ENV", "virtualenv", "publish-env",
            # Dependencies
            "node_modules", "npm-debug.log*", "yarn-debug.log*", "yarn-error.log*",
            # Build artifacts
            "build", "dist", "target", "bin", "out",
            # Cache and temp
            ".cache", "cache", "*.cache", "tmp", "temp", "*.tmp", "*.temp",
            # Logs
            "*.log", "logs",
            # OS specific
            ".DS_Store", "Thumbs.db", "desktop.ini",
            # Project specific
            ".ruff_cache", ".mypy_cache", ".pytest_cache", ".coverage",
            # Documentation build
            "_build", "site", ".doctrees",
            # Database
            "*.db", "*.sqlite", "*.sqlite3",
            # Archives
            "*.zip", "*.tar.gz", "*.rar", "*.7z",
            # Binary files
            "*.png", "*.jpg", "*.jpeg", "*.gif", "*.bmp", "*.ico",
            "*.pdf", "*.doc", "*.docx", "*.xls", "*.xlsx",
            # Large data files
            "*.jsonl", "*.parquet", "*.csv", "*.tsv",
        ])

        raw_include: list[str] = []
        if include:
            raw_include = include.split(",")

        return {
            "exclude": _compile_patterns(raw_exclude),
            "include": _compile_patterns(raw_include),
        }

    def _should_exclude_file(self, file_path: Path, compiled: _CompiledPatterns) -> bool:
        """Check if file should be excluded based on pre-compiled patterns."""
        file_name = file_path.name
        file_str_lower = str(file_path).lower()

        if any(file_str_lower.endswith(ext) for ext in TOON_EXTENSIONS):
            return True

        if file_name in compiled.exact or any(p in compiled.exact for p in file_path.parts):
            return True

        if compiled.regex and (
            compiled.regex.search(file_name)
            or any(compiled.regex.search(p) for p in file_path.parts)
        ):
            return True

        return False

    def _matches_include_pattern(self, file_path: Path, compiled: _CompiledPatterns) -> bool:
        """Check if file matches pre-compiled include patterns."""
        if compiled.is_empty:
            return True

        file_name = file_path.name
        if file_name in compiled.exact:
            return True

        if compiled.regex and compiled.regex.search(file_name):
            return True

        return False
    
    def _handle_no_files_found(self, output_format: str) -> None:
        """Handle case when no files are found to validate."""
        from vallm.cli.output_formatters import output_batch_empty
        output_batch_empty(output_format)
    
    def _show_validation_start(self, filtered_files: list[Path], output_format: str) -> None:
        """Show validation start message."""
        if output_format == "rich":
            self.console.print(f"[bold]Validating {len(filtered_files)} files...[/bold]")
    
    def _read_file_text(self, file_path: Path) -> Optional[str]:
        """Read file as text; return None on encoding error."""
        try:
            return file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return None

    def _detect_file_language(self, file_path: Path):
        """Detect language object or return None for unsupported files."""
        return detect_language(file_path)

    def _show_progress(self, i: int, total: int, file_path: Path, output_format: str) -> None:
        """Print per-file progress line in rich mode."""
        if output_format == "rich":
            self.console.print(f"[dim]Processing {i}/{total}: {file_path}[/dim]")

    def _handle_validation_result(
        self,
        result,
        file_path: Path,
        lang_obj,
        output_format: str,
        show_issues: bool,
        results_by_language: dict,
        failed_files: list,
    ) -> bool:
        """Record result; return True if the file passed."""
        language = lang_obj.tree_sitter_id
        results_by_language.setdefault(language, []).append(result)

        if result.verdict.value == "pass":
            return True

        failed_files.append((file_path, f"Validation {result.verdict.value}"))
        if output_format == "rich":
            if result.all_issues and show_issues:
                self.console.print(
                    f"\n[red]✗ {file_path} ({lang_obj.display_name}) - {result.verdict.value}[/red]"
                )
                severity_colors = {"error": "red", "warning": "yellow", "info": "blue"}
                for issue in result.all_issues:
                    location = f" (line {issue.line})" if issue.line else ""
                    color = severity_colors.get(issue.severity.value, "white")
                    self.console.print(
                        f"  [{color}]• {issue.rule}: {issue.message}{location}[/{color}]"
                    )
            else:
                self.console.print(
                    f"[red]✗[/red] {file_path} ({lang_obj.display_name}) - {result.verdict.value}"
                )
        return False

    def _show_verbose_output(self, file_path: Path, result, show_issues: bool) -> None:
        """Print verbose per-file details."""
        self.console.print(f"\n[bold]{file_path}[/bold]")
        from vallm.cli.output_formatters import output_validate_result
        output_validate_result(result, "text", True)
        if show_issues and result.all_issues:
            for issue in result.all_issues:
                location = f" (line {issue.line})" if issue.line else ""
                self.console.print(f"  {issue.severity.value}: {issue.message}{location}")

    def _process_files(
        self,
        filtered_files: list[Path],
        settings: VallmSettings,
        output_format: str,
        fail_fast: bool,
        verbose: bool,
        show_issues: bool,
    ) -> tuple[dict, list, int, list]:
        """Process all files for validation."""
        use_parallel = (
            not fail_fast
            and not verbose
            and len(filtered_files) >= 4
            and _MAX_WORKERS > 1
        )
        if use_parallel:
            return self._process_files_parallel(
                filtered_files, settings, output_format, show_issues,
            )
        return self._process_files_sequential(
            filtered_files, settings, output_format, fail_fast, verbose, show_issues,
        )

    def _process_files_parallel(
        self,
        filtered_files: list[Path],
        settings: VallmSettings,
        output_format: str,
        show_issues: bool,
    ) -> tuple[dict, list, int, list]:
        """Process files using a thread pool for CPU-bound validators."""
        results_by_language: dict = {}
        failed_files: list = []
        passed_count = 0
        total = len(filtered_files)
        done = 0

        with ThreadPoolExecutor(max_workers=_MAX_WORKERS) as pool:
            futures = {
                pool.submit(_validate_single_file, fp, settings): fp
                for fp in filtered_files
            }
            for future in as_completed(futures):
                done += 1
                try:
                    file_path, lang_obj, result, error = future.result()
                except Exception as e:
                    file_path = futures[future]
                    failed_files.append((file_path, f"Error: {str(e)}"))
                    continue

                if error is not None:
                    failed_files.append((file_path, error))
                    continue

                self._show_progress(done, total, file_path, output_format)
                passed = self._handle_validation_result(
                    result, file_path, lang_obj, output_format,
                    show_issues, results_by_language, failed_files,
                )
                if passed:
                    passed_count += 1

        return results_by_language, failed_files, passed_count, filtered_files

    def _process_files_sequential(
        self,
        filtered_files: list[Path],
        settings: VallmSettings,
        output_format: str,
        fail_fast: bool,
        verbose: bool,
        show_issues: bool,
    ) -> tuple[dict, list, int, list]:
        """Process files sequentially (used for fail_fast / verbose modes)."""
        from vallm.validators.file_cache import get_file_cache

        results_by_language: dict = {}
        failed_files: list = []
        passed_count = 0
        total = len(filtered_files)
        cache = get_file_cache()

        for i, file_path in enumerate(filtered_files, 1):
            try:
                self._show_progress(i, total, file_path, output_format)

                lang_obj = self._detect_file_language(file_path)
                if lang_obj is None:
                    failed_files.append((file_path, "Unsupported file type"))
                    continue

                cached = cache.get(file_path)
                if cached is not None:
                    result = cached
                else:
                    code = self._read_file_text(file_path)
                    if code is None:
                        failed_files.append((file_path, "Unable to read file (binary?)"))
                        continue

                    proposal = Proposal(
                        code=code,
                        language=lang_obj.tree_sitter_id,
                        filename=str(file_path),
                    )
                    result = validate(proposal, settings)
                    cache.set(file_path, result)

                passed = self._handle_validation_result(
                    result, file_path, lang_obj, output_format,
                    show_issues, results_by_language, failed_files,
                )
                if passed:
                    passed_count += 1

                if verbose:
                    self._show_verbose_output(file_path, result, show_issues)

                if fail_fast and result.verdict.value != "pass":
                    if output_format == "rich":
                        self.console.print(
                            f"[red]Stopping early due to failure: {file_path}[/red]"
                        )
                    break

            except Exception as e:
                failed_files.append((file_path, f"Error: {str(e)}"))
                if fail_fast:
                    if output_format == "rich":
                        self.console.print(
                            f"[red]Stopping early due to error: {file_path}[/red]"
                        )
                    break

        return results_by_language, failed_files, passed_count, filtered_files
