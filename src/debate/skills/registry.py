"""SkillRegistry — maps skill name strings to AgentSkill instances.

Input: AgentSkill instances via register()
Output: get(name) -> AgentSkill, list_names() -> list[str]
Setup: use default_registry() to get a pre-populated instance
"""

from ..services.search_service import SearchService
from .base_skill import AgentSkill
from .persuasion_scoring import PersuasionScoringSkill
from .quality_standards import QualityStandardsSkill
from .research_analysis import ResearchAnalysisSkill


class SkillRegistry:
    """
    Input: AgentSkill instances
    Output: get(name: str) -> AgentSkill, list_names() -> list[str]
    Setup: register() adds skills; get() retrieves by name
    """

    def __init__(self) -> None:
        """Initialize empty registry."""
        self._skills: dict[str, AgentSkill] = {}

    def register(self, skill: AgentSkill) -> None:
        """Register a skill instance under its name.

        Args:
            skill: The skill to register.
        """
        self._skills[skill.name] = skill

    def get(self, name: str) -> AgentSkill:
        """Retrieve a skill by name.

        Args:
            name: The skill's kebab-case identifier.

        Returns:
            The registered AgentSkill instance.

        Raises:
            KeyError: If no skill with that name is registered.
        """
        if name not in self._skills:
            valid = ", ".join(sorted(self._skills))
            raise KeyError(f"Unknown skill '{name}'. Valid: {valid}")
        return self._skills[name]

    def list_names(self) -> list[str]:
        """Return sorted list of all registered skill names.

        Returns:
            Sorted list of skill name strings.
        """
        return sorted(self._skills)


def default_registry(search_service: SearchService | None = None) -> SkillRegistry:
    """Create a SkillRegistry pre-populated with all built-in skills.

    Args:
        search_service: SearchService for ResearchAnalysisSkill.
            Defaults to a new SearchService() if None.

    Returns:
        Populated SkillRegistry with research-analysis, quality-standards,
        and persuasion-scoring.
    """
    registry = SkillRegistry()
    registry.register(ResearchAnalysisSkill(search_service or SearchService()))
    registry.register(QualityStandardsSkill())
    registry.register(PersuasionScoringSkill())
    return registry
