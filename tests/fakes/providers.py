"""FakeProvider — a scripted LLM provider for the test harness.

Returns responses from a preset list in sequence.
When the list is exhausted, returns an empty string.
Tracks no usage (get_usage always returns zeros), which is fine for
tests that verify orchestration flow rather than cost accounting.
"""

from collections.abc import Callable

from debate.providers.base_provider import LLMProvider


class FakeProvider(LLMProvider):
    """Scripted provider that returns preset string responses in sequence.

    Prefer this over a bare MagicMock when the test cares about the
    provider contract (model, temperature, timeout, get_usage) rather
    than asserting call counts.
    """

    def __init__(self, responses: list[str] | None = None) -> None:
        super().__init__(
            provider_name="fake",
            model="fake-model",
            base_url=None,
            temperature=0.7,
            timeout=30.0,
        )
        self._responses = list(responses or ['""'])
        self._idx = 0

    def _chat(
        self,
        messages: list[dict],
        timeout: float,
        tools: list[dict] | None = None,
        tool_executor: Callable | None = None,
    ) -> str:
        if self._idx < len(self._responses):
            resp = self._responses[self._idx]
            self._idx += 1
            return resp
        return '""'
