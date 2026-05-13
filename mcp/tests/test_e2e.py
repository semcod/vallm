#!/usr/bin/env python3
"""
Docker e2e tests for MCP Vallm integration

Tests the complete MCP workflow with Docker containers.
"""

import json
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(SRC_DIR))


def run_command(cmd, cwd=None, timeout=30):
    """Run command and return result."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, cwd=cwd, timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"


def test_mcp_server_startup():
    """Test MCP server startup and basic communication."""
    print("🚀 Testing MCP server startup...")

    process = subprocess.Popen(
        [sys.executable, "-m", "mcp.server.self_server"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=str(PROJECT_ROOT),
    )

    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {},
    }

    try:
        stdout, stderr = process.communicate(input=json.dumps(init_request) + "\n", timeout=5)
        if process.returncode != 0:
            print(f"❌ MCP server failed: {stderr}")
            return False

        response = json.loads(stdout.strip().splitlines()[-1])
        server_info = response.get("result", {}).get("serverInfo", {})
        if (
            response.get("result", {}).get("protocolVersion") == "0.1.0"
            and server_info.get("name") == "vallm"
        ):
            print(
                f"✅ MCP server startup successful: {server_info.get('name')} v{server_info.get('version')}"
            )
            return True

        print(f"❌ Unexpected initialize response: {response}")
        return False

    except Exception as e:
        print(f"❌ MCP server test failed: {e}")
        process.terminate()
        return False


def test_syntax_validation():
    """Test syntax validation via MCP."""
    print("🔍 Testing syntax validation...")

    try:
        # Import and test directly
        from mcp.server._tools_vallm import validate_syntax

        # Test valid Python code
        result = validate_syntax('print("hello world")', "python")

        if result.get("success") and result.get("verdict") == "pass":
            print("✅ Syntax validation test passed")
            return True
        else:
            print(f"❌ Syntax validation failed: {result}")
            return False

    except Exception as e:
        print(f"❌ Syntax validation test failed: {e}")
        return False


def test_security_validation():
    """Test security validation via MCP."""
    print("🔒 Testing security validation...")

    try:
        from mcp.server._tools_vallm import validate_security

        # Test code with security issues
        result = validate_security('eval("1+1")', "python")

        if result.get("success") and len(result.get("issues", [])) > 0:
            print("✅ Security validation test passed - issues detected")
            return True
        else:
            print(f"❌ Security validation failed: {result}")
            return False

    except Exception as e:
        print(f"❌ Security validation test failed: {e}")
        return False


def test_full_pipeline():
    """Test full validation pipeline."""
    print("🔄 Testing full validation pipeline...")

    try:
        from mcp.server._tools_vallm import validate_code

        # Test code with multiple issues
        code = """
def dangerous_function():
    eval("1+1")
    exec("print('hello')")
    import os
    os.system("ls")
    return 42
"""

        result = validate_code(code, "python")

        if result.get("success") and result.get("summary", {}).get("total_issues", 0) > 0:
            print(
                f"✅ Full pipeline test passed - {result['summary']['total_issues']} issues detected"
            )
            return True
        else:
            print(f"❌ Full pipeline test failed: {result}")
            return False

    except Exception as e:
        print(f"❌ Full pipeline test failed: {e}")
        return False


def test_docker_build():
    """Test Docker build process."""
    print("🐳 Testing Docker build...")

    success, stdout, stderr = run_command(
        "docker build -t vallm-mcp-test -f mcp/tests/Dockerfile.test .",
        cwd=str(PROJECT_ROOT),
        timeout=120,
    )

    if success:
        print("✅ Docker build successful")
        return True
    else:
        print(f"❌ Docker build failed: {stderr}")
        return False


def test_docker_run():
    """Test Docker container execution."""
    print("🏃 Testing Docker container execution...")

    success, stdout, stderr = run_command(
        "docker run --rm vallm-mcp-test", cwd=str(PROJECT_ROOT), timeout=30
    )

    if success and "ALL DOCKER E2E TESTS PASSED" in stdout:
        print("✅ Docker container test successful")
        return True
    else:
        print(f"❌ Docker container test failed: {stderr}")
        return False


def main():
    """Run all e2e tests."""
    print("🧪 Starting MCP Vallm E2E Tests\n")

    tests = [
        ("Docker Build", test_docker_build),
        ("Docker Run", test_docker_run),
        ("Syntax Validation", test_syntax_validation),
        ("Security Validation", test_security_validation),
        ("Full Pipeline", test_full_pipeline),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")

    print(f"\n📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("💥 SOME TESTS FAILED!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
