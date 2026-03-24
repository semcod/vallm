#!/usr/bin/env python3
"""
MCP Vallm Integration Example

Demonstrates how to use vallm's MCP tools for code validation.
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
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


def example_syntax_validation():
    """Example: Syntax validation for multiple languages."""
    print("=== Syntax Validation Examples ===\n")
    
    # Python
    python_code = '''
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
'''
    result = validate_syntax(python_code, 'python')
    print(f"Python code verdict: {result['verdict']} (score: {result['score']})")
    
    # JavaScript
    js_code = '''
function fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n-1) + fibonacci(n-2);
}
'''
    result = validate_syntax(js_code, 'javascript')
    print(f"JavaScript code verdict: {result['verdict']} (score: {result['score']})")
    
    # Invalid code
    invalid_code = 'def broken(): print("hello"'  # Missing closing paren
    result = validate_syntax(invalid_code, 'python')
    print(f"Invalid code verdict: {result['verdict']}")
    print(f"Issues found: {len(result['issues'])}")
    for issue in result['issues']:
        print(f"  - {issue['message']} (line {issue['line']})")
    print()


def example_security_validation():
    """Example: Security vulnerability detection."""
    print("=== Security Validation Examples ===\n")
    
    # Secure code
    secure_code = '''
def safe_user_input(username):
    if not username or len(username) > 50:
        return None
    return username.strip()
'''
    result = validate_security(secure_code, 'python')
    print(f"Secure code verdict: {result['verdict']} (score: {result['score']})")
    
    # Insecure code
    insecure_code = '''
def dangerous_function(user_input):
    eval(user_input)  # Dangerous!
    exec(f"print({user_input})")  # Also dangerous!
    os.system(f"rm -rf {user_input}")  # Extremely dangerous!
'''
    result = validate_security(insecure_code, 'python')
    print(f"Insecure code verdict: {result['verdict']} (score: {result['score']})")
    print(f"Security issues found: {len(result['issues'])}")
    for issue in result['issues']:
        print(f"  - {issue['message']} (line {issue['line']}, severity: {issue['severity']})")
    print()


def example_full_pipeline():
    """Example: Full validation pipeline."""
    print("=== Full Pipeline Validation Example ===\n")
    
    # Code with multiple issues
    problematic_code = '''
import nonexistent_module
import another_fake

def bad_function():
    eval("1+1")
    exec("print('hello')")
    print("missing paren"  # Syntax error
    
    # High complexity
    def complex_function(a, b, c, d, e, f, g, h, i, j):
        if a:
            if b:
                if c:
                    if d:
                        if e:
                            return True
        return False
'''
    result = validate_code(
        problematic_code, 
        'python',
        enable_syntax=True,
        enable_imports=True,
        enable_security=True,
        enable_complexity=True
    )
    
    print(f"Overall verdict: {result['verdict']} (score: {result['score']})")
    print(f"Summary: {result['summary']['total_issues']} issues, {result['summary']['error_count']} errors")
    
    print("\nValidator results:")
    for validator_result in result['results']:
        print(f"  {validator_result['validator']}: score {validator_result['score']}, {len(validator_result['issues'])} issues")
    
    print("\nAll issues:")
    for issue in result['all_issues']:
        print(f"  - [{issue['validator']}] {issue['message']} (line {issue['line']}, severity: {issue['severity']})")
    print()


def example_selective_validation():
    """Example: Selective validator usage."""
    print("=== Selective Validation Example ===\n")
    
    code_with_eval = '''
def function_with_eval():
    eval("1+1")
    return "done"
'''
    
    # Only syntax and imports (skip security)
    result = validate_code(
        code_with_eval,
        'python',
        enable_syntax=True,
        enable_imports=True,
        enable_security=False,  # Skip security check
        enable_complexity=False
    )
    
    print("Validation with security disabled:")
    print(f"Verdict: {result['verdict']} (score: {result['score']})")
    validators_run = [r['validator'] for r in result['results']]
    print(f"Validators run: {validators_run}")
    
    # Only security check
    result = validate_code(
        code_with_eval,
        'python',
        enable_syntax=False,
        enable_imports=False,
        enable_security=True,  # Only security
        enable_complexity=False
    )
    
    print("\nValidation with security only:")
    print(f"Verdict: {result['verdict']} (score: {result['score']})")
    validators_run = [r['validator'] for r in result['results']]
    print(f"Validators run: {validators_run}")
    print()


def main():
    """Run all examples."""
    print("Vallm MCP Integration Examples")
    print("=" * 40)
    print()
    
    try:
        example_syntax_validation()
        example_security_validation()
        example_full_pipeline()
        example_selective_validation()
        
        print("🎉 All examples completed successfully!")
        print("\nTo use these tools with MCP:")
        print("1. Start the server: python3 mcp_server.py")
        print("2. Configure Claude Desktop with the MCP server")
        print("3. Use the validate_* tools in your conversations")
        
    except Exception as e:
        print(f"❌ Example failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
