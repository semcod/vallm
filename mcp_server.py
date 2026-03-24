#!/usr/bin/env python3
"""
MCP Server startup script for vallm integration.

This script starts the Model Context Protocol server for vallm validators,
exposing validation tools as MCP endpoints for LLM tool calling.

Usage:
    python mcp_server.py

Configuration for Claude Desktop (claude_desktop_config.json):
{
  "mcpServers": {
    "vallm": {
      "command": "python",
      "args": ["/path/to/vallm/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/path/to/vallm/src"
      }
    }
  }
}
"""

from mcp.server.self_server import main

if __name__ == "__main__":
    main()
