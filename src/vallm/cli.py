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


def _build_validate_settings(
    config: Optional[Path],
    enable_semantic: bool,
    enable_security: bool,
    model: Optional[str],
    verbose: bool,
):
    """Build settings for validation."""
    from vallm.config import VallmSettings

    settings = VallmSettings()
    if config and config.exists():
        settings = VallmSettings.from_toml(config)

    settings.enable_semantic = enable_semantic
    settings.enable_security = enable_security
    if model:
        settings.llm_model = model
    settings.verbose = verbose
    return settings


def _detect_and_log_language(file: Optional[Path], language: Optional[str]) -> str:
    """Auto-detect language and log if detected from file."""
    from vallm.core.languages import detect_language, get_language_for_validation

    detected_language = get_language_for_validation(file if file else "python", language)
    if language is None and file:
        lang_obj = detect_language(file)
        if lang_obj:
            console.print(f"[dim]Detected language: {lang_obj.display_name}[/dim]")
    return detected_language


def _build_proposal(
    code_str: str,
    detected_language: str,
    ref_code: Optional[str],
    file: Optional[Path],
):
    """Build a Proposal from loaded code and settings."""
    from vallm.core.proposal import Proposal

    return Proposal(
        code=code_str,
        language=detected_language,
        reference_code=ref_code,
        filename=str(file) if file else None,
    )


def _output_validate_result(result, output_format: str, verbose: bool):
    """Output validation result in the specified format."""
    if output_format == "json":
        _output_json(result)
    elif output_format == "text":
        _output_text(result)
    else:
        _output_rich(result, verbose)


def _exit_on_verdict(result):
    """Exit with appropriate code based on validation verdict."""
    from vallm.scoring import Verdict

    if result.verdict == Verdict.FAIL:
        raise typer.Exit(2)
    elif result.verdict == Verdict.REVIEW:
        raise typer.Exit(1)


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
    from vallm.scoring import validate as run_validate

    # Load code
    code_str = _load_code(file, code)

    # Load reference
    ref_code = _load_reference(reference)

    # Build settings
    settings = _build_validate_settings(config, enable_semantic, enable_security, model, verbose)

    # Auto-detect language from file if not specified
    detected_language = _detect_and_log_language(file, language)

    # Build proposal
    proposal = _build_proposal(code_str, detected_language, ref_code, file)

    # Run validation
    with console.status("[bold green]Running validation pipeline..."):
        result = run_validate(proposal, settings)

    # Output
    _output_validate_result(result, output_format, verbose)

    # Exit code based on verdict
    _exit_on_verdict(result)


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
        console.error(f"[red]Error: File not found: {file}[/red]")
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
    use_gitignore: bool = typer.Option(True, "--use-gitignore/--no-gitignore", help="Respect .gitignore patterns (default: True)"),
    output_format: str = typer.Option("rich", "--format", "-f", help="Output format: rich, json, yaml, toon, text"),
    fail_fast: bool = typer.Option(False, "--fail-fast", "-x", help="Stop on first failure"),
    enable_semantic: bool = typer.Option(False, "--semantic", help="Enable LLM-as-judge"),
    enable_security: bool = typer.Option(False, "--security", help="Enable security checks"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="LLM model for semantic"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed validation results for each file"),
    show_issues: bool = typer.Option(False, "--show-issues", "-i", help="Show issues for failed files"),
):
    """Validate multiple files with auto-detected languages."""
    settings = _load_batch_settings(enable_semantic, enable_security, model, verbose)
    gitignore_parser = _load_gitignore_parser(use_gitignore)
    
    files_to_validate = _build_file_list(paths, recursive)
    filtered_files = _filter_files(
        files_to_validate, include, exclude, gitignore_parser, use_gitignore
    )
    
    if not filtered_files:
        _handle_no_files_found(output_format)
        return
    
    _show_validation_start(filtered_files, output_format)
    
    results_by_language, failed_files, passed_count = _process_files(
        filtered_files, settings, output_format, fail_fast, verbose, show_issues
    )
    
    _output_batch_results(
        results_by_language, filtered_files, passed_count, failed_files, output_format
    )
    
    if failed_files:
        raise typer.Exit(2)


