"""JudgeAgent — mediates debate and decides winner.

Skills injected via config; defaults to persuasion-scoring which evaluates
persuasiveness and communication quality, not factual correctness.
"""

from ..skills.base_skill import AgentSkill
from .base_agent import AgentBase


class JudgeAgent(AgentBase):
    """
    Input: provider, model, temperature, timeout, topic, skills
    Output: think(prompt) -> dict with verdict, scores, justification
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
    ) -> None:
        """Initialize JudgeAgent.

        Args:
            provider: LLM provider instance.
            model: Model name.
            temperature: Sampling temperature.
            timeout: Request timeout in seconds.
            topic: The debate topic.
            skills: Optional list of AgentSkill instances.
        """
        super().__init__(provider, model, temperature, timeout, skills)
        self.topic = topic

    @property
    def role(self) -> str:
        """Return 'judge' role identifier."""
        return "judge"

    def _build_system_prompt(self) -> str:
        """Build system prompt with injected skill instructions.

        Returns:
            System prompt for judging and scoring the debate,
            with skill block appended when skills are assigned.
        """
        base = (
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
        skill_block = self._build_skill_block()
        return f"{base}\n\n{skill_block}" if skill_block else base
