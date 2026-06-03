"""Tests for GeminiProvider usage tracking."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from debate.providers.gemini_provider import GeminiProvider
from tests.unit.test_providers.contract import assert_usage_recorded, assert_usage_zero


def _make_provider() -> GeminiProvider:
    return GeminiProvider(
        model="gemini-1.5-flash",
        base_url=None,
        temperature=0.7,
        timeout=30.0,
        api_key="test-key",
    )


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
