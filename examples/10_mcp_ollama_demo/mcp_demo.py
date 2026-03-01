#!/usr/bin/env python3
"""
MCP Demo: code2llm + vallm + Ollama integration

Shows the complete workflow:
1. code2llm analyzes existing code structure
2. Sends code to Ollama (Qwen 2.5 Coder 7B) for refactoring suggestions
3. vallm validates LLM response for correctness
4. If validation fails, sends feedback to LLM for corrections
5. Logs entire process
"""

import json
import logging
import sys
import time
from pathlib import Path
from typing import Optional

import requests

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('mcp_demo.log')
    ]
)
logger = logging.getLogger('mcp_demo')

# Colors for terminal output
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


def log_section(title: str):
    """Print a section header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE} {title}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")
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


def analyze_with_code2llm(code_path: Path) -> dict:
    """Analyze code structure using code2llm."""
    log_step(1, "Analyzing code structure with code2llm")
    
    try:
        from code2llm import analyze_file
        
        logger.info(f"Analyzing file: {code_path}")
        result = analyze_file(str(code_path))
        
        print(f"{Colors.GREEN}✓ Analysis complete{Colors.END}")
        print(f"  Functions found: {len(result.get('functions', []))}")
        print(f"  Classes found: {len(result.get('classes', []))}")
        print(f"  Complexity: {result.get('complexity', 'N/A')}")
        
        return result
    except ImportError:
        logger.warning("code2llm not available, using basic analysis")
        # Fallback analysis
        code = code_path.read_text()
        lines = code.split('\n')
        
        functions = [l for l in lines if l.strip().startswith('def ')]
        classes = [l for l in lines if l.strip().startswith('class ')]
        
        print(f"{Colors.YELLOW}⚠ code2llm not installed, using basic analysis{Colors.END}")
        print(f"  Functions found: {len(functions)}")
        print(f"  Classes found: {len(classes)}")
        print(f"  Total lines: {len(lines)}")
        
        return {
            'functions': functions,
            'classes': classes,
            'total_lines': len(lines),
            'source': code
        }


def validate_with_vallm(code: str, description: str = "Code") -> dict:
    """Validate code using vallm."""
    from vallm import Proposal, validate, VallmSettings
    
    logger.info(f"Validating code with vallm: {description}")
    
    settings = VallmSettings(
        enable_syntax=True,
        enable_imports=True,
        enable_complexity=True,
        enable_security=True,  # Enable security checks
        enable_semantic=False,
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


def call_ollama(prompt: str, model: str = "qwen2.5-coder:7b", temperature: float = 0.2) -> str:
    """Call Ollama API."""
    logger.info(f"Calling Ollama with model: {model}")
    
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "top_p": 0.9,
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()
        return result.get('response', '')
    except requests.exceptions.ConnectionError:
        logger.error("Cannot connect to Ollama. Is it running?")
        print(f"{Colors.RED}✗ Error: Cannot connect to Ollama at localhost:11434{Colors.END}")
        print(f"  Make sure Ollama is running: ollama serve")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Ollama API error: {e}")
        print(f"{Colors.RED}✗ Error calling Ollama: {e}{Colors.END}")
        sys.exit(1)


def generate_refactoring_prompt(code: str, analysis: dict) -> str:
    """Generate prompt for LLM to refactor code."""
    issues = analysis.get('issues', [])
    
    prompt = f"""You are an expert Python code reviewer. Analyze and refactor the following legacy code to fix all issues.

LEGACY CODE:
```python
{code}
```

ISSUES TO FIX:
{chr(10).join(f"- {i['message']}" for i in issues) if issues else "- Fix security vulnerabilities (eval, exec, pickle, SQL injection, command injection)"}
- Reduce cyclomatic complexity (avoid deep nesting)
- Remove duplicate code
- Remove dead code and unused imports
- Use constants instead of magic numbers
- Follow SOLID principles (single responsibility)
- Add proper error handling
- Remove hardcoded credentials

REQUIREMENTS:
1. Return ONLY valid Python code, no explanations
2. Include all necessary imports
3. Keep the same functionality
4. Make the code production-ready
5. Add type hints where appropriate
6. Include docstrings for public functions

