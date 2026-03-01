"""Example 3: Security validation.

Demonstrates: pattern-based security checks and AST-based detection.
"""

import json
from pathlib import Path
from vallm import Proposal, VallmSettings
from vallm.validators.security import SecurityValidator

# Code with security issues
insecure_code = """
import os
import pickle
import yaml

def process_user_input(data):
    # Dangerous: eval on user input
    result = eval(data)

    # Dangerous: exec
    exec(f"print({data})")

    # Dangerous: os.system
    os.system(f"echo {data}")

    # Dangerous: pickle.loads
    obj = pickle.loads(data.encode())

    # Dangerous: yaml.load without Loader
    config = yaml.load(data)

    # Hardcoded secret
    api_key = "sk-1234567890abcdef"

    return result
"""

# Secure alternative
secure_code = """
import subprocess
import json
import yaml

def process_user_input(data: str) -> dict:
    # Safe: json.loads for structured data
    parsed = json.loads(data)

    # Safe: subprocess with list args
    result = subprocess.run(
        ["echo", str(parsed.get("message", ""))],
        capture_output=True,
        text=True,
    )

    # Safe: yaml.safe_load
    config = yaml.safe_load(data)

    return {"result": result.stdout, "config": config}
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
    validator = SecurityValidator()
    all_results = {}

    print("=" * 60)
    print("Checking INSECURE code")
    print("=" * 60)
    proposal = Proposal(code=insecure_code, language="python")
    result = validator.validate(proposal, {})
    print(f"Score: {result.score:.2f}")
    print(f"Issues ({len(result.issues)}):")
    for issue in result.issues:
        print(f"  {issue}")
    
    # Store result data
    all_results["insecure_code"] = {
        "score": result.score,
        "issues_count": len(result.issues),
        "issues": [str(issue) for issue in result.issues]
    }

    print("\n" + "=" * 60)
    print("Checking SECURE code")
    print("=" * 60)
    proposal = Proposal(code=secure_code, language="python")
    result = validator.validate(proposal, {})
    print(f"Score: {result.score:.2f}")
    print(f"Issues ({len(result.issues)}):")
    for issue in result.issues:
        print(f"  {issue}")
    
    # Store result data
    all_results["secure_code"] = {
        "score": result.score,
        "issues_count": len(result.issues),
        "issues": [str(issue) for issue in result.issues]
    }

    # Save all analysis data
    save_analysis_data("security_check", all_results)
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Insecure code: {all_results['insecure_code']['score']:.2f} ({all_results['insecure_code']['issues_count']} issues)")
    print(f"Secure code: {all_results['secure_code']['score']:.2f} ({all_results['secure_code']['issues_count']} issues)")


if __name__ == "__main__":
    main()
