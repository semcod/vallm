def _assert_summary_section(output: str) -> None:
    assert "# vallm batch | 8f | 2✓ 1⚠ 1✗ | 2026-03-26" in output
    assert "SUMMARY:" in output
    assert "scanned: 8  passed: 2 (25.0%)  warnings: 1  errors: 1  unsupported: 5" in output


def _assert_warnings_section(output: str) -> None:
    assert "WARNINGS[1]{path,score}:" in output
    assert "src/warn.py,0.97" in output
    assert "src/pass.py" not in output
    assert "issues[1]{rule,severity,message,line}:" in output
    assert "complexity.cyclomatic,warning,validate_code CC=22 (max:15),185" in output


def _assert_unsupported_patterns(output: str) -> None:
    assert "*.md,1" in output
    assert "Dockerfile*,1" in output
    assert "*.txt,1" in output
    assert "*.example,1" in output
    assert "other,1" in output


def _assert_unsupported_section(output: str) -> None:
    assert "UNSUPPORTED[5]{bucket,count}:" in output
    _assert_unsupported_patterns(output)
    assert "FILES:" not in output
    assert "FAILED:" not in output
