"""Tests for LLMProvider base class."""

import pytest

from debate.providers.base_provider import LLMProvider


class DummyProvider(LLMProvider):
    """Concrete subclass for testing abstract base."""

    def _chat(self, messages: list[dict], timeout: float) -> str:
        return "dummy response"


@pytest.fixture
def provider() -> DummyProvider:
    """Return a dummy provider."""
    return DummyProvider(
        provider_name="dummy",
        model="test-model",
        base_url=None,
        temperature=0.7,
        timeout=30.0,
    )


class TestLLMProviderInit:
    """Test provider initialization."""

    def test_sets_model(self, provider: DummyProvider) -> None:
        """Provider stores model name."""
        assert provider.model == "test-model"

    def test_sets_temperature(self, provider: DummyProvider) -> None:
        """Provider stores temperature."""
        assert provider.temperature == 0.7

    def test_sets_timeout(self, provider: DummyProvider) -> None:
        """Provider stores timeout."""
        assert provider.timeout == 30.0

    def test_abstract_cannot_instantiate(self) -> None:
        """LLMProvider cannot be instantiated directly."""
        with pytest.raises(TypeError):
            LLMProvider()  # type: ignore[abstract]


class TestLLMProviderChat:
    """Test chat method."""

    def test_chat_returns_response(self, provider: DummyProvider) -> None:
        """Chat returns the provider response."""
        result = provider.chat([{"role": "user", "content": "hello"}])
        assert result == "dummy response"

    def test_chat_passes_messages(self) -> None:
        """Chat passes messages to _chat implementation."""
        received = []

        class CaptureProvider(LLMProvider):
            def _chat(self, msgs: list[dict], timeout: float) -> str:
                received.extend(msgs)
                return "ok"

        prov = CaptureProvider("cap", "m", None, 0.5, 10.0)
        msgs = [{"role": "system", "content": "be nice"}]
        prov.chat(msgs)
        assert received == msgs
