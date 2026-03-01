#!/usr/bin/env python3
"""
Simple Ollama Demo: code2llm → Ollama → vallm → Tests → code2llm

Shows basic autonomous refactoring workflow with Ollama
"""

import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

import requests

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('ollama_simple.log')
    ]
)
logger = logging.getLogger('ollama_simple')

# Colors
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def log_section(title: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE} {title}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")
    logger.info(f"SECTION: {title}")

def log_step(step: int, description: str):
    print(f"\n{Colors.CYAN}Step {step}: {description}{Colors.END}")
    logger.info(f"STEP {step}: {description}")

def analyze_with_code2llm(code_path: Path) -> Dict:
    """Simple code2llm analysis."""
    log_step(1, "Analyzing code with code2llm")
    
    try:
        from code2llm import ProjectAnalyzer
        
        analyzer = ProjectAnalyzer()
        result = analyzer.analyze_project(str(code_path.parent))
        
        print(f"{Colors.GREEN}✓ Analysis complete{Colors.END}")
        print(f"  Functions: {result.get_function_count()}")
        print(f"  Classes: {result.get_class_count()}")
        print(f"  Code smells: {len(result.smells)}")
        
        return {
            'functions': result.get_function_count(),
            'classes': result.get_class_count(),
            'smells': len(result.smells),
            'source': code_path.read_text()
        }
    except Exception as e:
        logger.warning(f"code2llm failed: {e}")
        # Fallback
        code = code_path.read_text()
        lines = code.split('\n')
        functions = [l for l in lines if l.strip().startswith('def ')]
        classes = [l for l in lines if l.strip().startswith('class ')]
        
        print(f"{Colors.YELLOW}⚠ Basic analysis{Colors.END}")
        print(f"  Functions: {len(functions)}")
        print(f"  Classes: {len(classes)}")
        
        return {
            'functions': len(functions),
            'classes': len(classes),
            'smells': 0,
            'source': code
        }

def call_ollama(prompt: str, model: str = "qwen2.5-coder:7b") -> str:
    """Call Ollama API."""
    logger.info(f"Calling Ollama with model: {model}")
    
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "top_p": 0.9,
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        return result.get('response', '')
    except Exception as e:
        logger.error(f"Ollama error: {e}")
        print(f"{Colors.RED}✗ Ollama error: {e}{Colors.END}")
        sys.exit(1)

def validate_with_vallm(code: str) -> Dict:
    """Simple vallm validation."""
    log_step(3, "Validating with vallm")
    
    try:
        from vallm import Proposal, validate, VallmSettings
        
        settings = VallmSettings(
            enable_syntax=True,
            enable_imports=True,
            enable_security=True,
            enable_semantic=False,
        )
        
        proposal = Proposal(
            code=code,
            language="python",
            filename="refactored.py"
        )
        
        result = validate(proposal, settings)
        
        verdict_color = Colors.GREEN if result.verdict.value == "pass" else Colors.YELLOW if result.verdict.value == "review" else Colors.RED
        
        print(f"\n{verdict_color}Validation: {result.verdict.value.upper()} (score: {result.weighted_score:.2f}){Colors.END}")
        
        return {
            'verdict': result.verdict.value,
            'score': result.weighted_score,
            'issues': len(result.error_count) + len(result.warning_count)
        }
    except Exception as e:
        logger.warning(f"vallm validation failed: {e}")
        print(f"{Colors.YELLOW}⚠ vallm validation failed{Colors.END}")
        return {'verdict': 'unknown', 'score': 0.5, 'issues': 0}

def run_simple_test(code: str) -> Dict:
    """Simple syntax test."""
    log_step(4, "Running syntax test")
    
    try:
        compile(code, '<string>', 'exec')
        print(f"{Colors.GREEN}✓ Syntax test passed{Colors.END}")
        return {'success': True, 'error': None}
    except SyntaxError as e:
        print(f"{Colors.RED}✗ Syntax error: {e}{Colors.END}")
        return {'success': False, 'error': str(e)}

def generate_ollama_prompt(code: str, analysis: Dict) -> str:
    """Generate simple prompt for Ollama."""
    return f"""Refactor this Python code to fix issues and improve quality:

ORIGINAL CODE:
```python
{code}
```

ISSUES TO FIX:
- Remove security vulnerabilities
- Improve code structure
- Add error handling
- Follow Python best practices

REQUIREMENTS:
1. Return ONLY valid Python code
2. Keep the same functionality
3. Make it production-ready

REFACTORED CODE:
```python
"""

def extract_code_from_response(response: str) -> str:
    """Extract Python code from response."""
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
    
    return response.strip()

