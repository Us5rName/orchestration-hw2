"""ConAgent — argues the negative side using quality-standards skill.

Skill: quality-standards — critical evaluation, finds weaknesses,
demands rigor. Contrasts with ProAgent's research-analysis skill.
"""

from .base_agent import AgentBase


class ConAgent(AgentBase):
    """
    Input: provider, model, temperature, timeout, topic
    Output: think(prompt) -> dict with con arguments
    Setup: quality-standards skill — challenges assumptions, demands rigor
    """

    def __init__(
        self,
        provider: object,
        model: str,
        temperature: float,
        timeout: float,
        topic: str,
    ) -> None:
        """Initialize ConAgent.

        Args:
            provider: LLM provider instance.
            model: Model name.
            temperature: Sampling temperature.
            timeout: Request timeout in seconds.
            topic: The debate topic.
        """
        super().__init__(provider, model, temperature, timeout)
        self.topic = topic

    @property
    def role(self) -> str:
        """Return 'con' role identifier."""
        return "con"

    def _build_system_prompt(self) -> str:
        """Build system prompt with quality-standards skill.

        Returns:
            System prompt instructing the agent to argue the negative side
            using critical evaluation and logical analysis.
        """
        return (
            "You are the CON debater in a formal debate. "
            "Your skill is quality-standards evaluation: you critically "
            "analyze arguments, identify logical fallacies, point out "
            "methodological weaknesses, and demand rigorous evidence.\n\n"
            f"TOPIC: {self.topic}\n"
            "POSITION: You argue AGAINST the topic.\n\n"
            "RULES:\n"
            "- Always respond in JSON format: "
            '{"content": "your counter-argument", "references": []}\n'
            "- Must directly address and counter the opponent's last argument\n"
            "- Never agree with the opponent or concede your position\n"
            "- Point out logical fallacies, weak evidence, and biases\n"
            "- Maintain respectful, politically correct language\n"
            "- Challenge the methodology behind the opponent's claims\n"
            "- You NEVER agree with the opponent — always find a weakness\n"
            "- Even valid points have limitations — find and exploit them"
        )
