"""ResearchAnalysisSkill — evidence-driven arguments with live internet search.

Wraps SearchService to expose search as a native LLM tool. Suitable for
Pro and Con debater agents that need to cite sources and data.
"""

from ..services.search_service import SearchService
from .base_skill import AgentSkill


class ResearchAnalysisSkill(AgentSkill):
    """
    Input: search_service (SearchService)
    Output: get_instructions() -> evidence-focused prompt injection
            get_tool_definition() -> search tool schema
            search(query) -> formatted citation strings
    Setup: wraps SearchService; suitable for Pro and Con agents
    """

    def __init__(self, search_service: SearchService) -> None:
        """Initialize with a SearchService instance.

        Args:
            search_service: The search backend to delegate to.
        """
        self._search_service = search_service

    @property
    def name(self) -> str:
        """Return 'research-analysis' skill identifier."""
        return "research-analysis"

    def get_instructions(self) -> str:
        """Return research-analysis skill instructions.

        Returns:
            Prompt text for evidence-driven, citation-backed arguments.
        """
        return (
            "SKILL — research-analysis: Build arguments using evidence, data, "
            "statistics, and cited sources. Always support claims with concrete "
            "examples. Use the 'search' tool to find current sources before arguing."
        )

    def get_tool_definition(self) -> dict:
        """Return the search tool schema in neutral format.

        Returns:
            Tool definition dict with name, description, and parameters.
        """
        return {
            "name": "search",
            "description": "Search the internet for evidence, statistics, or citations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query string.",
                    }
                },
                "required": ["query"],
            },
        }

    def search(self, query: str) -> list[str]:
        """Search and return formatted citation strings.

        Args:
            query: The search query.

        Returns:
            List of formatted strings with title, URL, and body snippet.
        """
        results = self._search_service.search(query)
        return [f"[{r['title']}]({r['href']}): {r['body'][:200]}" for r in results]
