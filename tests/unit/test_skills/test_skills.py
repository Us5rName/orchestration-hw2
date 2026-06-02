"""Tests for concrete skill implementations."""

from unittest.mock import MagicMock

import pytest

from debate.skills.persuasion_scoring import PersuasionScoringSkill
from debate.skills.quality_standards import QualityStandardsSkill
from debate.skills.research_analysis import ResearchAnalysisSkill


@pytest.fixture
def mock_search_service() -> MagicMock:
    """Return a mocked SearchService."""
    svc = MagicMock()
    svc.search.return_value = [
        {"title": "Test Title", "href": "https://example.com", "body": "Some body text."}
    ]
    return svc


@pytest.fixture
def research_skill(mock_search_service: MagicMock) -> ResearchAnalysisSkill:
    """Return ResearchAnalysisSkill with mocked search."""
    return ResearchAnalysisSkill(mock_search_service)


class TestResearchAnalysisSkill:
    """Tests for ResearchAnalysisSkill."""

    def test_name(self, research_skill: ResearchAnalysisSkill) -> None:
        """Skill name is 'research-analysis'."""
        assert research_skill.name == "research-analysis"

    def test_instructions_non_empty(self, research_skill: ResearchAnalysisSkill) -> None:
        """Instructions contain non-empty text."""
        assert len(research_skill.get_instructions()) > 0

    def test_tool_definition_structure(self, research_skill: ResearchAnalysisSkill) -> None:
        """Tool definition has required keys and search function."""
        tool = research_skill.get_tool_definition()
        assert tool is not None
        assert tool["name"] == "search"
        assert "description" in tool
        assert "parameters" in tool
        assert "query" in tool["parameters"]["properties"]

    def test_search_delegates_to_service(
        self, research_skill: ResearchAnalysisSkill, mock_search_service: MagicMock
    ) -> None:
        """search() delegates to SearchService and formats results."""
        results = research_skill.search("Real Madrid")
        mock_search_service.search.assert_called_once_with("Real Madrid")
        assert len(results) == 1
        assert "Test Title" in results[0]
        assert "https://example.com" in results[0]

    def test_search_truncates_body(
        self, research_skill: ResearchAnalysisSkill, mock_search_service: MagicMock
    ) -> None:
        """search() truncates body to 200 characters."""
        mock_search_service.search.return_value = [
            {"title": "T", "href": "u", "body": "x" * 300}
        ]
        results = research_skill.search("query")
        assert len(results[0]) < 230


class TestQualityStandardsSkill:
    """Tests for QualityStandardsSkill."""

    def test_name(self) -> None:
        """Skill name is 'quality-standards'."""
        assert QualityStandardsSkill().name == "quality-standards"

    def test_instructions_non_empty(self) -> None:
        """Instructions contain non-empty text."""
        assert len(QualityStandardsSkill().get_instructions()) > 0

    def test_no_tool_definition(self) -> None:
        """No tool definition — this skill is prompt-only."""
        assert QualityStandardsSkill().get_tool_definition() is None

    def test_search_returns_empty(self) -> None:
        """search() returns empty list — no search capability."""
        assert QualityStandardsSkill().search("anything") == []


class TestPersuasionScoringSkill:
    """Tests for PersuasionScoringSkill."""

    def test_name(self) -> None:
        """Skill name is 'persuasion-scoring'."""
        assert PersuasionScoringSkill().name == "persuasion-scoring"

    def test_instructions_non_empty(self) -> None:
        """Instructions contain non-empty text."""
        assert len(PersuasionScoringSkill().get_instructions()) > 0

    def test_no_tool_definition(self) -> None:
        """No tool definition — this skill is prompt-only."""
        assert PersuasionScoringSkill().get_tool_definition() is None
