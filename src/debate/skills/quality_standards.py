"""QualityStandardsSkill — critical evaluation and logical rigor.

Teaches an agent to challenge assumptions, identify fallacies, and demand
rigorous evidence. No tool use — pure logical critique.
"""

from .base_skill import AgentSkill


class QualityStandardsSkill(AgentSkill):
    """
    Input: none
    Output: get_instructions() -> critical-evaluation prompt injection
    Setup: no tool use; suitable for Pro and Con debater agents
    """

    @property
    def name(self) -> str:
        """Return 'quality-standards' skill identifier."""
        return "quality-standards"

    def get_instructions(self) -> str:
        """Return quality-standards skill instructions.

        Returns:
            Prompt text for critical evaluation and logical analysis.
        """
        return (
            "SKILL — quality-standards: Critically analyse your opponent's arguments. "
            "Identify logical fallacies, methodological weaknesses, and unsupported claims. "
            "Demand rigorous evidence. Challenge the quality and relevance of cited sources."
        )
