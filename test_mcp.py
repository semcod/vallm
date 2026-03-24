#!/usr/bin/env python3
"""
Test script for vallm MCP integration.

Tests all MCP tools to ensure they work correctly.
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"

# Add paths for imports
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(SRC_DIR))

from mcp.server._tools_vallm import (
    validate_syntax,
    validate_imports, 
    validate_security,
    validate_code
)


def test_validate_syntax():
    """Test syntax validation."""
    print("Testing validate_syntax...")
    
    # Test valid Python code
    result = validate_syntax('print("hello world")', 'python')
    assert result['success'] == True
    assert result['verdict'] == 'pass'
    print("✓ Valid Python code passed")
    
    # Test invalid Python code
    result = validate_syntax('print("hello world"', 'python')  # Missing closing paren
    assert result['success'] == True
    assert result['verdict'] == 'fail'
    assert len(result['issues']) > 0
    print("✓ Invalid Python code failed as expected")
    
    # Test multi-language support
    result = validate_syntax('console.log("hello");', 'javascript')
    assert result['success'] == True
    print("✓ JavaScript syntax validation works")


def test_validate_imports():
    """Test import validation."""
    print("\nTesting validate_imports...")
    
    # Test valid imports
    code = '''
import os
import sys
from typing import List
'''
    result = validate_imports(code, 'python')
    assert result['success'] == True
    print("✓ Valid imports passed")
    
    # Test invalid imports
    code = '''
import nonexistent_module
from fake import something
'''
    result = validate_imports(code, 'python')
    assert result['success'] == True
    # Should have issues for missing modules
    print(f"✓ Invalid imports detected {len(result['issues'])} issues")


def test_validate_security():
    """Test security validation."""
    print("\nTesting validate_security...")
    
    # Test secure code
    code = '''
def safe_function(x):
    return x * 2
'''
    result = validate_security(code, 'python')
    assert result['success'] == True
    assert result['verdict'] == 'pass'
    print("✓ Secure code passed")
    
    # Test insecure code
    code = '''
def dangerous_function():
    eval("1+1")
    exec("print('hello')")
    os.system("rm -rf /")
'''
    result = validate_security(code, 'python')
    assert result['success'] == True
    assert result['verdict'] in ['review', 'fail']
    assert len(result['issues']) > 0
    print(f"✓ Insecure code detected {len(result['issues'])} security issues")


def test_validate_code():
    """Test full pipeline validation."""
    print("\nTesting validate_code...")
    
    # Test good code
    code = '''
def fibonacci(n: int) -> int:
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
'''
    result = validate_code(code, 'python')
    assert result['success'] == True
    assert result['verdict'] == 'pass'
    print("✓ Good code passed full pipeline")
    
    # Test code with issues
    code = '''
def bad_function():
    eval("1+1")
    import nonexistent_module
    print("hello"  # Missing closing paren
'''
    result = validate_code(code, 'python')
    assert result['success'] == True
    assert result['verdict'] in ['review', 'fail']
    assert result['summary']['total_issues'] > 0
    print(f"✓ Code with issues detected {result['summary']['total_issues']} total issues")
    
    # Test with selective validators
    result = validate_code(
        code, 
        'python', 
        enable_syntax=False, 
        enable_security=False
    )
    assert result['success'] == True
    assert 'syntax' not in [r['validator'] for r in result['results']]
    assert 'security' not in [r['validator'] for r in result['results']]
    print("✓ Selective validator disabling works")


def main():
    """Run all tests."""
    print("Running vallm MCP integration tests...\n")
    
    try:
        test_validate_syntax()
        test_validate_imports()
        test_validate_security()
        test_validate_code()
        
        print("\n🎉 All tests passed! MCP integration is working correctly.")
        return 0
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