def _load_batch_settings(enable_semantic: bool, enable_security: bool, 
                        model: Optional[str], verbose: bool):
    """Load and configure settings for batch validation."""
    from vallm.config import VallmSettings
    
    settings = VallmSettings()
    settings.enable_semantic = enable_semantic
    settings.enable_security = enable_security
    if model:
        settings.llm_model = model
    settings.verbose = verbose
    return settings


def _load_gitignore_parser(use_gitignore: bool):
    """Load gitignore parser if enabled."""
    if not use_gitignore:
        return None
        
    from vallm.core.gitignore import load_gitignore
    
    gitignore_parser = load_gitignore()
    if gitignore_parser.root.exists():
        console.print(f"[dim]Using .gitignore from {gitignore_parser.root}[/dim]")
    else:
        console.print(f"[dim]No .gitignore found, using default excludes[/dim]")
    return gitignore_parser


def _build_file_list(paths: list[Path], recursive: bool) -> list[Path]:
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


def _filter_files(files: list[Path], include: Optional[str], exclude: Optional[str],
                 gitignore_parser, use_gitignore: bool) -> list[Path]:
    """Filter files based on patterns and gitignore."""
    filtered_files = []
    excluded_by_gitignore = 0
    
    patterns = _parse_filter_patterns(include, exclude)
    
    for f in files:
        if use_gitignore and gitignore_parser and gitignore_parser.matches(f):
            excluded_by_gitignore += 1
            continue
            
        if _should_exclude_file(f, patterns["exclude"]):
            continue
            
        if _matches_include_pattern(f, patterns["include"]):
            filtered_files.append(f)
    
    _report_gitignore_exclusions(excluded_by_gitignore)
    return filtered_files


def _parse_filter_patterns(include: Optional[str], exclude: Optional[str]) -> dict:
    """Parse include and exclude patterns from strings."""
    default_include = "*.py,*.js,*.ts,*.java,*.go,*.rs,*.cpp,*.c,*.rb,*.php"
    include_patterns = [p.strip() for p in (include or default_include).split(",")]
    exclude_patterns = [p.strip() for p in (exclude or "").split(",")] if exclude else []
    
    return {"include": include_patterns, "exclude": exclude_patterns}


def _should_exclude_file(file_path: Path, exclude_patterns: list[str]) -> bool:
    """Check if file should be excluded based on exclude patterns."""
    import fnmatch
    str_path = str(file_path)
    return any(
        fnmatch.fnmatch(str_path, p) or fnmatch.fnmatch(file_path.name, p)
        for p in exclude_patterns
    )


def _matches_include_pattern(file_path: Path, include_patterns: list[str]) -> bool:
    """Check if file matches any include pattern."""
    import fnmatch
    return any(fnmatch.fnmatch(file_path.name, p) for p in include_patterns)


def _report_gitignore_exclusions(count: int):
    """Report number of files excluded by gitignore."""
    if count > 0:
        console.print(f"[dim]Excluded {count} files by .gitignore[/dim]")


def _handle_no_files_found(output_format: str):
    """Handle case when no files are found to validate."""
    if output_format in ("json", "yaml", "toon"):
        _output_batch_empty(output_format)
    else:
        console.print("[yellow]No files found to validate[/yellow]")
    raise typer.Exit(0)


def _show_validation_start(filtered_files: list[Path], output_format: str):
    """Show validation start message for non-structured output formats."""
    if output_format not in ("json", "yaml", "toon"):
        console.print(f"[bold]Validating {len(filtered_files)} files...[/bold]\n")


