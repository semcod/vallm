#!/usr/bin/env python3
"""
Quick test script for MCP Vallm integration

Usage:
    python3 quick_test.py
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"

# Add src and project root to path
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(SRC_DIR))


def test_imports():
    """Test that all imports work correctly."""
    print("🔍 Testing imports...")

    try:
        from mcp.server._tools_vallm import (
            validate_syntax,
            validate_imports,
            validate_security,
            validate_code,
            TOOL_SCHEMA_VALLM,
            MCP_HANDLERS,
        )

        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_syntax_validation():
    """Test syntax validation."""
    print("🔍 Testing syntax validation...")

    try:
        from mcp.server._tools_vallm import validate_syntax

        # Test valid code
        result = validate_syntax('print("hello")', "python")

        if result.get("success") and result.get("verdict") == "pass":
            print("✅ Syntax validation working")
            return True
        else:
            print(f"❌ Syntax validation failed: {result}")
            return False

    except Exception as e:
        print(f"❌ Syntax validation error: {e}")
        return False


def test_security_validation():
    """Test security validation."""
    print("🔒 Testing security validation...")

    try:
        from mcp.server._tools_vallm import validate_security

        # Test code with security issues
        result = validate_security('eval("1+1")', "python")

        if result.get("success") and len(result.get("issues", [])) > 0:
            print(f"✅ Security validation working - {len(result['issues'])} issues found")
            return True
        else:
            print(f"❌ Security validation failed: {result}")
            return False

    except Exception as e:
        print(f"❌ Security validation error: {e}")
        return False


def test_tool_schema():
    """Test tool schema."""
    print("📋 Testing tool schema...")

    try:
        from mcp.server._tools_vallm import TOOL_SCHEMA_VALLM

        expected_tools = [
            "validate_syntax",
            "validate_imports",
            "validate_security",
            "validate_code",
        ]
        actual_tools = list(TOOL_SCHEMA_VALLM.keys())

        if all(tool in actual_tools for tool in expected_tools):
            print(f"✅ Tool schema correct: {actual_tools}")
            return True
        else:
            missing = [tool for tool in expected_tools if tool not in actual_tools]
            print(f"❌ Missing tools in schema: {missing}")
            return False

    except Exception as e:
        print(f"❌ Tool schema error: {e}")
        return False


def main():
    """Run quick tests."""
    print("🚀 MCP Vallm Quick Tests\n")

    tests = [
        test_imports,
        test_syntax_validation,
        test_security_validation,
        test_tool_schema,
    ]

    passed = 0
    total = len(tests)

    for test_func in tests:
        if test_func():
            passed += 1
        print()

    print(f"📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL QUICK TESTS PASSED!")
        return 0
    else:
        print("💥 SOME TESTS FAILED!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
