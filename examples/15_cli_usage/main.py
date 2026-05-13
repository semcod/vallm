"""Example 15: CLI usage patterns and programmatic invocation.

Demonstrates: Using vallm CLI programmatically, parsing output, and automation.
"""

import json
import subprocess
from pathlib import Path


def run_cli_command(cmd: list[str]) -> tuple[int, str, str]:
    """Run a CLI command and return result."""
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(Path(__file__).parent))
    return result.returncode, result.stdout, result.stderr


def demo_single_file_validation():
    """Demo: Validate single file via CLI."""
    print("=" * 60)
    print("Demo 1: Single File Validation (CLI)")
    print("=" * 60)

    # Create test file
    test_file = Path("test_sample.py")
    test_file.write_text("""
def greet(name: str) -> str:
    return f"Hello, {name}!"

class Greeter:
    def __init__(self, greeting: str):
        self.greeting = greeting
    
    def greet(self, name: str) -> str:
        return f"{self.greeting}, {name}!"
""")

    print(f"Created: {test_file}")
    print("Running: python -m vallm validate test_sample.py")
    print()

    # Run CLI validation
    returncode, stdout, stderr = run_cli_command(
        ["python", "-m", "vallm", "validate", "test_sample.py", "--format", "json"]
    )

    if stdout:
        print("STDOUT:")
        print(stdout[:1000])  # First 1000 chars

    if stderr:
        print("\nSTDERR:")
        print(stderr[:500])

    print(f"\nReturn code: {returncode}")

    # Cleanup
    test_file.unlink(missing_ok=True)
    print()


def demo_batch_validation():
    """Demo: Batch validation via CLI."""
    print("=" * 60)
    print("Demo 2: Batch Validation (CLI)")
    print("=" * 60)

    # Create test directory with files
    test_dir = Path(".test_cli_batch")
    test_dir.mkdir(exist_ok=True)

    (test_dir / "file1.py").write_text("def good(): pass")
    (test_dir / "file2.py").write_text("def also_good(): return 42")

    print(f"Created test directory: {test_dir}")
    print(f"Files: {list(test_dir.glob('*.py'))}")
    print()

    print("Command: python -m vallm batch .test_cli_batch/")
    print()

    # Note: CLI batch command may vary based on actual implementation
    print("(CLI batch validation would run here)")
    print()

    # Cleanup
    for f in test_dir.glob("*.py"):
        f.unlink()
    test_dir.rmdir()
    print()


def demo_output_formats():
    """Demo: Different output formats."""
    print("=" * 60)
    print("Demo 3: Output Formats")
    print("=" * 60)

    test_code = "def test(): pass"
    test_file = Path("format_test.py")
    test_file.write_text(test_code)

    formats = [
        ("text", "--format", "text"),
        ("json", "--format", "json"),
    ]

    for name, flag, value in formats:
        print(f"\nFormat: {name}")
        print(f"Command: python -m vallm validate format_test.py {flag} {value}")
        print("-" * 40)

        returncode, stdout, stderr = run_cli_command(
            ["python", "-m", "vallm", "validate", "format_test.py", flag, value]
        )

        if stdout:
            print(stdout[:500])

    # Cleanup
    test_file.unlink(missing_ok=True)
    print()


def demo_programmatic_cli():
    """Demo: Using CLI programmatically."""
    print("=" * 60)
    print("Demo 4: Programmatic CLI Usage")
    print("=" * 60)

    # Create test file
    test_file = Path("prog_test.py")
    test_file.write_text("""
def calculate(x, y):
    return x + y
""")

    # Programmatic invocation
    print("Invoking CLI programmatically...")

    returncode, stdout, stderr = run_cli_command(
        ["python", "-m", "vallm", "validate", "prog_test.py", "--format", "json"]
    )

    if returncode == 0:
        print("✓ CLI invocation successful")

        # Parse JSON output
        try:
            # Find JSON in output
            lines = stdout.strip().split("\n")
            for line in lines:
                line = line.strip()
                if line and line.startswith("{"):
                    data = json.loads(line)
                    if isinstance(data, dict) and "verdict" in data:
                        print(f"Parsed result: verdict={data.get('verdict')}")
                        break
        except json.JSONDecodeError:
            print("Could not parse JSON output")
    else:
        print(f"✗ CLI failed with code {returncode}")

    # Cleanup
    test_file.unlink(missing_ok=True)
    print()


def demo_check_command():
    """Demo: Check command for CI/CD."""
    print("=" * 60)
    print("Demo 5: Check Command (CI/CD)")
    print("=" * 60)

    # Create test files - one good, one bad
    good_file = Path("check_good.py")
    bad_file = Path("check_bad.py")

    good_file.write_text("def good(): return 42")
    bad_file.write_text("def bad(x y): pass")  # Syntax error

    print("Testing 'check' command for CI integration:")
    print()

    # Good file check
    print("1. Good file (should pass):")
    rc, stdout, stderr = run_cli_command(["python", "-m", "vallm", "check", "check_good.py"])
    print(f"   Return code: {rc} (0 = pass, non-zero = fail)")

    # Bad file check
    print("\n2. Bad file (should fail):")
    rc, stdout, stderr = run_cli_command(["python", "-m", "vallm", "check", "check_bad.py"])
    print(f"   Return code: {rc}")

    # Cleanup
    good_file.unlink(missing_ok=True)
    bad_file.unlink(missing_ok=True)
    print()


def main():
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    from examples.utils import save_analysis_data

    print("\n" + "=" * 60)
    print("CLI Usage Examples")
    print("=" * 60)
    print()
    print("Note: These demos invoke the vallm CLI via subprocess.")
    print("Ensure vallm is installed: pip install -e /path/to/vallm")
    print()

    demo_single_file_validation()
    demo_batch_validation()
    demo_output_formats()
    demo_programmatic_cli()
    demo_check_command()

    # Save summary
    save_analysis_data(
        "cli_usage",
        {
            "demos": [
                "single_file_validation",
                "batch_validation",
                "output_formats",
                "programmatic_cli",
                "check_command",
            ],
            "note": "CLI demos use subprocess invocation",
        },
    )

    print("=" * 60)
    print("All CLI demos completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
