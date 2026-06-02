"""GeminiProvider — Google Gemini API implementation of LLMProvider.

Input: model, base_url, temperature, timeout, api_key
Output: chat(messages, tools, tool_executor) -> str response
Setup: inherits LLMProvider; uses google-genai SDK; handles tool call loop natively
"""

import os
from collections.abc import Callable

from google import genai

from .base_provider import LLMProvider


class GeminiProvider(LLMProvider):
    """
    Input: model (str), base_url (str|None), temperature (float),
           timeout (float), api_key (str|None)
    Output: chat(messages, tools, tool_executor) -> str
    Setup: Google Genai SDK client; converts neutral tool defs to Gemini format
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

    def _chat(
        self,
        messages: list[dict],
        timeout: float,
        tools: list[dict] | None = None,
        tool_executor: Callable[[str, dict], str] | None = None,
    ) -> str:
        """Call Gemini generate_content API with optional tool loop.

        Args:
            messages: List of {role, content} dicts.
            timeout: Request timeout (set on client at init).
            tools: Optional neutral tool definitions.
            tool_executor: Optional callable for tool execution.

        Returns:
            Final assistant response text.
        """
        current_contents = [{"parts": [{"text": m["content"]}]} for m in messages]
        config: dict = {"temperature": self.temperature}
        if tools:
            config["tools"] = [self._build_gemini_tools(tools)]

        while True:
            response = self._client.models.generate_content(
                model=self.model,
                contents=current_contents,
                config=config,
            )
            part = response.candidates[0].content.parts[0]
            fc = getattr(part, "function_call", None)

            if not fc or not tool_executor:
                return part.text or ""

            result = tool_executor(fc.name, dict(fc.args))
            current_contents.append(
                {"role": "model", "parts": [{"function_call": {"name": fc.name, "args": dict(fc.args)}}]}
            )
            current_contents.append(
                {"parts": [{"function_response": {"name": fc.name, "response": {"result": result}}}]}
            )

    def _build_gemini_tools(self, tools: list[dict]) -> dict:
        """Convert neutral tool definitions to Gemini function_declarations format.

        Args:
            tools: List of neutral tool defs with name, description, parameters.

        Returns:
            Dict with function_declarations in Gemini format.
        """
        declarations = []
        for t in tools:
            props = {
                k: {"type": v["type"].upper()}
                for k, v in t["parameters"]["properties"].items()
            }
            declarations.append({
                "name": t["name"],
                "description": t["description"],
                "parameters": {
                    "type": "OBJECT",
                    "properties": props,
                    "required": t["parameters"].get("required", []),
                },
            })
        return {"function_declarations": declarations}
