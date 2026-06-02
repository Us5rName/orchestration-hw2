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
        self._usage: dict[str, int] = {"input_tokens": 0, "output_tokens": 0}

    def get_usage(self) -> dict[str, int]:
        """Return cumulative token usage for this provider instance.

        Returns:
            Dict with input_tokens and output_tokens counts.
        """
        return dict(self._usage)

    def _record_usage(self, input_tokens: int, output_tokens: int) -> None:
        """Accumulate a successful API call's token counts.

        Args:
            input_tokens: Prompt tokens reported by the API.
            output_tokens: Completion tokens reported by the API.
        """
        self._usage["input_tokens"] += input_tokens
        self._usage["output_tokens"] += output_tokens

    def _record_unavailable_usage(self) -> None:
        """Mark that the last API call returned no usage metadata.

        Intentional no-op: cumulative counters are left unchanged so callers
        can detect unavailable usage via a zero delta on get_usage().
        Subclasses must call this when the API does not return usage metadata.
        """
        return  # concrete no-op — not abstract

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
