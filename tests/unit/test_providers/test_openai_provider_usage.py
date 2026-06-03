"""Tests for OpenAIProvider usage tracking."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from debate.providers.openai_provider import OpenAIProvider
from tests.unit.test_providers.contract import assert_usage_recorded, assert_usage_zero


def _make_provider() -> OpenAIProvider:
    return OpenAIProvider(
        model="gpt-4o-mini",
        base_url=None,
        temperature=0.7,
        timeout=30.0,
        api_key="test-key",
    )


class TestOpenAIProviderUsageTracking:
    """Test usage recording branches."""

    def _simple_resp(self, mock_client: MagicMock) -> MagicMock:
        resp = MagicMock()
        resp.choices[0].finish_reason = "stop"
        resp.choices[0].message.content = "ok"
        mock_client.chat.completions.create.return_value = resp
        return resp

    @patch("debate.providers.openai_provider.OpenAI")
    def test_usage_none_leaves_counters_zero(self, mock_openai: MagicMock) -> None:
        """None usage records nothing."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        resp = self._simple_resp(mock_client)
        resp.usage = None
        prov = _make_provider()
        prov.chat([{"role": "user", "content": "hi"}])
        assert_usage_zero(prov)

    @patch("debate.providers.openai_provider.OpenAI")
    def test_usage_dict_records_tokens(self, mock_openai: MagicMock) -> None:
        """Dict usage records prompt and completion tokens."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        resp = self._simple_resp(mock_client)
        resp.usage = {"prompt_tokens": 10, "completion_tokens": 5}
        prov = _make_provider()
        prov.chat([{"role": "user", "content": "hi"}])
        assert_usage_recorded(prov, 10, 5)

    @patch("debate.providers.openai_provider.OpenAI")
    def test_usage_typed_object_records_tokens(self, mock_openai: MagicMock) -> None:
        """Typed usage object with int attrs records tokens."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        resp = self._simple_resp(mock_client)
        resp.usage = SimpleNamespace(prompt_tokens=20, completion_tokens=10)
        prov = _make_provider()
        prov.chat([{"role": "user", "content": "hi"}])
        assert_usage_recorded(prov, 20, 10)
