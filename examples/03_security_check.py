"""Example 3: Security validation.

Demonstrates: pattern-based security checks and AST-based detection.
"""

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


def main():
    validator = SecurityValidator()

    print("=" * 60)
    print("Checking INSECURE code")
    print("=" * 60)
    proposal = Proposal(code=insecure_code, language="python")
    result = validator.validate(proposal, {})
    print(f"Score: {result.score:.2f}")
    print(f"Issues ({len(result.issues)}):")
    for issue in result.issues:
        print(f"  {issue}")

    print("\n" + "=" * 60)
    print("Checking SECURE code")
    print("=" * 60)
    proposal = Proposal(code=secure_code, language="python")
    result = validator.validate(proposal, {})
    print(f"Score: {result.score:.2f}")
    print(f"Issues ({len(result.issues)}):")
    for issue in result.issues:
        print(f"  {issue}")


if __name__ == "__main__":
    main()
