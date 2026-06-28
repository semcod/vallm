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

from pathlib import Path
import json
import sys
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
