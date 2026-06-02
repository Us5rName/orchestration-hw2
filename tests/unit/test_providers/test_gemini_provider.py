"""Tests for GeminiProvider."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from debate.providers.gemini_provider import GeminiProvider
from tests.unit.test_providers.contract import (
    assert_base_attrs,
    assert_usage_recorded,
    assert_usage_zero,
)


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
        assert_base_attrs(prov, "gemini-1.5-flash", 0.7)

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
        mock_response.candidates[0].content.parts[0].function_call = None
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
        mock_response.candidates[0].content.parts[0].function_call = None
        mock_client.models.generate_content.return_value = mock_response

        prov = _make_provider()
        prov.chat([{"role": "user", "content": "test"}])
        kwargs = mock_client.models.generate_content.call_args.kwargs
        assert kwargs["model"] == "gemini-1.5-flash"


class TestGeminiProviderToolCalling:
    """Test Gemini native tool call loop."""

    @patch("debate.providers.gemini_provider.genai")
    def test_tool_call_executes_and_continues(self, mock_genai: MagicMock) -> None:
        """Provider executes tool and makes a second API call with result."""
        mock_client = MagicMock()
        mock_genai.Genai.return_value = mock_client

        fc = MagicMock()
        fc.name = "search"
        fc.args = {"query": "test"}

        # Access chain first so MagicMock caches and returns the same child mock
        tool_resp = MagicMock()
        tool_resp.candidates[0].content.parts[0].function_call = fc
        tool_resp.candidates[0].content.parts[0].text = None

        final_resp = MagicMock()
        final_resp.candidates[0].content.parts[0].function_call = None
        final_resp.candidates[0].content.parts[0].text = "Final answer"

        mock_client.models.generate_content.side_effect = [tool_resp, final_resp]

        prov = _make_provider()
        executor = MagicMock(return_value="search results")
        tools = [{"name": "search", "description": "...", "parameters": {
            "type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]
        }}]
        result = prov.chat([{"role": "user", "content": "hi"}], tools, executor)

        assert result == "Final answer"
        executor.assert_called_once_with("search", {"query": "test"})
        assert mock_client.models.generate_content.call_count == 2

    @patch("debate.providers.gemini_provider.genai")
    def test_no_tools_skips_loop(self, mock_genai: MagicMock) -> None:
        """Without tools, provider returns first response directly."""
        mock_client = MagicMock()
        mock_genai.Genai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.candidates[0].content.parts[0].function_call = None
        mock_response.candidates[0].content.parts[0].text = "Direct reply"
        mock_client.models.generate_content.return_value = mock_response

        prov = _make_provider()
        result = prov.chat([{"role": "user", "content": "hi"}])
        assert result == "Direct reply"


class TestGeminiProviderUsageTracking:
    """Test usage_metadata recording branches."""

    def _simple_resp(self, mock_client: MagicMock) -> MagicMock:
        resp = MagicMock()
        resp.candidates[0].content.parts[0].text = "ok"
        resp.candidates[0].content.parts[0].function_call = None
        mock_client.models.generate_content.return_value = resp
        return resp

    @patch("debate.providers.gemini_provider.genai")
    def test_usage_metadata_none_leaves_counters_zero(self, mock_genai: MagicMock) -> None:
        """None usage_metadata records nothing."""
        mock_client = MagicMock()
        mock_genai.Genai.return_value = mock_client
        resp = self._simple_resp(mock_client)
        resp.usage_metadata = None
        prov = _make_provider()
        prov.chat([{"role": "user", "content": "hi"}])
        assert_usage_zero(prov)

    @patch("debate.providers.gemini_provider.genai")
    def test_usage_metadata_dict_records_tokens(self, mock_genai: MagicMock) -> None:
        """Dict usage_metadata records prompt and candidates tokens."""
        mock_client = MagicMock()
        mock_genai.Genai.return_value = mock_client
        resp = self._simple_resp(mock_client)
        resp.usage_metadata = {"prompt_token_count": 10, "candidates_token_count": 5}
        prov = _make_provider()
        prov.chat([{"role": "user", "content": "hi"}])
        assert_usage_recorded(prov, 10, 5)

    @patch("debate.providers.gemini_provider.genai")
    def test_usage_metadata_typed_object_records_tokens(self, mock_genai: MagicMock) -> None:
        """Typed usage_metadata with int attrs records tokens."""
        mock_client = MagicMock()
        mock_genai.Genai.return_value = mock_client
        resp = self._simple_resp(mock_client)
        resp.usage_metadata = SimpleNamespace(prompt_token_count=20, candidates_token_count=10)
        prov = _make_provider()
        prov.chat([{"role": "user", "content": "hi"}])
        assert_usage_recorded(prov, 20, 10)