def run_simple_workflow(code_path: Path, max_iterations: int = 3):
    """Run simple refactoring workflow."""
    log_section("Simple Ollama Demo: code2llm → Ollama → vallm → Test")
    
    # Load original code
    original_code = code_path.read_text()
    print(f"{Colors.BOLD}Original code:{Colors.END}")
    print("```python")
    print(original_code[:200] + "..." if len(original_code) > 200 else original_code)
    print("```")
    
    current_code = original_code
    best_score = 0.0
    best_code = original_code
    
    for iteration in range(1, max_iterations + 1):
        log_section(f"Iteration {iteration}")
        
        # Step 1: Analyze with code2llm
        analysis = analyze_with_code2llm(code_path)
        
        # Step 2: Generate prompt and call Ollama
        log_step(2, "Calling Ollama for refactoring")
        
        if iteration == 1:
            prompt = generate_ollama_prompt(current_code, analysis)
        else:
            prompt = f"""Fix the issues in this code:

CURRENT CODE:
```python
{current_code}
```

VALIDATION ISSUES:
- Score: {validation['score']:.2f}
- Verdict: {validation['verdict']}
- Issues: {validation['issues']}

FIXED CODE:
```python
"""
        
        print(f"{Colors.CYAN}Sending prompt to Ollama...{Colors.END}")
        ollama_response = call_ollama(prompt)
        
        # Step 3: Extract code
        current_code = extract_code_from_response(ollama_response)
        
        # Save iteration
        iteration_file = Path(f"iteration_{iteration}.py")
        iteration_file.write_text(current_code)
        print(f"{Colors.GREEN}✓ Saved to {iteration_file}{Colors.END}")
        
        # Step 4: Validate with vallm
        validation = validate_with_vallm(current_code)
        
        # Step 5: Run syntax test
        test_result = run_simple_test(current_code)
        
        # Calculate overall score
        overall_score = validation['score'] * 0.7 + (1.0 if test_result['success'] else 0.0) * 0.3
        
        print(f"\n{Colors.BOLD}Iteration {iteration} Results:{Colors.END}")
        print(f"  Vallm score: {validation['score']:.2f}")
        print(f"  Test passed: {test_result['success']}")
        print(f"  Overall score: {overall_score:.2f}")
        
        # Track best version
        if overall_score > best_score:
            best_score = overall_score
            best_code = current_code
            Path("best_version.py").write_text(best_code)
            print(f"{Colors.GREEN}✓ New best version!{Colors.END}")
        
        # Check if we're done
        if (validation['verdict'] == 'pass' and 
            test_result['success'] and 
            overall_score >= 0.9):
            
            log_section("🎉 SUCCESS!")
            print(f"{Colors.GREEN}Perfect refactoring achieved in {iteration} iterations!{Colors.END}")
            return {
                'success': True,
                'iterations': iteration,
                'final_score': overall_score,
                'best_code': best_code
            }
    
    # Max iterations reached
    log_section("⚠ Max iterations reached")
    print(f"{Colors.YELLOW}Best score: {best_score:.2f}{Colors.END}")
    
    return {
        'success': False,
        'iterations': max_iterations,
        'best_score': best_score,
        'best_code': best_code
    }

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Simple Ollama Demo')
    parser.add_argument('--file', type=str, default='legacy_code/simple_buggy.py',
                        help='Path to legacy code file')
    parser.add_argument('--max-iterations', type=int, default=3,
                        help='Maximum iterations')
    
    args = parser.parse_args()
    
    code_path = Path(args.file)
    if not code_path.exists():
        print(f"{Colors.RED}Error: File not found: {code_path}{Colors.END}")
        sys.exit(1)
    
    print(f"{Colors.BOLD}Simple Ollama Demo: code2llm → Ollama → vallm → Test{Colors.END}")
    print(f"File: {code_path.absolute()}")
    
    # Check Ollama
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        print(f"{Colors.GREEN}✓ Ollama is running{Colors.END}")
    except:
        print(f"{Colors.RED}✗ Ollama not running. Start with: ollama serve{Colors.END}")
        sys.exit(1)
    
    result = run_simple_workflow(code_path, max_iterations=args.max_iterations)
    
    # Summary
    log_section("SUMMARY")
    if result['success']:
        print(f"{Colors.GREEN}🎉 SUCCESS!{Colors.END}")
        print(f"  Iterations: {result['iterations']}")
        print(f"  Final score: {result['final_score']:.2f}")
        print(f"  Best version: best_version.py")
    else:
        print(f"{Colors.YELLOW}⚠ Completed{Colors.END}")
        print(f"  Best score: {result['best_score']:.2f}")
        print(f"  Best version: best_version.py")
    
    print(f"\n{Colors.CYAN}Generated files:{Colors.END}")
    for i in range(1, result['iterations'] + 1):
        print(f"  - iteration_{i}.py")
    print(f"  - best_version.py")
    print(f"  - ollama_simple.log")

if __name__ == "__main__":
    main()
