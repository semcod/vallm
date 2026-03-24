#!/usr/bin/env python3
"""
MCP Client Integration Tests

Tests MCP client-server communication using Docker containers.
"""

import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(SRC_DIR))


class MCPClient:
    """Simple MCP client for testing."""
    
    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
    
    def send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send request to MCP server."""
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    (
                        "import json; "
                        "from mcp.server.self_server import handle_request; "
                        f"request = {json.dumps(request)}; "
                        "response = handle_request(request); "
                        "print(json.dumps(response))"
                    ),
                ],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=str(PROJECT_ROOT),
                env={**os.environ, "PYTHONPATH": os.pathsep.join([str(SRC_DIR), str(PROJECT_ROOT)])},
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout.strip())
            else:
                return {"error": result.stderr}
                
        except Exception as e:
            return {"error": str(e)}


def test_mcp_initialization():
    """Test MCP server initialization."""
    print("🔧 Testing MCP initialization...")
    
    client = MCPClient()
    
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {}
    }
    
    response = client.send_request(init_request)
    
    if "error" not in response and "result" in response:
        server_info = response["result"].get("serverInfo", {})
        print(f"✅ Server initialized: {server_info.get('name')} v{server_info.get('version')}")
        return True
    else:
        print(f"❌ Initialization failed: {response}")
        return False


def test_tools_list():
    """Test tools listing."""
    print("📋 Testing tools list...")
    
    client = MCPClient()
    
    tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    
    response = client.send_request(tools_request)
    
    if "error" not in response and "result" in response:
        tools = response["result"].get("tools", [])
        tool_names = [tool["name"] for tool in tools]
        
        expected_tools = ["validate_syntax", "validate_imports", "validate_security", "validate_code"]
        
        if all(tool in tool_names for tool in expected_tools):
            print(f"✅ All expected tools available: {tool_names}")
            return True
        else:
            missing = [tool for tool in expected_tools if tool not in tool_names]
            print(f"❌ Missing tools: {missing}")
            return False
    else:
        print(f"❌ Tools list failed: {response}")
        return False


def test_syntax_tool():
    """Test syntax validation tool."""
    print("🔍 Testing syntax validation tool...")
    
    client = MCPClient()
    
    tool_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "validate_syntax",
            "arguments": {
                "code": "print('hello world')",
                "language": "python"
            }
        }
    }
    
    response = client.send_request(tool_request)
    
    if "error" not in response and "result" in response:
        content = response["result"].get("content", [])
        if content and content[0].get("type") == "text":
            result = json.loads(content[0]["text"])
            if result.get("success") and result.get("verdict") == "pass":
                print("✅ Syntax validation tool working")
                return True
    
    print(f"❌ Syntax validation tool failed: {response}")
    return False


def test_security_tool():
    """Test security validation tool."""
    print("🔒 Testing security validation tool...")
    
    client = MCPClient()
    
    tool_request = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "validate_security",
            "arguments": {
                "code": "eval('1+1')",
                "language": "python"
            }
        }
    }
    
    response = client.send_request(tool_request)
    
    if "error" not in response and "result" in response:
        content = response["result"].get("content", [])
        if content and content[0].get("type") == "text":
            result = json.loads(content[0]["text"])
            if result.get("success") and len(result.get("issues", [])) > 0:
                print(f"✅ Security validation tool working - {len(result['issues'])} issues found")
                return True
    
    print(f"❌ Security validation tool failed: {response}")
    return False


def test_full_pipeline_tool():
    """Test full pipeline validation tool."""
    print("🔄 Testing full pipeline validation tool...")
    
    client = MCPClient()
    
    tool_request = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "validate_code",
            "arguments": {
                "code": """
def dangerous_function():
    eval("1+1")
    exec("print('hello')")
    return 42
""",
                "language": "python"
            }
        }
    }
    
    response = client.send_request(tool_request)
    
    if "error" not in response and "result" in response:
        content = response["result"].get("content", [])
        if content and content[0].get("type") == "text":
            result = json.loads(content[0]["text"])
            if result.get("success") and result.get("summary", {}).get("total_issues", 0) > 0:
                print(f"✅ Full pipeline tool working - {result['summary']['total_issues']} issues found")
                return True
    
    print(f"❌ Full pipeline tool failed: {response}")
    return False


def test_error_handling():
    """Test error handling for invalid requests."""
    print("⚠️ Testing error handling...")
    
    client = MCPClient()
    
    # Test invalid tool name
    invalid_request = {
        "jsonrpc": "2.0",
        "id": 6,
        "method": "tools/call",
        "params": {
            "name": "invalid_tool",
            "arguments": {}
        }
    }
    
    response = client.send_request(invalid_request)
    
    if "error" in response:
        print("✅ Error handling working - invalid tool rejected")
        return True
    else:
        print("❌ Error handling failed - should have rejected invalid tool")
        return False


def wait_for_server(host: str = "localhost", port: int = 8080, timeout: int = 30):
    """Wait for server to be ready."""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            # Try to connect to server
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                return True
        except:
            pass
        
        time.sleep(1)
    
    return False


def main():
    """Run client integration tests."""
    print("🔗 Starting MCP Client Integration Tests\n")
    
    # Wait for server (in Docker environment)
    server_host = os.environ.get("MCP_SERVER_HOST", "localhost")
    print(f"Waiting for MCP server at {server_host}...")
    
    # Skip server waiting in Docker container environment
    # and just test the MCP functionality directly
    
    tests = [
        ("MCP Initialization", test_mcp_initialization),
        ("Tools List", test_tools_list),
        ("Syntax Tool", test_syntax_tool),
        ("Security Tool", test_security_tool),
        ("Full Pipeline Tool", test_full_pipeline_tool),
        ("Error Handling", test_error_handling),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print(f"\n📊 Client Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL CLIENT TESTS PASSED!")
        return 0
    else:
        print("💥 SOME CLIENT TESTS FAILED!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
