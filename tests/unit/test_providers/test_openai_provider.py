"""Tests for OpenAIProvider."""

from unittest.mock import MagicMock, patch

from debate.providers.openai_provider import OpenAIProvider
from tests.unit.test_providers.contract import assert_base_attrs


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
        assert_base_attrs(prov, "gpt-4o-mini", 0.7)
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
        mock_response.choices[0].finish_reason = "stop"
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
        mock_response.choices[0].finish_reason = "stop"
        mock_client.chat.completions.create.return_value = mock_response

        prov = _make_provider()
        prov.chat([{"role": "user", "content": "test"}])
        call_kwargs = mock_client.chat.completions.create.call_args
        assert call_kwargs.kwargs["model"] == "gpt-4o-mini"
        assert call_kwargs.kwargs["temperature"] == 0.7


class TestOpenAIProviderToolCalling:
    """Test OpenAI native tool call loop."""

    @patch("debate.providers.openai_provider.OpenAI")
    def test_tool_call_executes_and_continues(self, mock_openai: MagicMock) -> None:
        """Provider executes tool and makes a second API call with result."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        tool_resp = MagicMock()
        tool_resp.choices[0].finish_reason = "tool_calls"
        tool_resp.choices[0].message.content = None
        tool_resp.choices[0].message.tool_calls[0].id = "call_1"
        tool_resp.choices[0].message.tool_calls[0].function.name = "search"
        tool_resp.choices[0].message.tool_calls[0].function.arguments = '{"query": "test"}'

        final_resp = MagicMock()
        final_resp.choices[0].finish_reason = "stop"
        final_resp.choices[0].message.content = "Final answer"

        mock_client.chat.completions.create.side_effect = [tool_resp, final_resp]

        prov = _make_provider()
        executor = MagicMock(return_value="search results")
        tools = [{"name": "search", "description": "...", "parameters": {
            "type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]
        }}]
        result = prov.chat([{"role": "user", "content": "hi"}], tools, executor)

        assert result == "Final answer"
        executor.assert_called_once_with("search", {"query": "test"})
        assert mock_client.chat.completions.create.call_count == 2

    @patch("debate.providers.openai_provider.OpenAI")
    def test_no_tools_skips_loop(self, mock_openai: MagicMock) -> None:
        """Without tools, provider returns first response directly."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices[0].finish_reason = "stop"
        mock_response.choices[0].message.content = "Direct reply"
        mock_client.chat.completions.create.return_value = mock_response

        prov = _make_provider()
        result = prov.chat([{"role": "user", "content": "hi"}])
        assert result == "Direct reply"
        assert mock_client.chat.completions.create.call_count == 1


