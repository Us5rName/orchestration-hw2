"""OpenAIProvider — OpenAI API implementation of LLMProvider.

Input: model, base_url, temperature, timeout, api_key
Output: chat(messages) -> str response
Setup: inherits LLMProvider; uses openai SDK
"""

import os

from openai import OpenAI

from .base_provider import LLMProvider


class OpenAIProvider(LLMProvider):
    """
    Input: model (str), base_url (str|None), temperature (float),
           timeout (float), api_key (str|None)
    Output: chat(messages: list[dict]) -> str
    Setup: OpenAI SDK client with optional custom base_url
    """

    def __init__(
        self,
        model: str,
        base_url: str | None,
        temperature: float,
        timeout: float,
        api_key: str | None = None,
    ) -> None:
        """Initialize OpenAI provider.

        Args:
            model: OpenAI model name.
            base_url: Custom endpoint or None for default.
            temperature: Sampling temperature.
            timeout: Request timeout in seconds.
            api_key: API key or None to use env var.
        """
        super().__init__("openai", model, base_url, temperature, timeout)
        self._client = OpenAI(
            api_key=api_key or os.environ.get("OPENAI_API_KEY"),
            base_url=base_url,
            timeout=timeout,
        )

    def _chat(self, messages: list[dict], timeout: float) -> str:
        """Call OpenAI chat completions API.

        Args:
            messages: List of {role, content} dicts.
            timeout: Request timeout (unused, set on client).

        Returns:
            Assistant response text.
        """
        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
        )
        return response.choices[0].message.content or ""
