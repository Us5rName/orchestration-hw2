"""Tests for SearchService."""

from unittest.mock import MagicMock, patch

import pytest

from debate.services.search_service import SearchService


@pytest.fixture
def service() -> SearchService:
    """Return a SearchService instance."""
    return SearchService()


class TestSearchServiceSearch:
    """Test search functionality."""

    @patch("debate.services.search_service.DDGS")
    def test_returns_results(self, mock_ddgs_cls: MagicMock, service: SearchService) -> None:
        """Search returns a list of result dicts."""
        mock_ddgs = MagicMock()
        mock_ddgs_cls.return_value.__enter__.return_value = mock_ddgs
        mock_ddgs.text.return_value = [
            {"title": "Result 1", "href": "http://example.com/1", "body": "desc 1"},
            {"title": "Result 2", "href": "http://example.com/2", "body": "desc 2"},
        ]
        results = service.search("test query")
        assert len(results) == 2
        assert results[0]["title"] == "Result 1"

    @patch("debate.services.search_service.DDGS")
    def test_passes_max_results(self, mock_ddgs_cls: MagicMock, service: SearchService) -> None:
        """Search respects max_results parameter."""
        mock_ddgs = MagicMock()
        mock_ddgs_cls.return_value.__enter__.return_value = mock_ddgs
        mock_ddgs.text.return_value = []
        service.search("query", max_results=5)
        mock_ddgs.text.assert_called_once()
        assert mock_ddgs.text.call_args.kwargs["max_results"] == 5

    @patch("debate.services.search_service.DDGS")
    def test_empty_results(self, mock_ddgs_cls: MagicMock, service: SearchService) -> None:
        """Search returns empty list when no results."""
        mock_ddgs = MagicMock()
        mock_ddgs_cls.return_value.__enter__.return_value = mock_ddgs
        mock_ddgs.text.return_value = []
        results = service.search("no results")
        assert results == []
