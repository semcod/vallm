#!/usr/bin/env python3
"""
Claude Code Autonomous Demo: code2llm → Claude Code → vallm → Runtime Test → code2llm

Shows complete autonomous refactoring workflow:
1. code2llm analyzes existing code structure and smells
2. Claude Code generates refactored solution
3. vallm validates LLM response for correctness and security
4. Runtime tests validate functionality
5. code2llm re-analyzes to verify improvements
6. Loop until all criteria met
"""

import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('claude_autonomous.log')
    ]
)
logger = logging.getLogger('claude_autonomous')

# Colors for terminal output
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    END = '\033[0m'


def log_section(title: str):
    """Print a section header."""
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.MAGENTA} {title}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.MAGENTA}{'='*80}{Colors.END}\n")
    logger.info(f"SECTION: {title}")


def log_step(step: int, description: str):
    """Print a step."""
    print(f"\n{Colors.CYAN}Step {step}: {description}{Colors.END}")
    logger.info(f"STEP {step}: {description}")


def log_code(label: str, code: str, max_lines: int = 30):
    """Log code with label."""
    lines = code.split('\n')
    if len(lines) > max_lines:
        show_lines = lines[:max_lines//2] + ['...'] + lines[-max_lines//2:]
    else:
        show_lines = lines
    
    print(f"\n{Colors.BOLD}{label}:{Colors.END}")
    print("```python")
    print('\n'.join(show_lines))
    print("```")


def analyze_with_code2llm(code_path: Path) -> Dict:
    """Analyze code structure and smells using code2llm."""
    log_step(1, "Analyzing code structure with code2llm")
    
    try:
        from code2llm import ProjectAnalyzer
        
        logger.info(f"Analyzing file: {code_path}")
        analyzer = ProjectAnalyzer()
        
        # Analyze the directory containing the file
        project_result = analyzer.analyze_project(str(code_path.parent))
        
        print(f"{Colors.GREEN}✓ Analysis complete{Colors.END}")
        print(f"  Functions found: {project_result.get_function_count()}")
        print(f"  Classes found: {project_result.get_class_count()}")
        print(f"  Modules: {len(project_result.modules)}")
        print(f"  Code smells detected: {len(project_result.smells)}")
        print(f"  Entry points: {len(project_result.entry_points)}")
        print(f"  Coupling issues: {len(project_result.coupling)}")
        
        # Extract detailed information
        functions_info = [{'name': f.name, 'line': f.line_start, 'complexity': getattr(f, 'complexity', 'N/A')} for f in project_result.functions]
        classes_info = [{'name': c.name, 'line': c.line_start, 'methods': len(getattr(c, 'methods', []))} for c in project_result.classes]
        smells_info = [{'type': s.type, 'message': s.message, 'line': s.line, 'severity': getattr(s, 'severity', 'medium')} for s in project_result.smells]
        coupling_info = [{'from_module': c.from_module, 'to_module': c.to_module, 'strength': c.strength} for c in project_result.coupling]
        
        return {
            'functions': functions_info,
            'classes': classes_info,
            'modules': list(project_result.modules),
            'total_lines': len(code_path.read_text().split('\n')),
            'source': code_path.read_text(),
            'smells': smells_info,
            'coupling': coupling_info,
            'entry_points': list(project_result.entry_points),
            'metrics': project_result.metrics,
            'issues': []  # Will be filled by vallm validation
        }
    except Exception as e:
        logger.warning(f"code2llm analysis failed: {e}, using basic analysis")
        # Fallback analysis
        code = code_path.read_text()
        lines = code.split('\n')
        
        functions = [l for l in lines if l.strip().startswith('def ')]
        classes = [l for l in lines if l.strip().startswith('class ')]
        
        print(f"{Colors.YELLOW}⚠ code2llm analysis failed, using basic analysis{Colors.END}")
        print(f"  Functions found: {len(functions)}")
        print(f"  Classes found: {len(classes)}")
        print(f"  Total lines: {len(lines)}")
        
        return {
            'functions': functions,
            'classes': classes,
            'total_lines': len(lines),
            'source': code,
            'smells': [],
            'coupling': [],
            'issues': []
        }


def call_claude_code(prompt: str, model: str = "claude-3-5-sonnet-20241022", temperature: float = 0.1) -> str:
    """Call Claude Code API."""
    logger.info(f"Calling Claude Code with model: {model}")
    
    # Check for Claude Code CLI or API
    claude_api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not claude_api_key:
        logger.error("ANTHROPIC_API_KEY not found")
        print(f"{Colors.RED}✗ Error: ANTHROPIC_API_KEY environment variable not set{Colors.END}")
        print(f"  Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)
    
    url = "https://api.anthropic.com/v1/messages"
    
    headers = {
        "x-api-key": claude_api_key,
        "content-type": "application/json",
        "anthropic-version": "2023-06-01"
    }
    
    payload = {
        "model": model,
        "max_tokens": 4000,
        "temperature": temperature,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=120)
        response.raise_for_status()
        result = response.json()
        return result['content'][0]['text']
    except requests.exceptions.ConnectionError:
        logger.error("Cannot connect to Claude API")
        print(f"{Colors.RED}✗ Error: Cannot connect to Claude API{Colors.END}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Claude API error: {e}")
        print(f"{Colors.RED}✗ Error calling Claude: {e}{Colors.END}")
        sys.exit(1)


def validate_with_vallm(code: str, description: str = "Code") -> Dict:
    """Validate code using vallm."""
    from vallm import Proposal, validate, VallmSettings
    
    logger.info(f"Validating code with vallm: {description}")
    
    settings = VallmSettings(
        enable_syntax=True,
        enable_imports=True,
        enable_complexity=True,
        enable_security=True,
        enable_semantic=True,  # Enable semantic analysis
        enable_performance=True,  # Enable performance checks
    )
    
    proposal = Proposal(
        code=code,
        language="python",
        filename="refactored_code.py"
    )
    
    result = validate(proposal, settings)
    
    # Log results
    verdict_color = Colors.GREEN if result.verdict.value == "pass" else Colors.YELLOW if result.verdict.value == "review" else Colors.RED
    
    print(f"\n{verdict_color}Validation Result: {result.verdict.value.upper()} (score: {result.weighted_score:.2f}){Colors.END}")
    
    for r in result.results:
        icon = "✓" if r.score >= 0.8 else "⚠" if r.score >= 0.5 else "✗"
        color = Colors.GREEN if r.score >= 0.8 else Colors.YELLOW if r.score >= 0.5 else Colors.RED
        print(f"  {color}{icon} {r.validator}: {r.score:.2f}{Colors.END}")
        
        for issue in r.issues:
            issue_color = Colors.RED if issue.severity.value == "error" else Colors.YELLOW
            print(f"      {issue_color}  - {issue.message}{Colors.END}")
    
    return {
        'verdict': result.verdict.value,
        'score': result.weighted_score,
        'errors': result.error_count,
        'warnings': result.warning_count,
        'issues': [
            {
                'validator': r.validator,
                'message': i.message,
                'severity': i.severity.value,
                'line': i.line
            }
            for r in result.results
            for i in r.issues
        ]
    }


def run_runtime_tests(code_path: Path, test_file: Optional[Path] = None) -> Dict:
    """Run runtime tests on the refactored code."""
    log_step(4, "Running runtime tests")
    
    try:
        # Create a test file if not provided
        if not test_file or not test_file.exists():
            test_file = code_path.parent / f"test_{code_path.stem}.py"
            create_basic_tests(code_path, test_file)
        
        print(f"{Colors.CYAN}Running tests: {test_file}{Colors.END}")
        
        # Run the tests
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(test_file), "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        success = result.returncode == 0
        
        print(f"{Colors.GREEN if success else Colors.RED}Tests {'PASSED' if success else 'FAILED'}{Colors.END}")
        
        if not success:
            print(f"{Colors.YELLOW}Test output:{Colors.END}")
            print(result.stdout)
            print(f"{Colors.RED}Test errors:{Colors.END}")
            print(result.stderr)
        
        return {
            'success': success,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode,
            'tests_run': result.stdout.count("passed") + result.stdout.count("failed")
        }
        
    except subprocess.TimeoutExpired:
        print(f"{Colors.RED}✗ Tests timed out{Colors.END}")
        return {
            'success': False,
            'stdout': '',
            'stderr': 'Tests timed out',
            'returncode': -1,
            'tests_run': 0
        }
    except Exception as e:
        print(f"{Colors.RED}✗ Error running tests: {e}{Colors.END}")
        return {
            'success': False,
            'stdout': '',
            'stderr': str(e),
            'returncode': -1,
            'tests_run': 0
        }


def create_basic_tests(code_path: Path, test_file: Path):
    """Create basic tests for the code."""
    code = code_path.read_text()
    
    # Extract functions and classes
    functions = [line.strip() for line in code.split('\n') if line.strip().startswith('def ')]
    classes = [line.strip() for line in code.split('\n') if line.strip().startswith('class ')]
    
    test_content = f'''"""
Auto-generated tests for {code_path.name}
"""

import pytest
import sys
from pathlib import Path

# Add the directory containing the module to Python path
sys.path.insert(0, str({code_path.parent!r}))

'''
    
    # Add basic test structure
    for func_line in functions:
        func_name = func_line.replace('def ', '').split('(')[0]
        test_content += f'''

def test_{func_name}_exists():
    """Test that {func_name} function exists."""
    from {code_path.stem} import {func_name}
    assert callable({func_name})
'''
    
    for class_line in classes:
        class_name = class_line.replace('class ', '').split('(')[0].split(':')[0]
        test_content += f'''

def test_{class_name.lower()}_exists():
    """Test that {class_name} class exists."""
    from {code_path.stem} import {class_name}
    assert {class_name}
'''
    
    test_content += '''

if __name__ == "__main__":
    pytest.main([__file__])
'''
    
    test_file.write_text(test_content)
    print(f"{Colors.GREEN}✓ Created test file: {test_file}{Colors.END}")


def generate_claude_prompt(code: str, analysis: Dict, iteration: int = 1) -> str:
    """Generate comprehensive prompt for Claude Code."""
    
    smells_text = ""
    if analysis.get('smells'):
        smells_text = "\n".join([f"- [{s['type'].upper()}] Line {s['line']}: {s['message']}" for s in analysis['smells']])
    else:
        smells_text = "No code smells detected by code2llm"
    
    coupling_text = ""
    if analysis.get('coupling'):
        coupling_text = "\n".join([f"- {c['from_module']} → {c['to_module']} (strength: {c['strength']})" for c in analysis['coupling']])
    else:
        coupling_text = "No coupling issues detected"
    
    prompt = f"""You are an expert software architect and Python developer. Analyze and refactor the following legacy code to fix all identified issues.

LEGACY CODE:
```python
{code}
```

CODE2LLM ANALYSIS (Iteration {iteration}):
- Functions: {len(analysis.get('functions', []))}
- Classes: {len(analysis.get('classes', []))}
- Total lines: {analysis.get('total_lines', 0)}
- Entry points: {len(analysis.get('entry_points', []))}

CODE SMELLS DETECTED:
{smells_text}

COUPLING ISSUES:
{coupling_text}

METRICS:
{json.dumps(analysis.get('metrics', {}), indent=2)}

REFACTORING REQUIREMENTS:
1. Fix ALL identified code smells and coupling issues
2. Improve code structure following SOLID principles
3. Enhance maintainability and readability
4. Optimize performance where possible
5. Add proper error handling and logging
6. Include type hints and docstrings
7. Follow Python best practices (PEP 8)
8. Ensure thread safety if applicable
9. Add input validation and sanitization
10. Remove any security vulnerabilities

ARCHITECTURAL IMPROVEMENTS:
- Apply design patterns where appropriate
- Separate concerns properly
- Reduce complexity and improve cohesion
- Add proper abstraction layers
- Implement dependency injection if needed

OUTPUT REQUIREMENTS:
1. Return ONLY valid Python code
2. Include all necessary imports
3. Maintain the same functionality
4. Make the code production-ready
5. Add comprehensive docstrings
6. Include type hints for all functions
7. Add proper error handling
8. Follow clean code principles

REFACTORED CODE:
```python
"""
Refactored version with improved architecture, security, and maintainability.
"""
"""
    
    return prompt


def generate_feedback_prompt(current_code: str, validation: Dict, test_results: Dict, analysis: Dict) -> str:
    """Generate feedback prompt for Claude based on validation and test results."""
    
    validation_issues = ""
    if validation.get('issues'):
        validation_issues = "\n".join([
            f"- [{i['severity'].upper()}] {i['validator']}: {i['message']} (line {i['line']})"
            for i in validation['issues']
        ])
    else:
        validation_issues = "No validation issues"
    
    test_failures = ""
    if not test_results.get('success', True):
        test_failures = f"Test Output:\n{test_results.get('stdout', '')}\nTest Errors:\n{test_results.get('stderr', '')}"
    else:
        test_failures = "All tests passed"
    
    prompt = f"""The previous refactored code has issues that need to be fixed. Please address ALL problems below.

PREVIOUS CODE:
```python
{current_code}
```

VALIDATION ISSUES:
{validation_issues}

RUNTIME TEST RESULTS:
{test_failures}

CURRENT CODE2LLM ANALYSIS:
- Functions: {len(analysis.get('functions', []))}
- Classes: {len(analysis.get('classes', []))}
- Code smells: {len(analysis.get('smells', []))}
- Coupling issues: {len(analysis.get('coupling', []))}

CRITICAL FIXES NEEDED:
1. Fix ALL validation errors and warnings
2. Ensure ALL runtime tests pass
3. Address any remaining code smells
4. Improve performance and security
5. Follow clean architecture principles

REQUIREMENTS:
- Fix every single issue mentioned above
- Maintain existing functionality
- Improve code quality significantly
- Add proper error handling
- Include comprehensive tests
- Follow Python best practices

CORRECTED CODE:
```python
"""
Fixed and improved version addressing all validation and test failures.
"""
"""
    
    return prompt


def run_autonomous_workflow(code_path: Path, max_iterations: int = 5):
    """Run the complete autonomous refactoring workflow."""
    log_section("Claude Code Autonomous Demo: code2llm → Claude Code → vallm → Runtime Tests → code2llm")
    
    # Load legacy code
    legacy_code = code_path.read_text()
    log_code("LEGACY CODE", legacy_code)
    
    iteration = 1
    current_code = legacy_code
    best_score = 0.0
    best_code = legacy_code
    
    while iteration <= max_iterations:
        log_section(f"Iteration {iteration}")
        
        # Step 1: Analyze with code2llm
        analysis = analyze_with_code2llm(code_path)
        
        # Step 2: Generate prompt and call Claude Code
        if iteration == 1:
            log_step(2, "Sending to Claude Code for initial refactoring")
            prompt = generate_claude_prompt(current_code, analysis, iteration)
        else:
            log_step(2, "Requesting corrections from Claude Code")
            prompt = generate_feedback_prompt(current_code, validation, test_results, analysis)
        
        logger.info("Generated Claude Code prompt")
        print(f"\n{Colors.CYAN}Prompt sent to Claude (truncated):{Colors.END}")
        print(prompt[:500] + "...")
        
        claude_response = call_claude_code(prompt)
        
        log_step(3, "Received Claude Code response")
        log_code("CLAUDE RESPONSE", claude_response, max_lines=50)
        
        # Step 4: Extract and validate refactored code
        current_code = extract_code_from_response(claude_response)
        
        # Save current iteration
        iteration_file = Path(f"refactored_v{iteration}.py")
        iteration_file.write_text(current_code)
        print(f"\n{Colors.GREEN}✓ Iteration {iteration} saved to: {iteration_file}{Colors.END}")
        
        # Step 5: Validate with vallm
        log_step(4, "Validating with vallm")
        validation = validate_with_vallm(current_code, f"Refactored Code (v{iteration})")
        
        # Step 6: Run runtime tests
        test_results = run_runtime_tests(iteration_file)
        
        # Step 7: Calculate overall score
        vallm_score = validation['score']
        test_score = 1.0 if test_results['success'] else 0.0
        overall_score = (vallm_score * 0.7) + (test_score * 0.3)  # Weight vallm higher
        
        print(f"\n{Colors.BOLD}Iteration {iteration} Summary:{Colors.END}")
        print(f"  Vallm Score: {vallm_score:.2f}")
        print(f"  Test Score: {test_score:.2f}")
        print(f"  Overall Score: {overall_score:.2f}")
        
        # Track best version
        if overall_score > best_score:
            best_score = overall_score
            best_code = current_code
            Path("best_refactored.py").write_text(best_code)
            print(f"{Colors.GREEN}✓ New best version saved{Colors.END}")
        
        # Check if we've achieved our goals
        if (validation['verdict'] == 'pass' and 
            test_results['success'] and 
            len(analysis.get('smells', [])) == 0 and
            len(analysis.get('coupling', [])) == 0):
            
            log_section("🎉 SUCCESS: Perfect refactoring achieved!")
            print(f"{Colors.GREEN}✓ All criteria met in {iteration} iterations{Colors.END}")
            print(f"  Final score: {overall_score:.2f}")
            print(f"  Best version: best_refactored.py")
            
            return {
                'success': True,
                'iterations': iteration,
                'final_score': overall_score,
                'best_score': best_score,
                'final_code': best_code
            }
        
        iteration += 1
    
    # If we reach max iterations
    log_section("⚠ MAXIMUM ITERATIONS REACHED")
    print(f"{Colors.YELLOW}Best attempt after {max_iterations} iterations{Colors.END}")
    print(f"  Best score: {best_score:.2f}")
    print(f"  Best version: best_refactored.py")
    
    return {
        'success': False,
        'iterations': max_iterations,
        'best_score': best_score,
        'final_code': best_code,
        'issues': validation.get('issues', [])
    }


def extract_code_from_response(response: str) -> str:
    """Extract Python code from Claude response."""
    import re
    
    # Look for python code blocks
    pattern = r'```python\s*(.*?)```'
    matches = re.findall(pattern, response, re.DOTALL)
    
    if matches:
        return matches[0].strip()
    
    # Try generic code blocks
    pattern = r'```\s*(.*?)```'
    matches = re.findall(pattern, response, re.DOTALL)
    
    if matches:
        return matches[0].strip()
    
    # Return whole response if no code blocks found
    return response.strip()


def main():
    """Main entry point."""
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description='Claude Code Autonomous Demo')
    parser.add_argument('--file', type=str, default='legacy_code/data_processor.py',
                        help='Path to legacy code file')
    parser.add_argument('--max-iterations', type=int, default=5,
                        help='Maximum refactoring iterations')
    
    args = parser.parse_args()
    
    code_path = Path(args.file)
    if not code_path.exists():
        print(f"{Colors.RED}Error: File not found: {code_path}{Colors.END}")
        sys.exit(1)
    
    print(f"{Colors.BOLD}Claude Code Autonomous: code2llm → Claude Code → vallm → Tests → code2llm{Colors.END}")
    print(f"Processing: {code_path.absolute()}")
    print(f"Max iterations: {args.max_iterations}")
    
    # Check for API key
    if not os.environ.get('ANTHROPIC_API_KEY'):
        print(f"{Colors.RED}Error: ANTHROPIC_API_KEY environment variable not set{Colors.END}")
        print(f"Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)
    
    result = run_autonomous_workflow(code_path, max_iterations=args.max_iterations)
    
    # Summary
    log_section("FINAL SUMMARY")
    
    if result['success']:
        print(f"{Colors.GREEN}🎉 SUCCESS{Colors.END}")
        print(f"  Iterations: {result['iterations']}")
        print(f"  Final Score: {result['final_score']:.2f}/1.0")
        print(f"  Best Score: {result['best_score']:.2f}/1.0")
        print(f"  Output: best_refactored.py")
        print(f"  Log: claude_autonomous.log")
        sys.exit(0)
    else:
        print(f"{Colors.YELLOW}⚠ COMPLETED WITH LIMITATIONS{Colors.END}")
        print(f"  Iterations: {result['iterations']}")
        print(f"  Best Score: {result['best_score']:.2f}/1.0")
        print(f"  Remaining issues: {len(result.get('issues', []))}")
        print(f"  Output: best_refactored.py")
        print(f"  Log: claude_autonomous.log")
        sys.exit(1)


if __name__ == "__main__":
    main()
