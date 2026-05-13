#!/usr/bin/env python3
"""Tests for plugin system and validator discovery."""

import pluggy

import pytest

from vallm.hookspecs import VallmSpec, hookimpl
from vallm.core.proposal import Proposal
from vallm.scoring import ValidationResult, Issue, Severity


class MockValidator:
    """Mock validator for testing plugin system."""

    tier = 2
    name = "mock_validator"
    weight = 1.0

    @hookimpl
    def validate_proposal(self, proposal: Proposal, context: dict) -> ValidationResult:
        """Mock validation that always passes."""
        return ValidationResult(validator=self.name, score=1.0, weight=self.weight, issues=[])

    @hookimpl
    def get_validator_name(self) -> str:
        """Return validator name."""
        return self.name

    @hookimpl
    def get_validator_tier(self) -> int:
        """Return validator tier."""
        return self.tier


class TestPluginSystem:
    """Test cases for plugin system."""

    def test_plugin_manager_creation(self):
        """Test creating a plugin manager with vallm specs."""
        pm = pluggy.PluginManager("vallm")
        pm.add_hookspecs(VallmSpec)

        assert hasattr(pm.hook, "validate_proposal")
        assert hasattr(pm.hook, "get_validator_name")
        assert hasattr(pm.hook, "get_validator_tier")

    def test_register_validator(self):
        """Test registering a validator plugin."""
        pm = pluggy.PluginManager("vallm")
        pm.add_hookspecs(VallmSpec)

        validator = MockValidator()
        pm.register(validator)

        # Check that validator is registered
        assert validator in pm.get_plugins()

    def test_validate_proposal_hook(self):
        """Test calling validate_proposal through plugin system."""
        pm = pluggy.PluginManager("vallm")
        pm.add_hookspecs(VallmSpec)

        validator = MockValidator()
        pm.register(validator)

        proposal = Proposal(code="print('hello')", language="python")

        # Call the hook
        results = list(pm.hook.validate_proposal(proposal=proposal, context={}))

        assert len(results) == 1
        assert results[0].validator == "mock_validator"
        assert results[0].score == 1.0
        assert len(results[0].issues) == 0

    def test_multiple_validators(self):
        """Test running multiple validators through plugin system."""
        pm = pluggy.PluginManager("vallm")
        pm.add_hookspecs(VallmSpec)

        # Create multiple validators
        class StrictValidator(MockValidator):
            name = "strict_validator"
            tier = 1

            @hookimpl
            def validate_proposal(self, proposal: Proposal, context: dict) -> ValidationResult:
                issues = [
                    Issue(
                        message="Mock issue for testing",
                        severity=Severity.WARNING,
                        line=1,
                        rule="test.mock",
                    )
                ]
                return ValidationResult(
                    validator=self.name, score=0.8, weight=self.weight, issues=issues
                )

        validator1 = MockValidator()
        validator2 = StrictValidator()

        pm.register(validator1)
        pm.register(validator2)

        proposal = Proposal(code="print('hello')", language="python")

        # Call the hook
        results = list(pm.hook.validate_proposal(proposal=proposal, context={}))

        assert len(results) == 2

        # Check mock validator result
        mock_result = next(r for r in results if r.validator == "mock_validator")
        assert mock_result.score == 1.0
        assert len(mock_result.issues) == 0

        # Check strict validator result
        strict_result = next(r for r in results if r.validator == "strict_validator")
        assert strict_result.score == 0.8
        assert len(strict_result.issues) == 1

    def test_get_validator_info_hooks(self):
        """Test getting validator information through hooks."""
        pm = pluggy.PluginManager("vallm")
        pm.add_hookspecs(VallmSpec)

        validator = MockValidator()
        pm.register(validator)

        # Get validator name
        names = list(pm.hook.get_validator_name())
        assert "mock_validator" in names

        # Get validator tier
        tiers = list(pm.hook.get_validator_tier())
        assert 2 in tiers

    def test_plugin_error_handling(self):
        """Test error handling in plugin system."""
        pm = pluggy.PluginManager("vallm")
        pm.add_hookspecs(VallmSpec)

        class ErrorValidator:
            @hookimpl
            def validate_proposal(self, proposal: Proposal, context: dict) -> ValidationResult:
                raise Exception("Test error")

        validator = ErrorValidator()
        pm.register(validator)

        proposal = Proposal(code="print('hello')", language="python")

        # Should handle errors gracefully
        with pytest.raises(Exception):
            list(pm.hook.validate_proposal(proposal=proposal, context={}))


if __name__ == "__main__":
    pytest.main([__file__])
