"""AgentBase — abstract base for all debate agents.

Input: provider (LLMProvider), model, temperature, timeout
Output: think(prompt) -> dict with agent role, content, round
Setup: subclasses implement role and _build_system_prompt()
"""

import json
from abc import ABC, abstractmethod

from ..providers.base_provider import LLMProvider


class AgentBase(ABC):
    """
    Input: provider (LLMProvider), model (str), temperature (float),
           timeout (float)
    Output: think(prompt: str) -> dict with agent, content, round
    Setup: subclasses define role and _build_system_prompt()
    """

    def __init__(
        self,
        provider: LLMProvider,
        model: str,
        temperature: float,
        timeout: float,
    ) -> None:
        """Initialize agent with LLM provider and settings.

        Args:
            provider: The LLM provider to use for chat.
            model: Model name (passed through to provider).
            temperature: Sampling temperature.
            timeout: Request timeout in seconds.
        """
        self.provider = provider
        self.model = model
        self.temperature = temperature
        self.timeout = timeout

    @property
    @abstractmethod
    def role(self) -> str:
        """Return the agent's role identifier."""
        ...  # pragma: no cover

    @abstractmethod
    def _build_system_prompt(self) -> str:
        """Build the system prompt with skill and rules."""
        ...  # pragma: no cover

    def think(self, user_prompt: str) -> dict:
        """Send a prompt to the LLM and return a structured response.

        Args:
            user_prompt: The user/message prompt to send.

        Returns:
            Dict with agent role, content, and metadata.
        """
        messages = [
            {"role": "system", "content": self._build_system_prompt()},
            {"role": "user", "content": user_prompt},
        ]
        raw = self.provider.chat(messages)
        response = self._parse_response(raw)
        response["agent"] = self.role
        return response

    def _parse_response(self, raw: str) -> dict:
        """Parse raw LLM output into a structured dict.

        Args:
            raw: Raw string response from the LLM.

        Returns:
            Dict with at least 'content' key.
        """
        raw = raw.strip()
        if raw.startswith("{"):
            return json.loads(raw)
        return {"content": raw}
