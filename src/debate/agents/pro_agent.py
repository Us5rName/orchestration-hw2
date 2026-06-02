"""ProAgent — argues the positive side of the debate topic.

Skills injected via config; defaults to research-analysis for evidence-driven
arguments with live search. Skills are composable and config-driven.
"""

from .base_agent import AgentBase
from ..skills.base_skill import AgentSkill


class ProAgent(AgentBase):
    """
    Input: provider, model, temperature, timeout, topic, skills
    Output: think(prompt) -> dict with pro arguments
    Setup: skill instructions injected into system prompt via _build_skill_block()
    """

    def __init__(
        self,
        provider: object,
        model: str,
        temperature: float,
        timeout: float,
        topic: str,
        skills: list[AgentSkill] | None = None,
        logger: object | None = None,
    ) -> None:
        """Initialize ProAgent.

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
        """Return 'pro' role identifier."""
        return "pro"

    def _build_system_prompt(self) -> str:
        """Build system prompt with injected skill instructions.

        Returns:
            System prompt for arguing the positive side,
            with skill block appended when skills are assigned.
        """
        base = (
            "You are the PRO debater in a formal debate.\n\n"
            f"TOPIC: {self.topic}\n"
            "POSITION: You argue IN FAVOR of the topic.\n\n"
            "RULES:\n"
            "- Always respond in JSON format: "
            '{"content": "your argument", "references": ["source"]}\n'
            "- Must directly address and counter the opponent's last argument\n"
            "- Never agree with the opponent or concede your position\n"
            "- Maintain respectful, politically correct language\n"
            "- You NEVER agree with the opponent — always find a counter-argument\n"
            "- Even if opponent has valid points, show why your side is stronger"
        )
        skill_block = self._build_skill_block()
        return f"{base}\n\n{skill_block}" if skill_block else base
