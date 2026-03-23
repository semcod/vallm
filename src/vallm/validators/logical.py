"""Logical error validator using pyflakes."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
from typing import List

from vallm.core.proposal import Proposal
from vallm.scoring import Issue, Severity, ValidationResult


class LogicalErrorValidator:
    """Validator for logical errors using pyflakes."""
    
    tier = 1
    weight = 1.0
    
    def __init__(self, settings=None):
        """Initialize logical error validator."""
        self.settings = settings
    
    def validate(self, proposal: Proposal, context: dict) -> ValidationResult:
        """Validate code for logical errors using pyflakes.
        
        Args:
            proposal: Code proposal to validate
            context: Additional context
            
        Returns:
            ValidationResult with logical error issues
        """
        if proposal.language != "python":
            # Only supports Python for now
            return ValidationResult(
                validator="logical",
                score=1.0,
                weight=self.weight,
                issues=[],
                details={"language": proposal.language, "supported": False}
            )
        
        issues = self._check_pyflakes(proposal.code)
        
        return ValidationResult(
            validator="logical",
            score=1.0 - len(issues) / 10,  # Simple scoring
            weight=self.weight,
            issues=issues,
            details={
                "error_count": len(issues),
                "tool": "pyflakes"
            }
        )
    
    def _check_pyflakes(self, code: str) -> List[Issue]:
        """Check code with pyflakes and return issues.
        
        Args:
            code: Python code to check
            
        Returns:
            List of validation issues
        """
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Run pyflakes
            result = subprocess.run(
                ['pyflakes', temp_file],
                capture_output=True,
                text=True
            )
            
            # Clean up
            Path(temp_file).unlink()
            
            issues = []
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        issue = self._parse_pyflakes_line(line)
                        if issue:
                            issues.append(issue)
            
            return issues
            
        except (subprocess.SubprocessError, FileNotFoundError):
            # pyflakes not available or other error
            return []
    
    def _parse_pyflakes_line(self, line: str) -> Issue | None:
        """Parse a pyflakes output line into an Issue.
        
        Args:
            line: Pyflakes output line
            
        Returns:
            Issue object or None if parsing fails
        """
        try:
            # Example pyflakes output:
            # file.py:5: undefined name 'undefined_var'
            parts = line.split(':', 2)
            if len(parts) < 3:
                return None
            
            _, line_num, message = parts
            line_num = int(line_num)
            
            # Determine severity based on message
            severity = Severity.ERROR
            if any(keyword in message.lower() for keyword in [
                'unused', 'imported but unused', 'redefined', 'shadowed'
            ]):
                severity = Severity.WARNING
            
            return Issue(
                message=message.strip(),
                severity=severity,
                line=line_num,
                rule="pyflakes." + message.split()[0].lower()
            )
            
        except (ValueError, IndexError):
            return None


def create_validator(settings=None) -> LogicalErrorValidator:
    """Factory function for LogicalErrorValidator.
    
    Args:
        settings: Optional settings
        
    Returns:
        LogicalErrorValidator instance
    """
    return LogicalErrorValidator(settings)
