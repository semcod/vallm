"""Example 14: Advanced API usage patterns.

Demonstrates: Proposal creation, custom settings, result interpretation, and programmatic workflows.
"""

import json
from pathlib import Path


def demo_proposal_creation():
    """Demonstrate different ways to create validation proposals."""
    from vallm import Proposal

    print("=" * 60)
    print("Demo 1: Proposal Creation Methods")
    print("=" * 60)

    # Method 1: Direct code string
    code = """
def hello():
    return "Hello, World!"
"""
    proposal1 = Proposal(code=code, language="python")
    print(f"1. From code string: {len(proposal1.code)} chars")

    # Method 2: From file path
    # proposal2 = Proposal.from_file("path/to/file.py")
    print("2. From file: Proposal.from_file('file.py')")

    # Method 3: With metadata
    proposal3 = Proposal(
        code=code,
        language="python",
        filename="example.py",
        metadata={"author": "demo", "version": "1.0"},
    )
    print(f"3. With metadata: {proposal3.metadata}")

    print()


def demo_settings_customization():
    """Demonstrate VallmSettings customization."""
    from vallm.config import VallmSettings

    print("=" * 60)
    print("Demo 2: Settings Customization")
    print("=" * 60)

    # Default settings
    default = VallmSettings()
    print(f"Default: syntax={default.enable_syntax}, imports={default.enable_imports}")

    # Security-focused
    security = VallmSettings(
        enable_syntax=True,
        enable_imports=True,
        enable_complexity=False,
        enable_security=True,
        enable_semantic=False,
    )
    print(f"Security-focused: security={security.enable_security}")

    # Performance-focused
    performance = VallmSettings(
        enable_syntax=True,
        enable_imports=True,
        enable_complexity=True,
        enable_security=False,
        enable_semantic=False,
    )
    print(f"Performance-focused: complexity={performance.enable_complexity}")

    # Full validation
    full = VallmSettings(
        enable_syntax=True,
        enable_imports=True,
        enable_complexity=True,
        enable_security=True,
        enable_semantic=True,
    )
    print("Full validation: all validators enabled")

    print()


def demo_result_interpretation():
    """Demonstrate interpreting validation results."""
    from vallm import Proposal, validate, VallmSettings

    print("=" * 60)
    print("Demo 3: Result Interpretation")
    print("=" * 60)

    code_with_issues = """
import os
import sys
import json

def bad_function(x, y, z, a, b, c, d, e, f, g):
    if x > 0:
        if y > 0:
            if z > 0:
                return x + y + z
    return 0
"""

    settings = VallmSettings(
        enable_syntax=True,
        enable_imports=True,
        enable_complexity=True,
        enable_security=False,
    )

    proposal = Proposal(code=code_with_issues, language="python")
    result = validate(proposal, settings)

    # Overall result
    print(f"Verdict: {result.verdict.value}")
    print(f"Overall Score: {result.weighted_score:.2f}")
    print()

    # Per-validator results
    print("Validator Details:")
    for r in result.results:
        print(f"  {r.validator}:")
        print(f"    Score: {r.score:.2f}")
        print(f"    Issues: {len(r.issues)}")
        if r.issues:
            for issue in r.issues[:3]:  # Show first 3
                print(f"      - {str(issue)[:60]}...")
        print()

    # Decision logic
    if result.verdict.value == "PASS":
        print("✓ Code is ready for deployment")
    elif result.verdict.value == "WARNING":
        print("⚠ Code has issues but may be acceptable")
        print(f"  Recommendation: Review {sum(len(r.issues) for r in result.results)} issues")
    else:
        print("✗ Code has critical issues")
        print("  Recommendation: Fix before deployment")

    print()


def demo_workflow_integration():
    """Demonstrate integration into CI/CD workflows."""
    from vallm import Proposal, validate, VallmSettings

    print("=" * 60)
    print("Demo 4: CI/CD Workflow Integration")
    print("=" * 60)

    code_sample = """
def process_data(items):
    results = []
    for item in items:
        if item.valid:
            results.append(item.process())
    return results
"""

    # Gate configuration
    GATE_THRESHOLD = 0.8

    settings = VallmSettings(
        enable_syntax=True,
        enable_imports=True,
        enable_complexity=True,
        enable_security=True,
    )

    proposal = Proposal(code=code_sample, language="python")
    result = validate(proposal, settings)

    print(f"Quality Gate Check (threshold: {GATE_THRESHOLD}):")
    print(f"  Score: {result.weighted_score:.2f}")

    # Gate decision
    if result.weighted_score >= GATE_THRESHOLD:
        print(f"  ✓ PASS - Score >= {GATE_THRESHOLD}")
        print("  Proceeding with deployment...")
    else:
        print(f"  ✗ FAIL - Score < {GATE_THRESHOLD}")
        print("  Blocking deployment...")

    # Generate report
    report = {
        "timestamp": "2024-01-15T10:00:00Z",
        "gate": GATE_THRESHOLD,
        "result": {
            "score": result.weighted_score,
            "verdict": result.verdict.value,
            "passed": result.weighted_score >= GATE_THRESHOLD,
        },
        "validators": {
            r.validator: {"score": r.score, "issues": len(r.issues)} for r in result.results
        },
    }

    print("\nJSON Report:")
    print(json.dumps(report, indent=2))
    print()


def main():
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    from examples.utils import save_analysis_data

    print("\n" + "=" * 60)
    print("Advanced API Usage Examples")
    print("=" * 60)
    print()

    demo_proposal_creation()
    demo_settings_customization()
    demo_result_interpretation()
    demo_workflow_integration()

    # Save summary
    save_analysis_data(
        "api_advanced",
        {
            "demos": [
                "proposal_creation",
                "settings_customization",
                "result_interpretation",
                "workflow_integration",
            ],
            "status": "completed",
        },
    )

    print("=" * 60)
    print("All demos completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
