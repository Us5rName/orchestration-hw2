"""Agent skills package — modular, pluggable behaviour units for debate agents."""

from .base_skill import AgentSkill
from .persuasion_scoring import PersuasionScoringSkill
from .quality_standards import QualityStandardsSkill
from .registry import SkillRegistry, default_registry
from .research_analysis import ResearchAnalysisSkill

__all__ = [
    "AgentSkill",
    "ResearchAnalysisSkill",
    "QualityStandardsSkill",
    "PersuasionScoringSkill",
    "SkillRegistry",
    "default_registry",
]
