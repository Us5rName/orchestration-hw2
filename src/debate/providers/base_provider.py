"""LLMProvider — abstract base for all LLM provider implementations.

Input: provider_name, model, base_url, temperature, timeout
Output: chat(messages, tools, tool_executor) -> str response
Setup: subclasses implement _chat() for provider-specific API calls
"""

from abc import ABC, abstractmethod
from collections.abc import Callable


class LLMProvider(ABC):
    """
    Input: provider_name (str), model (str), base_url (str|None),
           temperature (float), timeout (float)
    Output: chat(messages, tools, tool_executor) -> str
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

    def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        tool_executor: Callable[[str, dict], str] | None = None,
    ) -> str:
        """Send messages to the LLM and return the response text.

        Handles the full tool-calling loop internally when tools are provided.

        Args:
            messages: List of {role, content} message dicts.
            tools: Optional list of neutral tool definition dicts.
            tool_executor: Optional callable(tool_name, args) -> result string.

        Returns:
            The assistant's final response as a string.
        """
        return self._chat(messages, self.timeout, tools, tool_executor)

    @abstractmethod
    def _chat(
        self,
        messages: list[dict],
        timeout: float,
        tools: list[dict] | None = None,
        tool_executor: Callable[[str, dict], str] | None = None,
    ) -> str:
        """Provider-specific chat implementation with optional tool loop.

        Args:
            messages: List of {role, content} message dicts.
            timeout: Request timeout in seconds.
            tools: Optional list of neutral tool definition dicts.
            tool_executor: Optional callable(tool_name, args) -> result string.

        Returns:
            The assistant's final response as a string.
        """
        ...  # pragma: no cover — abstract
