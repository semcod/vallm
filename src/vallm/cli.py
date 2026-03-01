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
    language: str = typer.Option("python", "--lang", "-l", help="Programming language"),
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

    # Build proposal
    proposal = Proposal(
        code=code_str,
        language=language,
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
    language: str = typer.Option("python", "--lang", "-l", help="Programming language"),
):
    """Quick syntax check only (tier 1)."""
    from vallm.core.proposal import Proposal
    from vallm.validators.syntax import SyntaxValidator

    if not file.exists():
        console.print(f"[red]Error: File not found: {file}[/red]")
        raise typer.Exit(1)

    code = file.read_text()
    proposal = Proposal(code=code, language=language, filename=str(file))
    result = SyntaxValidator().validate(proposal, {})

    if result.score == 1.0:
        console.print(f"[green]✓[/green] {file}: syntax OK")
    else:
        console.print(f"[red]✗[/red] {file}: syntax errors")
        for issue in result.issues:
            console.print(f"  {issue}")
        raise typer.Exit(1)


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