def _process_files(filtered_files: list[Path], settings, output_format: str,
                   fail_fast: bool, verbose: bool, show_issues: bool):
    """Process all files and collect validation results."""
    from vallm.core.languages import detect_language
    from vallm.core.proposal import Proposal
    from vallm.scoring import validate as run_validate, Verdict
    
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
            
            _handle_validation_result(
                file_path, result, lang_name, output_format, verbose, show_issues
            )
            
            if result.verdict == Verdict.PASS:
                passed_count += 1
            elif result.verdict == Verdict.FAIL:
                failed_files.append((file_path, result))
                
            if fail_fast and result.verdict == Verdict.FAIL:
                break
                
        except Exception as e:
            failed_files.append((file_path, None))
            if output_format == "rich":
                console.print(f"[red]✗[/red] {file_path} - error: {e}")
            if fail_fast:
                break
    
    return results_by_language, failed_files, passed_count


def _handle_validation_result(file_path: Path, result, lang_name: str, 
                              output_format: str, verbose: bool, show_issues: bool):
    """Handle and display individual validation results."""
    from vallm.scoring import Verdict
    
    if output_format != "rich":
        return
        
    if result.verdict == Verdict.PASS:
        console.print(f"[green]✓[/green] {file_path} ({lang_name})")
        if verbose:
            _show_file_details(result, show_issues)
    elif result.verdict == Verdict.REVIEW:
        console.print(f"[yellow]⚠[/yellow] {file_path} ({lang_name}) - needs review")
        if verbose:
            _show_file_details(result, show_issues)
    else:  # FAIL
        console.print(f"[red]✗[/red] {file_path} ({lang_name}) - failed")
        if verbose or show_issues:
            _show_file_details(result, show_issues)


def _output_batch_results(results_by_language, filtered_files, passed_count, 
                         failed_files, output_format: str):
    """Output batch validation results in the specified format."""
    if output_format == "json":
        _output_batch_json(results_by_language, filtered_files, passed_count, failed_files)
    elif output_format == "yaml":
        _output_batch_yaml(results_by_language, filtered_files, passed_count, failed_files)
    elif output_format == "toon":
        _output_batch_toon(results_by_language, filtered_files, passed_count, failed_files)
    elif output_format == "text":
        _output_batch_text(results_by_language, filtered_files, passed_count, failed_files)
    else:
        # Rich format (default)
        _output_batch_rich(results_by_language, filtered_files, passed_count, failed_files)


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


def _show_file_details(result, show_issues: bool):
    """Show detailed results for a single file."""
    for r in result.results:
        _print_validator_summary(r)
        _print_validator_issues(r)
        _print_validator_details(r, show_issues)


def _print_validator_summary(r):
    """Print summary line for a validator result."""
    status_icon = "✓" if r.score >= 0.8 else "⚠" if r.score >= 0.5 else "✗"
    color = "green" if r.score >= 0.8 else "yellow" if r.score >= 0.5 else "red"
    console.print(
        f"  [{color}]{status_icon} {r.validator}: {r.score:.2f} "
        f"(weight={r.weight:.1f}, confidence={r.confidence:.1f})[/{color}]"
    )


def _print_validator_issues(r):
    """Print issues for a validator result."""
    if not r.issues:
        return
        
    for issue in r.issues:
        icon = "🔴" if issue.severity.value == "error" else "🟡" if issue.severity.value == "warning" else "🔵"
        location = f"L{issue.line}" if issue.line else ""
        console.print(f"      {icon} [{location}] {issue.message}")


def _print_validator_details(r, show_issues: bool):
    """Print additional details for a validator result."""
    if not (r.details and show_issues):
        return
        
    for key, value in r.details.items():
        if key not in ("model", "raw_response"):
            console.print(f"      ℹ️  {key}: {value}")


def _output_batch_rich(results_by_language, filtered_files, passed_count, failed_files):
    """Output rich formatted batch summary."""
    _print_summary_header()
    table = _build_results_table(results_by_language)
    console.print(table)
    console.print(f"\nTotal: {len(filtered_files)} files, {passed_count} passed, {len(failed_files)} failed")
    _show_failed_files_details(failed_files)


def _print_summary_header():
    """Print the batch validation summary header."""
    console.print("\n" + "="*60)
    console.print("[bold]BATCH VALIDATION SUMMARY[/bold]")
    console.print("="*60)


