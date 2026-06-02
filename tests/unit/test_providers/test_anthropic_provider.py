"""Tests for AnthropicProvider."""

from unittest.mock import MagicMock, patch

from debate.providers.anthropic_provider import AnthropicProvider


def _make_provider() -> AnthropicProvider:
    """Helper to create a provider inside a patched context."""
    return AnthropicProvider(
        model="claude-3-haiku-20240307",
        base_url=None,
        temperature=0.7,
        timeout=30.0,
        api_key="test-key",
    )


class TestAnthropicProviderInit:
    """Test AnthropicProvider initialization."""

    @patch("debate.providers.anthropic_provider.Anthropic")
    def test_inherits_from_base(self, mock_cls: MagicMock) -> None:
        """Provider inherits LLMProvider attributes."""
        mock_cls.return_value = MagicMock()
        prov = _make_provider()
        assert prov.model == "claude-3-haiku-20240307"
        assert prov.temperature == 0.7

    @patch("debate.providers.anthropic_provider.Anthropic")
    def test_custom_base_url(self, mock_cls: MagicMock) -> None:
        """Custom base URL is stored."""
        mock_cls.return_value = MagicMock()
        prov = AnthropicProvider(
            model="claude-3-haiku-20240307",
            base_url="http://localhost:8080",
            temperature=0.5,
            timeout=10.0,
            api_key="test",
        )
        assert prov.base_url == "http://localhost:8080"


class TestAnthropicProviderChat:
    """Test Anthropic chat."""

    @patch("debate.providers.anthropic_provider.Anthropic")
    def test_chat_returns_content(self, mock_cls: MagicMock) -> None:
        """Chat returns assistant text."""
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_msg = MagicMock()
        mock_msg.stop_reason = "end_turn"
        mock_msg.content[0].text = "Anthropic reply"
        mock_client.messages.create.return_value = mock_msg

        prov = _make_provider()
        result = prov.chat([{"role": "user", "content": "hi"}])
        assert result == "Anthropic reply"

    @patch("debate.providers.anthropic_provider.Anthropic")
    def test_chat_passes_params(self, mock_cls: MagicMock) -> None:
        """Chat passes model and temperature to API."""
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_msg = MagicMock()
        mock_msg.stop_reason = "end_turn"
        mock_msg.content[0].text = "ok"
        mock_client.messages.create.return_value = mock_msg

        prov = _make_provider()
        prov.chat([{"role": "user", "content": "test"}])
        kwargs = mock_client.messages.create.call_args.kwargs
        assert kwargs["model"] == "claude-3-haiku-20240307"
        assert kwargs["temperature"] == 0.7


class TestAnthropicProviderToolCalling:
    """Test Anthropic native tool call loop."""

    @patch("debate.providers.anthropic_provider.Anthropic")
    def test_tool_call_executes_and_continues(self, mock_cls: MagicMock) -> None:
        """Provider executes tool and makes a second API call with result."""
        mock_client = MagicMock()
        mock_cls.return_value = mock_client

        tool_block = MagicMock()
        tool_block.type = "tool_use"
        tool_block.id = "tu_1"
        tool_block.name = "search"
        tool_block.input = {"query": "test"}

        tool_resp = MagicMock()
        tool_resp.stop_reason = "tool_use"
        tool_resp.content = [tool_block]

        final_resp = MagicMock()
        final_resp.stop_reason = "end_turn"
        final_resp.content[0].text = "Final answer"

        mock_client.messages.create.side_effect = [tool_resp, final_resp]

        prov = _make_provider()
        executor = MagicMock(return_value="search results")
        tools = [{"name": "search", "description": "...", "parameters": {
            "type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]
        }}]
        result = prov.chat([{"role": "user", "content": "hi"}], tools, executor)

        assert result == "Final answer"
        executor.assert_called_once_with("search", {"query": "test"})
        assert mock_client.messages.create.call_count == 2

    @patch("debate.providers.anthropic_provider.Anthropic")
    def test_no_tools_skips_loop(self, mock_cls: MagicMock) -> None:
        """Without tools, provider returns first response directly."""
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_msg = MagicMock()
        mock_msg.stop_reason = "end_turn"
        mock_msg.content[0].text = "Direct reply"
        mock_client.messages.create.return_value = mock_msg

        prov = _make_provider()
        result = prov.chat([{"role": "user", "content": "hi"}])
        assert result == "Direct reply"
        assert mock_client.messages.create.call_count == 1
