"""Knowledge base tool using Wikipedia API."""


import requests


def search_wikipedia(query: str, sentences: int = 5) -> str:
    """
    Search Wikipedia for scientific facts and definitions.

    Args:
        query: The search term or topic
        sentences: Number of sentences to return from the summary (default: 5)

    Returns:
        Wikipedia summary or error message
    """
    base_url = "https://en.wikipedia.org/api/rest_v1/page/summary/"

    # Clean query for URL
    search_term = query.replace(" ", "_")

    try:
        response = requests.get(
            f"{base_url}{search_term}",
            headers={"User-Agent": "Kosmo/1.0 (Cosmology Research Agent)"},
            timeout=10
        )

        if response.status_code == 404:
            # Try search API instead
            return _search_and_get_summary(query, sentences)

        if response.status_code != 200:
            return f"Error: Wikipedia API returned status {response.status_code}"

        data = response.json()

        if data.get("type") == "disambiguation":
            return f"'{query}' is ambiguous. Please be more specific. Related topics: {data.get('extract', 'N/A')}"

        title = data.get("title", query)
        extract = data.get("extract", "No summary available.")
        url = data.get("content_urls", {}).get("desktop", {}).get("page", "")

        # Truncate to requested sentences
        sentences_list = extract.split(". ")
        if len(sentences_list) > sentences:
            extract = ". ".join(sentences_list[:sentences]) + "."

        result = f"**{title}**\n\n{extract}"
        if url:
            result += f"\n\nSource: {url}"

        return result

    except requests.exceptions.Timeout:
        return "Error: Wikipedia request timed out."
    except requests.exceptions.RequestException as e:
        return f"Error accessing Wikipedia: {str(e)}"
    except Exception as e:
        return f"Error processing Wikipedia response: {str(e)}"


def _search_and_get_summary(query: str, sentences: int) -> str:
    """Search Wikipedia and get summary of the best match."""
    search_url = "https://en.wikipedia.org/w/api.php"

    try:
        # Search for the query
        search_response = requests.get(
            search_url,
            params={
                "action": "query",
                "list": "search",
                "srsearch": query,
                "format": "json",
                "srlimit": 3
            },
            headers={"User-Agent": "Kosmo/1.0 (Cosmology Research Agent)"},
            timeout=10
        )

        if search_response.status_code != 200:
            return f"Error: Wikipedia search returned status {search_response.status_code}"

        search_data = search_response.json()
        results = search_data.get("query", {}).get("search", [])

        if not results:
            return f"No Wikipedia articles found for: {query}"

        # Get summary of first result
        first_result = results[0]["title"]
        return search_wikipedia(first_result, sentences)

    except Exception as e:
        return f"Error searching Wikipedia: {str(e)}"
