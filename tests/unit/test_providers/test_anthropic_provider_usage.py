"""Tests for AnthropicProvider usage tracking."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from debate.providers.anthropic_provider import AnthropicProvider
from tests.unit.test_providers.contract import assert_usage_recorded, assert_usage_zero


def _make_provider() -> AnthropicProvider:
    return AnthropicProvider(
        model="claude-3-haiku-20240307",
        base_url=None,
        temperature=0.7,
        timeout=30.0,
        api_key="test-key",
    )


class TestAnthropicProviderUsageTracking:
    """Test usage recording branches."""

    def _simple_resp(self, mock_client: MagicMock) -> MagicMock:
        resp = MagicMock()
        resp.stop_reason = "end_turn"
        resp.content[0].text = "ok"
        mock_client.messages.create.return_value = resp
        return resp

    @patch("debate.providers.anthropic_provider.Anthropic")
    def test_usage_none_leaves_counters_zero(self, mock_cls: MagicMock) -> None:
        """None usage records nothing."""
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        resp = self._simple_resp(mock_client)
        resp.usage = None
        prov = _make_provider()
        prov.chat([{"role": "user", "content": "hi"}])
        assert_usage_zero(prov)

    @patch("debate.providers.anthropic_provider.Anthropic")
    def test_usage_dict_records_tokens(self, mock_cls: MagicMock) -> None:
        """Dict usage records input and output tokens."""
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        resp = self._simple_resp(mock_client)
        resp.usage = {"input_tokens": 10, "output_tokens": 5}
        prov = _make_provider()
        prov.chat([{"role": "user", "content": "hi"}])
        assert_usage_recorded(prov, 10, 5)

    @patch("debate.providers.anthropic_provider.Anthropic")
    def test_usage_typed_object_records_tokens(self, mock_cls: MagicMock) -> None:
        """Typed usage object with int attrs records tokens."""
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        resp = self._simple_resp(mock_client)
        resp.usage = SimpleNamespace(input_tokens=20, output_tokens=10)
        prov = _make_provider()
        prov.chat([{"role": "user", "content": "hi"}])
        assert_usage_recorded(prov, 20, 10)
