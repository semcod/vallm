"""Batch processing utilities for vallm CLI."""

from __future__ import annotations

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
            return {}, [], 0
        
        self._show_validation_start(filtered_files, output_format)
        
        results_by_language, failed_files, passed_count = self._process_files(
            filtered_files, settings, output_format, fail_fast, verbose, show_issues
        )
        
        return results_by_language, failed_files, passed_count
    
    def output_batch_results(
        self,
        results_by_language: dict,
        passed_count: int,
        failed_files: list,
        output_format: str,
    ) -> None:
        """Output batch validation results."""
        output_batch_results(
            results_by_language, [], passed_count, failed_files, output_format
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
        """Parse include and exclude patterns."""
        import fnmatch
        
        patterns = {"include": [], "exclude": []}
        
        if include:
            patterns["include"] = include.split(",")
        
        if exclude:
            patterns["exclude"] = exclude.split(",")
        
        # Add default exclude patterns
        patterns["exclude"].extend([
            "*.pyc", "*.pyo", "*.pyd", "__pycache__", ".git", ".pytest_cache",
            "*.egg-info", "build", "dist", ".tox", ".coverage", "htmlcov",
        ])
        
        return patterns
    
    def _should_exclude_file(self, file_path: Path, exclude_patterns: list[str]) -> bool:
        """Check if file should be excluded based on patterns."""
        import fnmatch
        
        file_str = str(file_path)
        for pattern in exclude_patterns:
            if fnmatch.fnmatch(file_str, pattern) or fnmatch.fnmatch(file_path.name, pattern):
                return True
        return False
    
    def _matches_include_pattern(self, file_path: Path, include_patterns: list[str]) -> bool:
        """Check if file matches include patterns."""
        import fnmatch
        
        if not include_patterns:
            return True
        
        file_str = str(file_path)
        for pattern in include_patterns:
            if fnmatch.fnmatch(file_str, pattern) or fnmatch.fnmatch(file_path.name, pattern):
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
    
    def _process_files(
        self,
        filtered_files: list[Path],
        settings: VallmSettings,
        output_format: str,
        fail_fast: bool,
        verbose: bool,
        show_issues: bool,
    ) -> tuple[dict, list, int]:
        """Process all files for validation."""
        results_by_language = {}
        failed_files = []
        passed_count = 0
        
        for i, file_path in enumerate(filtered_files, 1):
            try:
                # Show progress for rich output
                if output_format == "rich" and not verbose:
                    self.console.print(f"[dim]Processing {i}/{len(filtered_files)}: {file_path}[/dim]")
                
                # Read file
                try:
                    code = file_path.read_text(encoding='utf-8')
                except UnicodeDecodeError:
                    failed_files.append((file_path, "Unable to read file (binary?)"))
                    continue
                
                # Detect language
                lang_obj = detect_language(file_path)
                language = lang_obj.value[0]  # tree-sitter identifier
                
                # Create proposal
                proposal = Proposal(
                    code=code,
                    language=language,
                    filename=str(file_path),
                )
                
                # Validate
                result = validate(proposal, settings)
                
                # Group by language
                if language not in results_by_language:
                    results_by_language[language] = []
                results_by_language[language].append(result)
                
                # Count passed
                if result.verdict.value == "pass":
                    passed_count += 1
                else:
                    failed_files.append((file_path, f"Validation {result.verdict.value}"))
                
                # Show detailed output if verbose
                if verbose:
                    self.console.print(f"\n[bold]{file_path}[/bold]")
                    from vallm.cli.output_formatters import output_validate_result
                    output_validate_result(result, "text", True)
                    
                    if show_issues and result.all_issues:
                        for issue in result.all_issues:
                            location = f" (line {issue.line})" if issue.line else ""
                            self.console.print(f"  {issue.severity.value}: {issue.message}{location}")
                
                # Fail fast if requested
                if fail_fast and result.verdict.value != "pass":
                    if output_format == "rich":
                        self.console.print(f"[red]Stopping early due to failure: {file_path}[/red]")
                    break
                    
            except Exception as e:
                failed_files.append((file_path, f"Error: {str(e)}"))
                if fail_fast:
                    if output_format == "rich":
                        self.console.print(f"[red]Stopping early due to error: {file_path}[/red]")
                    break
        
        return results_by_language, failed_files, passed_count
