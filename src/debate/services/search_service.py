"""SearchService — DuckDuckGo search for internet citations.

Input: query (str), max_results (int)
Output: list of result dicts with title, href, body
Setup: duckduckgo-search SDK, no API key needed
"""

from ddgs import DDGS


class SearchService:
    """
    Input: query (str), max_results (int)
    Output: list[dict] with title, href, body keys
    Setup: free DuckDuckGo search, no API key required
    """

    def search(self, query: str, max_results: int = 5) -> list[dict]:
        """Search DuckDuckGo and return result snippets.

        Args:
            query: Search query string.
            max_results: Maximum number of results to return.

        Returns:
            List of dicts with title, href, and body keys.
        """
        with DDGS() as ddgs:
            raw = ddgs.text(query, max_results=max_results)
        return [{"title": r["title"], "href": r["href"], "body": r["body"]} for r in raw]
