"""Shared validation runner for example scripts."""

from __future__ import annotations

from typing import Any, Dict

from vallm.config import VallmSettings
from vallm.core.proposal import Proposal
from vallm.scoring import validate


def run_validation_examples(
    example_name: str,
    good_code: str,
    bad_code: str,
    complex_code: str,
    settings: VallmSettings | None = None,
) -> Dict[str, Any]:
    """Run standard validation examples (good, bad, complex code).
    
    Args:
        example_name: Name for saving analysis data
        good_code: Example of good code to validate
        bad_code: Example of bad code with issues
        complex_code: Example of complex code
        settings: Validation settings (uses default if None)
        
    Returns:
        Dictionary with all validation results
    """
    if settings is None:
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

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    return all_results
