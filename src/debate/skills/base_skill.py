"""AgentSkill — abstract base for all agent skill implementations.

Input: none at instantiation
Output: get_instructions() -> str, get_tool_definition() -> dict|None,
        search(query) -> list[str]
Setup: subclasses define name, get_instructions(), optionally get_tool_definition()
"""

from abc import ABC, abstractmethod


class AgentSkill(ABC):
    """
    Input: none
    Output: get_instructions() -> str prompt injection text
            get_tool_definition() -> dict | None (neutral tool schema)
            search(query: str) -> list[str] (default empty)
    Setup: subclasses define role-specific instructions and optional tools
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique kebab-case skill identifier."""
        ...  # pragma: no cover

    @abstractmethod
    def get_instructions(self) -> str:
        """Return skill-specific system prompt injection text.

        Returns:
            Instruction text to inject into the agent's system prompt.
        """
        ...  # pragma: no cover

    def get_tool_definition(self) -> dict | None:
        """Return neutral tool schema if this skill exposes a tool.

        Returns:
            Dict with name, description, parameters keys, or None.
        """
        return None

    def search(self, query: str) -> list[str]:
        """Execute a search and return formatted citation strings.

        Args:
            query: Search query string.

        Returns:
            List of formatted citation strings; empty by default.
        """
        return []
