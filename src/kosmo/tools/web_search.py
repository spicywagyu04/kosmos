"""Web search tool using Tavily API."""

import os

try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False


def web_search(query: str, max_results: int = 5) -> str:
    """
    Search the web for scientific information using Tavily API.

    Args:
        query: The search query string
        max_results: Maximum number of results to return (default: 5)

    Returns:
        Formatted string with search results including titles, URLs, and snippets
    """
    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        return "Error: TAVILY_API_KEY not found in environment variables."

    if not TAVILY_AVAILABLE:
        return "Error: tavily-python package not installed. Run: pip install tavily-python"

    try:
        client = TavilyClient(api_key=api_key)
        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results,
            include_domains=["arxiv.org", "nasa.gov", "esa.int", "wikipedia.org", "space.com"],
        )

        results = response.get("results", [])
        if not results:
            return f"No results found for query: {query}"

        output = f"Search Results for: {query}\n" + "=" * 50 + "\n\n"

        for i, result in enumerate(results, 1):
            title = result.get("title", "No title")
            url = result.get("url", "No URL")
            content = result.get("content", "No content available")

            output += f"{i}. {title}\n"
            output += f"   URL: {url}\n"
            output += f"   {content[:300]}...\n\n"

        return output

    except Exception as e:
        return f"Error performing web search: {str(e)}"
