"""CLI interface using Typer."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

app = typer.Typer(
    name="vallm",
    help="Validate LLM-generated code with a multi-tier pipeline.",
    no_args_is_help=True,
)
console = Console()


@app.command()
def validate(
    code: Optional[str] = typer.Option(None, "--code", "-c", help="Code string to validate"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="File to validate"),
    language: Optional[str] = typer.Option(None, "--lang", "-l", help="Programming language (auto-detected from file extension if not specified)"),
    reference: Optional[Path] = typer.Option(None, "--ref", "-r", help="Reference code file"),
    config: Optional[Path] = typer.Option(None, "--config", help="Path to vallm.toml"),
    enable_semantic: bool = typer.Option(False, "--semantic", help="Enable LLM-as-judge"),
    enable_security: bool = typer.Option(False, "--security", help="Enable security checks"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="LLM model for semantic"),
    output_format: str = typer.Option("rich", "--format", help="Output format: rich, json, text"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """Validate a code proposal through the vallm pipeline."""
    from vallm.config import VallmSettings
    from vallm.core.languages import detect_language, get_language_for_validation
    from vallm.core.proposal import Proposal
    from vallm.scoring import validate as run_validate

    # Load code
    if file:
        if not file.exists():
            console.print(f"[red]Error: File not found: {file}[/red]")
            raise typer.Exit(1)
        code_str = file.read_text()
    elif code:
        code_str = code
    else:
        console.print("[red]Error: Provide --code or --file[/red]")
        raise typer.Exit(1)

    # Load reference
    ref_code = None
    if reference and reference.exists():
        ref_code = reference.read_text()

    # Build settings
    settings = VallmSettings()
    if config and config.exists():
        settings = VallmSettings.from_toml(config)

    settings.enable_semantic = enable_semantic
    settings.enable_security = enable_security
    if model:
        settings.llm_model = model
    settings.verbose = verbose

    # Auto-detect language from file if not specified
    detected_language = get_language_for_validation(file if file else "python", language)
    if language is None and file:
        lang_obj = detect_language(file)
        if lang_obj:
            console.print(f"[dim]Detected language: {lang_obj.display_name}[/dim]")

    # Build proposal
    proposal = Proposal(
        code=code_str,
        language=detected_language,
        reference_code=ref_code,
        filename=str(file) if file else None,
    )

    # Run validation
    with console.status("[bold green]Running validation pipeline..."):
        result = run_validate(proposal, settings)

    # Output
    if output_format == "json":
        _output_json(result)
    elif output_format == "text":
        _output_text(result)
    else:
        _output_rich(result, verbose)

    # Exit code based on verdict
    from vallm.scoring import Verdict

    if result.verdict == Verdict.FAIL:
        raise typer.Exit(2)
    elif result.verdict == Verdict.REVIEW:
        raise typer.Exit(1)


@app.command()
def check(
    file: Path = typer.Argument(..., help="File to syntax-check"),
    language: Optional[str] = typer.Option(None, "--lang", "-l", help="Programming language (auto-detected if not specified)"),
):
    """Quick syntax check only (tier 1)."""
    from vallm.core.languages import detect_language
    from vallm.core.proposal import Proposal
    from vallm.validators.syntax import SyntaxValidator

    if not file.exists():
        console.print(f"[red]Error: File not found: {file}[/red]")
        raise typer.Exit(1)

    code = file.read_text()
    
    # Auto-detect language
    lang_obj = detect_language(file)
    lang = language or (lang_obj.tree_sitter_id if lang_obj else "python")
    
    if language is None and lang_obj:
        console.print(f"[dim]Detected language: {lang_obj.display_name}[/dim]")
    
    proposal = Proposal(code=code, language=lang, filename=str(file))
    result = SyntaxValidator().validate(proposal, {})

    if result.score == 1.0:
        console.print(f"[green]✓[/green] {file}: syntax OK")
    else:
        console.print(f"[red]✗[/red] {file}: syntax errors")
        for issue in result.issues:
            console.print(f"  {issue}")
        raise typer.Exit(1)


@app.command()
def batch(
    paths: list[Path] = typer.Argument(..., help="Files or directories to validate"),
    recursive: bool = typer.Option(False, "--recursive", "-r", help="Recurse into directories"),
    include: Optional[str] = typer.Option(None, "--include", help="File patterns to include (comma-separated, e.g., '*.py,*.js')"),
    exclude: Optional[str] = typer.Option(None, "--exclude", help="File patterns to exclude (comma-separated)"),
    output_format: str = typer.Option("rich", "--format", help="Output format: rich, json, text"),
    fail_fast: bool = typer.Option(False, "--fail-fast", "-x", help="Stop on first failure"),
):
    """Validate multiple files with auto-detected languages."""
    from vallm.config import VallmSettings
    from vallm.core.languages import detect_language, Language
    from vallm.core.proposal import Proposal
    from vallm.scoring import validate as run_validate, Verdict
    
    import fnmatch
    
    settings = VallmSettings()
    
    # Build file list
    files_to_validate: list[Path] = []
    include_patterns = [p.strip() for p in (include or "*.py,*.js,*.ts,*.java,*.go,*.rs,*.cpp,*.c,*.rb,*.php").split(",")]
    exclude_patterns = [p.strip() for p in (exclude or "node_modules/*,venv/*,.git/*,__pycache__/*").split(",")] if exclude else []
    
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
    
    # Filter by patterns
    filtered_files = []
    for f in files_to_validate:
        str_path = str(f)
        # Check excludes first
        if any(fnmatch.fnmatch(str_path, p) or fnmatch.fnmatch(f.name, p) for p in exclude_patterns):
            continue
        # Check includes
        if any(fnmatch.fnmatch(f.name, p) for p in include_patterns):
            filtered_files.append(f)
    
    if not filtered_files:
        console.print("[yellow]No files found to validate[/yellow]")
        raise typer.Exit(0)
    
    console.print(f"[bold]Validating {len(filtered_files)} files...[/bold]\n")
    
    results_by_language: dict[str, list[tuple[Path, any]]] = {}
    failed_files = []
    passed_count = 0
    
    for file_path in filtered_files:
        lang_obj = detect_language(file_path)
        lang_name = lang_obj.display_name if lang_obj else "Unknown"
        
        try:
            code = file_path.read_text()
            proposal = Proposal(
                code=code,
                language=lang_obj.tree_sitter_id if lang_obj else "python",
                filename=str(file_path)
            )
            
            result = run_validate(proposal, settings)
            
            if lang_name not in results_by_language:
                results_by_language[lang_name] = []
            results_by_language[lang_name].append((file_path, result))
            
            if result.verdict == Verdict.PASS:
                passed_count += 1
                console.print(f"[green]✓[/green] {file_path} ({lang_name})")
            elif result.verdict == Verdict.REVIEW:
                console.print(f"[yellow]⚠[/yellow] {file_path} ({lang_name}) - needs review")
            else:
                failed_files.append(file_path)
                console.print(f"[red]✗[/red] {file_path} ({lang_name}) - failed")
                
            if fail_fast and result.verdict == Verdict.FAIL:
                break
                
        except Exception as e:
            failed_files.append(file_path)
            console.print(f"[red]✗[/red] {file_path} - error: {e}")
            if fail_fast:
                break
    
    # Summary table
    console.print("\n" + "="*60)
    console.print("[bold]BATCH VALIDATION SUMMARY[/bold]")
    console.print("="*60)
    
    table = Table()
    table.add_column("Language", style="cyan")
    table.add_column("Files", justify="right")
    table.add_column("Passed", justify="right")
    table.add_column("Failed", justify="right")
    
    for lang, results in sorted(results_by_language.items()):
        passed = sum(1 for _, r in results if r.verdict == Verdict.PASS)
        failed = len(results) - passed
        table.add_row(lang, str(len(results)), f"[green]{passed}[/green]", f"[red]{failed}[/red]" if failed > 0 else str(failed))
    
    console.print(table)
    console.print(f"\nTotal: {len(filtered_files)} files, {passed_count} passed, {len(failed_files)} failed")
    
    if failed_files:
        raise typer.Exit(2)


@app.command()
def info():
    """Show vallm configuration and available validators."""
    from vallm.config import VallmSettings

    settings = VallmSettings()

    table = Table(title="vallm Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    for key, value in settings.model_dump().items():
        table.add_row(key, str(value))

    console.print(table)

    # Check optional deps
    console.print("\n[bold]Optional Dependencies:[/bold]")
    _check_dep("ollama", "LLM (Ollama)")
    _check_dep("litellm", "LLM (multi-provider)")
    _check_dep("bandit", "Security analysis")
    _check_dep("code_bert_score", "CodeBERTScore")
    _check_dep("networkx", "Graph analysis")


def _check_dep(module: str, label: str):
    try:
        __import__(module)
        console.print(f"  [green]✓[/green] {label} ({module})")
    except ImportError:
        console.print(f"  [dim]✗ {label} ({module}) — not installed[/dim]")


def _output_rich(result, verbose: bool):
    from vallm.scoring import Verdict

    # Verdict banner
    verdict_colors = {
        Verdict.PASS: "green",
        Verdict.REVIEW: "yellow",
        Verdict.FAIL: "red",
    }
    color = verdict_colors[result.verdict]
    console.print(
        Panel(
            f"[bold {color}]{result.verdict.value.upper()}[/bold {color}]"
            f"  Score: {result.weighted_score:.2f}",
            title="vallm Verdict",
        )
    )

    # Results table
    table = Table(title="Validator Results")
    table.add_column("Validator", style="cyan")
    table.add_column("Score", justify="right")
    table.add_column("Weight", justify="right")
    table.add_column("Issues", justify="right")

    for r in result.results:
        score_color = "green" if r.score >= 0.8 else "yellow" if r.score >= 0.5 else "red"
        table.add_row(
            r.validator,
            f"[{score_color}]{r.score:.2f}[/{score_color}]",
            f"{r.weight:.1f}",
            str(len(r.issues)),
        )

    console.print(table)

    # Issues
    if result.all_issues:
        console.print(f"\n[bold]Issues ({result.error_count} errors, {result.warning_count} warnings):[/bold]")
        for issue in result.all_issues:
            icon = "🔴" if issue.severity.value == "error" else "🟡" if issue.severity.value == "warning" else "🔵"
            console.print(f"  {icon} {issue}")

    if verbose:
        for r in result.results:
            if r.details:
                console.print(f"\n[dim]{r.validator} details: {r.details}[/dim]")


def _output_json(result):
    import json

    data = {
        "verdict": result.verdict.value,
        "score": result.weighted_score,
        "errors": result.error_count,
        "warnings": result.warning_count,
        "results": [
            {
                "validator": r.validator,
                "score": r.score,
                "weight": r.weight,
                "confidence": r.confidence,
                "issues": [
                    {
                        "message": i.message,
                        "severity": i.severity.value,
                        "line": i.line,
                        "rule": i.rule,
                    }
                    for i in r.issues
                ],
                "details": r.details,
            }
            for r in result.results
        ],
    }
    console.print_json(json.dumps(data))


def _output_text(result):
    print(f"Verdict: {result.verdict.value}")
    print(f"Score: {result.weighted_score:.2f}")
    for r in result.results:
        print(f"  {r.validator}: {r.score:.2f} (weight={r.weight})")
        for issue in r.issues:
            print(f"    {issue}")


if __name__ == "__main__":
    app()
