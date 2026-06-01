"""AnthropicProvider — Anthropic API implementation of LLMProvider.

Input: model, base_url, temperature, timeout, api_key
Output: chat(messages) -> str response
Setup: inherits LLMProvider; uses anthropic SDK
"""

import os

from anthropic import Anthropic

from .base_provider import LLMProvider


class AnthropicProvider(LLMProvider):
    """
    Input: model (str), base_url (str|None), temperature (float),
           timeout (float), api_key (str|None)
    Output: chat(messages: list[dict]) -> str
    Setup: Anthropic SDK client with optional custom base_url
    """

    def __init__(
        self,
        model: str,
        base_url: str | None,
        temperature: float,
        timeout: float,
        api_key: str | None = None,
    ) -> None:
        """Initialize Anthropic provider.

        Args:
            model: Anthropic model name.
            base_url: Custom endpoint or None for default.
            temperature: Sampling temperature.
            timeout: Request timeout in seconds.
            api_key: API key or None to use env var.
        """
        super().__init__("anthropic", model, base_url, temperature, timeout)
        self._client = Anthropic(
            api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"),
            base_url=base_url,
            timeout=timeout,
        )

    def _chat(self, messages: list[dict], timeout: float) -> str:
        """Call Anthropic messages API.

        Args:
            messages: List of {role, content} dicts.
            timeout: Request timeout (unused, set on client).

        Returns:
            Assistant response text.
        """
        response = self._client.messages.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=4096,
        )
        return response.content[0].text or ""
