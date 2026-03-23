"""Optimized batch processing utilities for vallm CLI with parallel processing."""

from __future__ import annotations

import asyncio
import concurrent.futures
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.progress import Progress, TaskID

from vallm.cli.output_formatters import (
    output_batch_empty,
    output_batch_results,
)
from vallm.config import VallmSettings
from vallm.core.gitignore import load_gitignore
from vallm.core.languages import detect_language
from vallm.core.proposal import Proposal
from vallm.scoring import validate, Verdict


class OptimizedBatchProcessor:
    """Optimized batch processor with parallel processing capabilities."""
    
    def __init__(self, console: Console):
        self.console = console
        # Use number of CPU cores, but cap at reasonable limit
        self.max_workers = min(os.cpu_count() or 4, 8)
    
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
        parallel: bool = True,
    ) -> tuple[dict, list, int]:
        """Process a batch of files for validation with optional parallel processing."""
        gitignore_parser = self._load_gitignore_parser(use_gitignore)
        
        files_to_validate = self._build_file_list(paths, recursive)
        filtered_files = self._filter_files(
            files_to_validate, include, exclude, gitignore_parser, use_gitignore
        )
        
        if not filtered_files:
            self._handle_no_files_found(output_format)
            return {}, [], 0
        
        self._show_validation_start(filtered_files, output_format, parallel)
        
        if parallel and len(filtered_files) > 1:
            results_by_language, failed_files, passed_count = self._process_files_parallel(
                filtered_files, settings, output_format, fail_fast, verbose, show_issues
            )
        else:
            results_by_language, failed_files, passed_count = self._process_files_sequential(
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
        """Filter files based on include/exclude patterns and gitignore."""
        filtered_files = []
        
        # Parse patterns
        include_patterns = include.split(',') if include else None
        exclude_patterns = exclude.split(',') if exclude else None
        
        for file_path in files:
            # Skip if excluded by gitignore
            if use_gitignore and gitignore_parser and gitignore_parser.matches(file_path):
                continue
            
            # Check include patterns
            if include_patterns:
                if not any(file_path.match(pattern.strip()) for pattern in include_patterns):
                    continue
            
            # Check exclude patterns
            if exclude_patterns:
                if any(file_path.match(pattern.strip()) for pattern in exclude_patterns):
                    continue
            
            filtered_files.append(file_path)
        
        return filtered_files
    
    def _process_files_sequential(
        self,
        filtered_files: list[Path],
        settings: VallmSettings,
        output_format: str,
        fail_fast: bool,
        verbose: bool,
        show_issues: bool,
    ) -> tuple[dict, list, int]:
        """Process files sequentially (original implementation)."""
        results_by_language = {}
        failed_files = []
        passed_count = 0
        
        for i, file_path in enumerate(filtered_files, 1):
            try:
                if output_format == "rich" and not verbose:
                    self.console.print(f"[dim]Processing {i}/{len(filtered_files)}: {file_path}[/dim]")
                
                result = self._validate_single_file(file_path, settings)
                
                if result is None:
                    continue
                
                language = result.language or "unknown"
                
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
                    self._show_detailed_result(file_path, result, show_issues)
                
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
    
    def _process_files_parallel(
        self,
        filtered_files: list[Path],
        settings: VallmSettings,
        output_format: str,
        fail_fast: bool,
        verbose: bool,
        show_issues: bool,
    ) -> tuple[dict, list, int]:
        """Process files in parallel using ThreadPoolExecutor."""
        results_by_language = {}
        failed_files = []
        passed_count = 0
        
        # Create progress bar for rich output
        progress = None
        task_id = None
        if output_format == "rich" and not verbose:
            progress = Progress(console=self.console)
            task_id = progress.add_task("[cyan]Validating files...", total=len(filtered_files))
            progress.start()
        
        try:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all validation tasks
                future_to_file = {
                    executor.submit(self._validate_single_file, file_path, settings): file_path
                    for file_path in filtered_files
                }
                
                # Process completed tasks
                for future in as_completed(future_to_file):
                    file_path = future_to_file[future]
                    
                    try:
                        result = future.result()
                        
                        if progress:
                            progress.advance(task_id)
                        
                        if result is None:
                            continue
                        
                        language = result.language or "unknown"
                        
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
                            self._show_detailed_result(file_path, result, show_issues)
                        
                        # Fail fast if requested
                        if fail_fast and result.verdict.value != "pass":
                            if output_format == "rich":
                                self.console.print(f"[red]Stopping early due to failure: {file_path}[/red]")
                            # Cancel remaining futures
                            for f in future_to_file:
                                f.cancel()
                            break
                            
                    except Exception as e:
                        failed_files.append((file_path, f"Error: {str(e)}"))
                        if fail_fast:
                            if output_format == "rich":
                                self.console.print(f"[red]Stopping early due to error: {file_path}[/red]")
                            break
        
        finally:
            if progress:
                progress.stop()
        
        return results_by_language, failed_files, passed_count
    
    def _validate_single_file(self, file_path: Path, settings: VallmSettings):
        """Validate a single file and return result."""
        try:
            # Read file
            code = file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            return None
        
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
        result.language = language  # Store language for grouping
        
        return result
    
    def _show_detailed_result(self, file_path: Path, result, show_issues: bool):
        """Show detailed validation result."""
        self.console.print(f"\n[bold]{file_path}[/bold]")
        from vallm.cli.output_formatters import output_validate_result
        output_validate_result(result, "text", True)
        
        if show_issues and result.all_issues:
            for issue in result.all_issues:
                location = f" (line {issue.line})" if issue.line else ""
                self.console.print(f"  {issue.severity.value}: {issue.message}{location}")
    
    def _show_validation_start(self, files: list[Path], output_format: str, parallel: bool = False):
        """Show validation start message."""
        if output_format == "rich":
            mode = "parallel" if parallel else "sequential"
            workers = f" ({self.max_workers} workers)" if parallel else ""
            self.console.print(f"[green]Validating {len(files)} files ({mode}{workers})...[/green]")
    
    def _handle_no_files_found(self, output_format: str):
        """Handle case when no files are found."""
        output_batch_empty(output_format)


# Factory function for easy instantiation
def create_optimized_batch_processor(console: Console) -> OptimizedBatchProcessor:
    """Create an optimized batch processor instance.
    
    Args:
        console: Rich console instance
        
    Returns:
        OptimizedBatchProcessor instance
    """
    return OptimizedBatchProcessor(console)
