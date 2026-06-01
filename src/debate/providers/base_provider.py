"""LLMProvider — abstract base for all LLM provider implementations.

Input: provider_name, model, base_url, temperature, timeout
Output: chat(messages) -> str response
Setup: subclasses implement _chat() for provider-specific API calls
"""

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """
    Input: provider_name (str), model (str), base_url (str|None),
           temperature (float), timeout (float)
    Output: chat(messages: list[dict]) -> str
    Setup: subclasses override _chat() for provider API
    """

    def __init__(
        self,
        provider_name: str,
        model: str,
        base_url: str | None,
        temperature: float,
        timeout: float,
    ) -> None:
        """Initialize provider with common settings.

        Args:
            provider_name: Identifier (openai, anthropic, gemini).
            model: Model name to use.
            base_url: Custom API endpoint or None for default.
            temperature: Sampling temperature.
            timeout: Request timeout in seconds.
        """
        self.provider_name = provider_name
        self.model = model
        self.base_url = base_url
        self.temperature = temperature
        self.timeout = timeout

    def chat(self, messages: list[dict]) -> str:
        """Send messages to the LLM and return the response text.

        Args:
            messages: List of {role, content} message dicts.

        Returns:
            The assistant's response as a string.
        """
        return self._chat(messages, self.timeout)

    @abstractmethod
    def _chat(self, messages: list[dict], timeout: float) -> str:
        """Provider-specific chat implementation.

        Args:
            messages: List of {role, content} message dicts.
            timeout: Request timeout in seconds.

        Returns:
            The assistant's response as a string.
        """
        ...  # pragma: no cover — abstract
