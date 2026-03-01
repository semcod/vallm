#!/usr/bin/env python3
"""
Version bump script for vallm package.
Updates version in pyproject.toml based on the specified bump type.
"""

import sys
import re
from pathlib import Path


def bump_version(version_str, bump_type):
    """Bump version string based on type."""
    # Parse version string (expected format: X.Y.Z)
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', version_str)
    if not match:
        raise ValueError(f"Invalid version format: {version_str}")
    
    major, minor, patch = map(int, match.groups())
    
    if bump_type == "patch":
        patch += 1
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")
    
    return f"{major}.{minor}.{patch}"


def main():
    if len(sys.argv) != 2:
        print("Usage: python bump_version.py <patch|minor|major>")
        sys.exit(1)
    
    bump_type = sys.argv[1]
    if bump_type not in ["patch", "minor", "major"]:
        print("Error: bump_type must be one of: patch, minor, major")
        sys.exit(1)
    
    # Read pyproject.toml
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    if not pyproject_path.exists():
        print(f"Error: {pyproject_path} not found")
        sys.exit(1)
    
    content = pyproject_path.read_text()
    
    # Find current version
    version_match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
    if not version_match:
        print("Error: version not found in pyproject.toml")
        sys.exit(1)
    
    current_version = version_match.group(1)
    new_version = bump_version(current_version, bump_type)
    
    # Update version in content
    new_content = re.sub(
        r'^version\s*=\s*"([^"]+)"',
        f'version = "{new_version}"',
        content,
        flags=re.MULTILINE
    )
    
    # Write back to file
    pyproject_path.write_text(new_content)
    
    print(f"Bumped {bump_type} version: {current_version} → {new_version}")


if __name__ == "__main__":
    main()
