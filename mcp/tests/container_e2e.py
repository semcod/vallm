#!/usr/bin/env python3
"""Container-side end-to-end tests for the vallm MCP server.

This script is intended to run *inside* the Docker image built for the MCP
integration. It starts the MCP server as a subprocess, exercises the JSON-RPC
request flow, and exits non-zero on failure.
"""

from __future__ import annotations

import json
import os
import select
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


class MCPServerSession:
    """Manage a running MCP server subprocess for JSON-RPC tests."""

    def __init__(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = os.pathsep.join([str(SRC_DIR), str(PROJECT_ROOT)])
        self._next_id = 1
        self.process = subprocess.Popen(
            [sys.executable, "-m", "mcp.server.self_server"],
            cwd=str(PROJECT_ROOT),
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

    def request(
        self, method: str, params: Optional[Dict[str, Any]] = None, timeout: float = 5.0
    ) -> Dict[str, Any]:
        """Send a JSON-RPC request and return the decoded response."""
        if self.process.stdin is None or self.process.stdout is None:
            raise RuntimeError("MCP server streams were not initialized")

        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id,
            "method": method,
            "params": params or {},
        }
        self._next_id += 1

        self.process.stdin.write(json.dumps(payload) + "\n")
        self.process.stdin.flush()

        ready, _, _ = select.select([self.process.stdout], [], [], timeout)
        if not ready:
            stderr = self._read_stderr()
            raise TimeoutError(f"Timed out waiting for response to {method}. Stderr: {stderr}")

        line = self.process.stdout.readline().strip()
        if not line:
            stderr = self._read_stderr()
            raise RuntimeError(f"Empty response for {method}. Stderr: {stderr}")

        return json.loads(line)

    def close(self) -> None:
        """Terminate the MCP server process."""
        if self.process.poll() is not None:
            return

        self.process.terminate()
        try:
            self.process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=3)

    def _read_stderr(self) -> str:
        if self.process.stderr is None:
            return ""
        try:
            return self.process.stderr.read() or ""
        except Exception:
            return ""


def unwrap_tool_result(response: Dict[str, Any]) -> Dict[str, Any]:
    """Decode the JSON string stored in MCP tool call content."""
    if "result" not in response:
        raise AssertionError(f"Expected result, got: {response}")

    content = response["result"].get("content", [])
    if not content:
        raise AssertionError(f"Missing content in response: {response}")

    text = content[0].get("text", "")
    if not text:
        raise AssertionError(f"Missing tool payload text: {response}")

    return json.loads(text)


def test_initialize(session: MCPServerSession) -> None:
    print("🔧 Testing MCP initialize...")
    response = session.request("initialize")
    result = response.get("result", {})
    server_info = result.get("serverInfo", {})

    assert result.get("protocolVersion") == "2024-11-05"
    assert server_info.get("name") == "vallm"
    print(f"✅ Initialized {server_info.get('name')} v{server_info.get('version')}")


def test_tools_list(session: MCPServerSession) -> None:
    print("📋 Testing tools/list...")
    response = session.request("tools/list")
    tools = response.get("result", {}).get("tools", [])
    tool_names = [tool.get("name") for tool in tools]

    expected = ["validate_syntax", "validate_imports", "validate_security", "validate_code"]
    missing = [tool for tool in expected if tool not in tool_names]

    assert not missing, f"Missing tools: {missing}"
    print(f"✅ Found tools: {tool_names}")


def test_validate_syntax(session: MCPServerSession) -> None:
    print("🔍 Testing validate_syntax...")
    response = session.request(
        "tools/call",
        {
            "name": "validate_syntax",
            "arguments": {"code": 'print("hello world")', "language": "python"},
        },
    )
    result = unwrap_tool_result(response)

    assert result.get("success") is True
    assert result.get("verdict") == "pass"
    print("✅ Syntax validation passed")


def test_validate_imports(session: MCPServerSession) -> None:
    print("📦 Testing validate_imports...")
    response = session.request(
        "tools/call",
        {
            "name": "validate_imports",
            "arguments": {
                "code": "import os\nfrom typing import List\n",
                "language": "python",
            },
        },
    )
    result = unwrap_tool_result(response)

    assert result.get("success") is True
    assert result.get("verdict") in {"pass", "review"}
    print("✅ Import validation executed")


def test_validate_security(session: MCPServerSession) -> None:
    print("🔒 Testing validate_security...")
    response = session.request(
        "tools/call",
        {
            "name": "validate_security",
            "arguments": {"code": 'eval("1+1")', "language": "python"},
        },
    )
    result = unwrap_tool_result(response)

    assert result.get("success") is True
    assert len(result.get("issues", [])) > 0
    print(f"✅ Security validation detected {len(result['issues'])} issue(s)")


def test_validate_code(session: MCPServerSession) -> None:
    print("🧪 Testing validate_code...")
    response = session.request(
        "tools/call",
        {
            "name": "validate_code",
            "arguments": {
                "code": """
def dangerous_function():
    eval("1+1")
    exec("print('hello')")
    return 42
""",
                "language": "python",
            },
        },
    )
    result = unwrap_tool_result(response)

    assert result.get("success") is True
    assert result.get("summary", {}).get("total_issues", 0) > 0
    print(f"✅ Full pipeline detected {result['summary']['total_issues']} issue(s)")


def test_invalid_tool(session: MCPServerSession) -> None:
    print("⚠️ Testing invalid tool handling...")
    response = session.request(
        "tools/call",
        {"name": "invalid_tool", "arguments": {}},
    )

    assert "error" in response, f"Expected JSON-RPC error, got: {response}"
    print("✅ Invalid tool rejected")


def main() -> int:
    print("🧪 Starting MCP Vallm Docker E2E tests\n")

    session = MCPServerSession()
    try:
        test_initialize(session)
        test_tools_list(session)
        test_validate_syntax(session)
        test_validate_imports(session)
        test_validate_security(session)
        test_validate_code(session)
        test_invalid_tool(session)

        print("\n🎉 ALL DOCKER E2E TESTS PASSED!")
        return 0
    except Exception as exc:
        print(f"\n💥 DOCKER E2E TEST FAILED: {exc}")
        return 1
    finally:
        session.close()


if __name__ == "__main__":
    sys.exit(main())
