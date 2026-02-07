"""Tests for the knowledge base (Wikipedia) tool."""

import unittest
from unittest.mock import MagicMock, patch

from kosmo.tools.knowledge_base import _search_and_get_summary, search_wikipedia


class TestSearchWikipediaBasic(unittest.TestCase):
    """Basic tests for search_wikipedia function."""

    @patch("kosmo.tools.knowledge_base.requests.get")
    def test_successful_search(self, mock_get):
        """Test successful Wikipedia search."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "title": "Dark matter",
            "extract": "Dark matter is a hypothetical form of matter. "
                      "It does not emit light. It is invisible. "
                      "It interacts gravitationally. It makes up most of the universe.",
            "content_urls": {
                "desktop": {
                    "page": "https://en.wikipedia.org/wiki/Dark_matter"
                }
            }
        }
        mock_get.return_value = mock_response

        result = search_wikipedia("dark matter")

        assert "**Dark matter**" in result
        assert "hypothetical form of matter" in result
        assert "Source:" in result

    @patch("kosmo.tools.knowledge_base.requests.get")
    def test_returns_title(self, mock_get):
        """Test that result includes the title."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "title": "Black hole",
            "extract": "A black hole is a region of spacetime.",
            "content_urls": {"desktop": {"page": "https://example.com"}}
        }
        mock_get.return_value = mock_response

        result = search_wikipedia("black hole")

        assert "**Black hole**" in result

    @patch("kosmo.tools.knowledge_base.requests.get")
    def test_returns_url(self, mock_get):
        """Test that result includes source URL."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "title": "Exoplanet",
            "extract": "An exoplanet is a planet outside the Solar System.",
            "content_urls": {
                "desktop": {
                    "page": "https://en.wikipedia.org/wiki/Exoplanet"
                }
            }
        }
        mock_get.return_value = mock_response

        result = search_wikipedia("exoplanet")

        assert "Source: https://en.wikipedia.org/wiki/Exoplanet" in result


class TestSearchWikipediaSentences(unittest.TestCase):
    """Tests for sentence truncation in search_wikipedia."""

    @patch("kosmo.tools.knowledge_base.requests.get")
    def test_default_sentences(self, mock_get):
        """Test default 5 sentences limit."""
        long_extract = ". ".join([f"Sentence {i}" for i in range(10)]) + "."
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "title": "Test",
            "extract": long_extract,
            "content_urls": {"desktop": {"page": ""}}
        }
        mock_get.return_value = mock_response

        result = search_wikipedia("test")

        # Should have 5 sentences
        assert "Sentence 0" in result
        assert "Sentence 4" in result
        assert "Sentence 5" not in result

    @patch("kosmo.tools.knowledge_base.requests.get")
    def test_custom_sentences_limit(self, mock_get):
        """Test custom sentence limit."""
        long_extract = ". ".join([f"Sentence {i}" for i in range(10)]) + "."
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "title": "Test",
            "extract": long_extract,
            "content_urls": {"desktop": {"page": ""}}
        }
        mock_get.return_value = mock_response

        result = search_wikipedia("test", sentences=3)

        assert "Sentence 0" in result
        assert "Sentence 2" in result
        assert "Sentence 3" not in result

    @patch("kosmo.tools.knowledge_base.requests.get")
    def test_fewer_sentences_than_limit(self, mock_get):
        """Test when extract has fewer sentences than limit."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "title": "Test",
            "extract": "First sentence. Second sentence.",
            "content_urls": {"desktop": {"page": ""}}
        }
        mock_get.return_value = mock_response

        result = search_wikipedia("test", sentences=10)

        assert "First sentence" in result
        assert "Second sentence" in result


