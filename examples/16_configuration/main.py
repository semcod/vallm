"""Example 16: Configuration and customization patterns.

Demonstrates: Config files, environment variables, and runtime configuration.
"""

import json
import os
from pathlib import Path


def demo_config_file():
    """Demo: Using configuration files."""
    print("=" * 60)
    print("Demo 1: Configuration Files")
    print("=" * 60)

    # Create a temporary config file
    config = {
        "validators": {
            "syntax": {"enabled": True, "weight": 0.3},
            "imports": {"enabled": True, "weight": 0.2},
            "complexity": {"enabled": True, "weight": 0.25},
            "security": {"enabled": True, "weight": 0.25},
        },
        "thresholds": {
            "pass": 0.8,
            "warning": 0.6,
        },
        "output": {
            "format": "json",
            "verbose": True,
        },
    }

    config_file = Path(".vallm_config_demo.json")
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Created config file: {config_file}")
    print("Contents:")
    print(json.dumps(config, indent=2))
    print()

    # Show how to load config
    print("Loading configuration...")
    with open(config_file) as f:
        loaded = json.load(f)

    print(f"Loaded {len(loaded['validators'])} validator configs")
    print(f"Pass threshold: {loaded['thresholds']['pass']}")
    print()

    # Cleanup
    config_file.unlink()


def demo_environment_variables():
    """Demo: Environment variable configuration."""
    print("=" * 60)
    print("Demo 2: Environment Variables")
    print("=" * 60)

    # Set environment variables for demo
    env_vars = {
        "VALLM_ENABLE_SYNTAX": "true",
        "VALLM_ENABLE_SECURITY": "true",
        "VALLM_ENABLE_SEMANTIC": "false",
        "VALLM_OUTPUT_FORMAT": "json",
        "VALLM_VERBOSE": "true",
    }

    print("Setting environment variables:")
    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"  {key}={value}")

    print()

    # Simulate reading from environment
    def get_env_config():
        return {
            "syntax": os.getenv("VALLM_ENABLE_SYNTAX", "true").lower() == "true",
            "security": os.getenv("VALLM_ENABLE_SECURITY", "false").lower() == "true",
            "semantic": os.getenv("VALLM_ENABLE_SEMANTIC", "false").lower() == "true",
            "output_format": os.getenv("VALLM_OUTPUT_FORMAT", "text"),
            "verbose": os.getenv("VALLM_VERBOSE", "false").lower() == "true",
        }

    config = get_env_config()
    print("Parsed configuration:")
    for key, value in config.items():
        print(f"  {key}: {value}")
    print()

    # Cleanup
    for key in env_vars:
        del os.environ[key]


def demo_runtime_configuration():
    """Demo: Runtime configuration changes."""
    print("=" * 60)
    print("Demo 3: Runtime Configuration")
    print("=" * 60)

    from vallm.config import VallmSettings

    # Base settings
    base_settings = VallmSettings(
        enable_syntax=True,
        enable_imports=True,
        enable_complexity=True,
        enable_security=False,
    )

    print("Base settings:")
    print(f"  syntax={base_settings.enable_syntax}")
    print(f"  security={base_settings.enable_security}")
    print()

    # Create variant for security audit
    security_settings = VallmSettings(
        enable_syntax=base_settings.enable_syntax,
        enable_imports=base_settings.enable_imports,
        enable_complexity=False,
        enable_security=True,
    )

    print("Security audit settings:")
    print(f"  syntax={security_settings.enable_syntax}")
    print(f"  security={security_settings.enable_security}")
    print(f"  complexity={security_settings.enable_complexity}")
    print()


def demo_profile_switching():
    """Demo: Switching between configuration profiles."""
    print("=" * 60)
    print("Demo 4: Configuration Profiles")
    print("=" * 60)

    profiles = {
        "default": {
            "syntax": True,
            "imports": True,
            "complexity": True,
            "security": False,
            "semantic": False,
        },
        "security": {
            "syntax": True,
            "imports": True,
            "complexity": False,
            "security": True,
            "semantic": False,
        },
        "strict": {
            "syntax": True,
            "imports": True,
            "complexity": True,
            "security": True,
            "semantic": True,
        },
        "minimal": {
            "syntax": True,
            "imports": False,
            "complexity": False,
            "security": False,
            "semantic": False,
        },
    }

    print("Available profiles:")
    for name, config in profiles.items():
        enabled = [k for k, v in config.items() if v]
        print(f"  {name:10} → {', '.join(enabled)}")
    print()

    # Select and apply profile
    selected = "security"
    profile = profiles[selected]

    print(f"Applying '{selected}' profile:")
    print(f"  Enabled validators: {[k for k, v in profile.items() if v]}")
    print()


def demo_threshold_configuration():
    """Demo: Configuring quality thresholds."""
    print("=" * 60)
    print("Demo 5: Quality Thresholds")
    print("=" * 60)

    from vallm import Proposal, validate, VallmSettings

    code_sample = """
def calculate_average(numbers):
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)
"""

    # Test with different thresholds
    thresholds = [
        ("Strict", 0.9),
        ("Standard", 0.75),
        ("Lenient", 0.6),
    ]

    settings = VallmSettings(
        enable_syntax=True,
        enable_imports=True,
        enable_complexity=True,
    )

    proposal = Proposal(code=code_sample, language="python")
    result = validate(proposal, settings)

    print(f"Code score: {result.weighted_score:.2f}")
    print()

    print("Gate decisions by threshold:")
    for name, threshold in thresholds:
        passed = result.weighted_score >= threshold
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {name:10} (≥{threshold:.2f}): {status}")
    print()


def main():
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    from examples.utils import save_analysis_data

    print("\n" + "=" * 60)
    print("Configuration and Customization Examples")
    print("=" * 60)
    print()

    demo_config_file()
    demo_environment_variables()
    demo_runtime_configuration()
    demo_profile_switching()
    demo_threshold_configuration()

    # Save summary
    save_analysis_data(
        "configuration",
        {
            "demos": [
                "config_file",
                "environment_variables",
                "runtime_configuration",
                "profile_switching",
                "threshold_configuration",
            ],
            "status": "completed",
        },
    )

    print("=" * 60)
    print("All configuration demos completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
