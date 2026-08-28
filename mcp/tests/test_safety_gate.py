from pathlib import Path

import pytest

from mcp.server.self_server import _guard_tool_call, _require_project_path


def test_regression_execution_requires_opt_in(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("VALLM_MCP_ALLOW_EXECUTE", raising=False)
    with pytest.raises(PermissionError, match="VALLM_MCP_ALLOW_EXECUTE"):
        _guard_tool_call("validate_code", {"code": "pass", "enable_regression": True})

    monkeypatch.setenv("VALLM_MCP_ALLOW_EXECUTE", "1")
    _guard_tool_call("validate_code", {"code": "pass", "enable_regression": True})


def test_project_paths_are_confined(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    monkeypatch.setenv("VALLM_MCP_PROJECT_ROOT", str(allowed))

    assert _require_project_path(str(allowed / "project")).startswith(str(allowed))
    with pytest.raises(PermissionError, match="VALLM_MCP_PROJECT_ROOT"):
        _require_project_path(str(tmp_path / "outside"))


def test_code_size_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VALLM_MCP_MAX_CODE_BYTES", "4")
    _guard_tool_call("validate_syntax", {"code": "pass"})
    with pytest.raises(ValueError, match="VALLM_MCP_MAX_CODE_BYTES"):
        _guard_tool_call("validate_syntax", {"code": "print(1)"})
