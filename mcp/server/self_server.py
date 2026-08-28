#!/usr/bin/env python3
"""
MCP Server for vallm integration

Provides Model Context Protocol server for vallm validators.
Exposes vallm validation tools as MCP endpoints for LLM tool calling.

Usage:
    python self_server.py

Configuration for Claude Desktop (claude_desktop_config.json):
{
  "mcpServers": {
    "vallm": {
      "command": "python",
      "args": ["/path/to/vallm/self_server.py"]
    }
  }
}
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Import vallm MCP tools
try:
    from mcp.server._tools_vallm import TOOL_SCHEMA_VALLM, MCP_HANDLERS
except ImportError as exc:
    print(f"Error: Could not import vallm MCP tools: {exc}", file=sys.stderr)
    sys.exit(1)

_PROTOCOL_VERSION = "2024-11-05"
_NOTIFICATIONS = frozenset({"notifications/initialized", "notifications/cancelled"})
_TRUE_VALUES = frozenset({"1", "true", "yes", "on"})
_DEFAULT_MAX_CODE_BYTES = 1_000_000


def _enabled(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in _TRUE_VALUES


def _max_code_bytes() -> int:
    try:
        return max(1, int(os.getenv("VALLM_MCP_MAX_CODE_BYTES", _DEFAULT_MAX_CODE_BYTES)))
    except ValueError:
        return _DEFAULT_MAX_CODE_BYTES


def _project_root() -> Path:
    return Path(os.getenv("VALLM_MCP_PROJECT_ROOT", ".")).expanduser().resolve()


def _require_project_path(raw_path: object) -> str:
    if not isinstance(raw_path, str) or not raw_path.strip():
        raise ValueError("project path must be a non-empty string")
    candidate = Path(raw_path).expanduser().resolve(strict=False)
    try:
        candidate.relative_to(_project_root())
    except ValueError as exc:
        raise PermissionError(
            "vallm MCP path is outside VALLM_MCP_PROJECT_ROOT"
        ) from exc
    return str(candidate)


def _guard_tool_call(tool_name: str, arguments: Dict[str, Any]) -> None:
    for field in ("code", "reference_code"):
        value = arguments.get(field)
        if isinstance(value, str) and len(value.encode("utf-8")) > _max_code_bytes():
            raise ValueError(f"{field} exceeds VALLM_MCP_MAX_CODE_BYTES")

    if tool_name == "validate_code" and bool(arguments.get("enable_regression", False)):
        if not _enabled("VALLM_MCP_ALLOW_EXECUTE"):
            raise PermissionError(
                "regression execution through MCP is disabled; set VALLM_MCP_ALLOW_EXECUTE=1"
            )

    if tool_name in {"validate_intract_project", "validate_intract_staged"}:
        arguments["path"] = _require_project_path(arguments.get("path", "."))
        if arguments.get("manifest"):
            arguments["manifest"] = _require_project_path(arguments["manifest"])


def handle_initialize(request_id: Any, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Handle MCP initialize request."""
    client_version = (params or {}).get("protocolVersion", _PROTOCOL_VERSION)
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "protocolVersion": client_version,
            "serverInfo": {"name": "vallm", "version": "1.0.0"},
            "capabilities": {"tools": {}},
        },
    }


def handle_tools_list(request_id: Any) -> Dict[str, Any]:
    """Handle tools/list request - return available vallm tools."""
    tools = []
    for tool_schema in TOOL_SCHEMA_VALLM.values():
        tools.append(
            {
                "name": tool_schema["name"],
                "description": tool_schema["description"],
                "inputSchema": tool_schema["parameters"],
            }
        )

    return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": tools}}


def handle_tools_call(request_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle tools/call request - execute vallm validation."""
    tool_name = params.get("name")
    arguments = params.get("arguments", {})

    if tool_name not in MCP_HANDLERS:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"},
        }

    try:
        _guard_tool_call(tool_name, arguments)
        # Call the appropriate handler
        result = MCP_HANDLERS[tool_name](arguments)

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]},
        }

    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32603, "message": f"Tool execution failed: {str(e)}"},
        }


def handle_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """Handle incoming MCP request."""
    method = request.get("method", "")
    params = request.get("params", {})
    request_id = request.get("id")

    if method in _NOTIFICATIONS:
        return {}
    if method == "initialize":
        return handle_initialize(request_id, params)
    elif method == "tools/list":
        return handle_tools_list(request_id)
    elif method == "tools/call":
        return handle_tools_call(request_id, params)
    else:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": f"Method '{method}' not found"},
        }


def main():
    """Main MCP server loop."""
    print("Vallm MCP Server starting...", file=sys.stderr)
    print(
        "Available tools: validate_syntax, validate_imports, validate_security, validate_code, validate_intent_contracts, validate_intract_project, validate_intract_staged",
        file=sys.stderr,
    )

    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                request = json.loads(line)
                response = handle_request(request)
                if response:
                    print(json.dumps(response), flush=True)
            except json.JSONDecodeError as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {"code": -32700, "message": f"Parse error: {str(e)}"},
                }
                print(json.dumps(error_response), flush=True)
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
                }
                print(json.dumps(error_response), flush=True)

    except KeyboardInterrupt:
        print("Vallm MCP Server shutting down...", file=sys.stderr)


if __name__ == "__main__":
    main()
