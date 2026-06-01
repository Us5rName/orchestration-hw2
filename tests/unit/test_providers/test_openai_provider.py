"""Tests for OpenAIProvider."""

from unittest.mock import MagicMock, patch

from debate.providers.openai_provider import OpenAIProvider


def _make_provider() -> OpenAIProvider:
    """Helper to create a provider inside a patched context."""
    return OpenAIProvider(
        model="gpt-4o-mini",
        base_url=None,
        temperature=0.7,
        timeout=30.0,
        api_key="test-key",
    )


class TestOpenAIProviderInit:
    """Test OpenAIProvider initialization."""

    @patch("debate.providers.openai_provider.OpenAI")
    def test_inherits_from_base(self, mock_openai: MagicMock) -> None:
        """Provider inherits LLMProvider attributes."""
        mock_openai.return_value = MagicMock()
        prov = _make_provider()
        assert prov.model == "gpt-4o-mini"
        assert prov.temperature == 0.7
        assert prov.timeout == 30.0

    @patch("debate.providers.openai_provider.OpenAI")
    def test_custom_base_url(self, mock_openai: MagicMock) -> None:
        """Custom base URL is stored."""
        mock_openai.return_value = MagicMock()
        prov = OpenAIProvider(
            model="gpt-4o-mini",
            base_url="http://localhost:8080/v1",
            temperature=0.5,
            timeout=10.0,
            api_key="test",
        )
        assert prov.base_url == "http://localhost:8080/v1"


class TestOpenAIProviderChat:
    """Test OpenAI chat."""

    @patch("debate.providers.openai_provider.OpenAI")
    def test_chat_returns_content(self, mock_openai: MagicMock) -> None:
        """Chat returns assistant message content."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Hello!"
        mock_client.chat.completions.create.return_value = mock_response

        prov = _make_provider()
        result = prov.chat([{"role": "user", "content": "hi"}])
        assert result == "Hello!"

    @patch("debate.providers.openai_provider.OpenAI")
    def test_chat_passes_params(self, mock_openai: MagicMock) -> None:
        """Chat passes model, messages, temperature to API."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "ok"
        mock_client.chat.completions.create.return_value = mock_response

        prov = _make_provider()
        prov.chat([{"role": "user", "content": "test"}])
        call_kwargs = mock_client.chat.completions.create.call_args
        assert call_kwargs.kwargs["model"] == "gpt-4o-mini"
        assert call_kwargs.kwargs["temperature"] == 0.7
