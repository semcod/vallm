"""Shared utilities for vallm examples."""

import json
import os
from pathlib import Path
from typing import Any


class Colors:
    """ANSI color codes for terminal output."""

    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    END = '\033[0m'

from vallm.config import VallmSettings
from vallm.core.proposal import Proposal
from vallm.scoring import validate

from .extract_code_from_response import extract_code_from_response


def save_analysis_data(example_name: str, result_data: dict) -> None:
    """Save analysis data to .vallm folder.
    
    Args:
        example_name: Name of the example
        result_data: Dictionary with analysis results
    """
    vallm_dir = Path(".vallm")
    vallm_dir.mkdir(exist_ok=True)
    
    # Save result summary
    summary_file = vallm_dir / f"{example_name}_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(result_data, f, indent=2, default=str)
    
    print(f"Analysis data saved to {summary_file}")


def run_validation_examples(
    example_name: str,
    good_code: str,
    bad_code: str,
    complex_code: str,
    settings: VallmSettings | None = None,
) -> dict:
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


def validate_code_example(
    name: str,
    code: str,
    settings,
    all_results: dict,
    include_issue_details: bool = False
) -> None:
    """Validate a code example and store results.
    
    Args:
        name: Example name identifier
        code: Code string to validate
        settings: VallmSettings instance
        all_results: Dictionary to store results in
        include_issue_details: Whether to include full issue details
    """
    from vallm import validate, Proposal
    
    print("=" * 60)
    print(f"Validating {name}")
    print("=" * 60)
    
    proposal = Proposal(code=code, language="python")
    result = validate(proposal, settings)
    
    print(f"Verdict: {result.verdict.value}")
    print(f"Score:   {result.weighted_score:.2f}")
    
    for r in result.results:
        print(f"  {r.validator}: score={r.score:.2f}, issues={len(r.issues)}")
        if r.issues:
            for issue in r.issues:
                print(f"    {issue}")
    
    # Store result data
    result_entry = {
        "verdict": result.verdict.value,
        "score": result.weighted_score,
        "validators": {
            r.validator: {
                "score": r.score, 
                "issues": len(r.issues),
            } for r in result.results
        }
    }
    
    if include_issue_details:
        for r in result.results:
            if r.issues:
                result_entry["validators"][r.validator]["issue_details"] = [
                    str(i) for i in r.issues
                ]
    
    all_results[name] = result_entry
    print()


def print_summary(all_results: dict) -> None:
    """Print summary of all validation results.
    
    Args:
        all_results: Dictionary with all results
    """
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for name, data in all_results.items():
        print(f"{name}: {data['verdict']} (score: {data['score']:.2f})")
