"""Example 8: Integration with code2llm for code analysis.

Demonstrates: Using code2llm to analyze code structure and vallm to validate quality.
"""

import json
from pathlib import Path

try:
    from code2llm import analyze_directory, analyze_file
    from code2llm.formats import TOONFormat
    CODE2LLM_AVAILABLE = True
except ImportError:
    CODE2LLM_AVAILABLE = False
    print("⚠️  code2llm not installed. Run: pip install code2llm")

from vallm import Proposal, validate, VallmSettings
from vallm.core.languages import detect_language


# Sample project structure to analyze
SAMPLE_PROJECT = {
    "math_utils.py": '''
"""Math utilities module."""

def factorial(n: int) -> int:
    """Calculate factorial."""
    if n < 0:
        raise ValueError("n must be non-negative")
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def fibonacci(n: int) -> list[int]:
    """Generate fibonacci sequence."""
    if n <= 0:
        return []
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    return fib
''',
    "string_utils.py": '''
"""String utilities module."""

def reverse(s: str) -> str:
    """Reverse a string."""
    return s[::-1]

def is_palindrome(s: str) -> bool:
    """Check if string is palindrome."""
    cleaned = ''.join(c.lower() for c in s if c.isalnum())
    return cleaned == cleaned[::-1]
''',
    "main.py": '''
"""Main application entry point."""
from math_utils import factorial, fibonacci
from string_utils import reverse, is_palindrome

def main():
    """Run demonstration."""
    print(f"Factorial of 5: {factorial(5)}")
    print(f"Fibonacci(10): {fibonacci(10)}")
    print(f"Reverse 'hello': {reverse('hello')}")
    print(f"'racecar' is palindrome: {is_palindrome('racecar')}")

if __name__ == "__main__":
    main()
''',
}


def create_sample_project(base_path: Path) -> None:
    """Create a sample project for analysis."""
    base_path.mkdir(parents=True, exist_ok=True)
    
    for filename, content in SAMPLE_PROJECT.items():
        (base_path / filename).write_text(content)
    
    # Create .gitignore
    (base_path / ".gitignore").write_text("""
__pycache__/
*.pyc
.venv/
*.log
""")


def analyze_with_code2llm(project_path: Path) -> dict:
    """Analyze project structure using code2llm."""
    if not CODE2LLM_AVAILABLE:
        return {"error": "code2llm not available"}
    
    print("=" * 60)
    print("Analyzing with code2llm...")
    print("=" * 60)
    
    # Analyze directory
    try:
        # Try different API versions
        try:
            from code2llm.analyzer import CodeAnalyzer
            analyzer = CodeAnalyzer(str(project_path))
            result = analyzer.analyze()
        except (ImportError, AttributeError):
            # Fallback to basic file analysis
            result = {
                "files": [],
                "languages": {},
            }
            for file_path in project_path.rglob("*.py"):
                if file_path.is_file():
                    lang = detect_language(file_path)
                    result["files"].append({
                        "path": str(file_path),
                        "language": lang.display_name if lang else "Unknown",
                    })
                    
                    lang_name = lang.display_name if lang else "Unknown"
                    result["languages"][lang_name] = result["languages"].get(lang_name, 0) + 1
        
        return result
    except Exception as e:
        return {"error": str(e)}


def validate_with_vallm(project_path: Path) -> dict:
    """Validate all Python files with vallm."""
    print("\n" + "=" * 60)
    print("Validating with vallm...")
    print("=" * 60)
    
    settings = VallmSettings(
        enable_syntax=True,
        enable_imports=True,
        enable_complexity=True,
        enable_security=False,
        enable_semantic=False,
    )
    
    results = []
    
    for file_path in project_path.rglob("*.py"):
        if file_path.is_file():
            try:
                code = file_path.read_text()
                proposal = Proposal(
                    code=code,
                    language="python",
                    filename=str(file_path.relative_to(project_path))
                )
                
                result = validate(proposal, settings)
                
                results.append({
                    "file": file_path.name,
                    "verdict": result.verdict.value,
                    "score": result.weighted_score,
                    "errors": result.error_count,
                    "warnings": result.warning_count,
                })
                
                icon = "✓" if result.verdict.value == "pass" else "⚠" if result.verdict.value == "review" else "✗"
                print(f"{icon} {file_path.name}: {result.verdict.value} (score: {result.weighted_score:.2f})")
                
            except Exception as e:
                print(f"✗ {file_path.name}: error - {e}")
                results.append({
                    "file": file_path.name,
                    "error": str(e),
                })
    
    return {"files": results}


def generate_report(code2llm_result: dict, vallm_result: dict, output_path: Path) -> None:
    """Generate combined analysis report."""
    report = {
        "analysis_tools": {
            "code2llm": CODE2LLM_AVAILABLE,
            "vallm": True,
        },
        "project_structure": code2llm_result,
        "quality_validation": vallm_result,
        "summary": {
            "total_files": len(vallm_result.get("files", [])),
            "passed": sum(1 for f in vallm_result.get("files", []) if f.get("verdict") == "pass"),
            "failed": sum(1 for f in vallm_result.get("files", []) if f.get("verdict") == "fail"),
        }
    }
    
    # Save report
    report_file = output_path / ".vallm" / "code2llm_integration_report.json"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📊 Report saved to {report_file}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("INTEGRATION SUMMARY")
    print("=" * 60)
    print(f"Total files analyzed: {report['summary']['total_files']}")
    print(f"Passed: {report['summary']['passed']}")
    print(f"Failed: {report['summary']['failed']}")
    
    if report['summary']['failed'] == 0:
        print("\n🎉 All files passed quality checks!")
    else:
        print(f"\n⚠️  {report['summary']['failed']} files need attention")


def main():
    """Main example function."""
    # Setup
    example_dir = Path(__file__).parent
    project_path = example_dir / "sample_project"
    
    print("🚀 code2llm + vallm Integration Example")
    print("=" * 60)
    
    # Create sample project
    print("\n📁 Creating sample project...")
    create_sample_project(project_path)
    print(f"   Created at: {project_path}")
    
    # Analyze with code2llm
    if CODE2LLM_AVAILABLE:
        code2llm_result = analyze_with_code2llm(project_path)
    else:
        print("\n⚠️  code2llm not available, skipping structure analysis")
        code2llm_result = {"note": "code2llm not installed"}
    
    # Validate with vallm
    vallm_result = validate_with_vallm(project_path)
    
    # Generate report
    generate_report(code2llm_result, vallm_result, example_dir)
    
    # Cleanup (optional)
    print("\n🧹 Cleaning up sample project...")
    import shutil
    shutil.rmtree(project_path, ignore_errors=True)
    print("   Done!")


if __name__ == "__main__":
    main()
