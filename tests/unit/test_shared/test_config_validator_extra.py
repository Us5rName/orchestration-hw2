"""Tests for config_validator — pricing, agent skills, and setup example."""

import json

import pytest

from debate.shared.config_validator import (
    ConfigValidationError,
    validate_agent_skills,
    validate_pricing,
)


class TestValidatePricing:
    """Test validate_pricing error cases."""

    def test_missing_pricing_section_raises(self) -> None:
        """No pricing key raises ConfigValidationError."""
        with pytest.raises(ConfigValidationError, match="Missing 'pricing'"):
            validate_pricing({})

    def test_invalid_unit_raises(self) -> None:
        """Unknown pricing unit raises ConfigValidationError."""
        with pytest.raises(ConfigValidationError, match="Invalid pricing unit"):
            validate_pricing({"pricing": {"unit": "per_token"}})

    def test_missing_role_raises(self) -> None:
        """Missing role entry raises ConfigValidationError."""
        with pytest.raises(ConfigValidationError, match="Missing pricing for role"):
            validate_pricing({"pricing": {"unit": "per_1m_tokens"}})

    def test_invalid_pricing_value_raises(self) -> None:
        """Non-numeric pricing value raises ConfigValidationError."""
        pricing = {
            "unit": "per_1m_tokens",
            "judge": {"input": "free", "output": 0.60},
            "pro": {"input": 0.15, "output": 0.60},
            "con": {"input": 0.15, "output": 0.60},
        }
        with pytest.raises(ConfigValidationError, match="Invalid pricing"):
            validate_pricing({"pricing": pricing})


class TestValidateAgentSkills:
    """Test validate_agent_skills error cases."""

    def test_judge_with_debater_skill_raises(self) -> None:
        """Judge assigned a debater skill raises ConfigValidationError."""
        cfg = {"agents": {"judge": {"skills": ["research-analysis"]}}}
        with pytest.raises(ConfigValidationError, match="Judge cannot use debater skills"):
            validate_agent_skills(cfg)

    def test_pro_with_judge_skill_raises(self) -> None:
        """Pro agent assigned a judge skill raises ConfigValidationError."""
        cfg = {"agents": {"pro": {"skills": ["persuasion-scoring"]}}}
        with pytest.raises(ConfigValidationError, match="cannot use judge skills"):
            validate_agent_skills(cfg)

    def test_config_validation_error_is_runtime_error(self) -> None:
        """ConfigValidationError is a RuntimeError."""
        exc = ConfigValidationError("bad config")
        assert isinstance(exc, RuntimeError)


class TestSetupExampleConsistency:
    """Verify setup_example.json satisfies the configuration schema."""

    def test_setup_example_has_pricing_section(self) -> None:
        """setup_example.json must include a pricing section."""
        from debate.shared.paths import PROJECT_ROOT
        example = PROJECT_ROOT / "config" / "setup_example.json"
        data = json.loads(example.read_text(encoding="utf-8"))
        assert "pricing" in data, "setup_example.json is missing the 'pricing' section"

    def test_setup_example_pricing_passes_validation(self) -> None:
        """Pricing section in setup_example.json must pass validate_pricing."""
        from debate.shared.paths import PROJECT_ROOT
        example = PROJECT_ROOT / "config" / "setup_example.json"
        data = json.loads(example.read_text(encoding="utf-8"))
        validate_pricing(data)  # must not raise
