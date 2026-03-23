"""Command handlers for vallm CLI."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from vallm.cli.batch_processor import BatchProcessor
from vallm.cli.settings_builders import build_validate_settings, build_batch_settings
from vallm.cli.output_formatters import output_validate_result
from vallm.core.languages import detect_language
from vallm.core.proposal import Proposal

console = Console()


def validate_command(
    code: Optional[str] = typer.Option(None, "--code", "-c", help="Code string to validate"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="File to validate"),
    language: Optional[str] = typer.Option(None, "--lang", "-l", help="Programming language"),
    reference: Optional[Path] = typer.Option(None, "--ref", "-r", help="Reference code file"),
    config: Optional[Path] = typer.Option(None, "--config", help="Path to vallm.toml"),
    enable_semantic: bool = typer.Option(False, "--semantic", help="Enable LLM-as-judge"),
    enable_security: bool = typer.Option(False, "--security", help="Enable security checks"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="LLM model for semantic"),
    output_format: str = typer.Option("rich", "--output", "-o", help="Output format"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed results"),
    exit_on_verdict: bool = typer.Option(False, "--exit", help="Exit with non-zero on fail/review"),
) -> None:
    """Validate code with the full pipeline."""
    # Load code
    code_str = _load_code(file, code)
    
    # Load reference if provided
    ref_code = _load_reference(reference)
    
    # Detect language
    detected_language = _detect_and_log_language(file, language)
    
    # Build settings
    settings = build_validate_settings(config, enable_semantic, enable_security, model, verbose)
    
    # Create proposal
    proposal = _build_proposal(code_str, detected_language, ref_code, file)
    
    # Run validation
    from vallm.scoring import validate
    
    result = validate(proposal, settings)
    
    # Output result
    output_validate_result(result, output_format, verbose)
    
    # Exit on verdict if requested
    if exit_on_verdict:
        _exit_on_verdict(result)


def check_command(
    code: Optional[str] = typer.Option(None, "--code", "-c", help="Code string to validate"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="File to validate"),
    language: Optional[str] = typer.Option(None, "--lang", "-l", help="Programming language"),
    output_format: str = typer.Option("rich", "--output", "-o", help="Output format"),
) -> None:
    """Quick syntax check only (tier 1)."""
    # Load code
    code_str = _load_code(file, code)
    
    # Detect language
    detected_language = _detect_and_log_language(file, language)
    
    # Create proposal
    proposal = _build_proposal(code_str, detected_language, None, file)
    
    # Run syntax-only validation
    from vallm.scoring import validate
    
    # Only enable syntax validator
    settings = build_validate_settings(None, False, False, None, False)
    settings.enable_syntax = True
    settings.enable_imports = False
    settings.enable_complexity = False
    settings.enable_security = False
    settings.enable_semantic = False
    
    result = validate(proposal, settings)
    
    # Output result
    output_validate_result(result, output_format, False)


def batch_command(
    paths: list[Path] = typer.Argument(..., help="Files or directories to validate"),
    recursive: bool = typer.Option(False, "--recursive", "-r", help="Search directories recursively"),
    include: Optional[str] = typer.Option(None, "--include", help="Include pattern (glob)"),
    exclude: Optional[str] = typer.Option(None, "--exclude", help="Exclude pattern (glob)"),
    use_gitignore: bool = typer.Option(True, "--gitignore/--no-gitignore", help="Respect .gitignore"),
    enable_semantic: bool = typer.Option(False, "--semantic", help="Enable LLM-as-judge"),
    enable_security: bool = typer.Option(False, "--security", help="Enable security checks"),
    no_imports: bool = typer.Option(False, "--no-imports", help="Skip import validation (faster)"),
    no_complexity: bool = typer.Option(False, "--no-complexity", help="Skip complexity analysis (faster)"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="LLM model for semantic"),
    format: str = typer.Option("rich", "--format", "-f", help="Output format"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory"),
    fail_fast: bool = typer.Option(False, "--fail-fast", help="Stop on first failure"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed validation results for each file"),
    show_issues: bool = typer.Option(False, "--show-issues", "-i", help="Show issues for failed files"),
) -> None:
    """Validate multiple files with auto-detected languages."""
    from vallm.cli.batch_processor import BatchProcessor
    processor = BatchProcessor(console)
    
    settings = build_batch_settings(enable_semantic, enable_security, model, verbose, no_imports, no_complexity)
    
    results_by_language, failed_files, passed_count, filtered_files = processor.process_batch(
        paths=paths,
        recursive=recursive,
        include=include,
        exclude=exclude,
        use_gitignore=use_gitignore,
        settings=settings,
        output_format=output_format,
        fail_fast=fail_fast,
        verbose=verbose,
        show_issues=show_issues,
    )
    
    processor.output_batch_results(
        results_by_language, passed_count, failed_files, output_format, filtered_files
    )
    
    if failed_files:
        raise typer.Exit(2)


def info_command(
    language: Optional[str] = typer.Option(None, "--lang", "-l", help="Show info for specific language"),
    clear_cache: bool = typer.Option(False, "--clear-cache", help="Clear semantic validation cache"),
) -> None:
    """Show information about supported languages and validators."""
    
    # Handle cache clearing first
    if clear_cache:
        from vallm.validators.semantic_cache import clear_semantic_cache, get_semantic_cache
        clear_semantic_cache()
        cache_stats = get_semantic_cache().get_cache_stats()
        console.print("[green]✓[/green] Semantic validation cache cleared")
        console.print(f"[dim]Cache stats: {cache_stats['total_entries']} entries cleared[/dim]")
        return
    
    from vallm.core.languages import Language
    from vallm.validators.base import BaseValidator
    
    if language:
        # Show info for specific language
        try:
            lang = Language(language.lower())
            _show_language_info(lang)
        except ValueError:
            console.error(f"[red]Error: Unsupported language: {language}[/red]")
            raise typer.Exit(1)
    else:
        # Show general info
        _show_general_info()


# Private helper functions

def _load_code(file: Optional[Path], code: Optional[str]) -> str:
    """Load code from file or string parameter."""
    if file:
        if not file.exists():
            console.error(f"[red]Error: File not found: {file}[/red]")
            raise typer.Exit(1)
        return file.read_text()
    elif code:
        return code
    else:
        console.error("[red]Error: Provide --code or --file[/red]")
        raise typer.Exit(1)


def _load_reference(reference: Optional[Path]) -> Optional[str]:
    """Load reference code if provided."""
    if reference and reference.exists():
        return reference.read_text()
    return None


def _detect_and_log_language(file: Optional[Path], language: Optional[str]) -> str:
    """Detect language and log it."""
    if language:
        detected_language = language
        console.print(f"[dim]Using specified language: {detected_language}[/dim]")
    elif file:
        lang_obj = detect_language(file)
        detected_language = lang_obj.value[0]  # tree-sitter identifier
        console.print(f"[dim]Detected language: {detected_language}[/dim]")
    else:
        detected_language = "python"  # default for string input
        console.print(f"[dim]Using default language: {detected_language}[/dim]")
    
    return detected_language


def _build_proposal(code_str: str, detected_language: str, ref_code: Optional[str], file: Optional[Path]) -> Proposal:
    """Build a proposal object."""
    from vallm.core.proposal import Proposal
    
    return Proposal(
        code=code_str,
        language=detected_language,
        reference_code=ref_code,
        filename=str(file) if file else None,
    )


def _exit_on_verdict(result) -> None:
    """Exit with appropriate code based on verdict."""
    from vallm.scoring import Verdict
    
    if result.verdict == Verdict.FAIL:
        raise typer.Exit(1)
    elif result.verdict == Verdict.REVIEW:
        raise typer.Exit(2)


def _show_language_info(language) -> None:
    """Show detailed information for a specific language."""
    console.print(f"[bold]{language.display_name}[/bold]")
    console.print(f"Value: {language.value}")
    console.print(f"Extensions: {', '.join(language.extensions)}")
    console.print(f"Tree-sitter language: {language.tree_sitter_language}")
    console.print(f"Compiled: {'Yes' if language.is_compiled() else 'No'}")
    
    # Show validators that support this language
    from vallm.validators.base import BaseValidator
    from vallm.validators.imports.factory import ImportValidatorFactory
    
    console.print("\n[bold]Supported Validators:[/bold]")
    
    # Syntax validator (supports all)
    console.print("  ✓ Syntax validation")
    
    # Import validation
    factory = ImportValidatorFactory()
    if language.value in factory.supported_languages():
        console.print("  ✓ Import validation")
    
    # Complexity validation
    from vallm.core.languages import LIZARD_SUPPORTED
    if language in LIZARD_SUPPORTED:
        console.print("  ✓ Complexity analysis")
    
    # Security validation (supports all)
    console.print("  ✓ Security analysis")
    
    # Semantic validation (supports all with LLM)
    console.print("  ✓ Semantic analysis (requires LLM)")


def _show_general_info() -> None:
    """Show general information about vallm."""
    from vallm.core.languages import Language
    from vallm.validators.imports.factory import ImportValidatorFactory
    from vallm.validators.semantic_cache import get_semantic_cache
    
    console.print("[bold]VALLM - Code Validation Tool[/bold]")
    console.print()
    
    console.print("[bold]Supported Languages:[/bold]")
    for lang in Language:
        console.print(f"  {lang.display_name} ({lang.tree_sitter_id}) - {lang.extension}")
    
    console.print("\n[bold]Available Validators:[/bold]")
    console.print("  1. Syntax validation - Fast syntax checking")
    console.print("  2. Import validation - Module resolution checking")
    console.print("  3. Complexity analysis - Cyclomatic complexity metrics")
    console.print("  4. Security analysis - Security pattern detection")
    console.print("  5. Semantic analysis - LLM-powered code review")
    
    # Show cache stats
    cache_stats = get_semantic_cache().get_cache_stats()
    console.print(f"\n[bold]Semantic Cache:[/bold]")
    console.print(f"  Cached entries: {cache_stats['total_entries']}")
    console.print(f"  Use 'vallm info --clear-cache' to clear cache")
    
    console.print("\n[bold]Import Validation Languages:[/bold]")
    factory = ImportValidatorFactory()
    for lang in factory.supported_languages():
        console.print(f"  {lang}")
