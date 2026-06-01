"""Tests for provider_factory."""

from unittest.mock import MagicMock, patch

import pytest

from debate.sdk.provider_factory import create_provider


@pytest.fixture
def mock_env():
    """Set fake API keys for testing."""
    import os

    os.environ["OPENAI_API_KEY"] = "fake-key"
    os.environ["ANTHROPIC_API_KEY"] = "fake-key"
    os.environ["GOOGLE_GENAI_API_KEY"] = "fake-key"
    yield
    del os.environ["OPENAI_API_KEY"]
    del os.environ["ANTHROPIC_API_KEY"]
    del os.environ["GOOGLE_GENAI_API_KEY"]


class TestCreateProvider:
    """Test provider factory."""

    @patch("debate.sdk.provider_factory.OpenAIProvider")
    def test_creates_openai_provider(self, mock_cls: MagicMock, mock_env: None) -> None:
        """Factory creates OpenAIProvider."""
        mock_cls.return_value = MagicMock(provider_name="openai", model="gpt-4o-mini")
        provider = create_provider("openai", {"model": "gpt-4o-mini"})
        assert provider.provider_name == "openai"
        mock_cls.assert_called_once()

    @patch("debate.sdk.provider_factory.AnthropicProvider")
    def test_creates_anthropic_provider(self, mock_cls: MagicMock, mock_env: None) -> None:
        """Factory creates AnthropicProvider."""
        mock_cls.return_value = MagicMock(provider_name="anthropic", model="claude-3")
        provider = create_provider("anthropic", {"model": "claude-3"})
        assert provider.provider_name == "anthropic"
        mock_cls.assert_called_once()

    @patch("debate.sdk.provider_factory.GeminiProvider")
    def test_creates_gemini_provider(self, mock_cls: MagicMock, mock_env: None) -> None:
        """Factory creates GeminiProvider."""
        mock_cls.return_value = MagicMock(provider_name="gemini", model="gemini-pro")
        provider = create_provider("gemini", {"model": "gemini-pro"})
        assert provider.provider_name == "gemini"
        mock_cls.assert_called_once()

    def test_unsupported_provider_raises(self, mock_env: None) -> None:
        """Unsupported provider type raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported provider"):
            create_provider("unknown", {})

    @patch("debate.sdk.provider_factory.OpenAIProvider")
    def test_default_model(self, mock_cls: MagicMock, mock_env: None) -> None:
        """Factory uses default model when not specified."""
        mock_cls.return_value = MagicMock(model="gpt-4o-mini")
        provider = create_provider("openai", {})
        assert provider.model == "gpt-4o-mini"

    @patch("debate.sdk.provider_factory.OpenAIProvider")
    def test_custom_temperature(self, mock_cls: MagicMock, mock_env: None) -> None:
        """Factory respects custom temperature."""
        mock_cls.return_value = MagicMock(temperature=0.9)
        provider = create_provider("openai", {"temperature": 0.9})
        assert provider.temperature == 0.9