REFACTORED CODE:
```python
"""
    
    return prompt


def extract_code_from_response(response: str) -> str:
    """Extract Python code from LLM response."""
    # Try to extract from markdown code blocks
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


def run_mcp_workflow(code_path: Path, max_iterations: int = 3):
    """Run the complete MCP workflow."""
    log_section("MCP Demo: code2llm + vallm + Ollama")
    
    # Load legacy code
    legacy_code = code_path.read_text()
    log_code("LEGACY CODE (with issues)", legacy_code)
    
    # Step 1: Analyze with code2llm
    analysis = analyze_with_code2llm(code_path)
    
    # Step 2: Initial validation with vallm
    log_step(2, "Validating legacy code with vallm")
    initial_validation = validate_with_vallm(legacy_code, "Legacy Code")
    
    # Step 3: Generate refactoring prompt and call Ollama
    log_step(3, "Sending to Ollama (Qwen 2.5 Coder 7B) for refactoring")
    
    prompt = generate_refactoring_prompt(legacy_code, initial_validation)
    logger.info("Generated refactoring prompt")
    
    print(f"\n{Colors.CYAN}Prompt sent to LLM (truncated):{Colors.END}")
    print(prompt[:500] + "...")
    
    ollama_response = call_ollama(prompt)
    
    log_step(4, "Received LLM response")
    log_code("LLM RESPONSE", ollama_response, max_lines=50)
    
    # Step 4: Extract and validate refactored code
    refactored_code = extract_code_from_response(ollama_response)
    
    iteration = 1
    current_code = refactored_code
    
    while iteration <= max_iterations:
        log_step(4 + iteration, f"Validating refactored code (iteration {iteration})")
        
        validation = validate_with_vallm(current_code, f"Refactored Code (v{iteration})")
        
        if validation['verdict'] == 'pass':
            log_section("✓ SUCCESS: Code passed all validations!")
            print(f"{Colors.GREEN}Refactoring successful after {iteration} iteration(s){Colors.END}")
            
            # Save final code
            output_path = Path("refactored_output.py")
            output_path.write_text(current_code)
            print(f"\n{Colors.GREEN}✓ Final code saved to: {output_path.absolute()}{Colors.END}")
            
            return {
                'success': True,
                'iterations': iteration,
                'final_code': current_code,
                'final_score': validation['score']
            }
        
        elif iteration < max_iterations:
            print(f"\n{Colors.YELLOW}⚠ Validation failed, requesting corrections from LLM...{Colors.END}")
            
            # Generate correction prompt with validation feedback
            correction_prompt = f"""The previous refactored code has issues. Fix them.

PREVIOUS CODE:
```python
{current_code}
```

VALIDATION ERRORS:
{chr(10).join(f"- [{i['severity']}] {i['validator']}: {i['message']}" for i in validation['issues'])}

Fix ALL these issues and return only the corrected Python code.

CORRECTED CODE:
```python
"""
            
            logger.info(f"Requesting corrections (iteration {iteration + 1})")
            response = call_ollama(correction_prompt, temperature=0.1)
            current_code = extract_code_from_response(response)
            
            log_code(f"LLM CORRECTION (iteration {iteration + 1})", current_code, max_lines=30)
        
        else:
            log_section("✗ FAILED: Maximum iterations reached")
            print(f"{Colors.RED}Could not produce valid code after {max_iterations} attempts{Colors.END}")
            
            # Save best attempt
            output_path = Path("refactored_output_best_attempt.py")
            output_path.write_text(current_code)
            print(f"\n{Colors.YELLOW}⚠ Best attempt saved to: {output_path.absolute()}{Colors.END}")
            
            return {
                'success': False,
                'iterations': iteration,
                'final_code': current_code,
                'final_score': validation['score'],
                'issues': validation['issues']
            }
        
        iteration += 1
    
    return {'success': False, 'error': 'Workflow incomplete'}


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='MCP Demo: code2llm + vallm + Ollama')
    parser.add_argument('--file', type=str, default='legacy_code/order_processor.py',
                        help='Path to legacy code file')
    parser.add_argument('--max-iterations', type=int, default=3,
                        help='Maximum correction iterations')
    
    args = parser.parse_args()
    
    code_path = Path(args.file)
    if not code_path.exists():
        print(f"{Colors.RED}Error: File not found: {code_path}{Colors.END}")
        sys.exit(1)
    
    print(f"{Colors.BOLD}MCP Demo: code2llm → Ollama → vallm → Iterate{Colors.END}")
    print(f"Processing: {code_path.absolute()}")
    
    result = run_mcp_workflow(code_path, max_iterations=args.max_iterations)
    
    # Summary
    log_section("FINAL SUMMARY")
    
    if result['success']:
        print(f"{Colors.GREEN}✓ SUCCESS{Colors.END}")
        print(f"  Iterations: {result['iterations']}")
        print(f"  Final Score: {result['final_score']:.2f}/1.0")
        print(f"  Log file: mcp_demo.log")
        sys.exit(0)
    else:
        print(f"{Colors.RED}✗ FAILED{Colors.END}")
        print(f"  Iterations: {result['iterations']}")
        print(f"  Final Score: {result.get('final_score', 0):.2f}/1.0")
        print(f"  Remaining issues: {len(result.get('issues', []))}")
        print(f"  Log file: mcp_demo.log")
        sys.exit(1)


if __name__ == "__main__":
    main()
