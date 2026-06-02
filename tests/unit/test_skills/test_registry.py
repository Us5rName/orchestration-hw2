"""Tests for SkillRegistry and default_registry factory."""

from unittest.mock import MagicMock

import pytest

from debate.skills.base_skill import AgentSkill
from debate.skills.registry import SkillRegistry, default_registry


def _make_skill(name: str) -> AgentSkill:
    """Create a minimal mock skill with the given name."""
    skill = MagicMock(spec=AgentSkill)
    skill.name = name
    return skill


class TestSkillRegistry:
    """Tests for SkillRegistry."""

    def test_register_and_get(self) -> None:
        """Registered skill can be retrieved by name."""
        registry = SkillRegistry()
        skill = _make_skill("my-skill")
        registry.register(skill)
        assert registry.get("my-skill") is skill

    def test_get_unknown_raises_key_error(self) -> None:
        """get() raises KeyError with helpful message for unknown names."""
        registry = SkillRegistry()
        registry.register(_make_skill("known"))
        with pytest.raises(KeyError, match="unknown-skill"):
            registry.get("unknown-skill")

    def test_key_error_lists_valid_names(self) -> None:
        """KeyError message includes valid skill names."""
        registry = SkillRegistry()
        registry.register(_make_skill("alpha"))
        registry.register(_make_skill("beta"))
        with pytest.raises(KeyError, match="alpha"):
            registry.get("missing")

    def test_list_names_sorted(self) -> None:
        """list_names returns sorted skill names."""
        registry = SkillRegistry()
        registry.register(_make_skill("zebra"))
        registry.register(_make_skill("alpha"))
        assert registry.list_names() == ["alpha", "zebra"]

    def test_register_overwrites_same_name(self) -> None:
        """Registering a skill with the same name replaces the previous one."""
        registry = SkillRegistry()
        skill1 = _make_skill("dup")
        skill2 = _make_skill("dup")
        registry.register(skill1)
        registry.register(skill2)
        assert registry.get("dup") is skill2


class TestDefaultRegistry:
    """Tests for default_registry factory."""

    def test_has_all_builtin_skills(self) -> None:
        """default_registry contains the three built-in skills."""
        mock_svc = MagicMock()
        registry = default_registry(search_service=mock_svc)
        names = registry.list_names()
        assert "research-analysis" in names
        assert "quality-standards" in names
        assert "persuasion-scoring" in names

    def test_uses_provided_search_service(self) -> None:
        """ResearchAnalysisSkill in default_registry uses the given SearchService."""
        mock_svc = MagicMock()
        mock_svc.search.return_value = [{"title": "T", "href": "u", "body": "b"}]
        registry = default_registry(search_service=mock_svc)
        registry.get("research-analysis").search("q")
        mock_svc.search.assert_called_once_with("q")
