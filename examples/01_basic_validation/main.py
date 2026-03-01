"""Example 1: Basic Python code validation using vallm's default pipeline.

Demonstrates: syntax, import, and complexity validation (Tier 1 & 2).
"""

import json
import os
from pathlib import Path
from vallm import Proposal, validate, VallmSettings

# Good code — should PASS
good_code = """
def fibonacci(n: int) -> list[int]:
    if n <= 0:
        return []
    if n == 1:
        return [0]
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i - 1] + fib[i - 2])
    return fib
"""

# Bad code — has syntax error, should FAIL
bad_code = """
def broken_function(x, y)
    return x + y
"""

# Complex code — should get warnings
complex_code = """
def overly_complex(a, b, c, d, e, f, g):
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        if f > 0:
                            if g > 0:
                                return a + b + c + d + e + f + g
                            else:
                                return a + b + c + d + e + f
                        else:
                            return a + b + c + d + e
                    else:
                        return a + b + c + d
                else:
                    return a + b + c
            else:
                return a + b
        else:
            return a
    else:
        return 0
"""

def save_analysis_data(example_name: str, result_data: dict):
    """Save analysis data to .vallm folder."""
    vallm_dir = Path(".vallm")
    vallm_dir.mkdir(exist_ok=True)
    
    # Save result summary
    summary_file = vallm_dir / f"{example_name}_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(result_data, f, indent=2, default=str)
    
    print(f"Analysis data saved to {summary_file}")


def main():
    settings = VallmSettings(
        enable_syntax=True,
        enable_imports=True,
        enable_complexity=True,
        enable_security=False,
        enable_semantic=False,
    )

    all_results = {}

    print("=" * 60)
    print("Example 1: Validating GOOD code")
    print("=" * 60)
    proposal = Proposal(code=good_code, language="python")
    result = validate(proposal, settings)
    print(f"Verdict: {result.verdict.value}")
    print(f"Score:   {result.weighted_score:.2f}")
    for r in result.results:
        print(f"  {r.validator}: score={r.score:.2f}, issues={len(r.issues)}")
    
    # Store result data
    all_results["good_code"] = {
        "verdict": result.verdict.value,
        "score": result.weighted_score,
        "validators": {r.validator: {"score": r.score, "issues": len(r.issues)} for r in result.results}
    }
    print()

    print("=" * 60)
    print("Example 2: Validating BAD code (syntax error)")
    print("=" * 60)
    proposal = Proposal(code=bad_code, language="python")
    result = validate(proposal, settings)
    print(f"Verdict: {result.verdict.value}")
    print(f"Score:   {result.weighted_score:.2f}")
    for r in result.results:
        print(f"  {r.validator}: score={r.score:.2f}, issues={len(r.issues)}")
        for issue in r.issues:
            print(f"    {issue}")
    
    # Store result data
    all_results["bad_code"] = {
        "verdict": result.verdict.value,
        "score": result.weighted_score,
        "validators": {r.validator: {"score": r.score, "issues": len(r.issues), "issue_details": [str(i) for i in r.issues]} for r in result.results}
    }
    print()

    print("=" * 60)
    print("Example 3: Validating COMPLEX code")
    print("=" * 60)
    proposal = Proposal(code=complex_code, language="python")
    result = validate(proposal, settings)
    print(f"Verdict: {result.verdict.value}")
    print(f"Score:   {result.weighted_score:.2f}")
    for r in result.results:
        print(f"  {r.validator}: score={r.score:.2f}, issues={len(r.issues)}")
        for issue in r.issues:
            print(f"    {issue}")
    
    # Store result data
    all_results["complex_code"] = {
        "verdict": result.verdict.value,
        "score": result.weighted_score,
        "validators": {r.validator: {"score": r.score, "issues": len(r.issues), "issue_details": [str(i) for i in r.issues]} for r in result.results}
    }

    # Save all analysis data
    save_analysis_data("basic_validation", all_results)
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for name, data in all_results.items():
        print(f"{name}: {data['verdict']} (score: {data['score']:.2f})")


if __name__ == "__main__":
    main()