class TestSearchWikipediaDisambiguation(unittest.TestCase):
    """Tests for disambiguation page handling."""

    @patch("kosmo.tools.knowledge_base.requests.get")
    def test_disambiguation_page(self, mock_get):
        """Test handling of disambiguation page."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "type": "disambiguation",
            "title": "Mercury",
            "extract": "Mercury may refer to: Mercury (planet), Mercury (element)"
        }
        mock_get.return_value = mock_response

        result = search_wikipedia("mercury")

        assert "ambiguous" in result.lower()
        assert "Please be more specific" in result


class TestSearchWikipedia404Fallback(unittest.TestCase):
    """Tests for 404 fallback to search API."""

    @patch("kosmo.tools.knowledge_base.requests.get")
    def test_404_triggers_search_fallback(self, mock_get):
        """Test that 404 triggers search API fallback."""
        # First call returns 404
        mock_404_response = MagicMock()
        mock_404_response.status_code = 404

        # Search API call
        mock_search_response = MagicMock()
        mock_search_response.status_code = 200
        mock_search_response.json.return_value = {
            "query": {
                "search": [
                    {"title": "Cosmic microwave background"}
                ]
            }
        }

        # Summary call for search result
        mock_summary_response = MagicMock()
        mock_summary_response.status_code = 200
        mock_summary_response.json.return_value = {
            "title": "Cosmic microwave background",
            "extract": "The CMB is electromagnetic radiation.",
            "content_urls": {"desktop": {"page": "https://example.com"}}
        }

        mock_get.side_effect = [mock_404_response, mock_search_response, mock_summary_response]

        search_wikipedia("cmb radiation")

        # Should have made multiple calls
        assert mock_get.call_count == 3

    @patch("kosmo.tools.knowledge_base.requests.get")
    def test_no_search_results(self, mock_get):
        """Test handling when search returns no results."""
        mock_404_response = MagicMock()
        mock_404_response.status_code = 404

        mock_search_response = MagicMock()
        mock_search_response.status_code = 200
        mock_search_response.json.return_value = {
            "query": {
                "search": []
            }
        }

        mock_get.side_effect = [mock_404_response, mock_search_response]

        result = search_wikipedia("xyznonexistent123")

        assert "No Wikipedia articles found" in result


class TestSearchWikipediaErrorHandling(unittest.TestCase):
    """Tests for error handling in search_wikipedia."""

    @patch("kosmo.tools.knowledge_base.requests.get")
    def test_timeout_error(self, mock_get):
        """Test handling of timeout error."""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout("Connection timed out")

        result = search_wikipedia("test")

        assert "timed out" in result.lower()

    @patch("kosmo.tools.knowledge_base.requests.get")
    def test_connection_error(self, mock_get):
        """Test handling of connection error."""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError("Failed to connect")

        result = search_wikipedia("test")

        assert "Error accessing Wikipedia" in result

    @patch("kosmo.tools.knowledge_base.requests.get")
    def test_request_exception(self, mock_get):
        """Test handling of generic request exception."""
        import requests
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        result = search_wikipedia("test")

        assert "Error accessing Wikipedia" in result

    @patch("kosmo.tools.knowledge_base.requests.get")
    def test_non_200_status(self, mock_get):
        """Test handling of non-200 status code."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        result = search_wikipedia("test")

        assert "Error" in result
        assert "500" in result

    @patch("kosmo.tools.knowledge_base.requests.get")
    def test_json_decode_error(self, mock_get):
        """Test handling of JSON decode error."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        result = search_wikipedia("test")

        assert "Error processing Wikipedia" in result


class TestSearchWikipediaUrlEncoding(unittest.TestCase):
    """Tests for URL encoding in search_wikipedia."""

    @patch("kosmo.tools.knowledge_base.requests.get")
    def test_spaces_converted_to_underscores(self, mock_get):
        """Test that spaces are converted to underscores."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "title": "Dark matter",
            "extract": "Test extract.",
            "content_urls": {"desktop": {"page": ""}}
        }
        mock_get.return_value = mock_response

        search_wikipedia("dark matter")

        # Check that the URL was called with underscores
        call_url = mock_get.call_args[0][0]
        assert "dark_matter" in call_url

    @patch("kosmo.tools.knowledge_base.requests.get")
    def test_user_agent_header(self, mock_get):
        """Test that User-Agent header is set."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "title": "Test",
            "extract": "Test.",
            "content_urls": {"desktop": {"page": ""}}
        }
        mock_get.return_value = mock_response

        search_wikipedia("test")

        call_kwargs = mock_get.call_args[1]
        assert "headers" in call_kwargs
        assert "User-Agent" in call_kwargs["headers"]
        assert "Kosmo" in call_kwargs["headers"]["User-Agent"]


class TestSearchWikipediaMissingData(unittest.TestCase):
    """Tests for handling missing data in response."""

    @patch("kosmo.tools.knowledge_base.requests.get")
    def test_missing_extract(self, mock_get):
        """Test handling of missing extract."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "title": "Test",
            "content_urls": {"desktop": {"page": ""}}
        }
        mock_get.return_value = mock_response

        result = search_wikipedia("test")

        assert "No summary available" in result

    @patch("kosmo.tools.knowledge_base.requests.get")
    def test_missing_url(self, mock_get):
        """Test handling of missing URL."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "title": "Test",
            "extract": "Test extract."
        }
        mock_get.return_value = mock_response

        result = search_wikipedia("test")

        # Should still work without URL
        assert "**Test**" in result
        assert "Test extract" in result

    @patch("kosmo.tools.knowledge_base.requests.get")
    def test_missing_title(self, mock_get):
        """Test handling of missing title."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "extract": "Test extract.",
            "content_urls": {"desktop": {"page": ""}}
        }
        mock_get.return_value = mock_response

        result = search_wikipedia("test_query")

        # Should use query as fallback title
        assert "**test_query**" in result


