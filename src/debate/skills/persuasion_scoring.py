"""PersuasionScoringSkill — score debates by persuasiveness.

Teaches the Judge agent to evaluate communication quality and persuasive
power, not factual correctness. No tool use.
"""

from .base_skill import AgentSkill


class PersuasionScoringSkill(AgentSkill):
    """
    Input: none
    Output: get_instructions() -> persuasion-scoring prompt injection
    Setup: no tool use; suitable for Judge agent only
    """

    @property
    def name(self) -> str:
        """Return 'persuasion-scoring' skill identifier."""
        return "persuasion-scoring"

    def get_instructions(self) -> str:
        """Return persuasion-scoring skill instructions.

        Returns:
            Prompt text for scoring persuasiveness, clarity, and quality.
        """
        return (
            "SKILL — persuasion-scoring: Score each debater on persuasiveness, "
            "clarity, and argument quality — NOT factual correctness. "
            "Produce differential scores (e.g. 80% vs 70%). No ties are allowed."
        )
