"""OpenAIProvider — OpenAI API implementation of LLMProvider.

Input: model, base_url, temperature, timeout, api_key
Output: chat(messages, tools, tool_executor) -> str response
Setup: inherits LLMProvider; uses openai SDK; handles tool call loop natively
"""

import json
import os
from collections.abc import Callable

from openai import OpenAI

from .base_provider import LLMProvider


class OpenAIProvider(LLMProvider):
    """
    Input: model (str), base_url (str|None), temperature (float),
           timeout (float), api_key (str|None)
    Output: chat(messages, tools, tool_executor) -> str
    Setup: OpenAI SDK client; translates neutral tool defs to OpenAI format
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

    def _chat(
        self,
        messages: list[dict],
        timeout: float,
        tools: list[dict] | None = None,
        tool_executor: Callable[[str, dict], str] | None = None,
    ) -> str:
        """Call OpenAI chat completions API with optional tool loop.

        Args:
            messages: List of {role, content} dicts.
            timeout: Request timeout (set on client at init).
            tools: Optional neutral tool definitions.
            tool_executor: Optional callable for tool execution.

        Returns:
            Final assistant response text.
        """
        current_messages = list(messages)
        openai_tools = [{"type": "function", "function": t} for t in (tools or [])]

        while True:
            kwargs: dict = {
                "model": self.model,
                "messages": current_messages,
                "temperature": self.temperature,
            }
            if openai_tools:
                kwargs["tools"] = openai_tools

            response = self._client.chat.completions.create(**kwargs)
            usage = response.usage
            if usage is not None:
                pt = getattr(usage, "prompt_tokens", 0)
                ct = getattr(usage, "completion_tokens", 0)
                if isinstance(pt, int):
                    self._usage["input_tokens"] += pt
                if isinstance(ct, int):
                    self._usage["output_tokens"] += ct
            msg = response.choices[0].message

            if response.choices[0].finish_reason != "tool_calls" or not tool_executor:
                return msg.content or ""

            tool_call = msg.tool_calls[0]
            args = json.loads(tool_call.function.arguments)
            result = tool_executor(tool_call.function.name, args)

            current_messages.append({
                "role": "assistant",
                "content": msg.content,
                "tool_calls": [{
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments,
                    },
                }],
            })
            current_messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_call.function.name,
                "content": str(result),
            })
