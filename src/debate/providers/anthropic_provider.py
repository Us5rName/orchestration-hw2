"""AnthropicProvider — Anthropic API implementation of LLMProvider.

Input: model, base_url, temperature, timeout, api_key
Output: chat(messages, tools, tool_executor) -> str response
Setup: inherits LLMProvider; uses anthropic SDK; handles tool call loop natively
"""

import os
from collections.abc import Callable

from anthropic import Anthropic

from .base_provider import LLMProvider


class AnthropicProvider(LLMProvider):
    """
    Input: model (str), base_url (str|None), temperature (float),
           timeout (float), api_key (str|None)
    Output: chat(messages, tools, tool_executor) -> str
    Setup: Anthropic SDK client; translates neutral tool defs to Anthropic format
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

    def _chat(
        self,
        messages: list[dict],
        timeout: float,
        tools: list[dict] | None = None,
        tool_executor: Callable[[str, dict], str] | None = None,
    ) -> str:
        """Call Anthropic messages API with optional tool loop.

        Args:
            messages: List of {role, content} dicts.
            timeout: Request timeout (set on client at init).
            tools: Optional neutral tool definitions.
            tool_executor: Optional callable for tool execution.

        Returns:
            Final assistant response text.
        """
        current_messages = list(messages)
        anthropic_tools = [
            {"name": t["name"], "description": t["description"], "input_schema": t["parameters"]}
            for t in (tools or [])
        ]

        while True:
            kwargs: dict = {
                "model": self.model,
                "messages": current_messages,
                "temperature": self.temperature,
                "max_tokens": 4096,
            }
            if anthropic_tools:
                kwargs["tools"] = anthropic_tools

            response = self._client.messages.create(**kwargs)

            if response.stop_reason != "tool_use" or not tool_executor:
                return response.content[0].text or ""

            tool_block = next(b for b in response.content if b.type == "tool_use")
            result = tool_executor(tool_block.name, tool_block.input)

            current_messages.append({
                "role": "assistant",
                "content": [
                    {"type": "tool_use", "id": tool_block.id,
                     "name": tool_block.name, "input": tool_block.input}
                ],
            })
            current_messages.append({
                "role": "user",
                "content": [
                    {"type": "tool_result", "tool_use_id": tool_block.id, "content": str(result)}
                ],
            })
