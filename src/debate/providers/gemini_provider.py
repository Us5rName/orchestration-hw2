"""GeminiProvider — Google Gemini API implementation of LLMProvider.

Input: model, base_url, temperature, timeout, api_key
Output: chat(messages) -> str response
Setup: inherits LLMProvider; uses google-genai SDK
"""

import os

from google import genai

from .base_provider import LLMProvider


class GeminiProvider(LLMProvider):
    """
    Input: model (str), base_url (str|None), temperature (float),
           timeout (float), api_key (str|None)
    Output: chat(messages: list[dict]) -> str
    Setup: Google Genai SDK client with optional custom base_url
    """

    def __init__(
        self,
        model: str,
        base_url: str | None,
        temperature: float,
        timeout: float,
        api_key: str | None = None,
    ) -> None:
        """Initialize Gemini provider.

        Args:
            model: Gemini model name.
            base_url: Custom endpoint or None for default.
            temperature: Sampling temperature.
            timeout: Request timeout in seconds.
            api_key: API key or None to use env var.
        """
        super().__init__("gemini", model, base_url, temperature, timeout)
        self._client = genai.Genai(
            api_key=api_key or os.environ.get("GOOGLE_GENAI_API_KEY"),
            http_options={"timeout": int(timeout * 1000)},
        )

    def _chat(self, messages: list[dict], timeout: float) -> str:
        """Call Gemini generate_content API.

        Args:
            messages: List of {role, content} dicts.
            timeout: Request timeout (unused, set on client).

        Returns:
            Assistant response text.
        """
        response = self._client.models.generate_content(
            model=self.model,
            contents={"parts": [{"text": m["content"]} for m in messages]},
            config={"temperature": self.temperature},
        )
        return response.candidates[0].content.parts[0].text or ""
