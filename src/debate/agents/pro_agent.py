"""ProAgent — argues the positive side using research-analysis skill.

Skill: research-analysis — evidence-driven, data-backed, cites sources.
Contrasts with ConAgent's quality-standards skill for real contradiction.
"""

from .base_agent import AgentBase


class ProAgent(AgentBase):
    """
    Input: provider, model, temperature, timeout, topic
    Output: think(prompt) -> dict with pro arguments
    Setup: research-analysis skill — builds evidence-based arguments
    """

    def __init__(
        self,
        provider: object,
        model: str,
        temperature: float,
        timeout: float,
        topic: str,
    ) -> None:
        """Initialize ProAgent.

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
        """Return 'pro' role identifier."""
        return "pro"

    def _build_system_prompt(self) -> str:
        """Build system prompt with research-analysis skill.

        Returns:
            System prompt instructing the agent to argue the positive side
            using evidence, data, and citations.
        """
        return (
            "You are the PRO debater in a formal debate. "
            "Your skill is research-analysis: you build arguments using "
            "evidence, data, statistics, and cited sources. "
            "You always support claims with concrete examples and references.\n\n"
            f"TOPIC: {self.topic}\n"
            "POSITION: You argue IN FAVOR of the topic.\n\n"
            "RULES:\n"
            "- Always respond in JSON format: "
            '{"content": "your argument", "references": ["source"]}\n'
            "- Must directly address and counter the opponent's last argument\n"
            "- Never agree with the opponent or concede your position\n"
            "- Cite specific studies, data, or historical examples\n"
            "- Maintain respectful, politically correct language\n"
            "- If opponent makes false claims, correct them with evidence\n"
            "- You NEVER agree with the opponent — always find a counter-argument\n"
            "- Even if opponent has valid points, show why your side is stronger"
        )
