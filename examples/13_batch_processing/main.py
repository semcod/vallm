"""Example 13: Batch processing of multiple files.

Demonstrates: Validating entire directories, filtering files, and generating batch reports.
"""

from pathlib import Path


def main():
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    from vallm import Proposal, validate, VallmSettings
    from examples.utils import save_analysis_data

    # Create test files
    test_dir = Path(".test_batch_files")
    test_dir.mkdir(exist_ok=True)

    files_content = {
        "good_file.py": """
def calculate_sum(a: int, b: int) -> int:
    return a + b

class Calculator:
    def add(self, x, y):
        return x + y
""",
        "bad_file.py": """
def broken_function(x, y)
    return x + y

import os
os.system("rm -rf /")  # Security issue
""",
        "complex_file.py": """
def nested_ifs(a, b, c, d, e):
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        return a + b + c + d + e
                    return a + b + c + d
                return a + b + c
            return a + b
        return a
    return 0
""",
    }

    for name, content in files_content.items():
        (test_dir / name).write_text(content)

    # Settings for batch validation
    settings = VallmSettings(
        enable_syntax=True,
        enable_imports=True,
        enable_complexity=True,
        enable_security=True,
    )

    print("=" * 60)
    print("Batch Validation Example")
    print("=" * 60)
    print(f"Validating files in: {test_dir}")
    print()

    # Collect files for batch validation
    files = list(test_dir.glob("*.py"))
    print(f"Found {len(files)} files to validate:\n")
    for f in files:
        print(f"  - {f.name}")
    print()

    # Run batch validation (loop through files)
    results = []
    for file_path in files:
        code = file_path.read_text()
        proposal = Proposal(code=code, language="python", filename=str(file_path))
        result = validate(proposal, settings)
        results.append((file_path.name, result))

    # Display results
    print("=" * 60)
    print("Validation Results")
    print("=" * 60)

    all_results = {}
    for file_name, result in results:
        print(f"\n{file_name}:")
        print(f"  Verdict: {result.verdict.value}")
        print(f"  Score:   {result.weighted_score:.2f}")
        print(f"  Issues:  {sum(len(r.issues) for r in result.results)}")

        for r in result.results:
            if r.issues:
                print(f"    {r.validator}: {len(r.issues)} issues")

        all_results[file_name] = {
            "verdict": result.verdict.value,
            "score": result.weighted_score,
            "validators": {
                r.validator: {"score": r.score, "issues": len(r.issues)} for r in result.results
            },
        }

    # Print batch summary
    print("\n" + "=" * 60)
    print("Batch Summary")
    print("=" * 60)
    passed = sum(1 for _, r in results if r.verdict.value == "PASS")
    failed = sum(1 for _, r in results if r.verdict.value == "FAIL")
    warning = sum(1 for _, r in results if r.verdict.value == "WARNING")
    print(f"  Passed:  {passed}")
    print(f"  Failed:  {failed}")
    print(f"  Warning: {warning}")

    # Save analysis data
    save_analysis_data(
        "batch_processing",
        {
            "files_validated": len(files),
            "results": all_results,
            "summary": {"passed": passed, "failed": failed, "warning": warning},
        },
    )

    # Cleanup
    for f in files:
        f.unlink()
    test_dir.rmdir()

    print("\n✓ Batch validation complete!")


if __name__ == "__main__":
    main()