def _build_results_table(results_by_language):
    """Build the Rich table with validation results by language."""
    table = Table()
    table.add_column("Language", style="cyan")
    table.add_column("Files", justify="right")
    table.add_column("Passed", justify="right")
    table.add_column("Failed", justify="right")
    table.add_column("Review", justify="right")
    
    for lang, results in sorted(results_by_language.items()):
        passed = sum(1 for _, r in results if r.verdict == Verdict.PASS)
        failed = sum(1 for _, r in results if r.verdict == Verdict.FAIL)
        review = len(results) - passed - failed
        
        passed_str = f"[green]{passed}[/green]" if passed > 0 else str(passed)
        failed_str = f"[red]{failed}[/red]" if failed > 0 else str(failed)
        review_str = f"[yellow]{review}[/yellow]" if review > 0 else str(review)
        
        table.add_row(lang, str(len(results)), passed_str, failed_str, review_str)
    
    return table


def _show_failed_files_details(failed_files):
    """Show detailed information about failed files."""
    if not failed_files:
        return
        
    console.print("\n[bold red]Failed Files:[/bold red]")
    for file_path, result in failed_files:
        if not result:
            continue
        _print_failed_file_details(file_path, result)


def _print_failed_file_details(file_path, result):
    """Print details for a single failed file."""
    console.print(f"\n[red]✗ {file_path}[/red]")
    console.print(f"  Score: {result.weighted_score:.2f} (threshold: 0.5)")
    
    for r in result.results:
        if r.score < 0.8:
            console.print(f"  [yellow]  {r.validator}: {r.score:.2f}[/yellow]")
            _print_validator_issues(r)


def _print_validator_issues(validator_result):
    """Print issues for a specific validator result."""
    if validator_result.issues:
        for issue in validator_result.issues[:3]:
            console.print(f"    - {issue.message}")
    
    if validator_result.details and "summary" in validator_result.details:
        summary = validator_result.details["summary"][:100]
        console.print(f"    [dim]Summary: {summary}...[/dim]")


def _output_batch_text(results_by_language, filtered_files, passed_count, failed_files):
    """Output plain text batch summary."""
    print("\n" + "="*60)
    print("BATCH VALIDATION SUMMARY")
    print("="*60)
    
    for lang, results in sorted(results_by_language.items()):
        passed = sum(1 for _, r in results if r.verdict == Verdict.PASS)
        failed = sum(1 for _, r in results if r.verdict == Verdict.FAIL)
        review = len(results) - passed - failed
        print(f"{lang}: {len(results)} files, {passed} passed, {failed} failed, {review} review")
    
    print(f"\nTotal: {len(filtered_files)} files, {passed_count} passed, {len(failed_files)} failed")
    
    # Show individual results
    print("\nIndividual Results:")
    for lang, results in sorted(results_by_language.items()):
        for file_path, result in results:
            status = result.verdict.value.upper()
            print(f"{file_path}: {status} (score: {result.weighted_score:.2f})")
            if result.verdict != Verdict.PASS:
                for r in result.results:
                    if r.score < 0.8:
                        print(f"  - {r.validator}: {r.score:.2f}")
                        for issue in r.issues[:2]:
                            print(f"    - {issue.message}")


