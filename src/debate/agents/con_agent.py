"""ConAgent — argues the negative side of the debate topic.

Skills injected via config; defaults to quality-standards for critical
evaluation, optionally combined with research-analysis for counter-evidence.
"""

from ..providers.base_provider import LLMProvider
from ..shared.protocols import LoggerProtocol
from ..skills.base_skill import AgentSkill
from .base_agent import AgentBase


class ConAgent(AgentBase):
    """
    Input: provider, model, temperature, timeout, topic, skills
    Output: think(prompt) -> dict with con arguments
    Setup: skill instructions injected into system prompt via _build_skill_block()
    """

    def __init__(
        self,
        provider: LLMProvider,
        model: str,
        temperature: float,
        timeout: float,
        topic: str,
        skills: list[AgentSkill] | None = None,
        logger: LoggerProtocol | None = None,
    ) -> None:
        """Initialize ConAgent.

        Args:
            provider: LLM provider instance.
            model: Model name.
            temperature: Sampling temperature.
            timeout: Request timeout in seconds.
            topic: The debate topic.
            skills: Optional list of AgentSkill instances.
            logger: Optional LogManager for structured logging.
        """
        super().__init__(provider, model, temperature, timeout, skills, logger)
        self.topic = topic

    @property
    def role(self) -> str:
        """Return 'con' role identifier."""
        return "con"

    def _build_system_prompt(self) -> str:
        """Build system prompt with injected skill instructions.

        Returns:
            System prompt for arguing the negative side,
            with skill block appended when skills are assigned.
        """
        base = (
            "You are the CON debater in a formal debate.\n\n"
            f"TOPIC: {self.topic}\n"
            "POSITION: You argue AGAINST the topic.\n\n"
            "RULES:\n"
            "- Always respond in JSON format: "
            '{"content": "your counter-argument", "references": []}\n'
            "- Must directly address and counter the opponent's last argument\n"
            "- Never agree with the opponent or concede your position\n"
            "- Maintain respectful, politically correct language\n"
            "- You NEVER agree with the opponent — always find a weakness\n"
            "- Even valid points have limitations — find and exploit them"
        )
        skill_block = self._build_skill_block()
        return f"{base}\n\n{skill_block}" if skill_block else base
