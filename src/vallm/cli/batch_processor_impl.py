from __future__ import annotations
from pathlib import Path
from typing import Optional
from rich.console import Console
from vallm.cli.batch_processor_files import build_file_list
from vallm.cli.batch_processor_filter import parse_filter_patterns, should_exclude_file, matches_include_pattern
from vallm.cli.output_formatters import output_batch_empty as render_batch_empty, output_batch_results as render_batch_results
from vallm.core.gitignore import load_gitignore
from vallm.core.languages import detect_language

class BatchProcessor:
    def __init__(self, console: Console):
        self.console = console

    def _filter_files(self, files: list[Path], include: Optional[str], exclude: Optional[str], gitignore_parser, use_gitignore: bool) -> list[Path]:
        filtered_files = []
        excluded_by_gitignore = 0
        patterns = parse_filter_patterns(include, exclude)
        for f in files:
            if use_gitignore and gitignore_parser and gitignore_parser.matches(f):
                excluded_by_gitignore += 1
                continue
            if should_exclude_file(f, patterns["exclude"]): continue
            if matches_include_pattern(f, patterns["include"]): filtered_files.append(f)
        if excluded_by_gitignore > 0: self.console.print(f"[dim]Excluded {excluded_by_gitignore} files by .gitignore[/dim]")
        return filtered_files

    def _load_gitignore_parser(self, use_gitignore: bool):
        if not use_gitignore: return None
        gitignore_parser = load_gitignore()
        msg = f"[dim]Using .gitignore from {gitignore_parser.root}[/dim]" if gitignore_parser.root.exists() else "[dim]No .gitignore found, using default excludes[/dim]"
        self.console.print(msg)
        return gitignore_parser