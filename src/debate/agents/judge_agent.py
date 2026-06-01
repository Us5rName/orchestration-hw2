"""JudgeAgent — mediates debate and decides winner.

Skill: evaluates persuasiveness and communication quality,
NOT factual correctness. Must declare a winner — no ties allowed.
"""

from .base_agent import AgentBase


class JudgeAgent(AgentBase):
    """
    Input: provider, model, temperature, timeout, topic
    Output: think(prompt) -> dict with verdict, scores, justification
    Setup: scores persuasiveness, enforces rules, forbids ties
    """

    def __init__(
        self,
        provider: object,
        model: str,
        temperature: float,
        timeout: float,
        topic: str,
    ) -> None:
        """Initialize JudgeAgent.

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
        """Return 'judge' role identifier."""
        return "judge"

    def _build_system_prompt(self) -> str:
        """Build system prompt for judge role.

        Returns:
            System prompt instructing the agent to mediate and score
            based on persuasiveness, not factual correctness.
        """
        return (
            "You are the JUDGE in a formal debate. "
            "You do NOT need expertise on the topic. "
            "Your job is to evaluate PERSUASIVENESS, not factual correctness.\n\n"
            f"TOPIC: {self.topic}\n\n"
            "RULES:\n"
            "- Score each side on persuasiveness, clarity, and argument quality\n"
            "- You MUST declare a winner — there is NO TIE allowed\n"
            "- Use differential scoring (e.g., 80% vs 70%)\n"
            "- Provide a clear justification for your decision\n"
            "- If debaters try to agree, remind them of their positions\n"
            "- Always respond in JSON format:\n"
            '  {"winner": "pro or con", "pro_score": 80, "con_score": 70, '
            '"justification": "reason"}\n'
            "- When relaying messages between debaters, forward the argument\n"
            "- Enforce respectful, politically correct language"
        )
