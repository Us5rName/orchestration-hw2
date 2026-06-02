"""AgentBase — abstract base for all debate agents.

Input: provider (LLMProvider), model, temperature, timeout, skills
Output: think(prompt) -> dict with agent role, content, round
Setup: subclasses implement role and _build_system_prompt();
       skill instructions and tool calls are composed automatically
"""

import json
from abc import ABC, abstractmethod

from ..providers.base_provider import LLMProvider
from ..shared.protocols import LoggerProtocol
from ..skills.base_skill import AgentSkill


class AgentBase(ABC):
    """
    Input: provider (LLMProvider), model (str), temperature (float),
           timeout (float), skills (list[AgentSkill])
    Output: think(prompt: str) -> dict with agent, content, round
    Setup: subclasses define role and _build_system_prompt();
           skills inject instructions and expose tools automatically
    """

    def __init__(
        self,
        provider: LLMProvider,
        model: str,
        temperature: float,
        timeout: float,
        skills: list[AgentSkill] | None = None,
        logger: LoggerProtocol | None = None,
    ) -> None:
        """Initialize agent with LLM provider, settings, and skills.

        Args:
            provider: The LLM provider to use for chat.
            model: Model name (passed through to provider).
            temperature: Sampling temperature.
            timeout: Request timeout in seconds.
            skills: Optional list of AgentSkill instances to compose.
            logger: Optional LogManager for structured logging.
        """
        self.provider = provider
        self.model = model
        self.temperature = temperature
        self.timeout = timeout
        self.skills = skills or []
        self._logger = logger

    @property
    @abstractmethod
    def role(self) -> str:
        """Return the agent's role identifier."""
        ...  # pragma: no cover

    @abstractmethod
    def _build_system_prompt(self) -> str:
        """Build the system prompt, incorporating skill instructions."""
        ...  # pragma: no cover

    def _build_skill_block(self) -> str:
        """Concatenate instruction text from all assigned skills.

        Returns:
            Newline-joined skill instructions, empty string if no skills.
        """
        parts = [s.get_instructions() for s in self.skills]
        return "\n".join(parts)

    def _get_tools(self) -> list[dict]:
        """Collect tool definitions from all skills that expose one.

        Returns:
            List of neutral tool definition dicts.
        """
        return [t for s in self.skills if (t := s.get_tool_definition()) is not None]

    def _execute_tool(self, name: str, args: dict) -> str:
        """Dispatch a tool call to the skill that handles it.

        Args:
            name: Tool name (e.g. 'search').
            args: Tool argument dict.

        Returns:
            Tool result as a string; empty string if no handler found.
        """
        query = args.get("query", "")
        self._log("%s tool call: %s(query=%r)", self.role.upper(), name, query)
        if name == "search":
            for skill in self.skills:
                results = skill.search(query)
                if results:
                    self._log(
                        "%s tool result: %d item(s) returned", self.role.upper(), len(results)
                    )
                    return "\n".join(results)
        self._log("%s tool result: no handler for '%s'", self.role.upper(), name)
        return ""

    def think(self, user_prompt: str) -> dict:
        """Send a prompt to the LLM and return a structured response.

        Passes skill tools to the provider for native tool calling when
        any skill exposes a tool definition.

        Args:
            user_prompt: The user/message prompt to send.

        Returns:
            Dict with agent role, content, and metadata.
        """
        if self.skills:
            self._log(
                "%s skills active: %s",
                self.role.upper(),
                ", ".join(s.name for s in self.skills),
            )
        messages = [
            {"role": "system", "content": self._build_system_prompt()},
            {"role": "user", "content": user_prompt},
        ]
        tools = self._get_tools()
        tool_executor = self._execute_tool if tools else None
        raw = self.provider.chat(messages, tools or None, tool_executor)
        response = self._parse_response(raw)
        response["agent"] = self.role
        return response

    def _log(self, message: str, *args: object) -> None:
        """Emit an info log if a logger is configured."""
        if self._logger is not None:
            self._logger.info(message % args)

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
