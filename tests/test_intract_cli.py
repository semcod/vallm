"""E2E tests for vallm intract CLI command."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

FULL_STACK = Path(__file__).resolve().parents[2] / "intract" / "examples" / "full-stack"


@pytest.mark.integration
def test_intract_cli_passes_on_full_stack_demo():
    pytest.importorskip("intract")
    if not FULL_STACK.exists():
        pytest.skip("full-stack demo not available")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "vallm",
            "intract",
            str(FULL_STACK),
            "--manifest",
            str(FULL_STACK / "intract.yaml"),
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert '"should_fail": false' in result.stdout or '"should_fail":false' in result.stdout


@pytest.mark.integration
def test_intract_cli_fails_on_violation(tmp_path: Path):
    pytest.importorskip("intract")

    source = (
        "# @intract.v1 scope:function intent:validate:user forbid:network\n"
        "import requests\n"
        "def validate_user():\n"
        "    return requests.get('https://example.com')\n"
    )
    target = tmp_path / "auth.py"
    target.write_text(source, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "-m", "vallm", "intract", str(tmp_path), "--format", "json"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "violation" in result.stdout.lower()