def _output_batch_json(results_by_language, filtered_files, passed_count, failed_files):
    """Output JSON batch summary."""
    import json
    
    data = {
        "summary": {
            "total_files": len(filtered_files),
            "passed": passed_count,
            "failed": len(failed_files),
            "failed_files_count": len([f for f in failed_files if f[1] is not None]),
            "error_files_count": len([f for f in failed_files if f[1] is None]),
        },
        "by_language": {},
        "files": [],
    }
    
    for lang, results in sorted(results_by_language.items()):
        passed = sum(1 for _, r in results if r.verdict == Verdict.PASS)
        failed = sum(1 for _, r in results if r.verdict == Verdict.FAIL)
        review = len(results) - passed - failed
        data["by_language"][lang] = {
            "total": len(results),
            "passed": passed,
            "failed": failed,
            "review": review,
        }
    
    for lang, results in sorted(results_by_language.items()):
        for file_path, result in results:
            file_data = {
                "path": str(file_path),
                "language": lang,
                "verdict": result.verdict.value,
                "score": result.weighted_score,
                "validators": [
                    {
                        "name": r.validator,
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
                "errors": result.error_count,
                "warnings": result.warning_count,
            }
            data["files"].append(file_data)
    
    print(json.dumps(data, indent=2, default=str))


def _output_batch_yaml(results_by_language, filtered_files, passed_count, failed_files):
    """Output YAML batch summary."""
    print("# vallm batch validation results")
    print("---")
    print(f"summary:")
    print(f"  total_files: {len(filtered_files)}")
    print(f"  passed: {passed_count}")
    print(f"  failed: {len(failed_files)}")
    print(f"by_language:")
    
    for lang, results in sorted(results_by_language.items()):
        passed = sum(1 for _, r in results if r.verdict == Verdict.PASS)
        failed = sum(1 for _, r in results if r.verdict == Verdict.FAIL)
        review = len(results) - passed - failed
        print(f"  {lang}:")
        print(f"    total: {len(results)}")
        print(f"    passed: {passed}")
        print(f"    failed: {failed}")
        print(f"    review: {review}")
    
    print(f"files:")
    for lang, results in sorted(results_by_language.items()):
        for file_path, result in results:
            print(f"  - path: {file_path}")
            print(f"    language: {lang}")
            print(f"    verdict: {result.verdict.value}")
            print(f"    score: {result.weighted_score:.2f}")
            if result.verdict != Verdict.PASS:
                print(f"    validators:")
                for r in result.results:
                    if r.score < 0.8:
                        print(f"      - name: {r.validator}")
                        print(f"        score: {r.score:.2f}")
                        if r.issues:
                            print(f"        issues:")
                            for issue in r.issues[:3]:
                                print(f"          - {issue.message}")


def _output_batch_toon(results_by_language, filtered_files, passed_count, failed_files):
    """Output TOON format batch summary."""
    print(f"# vallm batch | {len(filtered_files)}f | {passed_count}✓ {len(failed_files)}✗")
    print()
    print("SUMMARY:")
    print(f"  total: {len(filtered_files)}")
    print(f"  passed: {passed_count}")
    print(f"  failed: {len(failed_files)}")
    print()
    print("BY_LANGUAGE:")
    for lang, results in sorted(results_by_language.items()):
        passed = sum(1 for _, r in results if r.verdict == Verdict.PASS)
        failed = sum(1 for _, r in results if r.verdict == Verdict.FAIL)
        print(f"  {lang}: {len(results)} (✓{passed} ✗{failed})")
    print()
    print("FILES:")
    for lang, results in sorted(results_by_language.items()):
        for file_path, result in results:
            icon = "✓" if result.verdict == Verdict.PASS else "⚠" if result.verdict == Verdict.REVIEW else "✗"
            print(f"  {icon} {file_path} ({lang}) score={result.weighted_score:.2f}")
            if result.verdict == Verdict.FAIL:
                for r in result.results:
                    if r.score < 0.8:
                        print(f"    ! {r.validator}: {r.score:.2f}")
                        for issue in r.issues[:2]:
                            print(f"      - {issue.message}")


def _output_batch_empty(output_format: str):
    """Output empty results."""
    if output_format == "json":
        import json
        print(json.dumps({"summary": {"total_files": 0}, "files": []}))
    elif output_format == "yaml":
        print("# vallm batch validation results")
        print("---")
        print("summary:")
        print("  total_files: 0")
        print("files: []")
    elif output_format == "toon":
        print("# vallm batch | 0f")
        print("SUMMARY:")
        print("  total: 0")
        print("FILES: []")


def _output_json(result):
    """Output single file validation result as JSON (used by validate command)."""
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
    """Output single file validation result as text (used by validate command)."""
    print(f"Verdict: {result.verdict.value}")
    print(f"Score: {result.weighted_score:.2f}")
    for r in result.results:
        print(f"  {r.validator}: {r.score:.2f} (weight={r.weight})")
        for issue in r.issues:
            print(f"    {issue}")


if __name__ == "__main__":
    app()
