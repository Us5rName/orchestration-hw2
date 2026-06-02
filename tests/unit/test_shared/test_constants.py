"""Tests for constants module."""

from debate import constants


class TestConstants:
    """Test that all constants are defined."""

    def test_role_constants(self) -> None:
        """Role constants exist."""
        assert constants.ROLE_JUDGE == "judge"
        assert constants.ROLE_PRO == "pro"
        assert constants.ROLE_CON == "con"

    def test_message_type_constants(self) -> None:
        """Message type constants exist."""
        assert constants.MSG_TYPE_ARGUMENT == "argument"
        assert constants.MSG_TYPE_VERDICT == "verdict"
        assert constants.MSG_TYPE_RULE_ENFORCEMENT == "rule_enforcement"

    def test_provider_constants(self) -> None:
        """Provider constants exist."""
        assert constants.PROVIDER_OPENAI == "openai"
        assert constants.PROVIDER_ANTHROPIC == "anthropic"
        assert constants.PROVIDER_GEMINI == "gemini"

    def test_path_constants_not_in_constants_module(self) -> None:
        """Path constants live in shared.paths, not constants."""
        assert not hasattr(constants, "DEFAULT_CONFIG_PATH")
        assert not hasattr(constants, "DEFAULT_RATE_LIMITS_PATH")
        assert not hasattr(constants, "DEFAULT_LOGGING_PATH")
