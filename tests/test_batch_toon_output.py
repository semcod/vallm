import io
from datetime import date
from pathlib import Path

from rich.console import Console
from typer.testing import CliRunner

from vallm.cli import output_formatters
from vallm.cli import app
from vallm.cli.batch_processor import BatchProcessor
from vallm.scoring import Issue, PipelineResult, Severity, ValidationResult, Verdict


class FixedDate(date):
    @classmethod
    def today(cls):
        return cls(2026, 3, 26)


def make_result(filename: str, verdict: Verdict, score: float, issues: list[Issue] | None = None) -> PipelineResult:
    validation_result = ValidationResult(
        validator="test",
        score=score,
        issues=issues or [],
    )
    return PipelineResult(results=[validation_result], verdict=verdict, filename=filename)


def test_batch_processor_skips_toon_files():
    processor = BatchProcessor(Console(file=io.StringIO()))

    assert processor._should_exclude_file(Path("project/validation.toon.yaml"), []) is True
    assert processor._should_exclude_file(Path("project/validation.toon"), []) is True
    assert processor._should_exclude_file(Path("project/validation.yaml"), []) is False


def test_output_batch_toon_is_compact_and_groups_sections(capsys, monkeypatch):
    monkeypatch.setattr(output_formatters, "date", FixedDate)

    results_by_language = {
        "python": [
            make_result(
                "src/warn.py",
                Verdict.PASS,
                0.97,
                [
                    Issue(
                        message="validate_code CC=22 (max:15)",
                        severity=Severity.WARNING,
                        line=185,
                        rule="complexity.cyclomatic",
                    ),
                ],
            ),
            make_result("src/pass.py", Verdict.PASS, 1.0),
            make_result(
                "src/fail.py",
                Verdict.FAIL,
                0.91,
                [
                    Issue(
                        message="Module 'missing.module' not found",
                        severity=Severity.ERROR,
                        line=12,
                        rule="python.import.resolvable",
                    ),
                ],
            ),
        ]
    }

    filtered_files = [
        Path("src/warn.py"),
        Path("src/pass.py"),
        Path("src/fail.py"),
        Path("README.md"),
        Path("Dockerfile.test"),
        Path("notes.txt"),
        Path("config.example"),
        Path("misc"),
    ]
    failed_files = [
        (Path("README.md"), "Unsupported file type"),
        (Path("Dockerfile.test"), "Unsupported file type"),
        (Path("notes.txt"), "Unsupported file type"),
        (Path("config.example"), "Unsupported file type"),
        (Path("misc"), "Unsupported file type"),
    ]

    output_formatters.output_batch_toon(
        results_by_language,
        filtered_files,
        passed_count=2,
        failed_files=failed_files,
    )

    output = capsys.readouterr().out

    assert "# vallm batch | 8f | 2✓ 1⚠ 1✗ | 2026-03-26" in output
    assert "SUMMARY:" in output
    assert "scanned: 8  passed: 2 (25.0%)  warnings: 1  errors: 1  unsupported: 5" in output
    assert "WARNINGS[1]{path,score}:" in output
    assert "src/warn.py,0.97" in output
    assert "src/pass.py" not in output
    assert "issues[1]{rule,severity,message,line}:" in output
    assert "complexity.cyclomatic,warning,validate_code CC=22 (max:15),185" in output
    assert "ERRORS[1]{path,score}:" in output
    assert "src/fail.py,0.91" in output
    assert "python.import.resolvable,error,Module 'missing.module' not found,12" in output
    assert "UNSUPPORTED[5]{bucket,count}:" in output
    assert "*.md,1" in output
    assert "Dockerfile*,1" in output
    assert "*.txt,1" in output
    assert "*.example,1" in output
    assert "other,1" in output
    assert "FILES:" not in output
    assert "FAILED:" not in output


def test_batch_exits_zero_with_only_unsupported_files(tmp_path):
    """Regression: unsupported files must not cause Exit(2); only real validation failures should."""
    runner = CliRunner()
    unsupported = tmp_path / "data.md"
    unsupported.write_text("# Just a readme", encoding="utf-8")

    result = runner.invoke(app, ["batch", str(tmp_path), "--recursive", "--no-gitignore"])
    assert result.exit_code == 0, f"Expected 0, got {result.exit_code}:\n{result.output}"


def test_batch_exits_two_with_real_validation_failure(tmp_path, monkeypatch):
    """Regression: actual validation failure (syntax error) must produce Exit(2)."""
    monkeypatch.setattr(
        BatchProcessor,
        "_parse_filter_patterns",
        lambda self, include, exclude: {"include": [], "exclude": []},
    )
    runner = CliRunner()
    bad_py = tmp_path / "bad.py"
    bad_py.write_text("def foo(\n", encoding="utf-8")

    result = runner.invoke(app, ["batch", str(bad_py)])
    assert result.exit_code == 2, f"Expected 2, got {result.exit_code}:\n{result.output}"