class TestSearchAndGetSummary(unittest.TestCase):
    """Tests for _search_and_get_summary helper function."""

    @patch("kosmo.tools.knowledge_base.requests.get")
    def test_search_returns_results(self, mock_get):
        """Test search with valid results."""
        mock_search_response = MagicMock()
        mock_search_response.status_code = 200
        mock_search_response.json.return_value = {
            "query": {
                "search": [
                    {"title": "Result One"},
                    {"title": "Result Two"},
                    {"title": "Result Three"}
                ]
            }
        }

        mock_summary_response = MagicMock()
        mock_summary_response.status_code = 200
        mock_summary_response.json.return_value = {
            "title": "Result One",
            "extract": "This is the first result.",
            "content_urls": {"desktop": {"page": ""}}
        }

        mock_get.side_effect = [mock_search_response, mock_summary_response]

        result = _search_and_get_summary("test", 5)

        assert "Result One" in result

    @patch("kosmo.tools.knowledge_base.requests.get")
    def test_search_api_error(self, mock_get):
        """Test handling of search API error."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        result = _search_and_get_summary("test", 5)

        assert "Error" in result
        assert "500" in result

    @patch("kosmo.tools.knowledge_base.requests.get")
    def test_search_exception(self, mock_get):
        """Test handling of exception during search."""
        mock_get.side_effect = Exception("Network error")

        result = _search_and_get_summary("test", 5)

        assert "Error searching Wikipedia" in result


class TestSearchWikipediaAgentIntegration(unittest.TestCase):
    """Tests for integration with the agent tool system."""

    def test_wikipedia_tool_exists(self):
        """Test that search_wikipedia tool is properly integrated in agent."""
        from kosmo.agent import create_tools

        tools = create_tools()
        tool_names = [t.name for t in tools]
        assert "search_wikipedia" in tool_names

    def test_wikipedia_tool_description(self):
        """Test that search_wikipedia tool has proper description."""
        from kosmo.agent import create_tools

        tools = create_tools()
        wiki_tool = next(t for t in tools if t.name == "search_wikipedia")
        assert "wikipedia" in wiki_tool.description.lower()
        assert "knowledge" in wiki_tool.description.lower() or "fact" in wiki_tool.description.lower()

    def test_wikipedia_tool_callable(self):
        """Test that search_wikipedia tool is callable."""
        from kosmo.agent import create_tools

        tools = create_tools()
        wiki_tool = next(t for t in tools if t.name == "search_wikipedia")
        assert callable(wiki_tool.func)


if __name__ == "__main__":
    unittest.main()
