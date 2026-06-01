"""Tests for GeminiProvider."""

from unittest.mock import MagicMock, patch

from debate.providers.gemini_provider import GeminiProvider


def _make_provider() -> GeminiProvider:
    """Helper to create a provider inside a patched context."""
    return GeminiProvider(
        model="gemini-1.5-flash",
        base_url=None,
        temperature=0.7,
        timeout=30.0,
        api_key="test-key",
    )


class TestGeminiProviderInit:
    """Test GeminiProvider initialization."""

    @patch("debate.providers.gemini_provider.genai")
    def test_inherits_from_base(self, mock_genai: MagicMock) -> None:
        """Provider inherits LLMProvider attributes."""
        mock_genai.Genai.return_value = MagicMock()
        prov = _make_provider()
        assert prov.model == "gemini-1.5-flash"
        assert prov.temperature == 0.7

    @patch("debate.providers.gemini_provider.genai")
    def test_custom_base_url(self, mock_genai: MagicMock) -> None:
        """Custom base URL is stored."""
        mock_genai.Genai.return_value = MagicMock()
        prov = GeminiProvider(
            model="gemini-1.5-flash",
            base_url="http://localhost:8080",
            temperature=0.5,
            timeout=10.0,
            api_key="test",
        )
        assert prov.base_url == "http://localhost:8080"


class TestGeminiProviderChat:
    """Test Gemini chat."""

    @patch("debate.providers.gemini_provider.genai")
    def test_chat_returns_content(self, mock_genai: MagicMock) -> None:
        """Chat returns candidate text."""
        mock_client = MagicMock()
        mock_genai.Genai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.candidates[0].content.parts[0].text = "Gemini reply"
        mock_client.models.generate_content.return_value = mock_response

        prov = _make_provider()
        result = prov.chat([{"role": "user", "content": "hi"}])
        assert result == "Gemini reply"

    @patch("debate.providers.gemini_provider.genai")
    def test_chat_passes_params(self, mock_genai: MagicMock) -> None:
        """Chat passes model and temperature to API."""
        mock_client = MagicMock()
        mock_genai.Genai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.candidates[0].content.parts[0].text = "ok"
        mock_client.models.generate_content.return_value = mock_response

        prov = _make_provider()
        prov.chat([{"role": "user", "content": "test"}])
        kwargs = mock_client.models.generate_content.call_args.kwargs
        assert kwargs["model"] == "gemini-1.5-flash"
