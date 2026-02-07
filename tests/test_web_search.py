"""Tests for the web search tool."""

import os
import unittest
from unittest.mock import MagicMock, patch

from kosmo.tools.web_search import TAVILY_AVAILABLE, web_search


class TestWebSearchApiKey(unittest.TestCase):
    """Tests for API key handling."""

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_api_key(self):
        """Test error when TAVILY_API_KEY is not set."""
        # Ensure the key is not in environment
        if "TAVILY_API_KEY" in os.environ:
            del os.environ["TAVILY_API_KEY"]

        result = web_search("test query")

        assert "Error" in result
        assert "TAVILY_API_KEY" in result
        assert "not found" in result.lower()

    @patch.dict(os.environ, {"TAVILY_API_KEY": ""}, clear=True)
    def test_empty_api_key(self):
        """Test error when TAVILY_API_KEY is empty."""
        result = web_search("test query")

        assert "Error" in result
        assert "TAVILY_API_KEY" in result


class TestWebSearchPackageAvailability(unittest.TestCase):
    """Tests for tavily package availability."""

    @patch.dict(os.environ, {"TAVILY_API_KEY": "test_key"})
    @patch("kosmo.tools.web_search.TAVILY_AVAILABLE", False)
    def test_tavily_not_installed(self):
        """Test error when tavily-python is not installed."""
        result = web_search("test query")

        assert "Error" in result
        assert "tavily-python" in result
        assert "pip install" in result


@unittest.skipUnless(TAVILY_AVAILABLE, "Tavily package not installed")
class TestWebSearchWithMockedClient(unittest.TestCase):
    """Tests for web_search with mocked Tavily client."""

    @patch.dict(os.environ, {"TAVILY_API_KEY": "test_key"})
    @patch("kosmo.tools.web_search.TavilyClient")
    def test_successful_search(self, mock_client_class):
        """Test successful search with results."""
        mock_client = MagicMock()
        mock_client.search.return_value = {
            "results": [
                {
                    "title": "Dark Matter - NASA",
                    "url": "https://nasa.gov/dark-matter",
                    "content": "Dark matter is a type of matter thought to be responsible for much of the mass in the universe."
                }
            ]
        }
        mock_client_class.return_value = mock_client

        result = web_search("dark matter")

        assert "Search Results for: dark matter" in result
        assert "Dark Matter - NASA" in result
        assert "nasa.gov" in result

    @patch.dict(os.environ, {"TAVILY_API_KEY": "test_key"})
    @patch("kosmo.tools.web_search.TavilyClient")
    def test_multiple_results(self, mock_client_class):
        """Test search returning multiple results."""
        mock_client = MagicMock()
        mock_client.search.return_value = {
            "results": [
                {"title": "Result 1", "url": "https://example1.com", "content": "Content 1"},
                {"title": "Result 2", "url": "https://example2.com", "content": "Content 2"},
                {"title": "Result 3", "url": "https://example3.com", "content": "Content 3"},
            ]
        }
        mock_client_class.return_value = mock_client

        result = web_search("test", max_results=3)

        assert "1. Result 1" in result
        assert "2. Result 2" in result
        assert "3. Result 3" in result

    @patch.dict(os.environ, {"TAVILY_API_KEY": "test_key"})
    @patch("kosmo.tools.web_search.TavilyClient")
    def test_no_results(self, mock_client_class):
        """Test search with no results."""
        mock_client = MagicMock()
        mock_client.search.return_value = {"results": []}
        mock_client_class.return_value = mock_client

        result = web_search("xyznonexistent123")

        assert "No results found" in result
        assert "xyznonexistent123" in result

    @patch.dict(os.environ, {"TAVILY_API_KEY": "test_key"})
    @patch("kosmo.tools.web_search.TavilyClient")
    def test_result_formatting(self, mock_client_class):
        """Test that results are properly formatted."""
        mock_client = MagicMock()
        mock_client.search.return_value = {
            "results": [
                {
                    "title": "Test Title",
                    "url": "https://test.com/page",
                    "content": "Test content goes here."
                }
            ]
        }
        mock_client_class.return_value = mock_client

        result = web_search("test")

        assert "1. Test Title" in result
        assert "URL: https://test.com/page" in result
        assert "Test content goes here." in result

    @patch.dict(os.environ, {"TAVILY_API_KEY": "test_key"})
    @patch("kosmo.tools.web_search.TavilyClient")
    def test_content_truncation(self, mock_client_class):
        """Test that long content is truncated."""
        long_content = "x" * 500  # Longer than 300 character limit
        mock_client = MagicMock()
        mock_client.search.return_value = {
            "results": [
                {
                    "title": "Test",
                    "url": "https://test.com",
                    "content": long_content
                }
            ]
        }
        mock_client_class.return_value = mock_client

        result = web_search("test")

        # Content should be truncated to 300 chars + "..."
        assert "..." in result
        # Should not contain the full 500 characters of content
        assert long_content not in result

    @patch.dict(os.environ, {"TAVILY_API_KEY": "test_key"})
    @patch("kosmo.tools.web_search.TavilyClient")
    def test_max_results_parameter(self, mock_client_class):
        """Test that max_results parameter is passed to client."""
        mock_client = MagicMock()
        mock_client.search.return_value = {"results": []}
        mock_client_class.return_value = mock_client

        web_search("test", max_results=10)

        mock_client.search.assert_called_once()
        call_kwargs = mock_client.search.call_args[1]
        assert call_kwargs["max_results"] == 10

    @patch.dict(os.environ, {"TAVILY_API_KEY": "test_key"})
    @patch("kosmo.tools.web_search.TavilyClient")
    def test_search_depth_advanced(self, mock_client_class):
        """Test that search depth is set to advanced."""
        mock_client = MagicMock()
        mock_client.search.return_value = {"results": []}
        mock_client_class.return_value = mock_client

        web_search("test")

        call_kwargs = mock_client.search.call_args[1]
        assert call_kwargs["search_depth"] == "advanced"

    @patch.dict(os.environ, {"TAVILY_API_KEY": "test_key"})
    @patch("kosmo.tools.web_search.TavilyClient")
    def test_domain_filtering(self, mock_client_class):
        """Test that domain filtering is applied."""
        mock_client = MagicMock()
        mock_client.search.return_value = {"results": []}
        mock_client_class.return_value = mock_client

        web_search("test")

        call_kwargs = mock_client.search.call_args[1]
        include_domains = call_kwargs["include_domains"]

        assert "arxiv.org" in include_domains
        assert "nasa.gov" in include_domains
        assert "esa.int" in include_domains
        assert "wikipedia.org" in include_domains
        assert "space.com" in include_domains


@unittest.skipUnless(TAVILY_AVAILABLE, "Tavily package not installed")
class TestWebSearchErrorHandling(unittest.TestCase):
    """Tests for error handling in web_search."""

    @patch.dict(os.environ, {"TAVILY_API_KEY": "test_key"})
    @patch("kosmo.tools.web_search.TavilyClient")
    def test_api_exception(self, mock_client_class):
        """Test handling of API exception."""
        mock_client = MagicMock()
        mock_client.search.side_effect = Exception("API rate limit exceeded")
        mock_client_class.return_value = mock_client

        result = web_search("test")

        assert "Error performing web search" in result
        assert "API rate limit exceeded" in result

    @patch.dict(os.environ, {"TAVILY_API_KEY": "test_key"})
    @patch("kosmo.tools.web_search.TavilyClient")
    def test_network_error(self, mock_client_class):
        """Test handling of network error."""
        mock_client = MagicMock()
        mock_client.search.side_effect = Exception("Connection refused")
        mock_client_class.return_value = mock_client

        result = web_search("test")

        assert "Error performing web search" in result

    @patch.dict(os.environ, {"TAVILY_API_KEY": "test_key"})
    @patch("kosmo.tools.web_search.TavilyClient")
    def test_invalid_api_key(self, mock_client_class):
        """Test handling of invalid API key."""
        mock_client = MagicMock()
        mock_client.search.side_effect = Exception("Invalid API key")
        mock_client_class.return_value = mock_client

        result = web_search("test")

        assert "Error performing web search" in result


@unittest.skipUnless(TAVILY_AVAILABLE, "Tavily package not installed")
class TestWebSearchMissingFields(unittest.TestCase):
    """Tests for handling missing fields in results."""

    @patch.dict(os.environ, {"TAVILY_API_KEY": "test_key"})
    @patch("kosmo.tools.web_search.TavilyClient")
    def test_missing_title(self, mock_client_class):
        """Test handling of missing title in result."""
        mock_client = MagicMock()
        mock_client.search.return_value = {
            "results": [
                {"url": "https://test.com", "content": "Test content"}
            ]
        }
        mock_client_class.return_value = mock_client

        result = web_search("test")

        assert "No title" in result

    @patch.dict(os.environ, {"TAVILY_API_KEY": "test_key"})
    @patch("kosmo.tools.web_search.TavilyClient")
    def test_missing_url(self, mock_client_class):
        """Test handling of missing URL in result."""
        mock_client = MagicMock()
        mock_client.search.return_value = {
            "results": [
                {"title": "Test Title", "content": "Test content"}
            ]
        }
        mock_client_class.return_value = mock_client

        result = web_search("test")

        assert "No URL" in result

    @patch.dict(os.environ, {"TAVILY_API_KEY": "test_key"})
    @patch("kosmo.tools.web_search.TavilyClient")
    def test_missing_content(self, mock_client_class):
        """Test handling of missing content in result."""
        mock_client = MagicMock()
        mock_client.search.return_value = {
            "results": [
                {"title": "Test Title", "url": "https://test.com"}
            ]
        }
        mock_client_class.return_value = mock_client

        result = web_search("test")

        assert "No content available" in result

    @patch.dict(os.environ, {"TAVILY_API_KEY": "test_key"})
    @patch("kosmo.tools.web_search.TavilyClient")
    def test_missing_results_key(self, mock_client_class):
        """Test handling of missing results key in response."""
        mock_client = MagicMock()
        mock_client.search.return_value = {}
        mock_client_class.return_value = mock_client

        result = web_search("test")

        assert "No results found" in result


class TestWebSearchAgentIntegration(unittest.TestCase):
    """Tests for integration with the agent tool system."""

    def test_web_search_tool_exists(self):
        """Test that web_search tool is properly integrated in agent."""
        from kosmo.agent import create_tools

        tools = create_tools()
        tool_names = [t.name for t in tools]
        assert "web_search" in tool_names

    def test_web_search_tool_description(self):
        """Test that web_search tool has proper description."""
        from kosmo.agent import create_tools

        tools = create_tools()
        search_tool = next(t for t in tools if t.name == "web_search")
        description = search_tool.description.lower()
        assert "search" in description
        assert "web" in description or "arxiv" in description or "nasa" in description

    def test_web_search_tool_callable(self):
        """Test that web_search tool is callable."""
        from kosmo.agent import create_tools

        tools = create_tools()
        search_tool = next(t for t in tools if t.name == "web_search")
        assert callable(search_tool.func)


class TestWebSearchDefaultParameters(unittest.TestCase):
    """Tests for default parameter values."""

    def test_default_max_results(self):
        """Test default max_results is 5."""
        import inspect

        sig = inspect.signature(web_search)
        max_results_param = sig.parameters["max_results"]
        assert max_results_param.default == 5


@unittest.skipUnless(TAVILY_AVAILABLE, "Tavily package not installed")
class TestWebSearchClientInitialization(unittest.TestCase):
    """Tests for Tavily client initialization."""

    @patch.dict(os.environ, {"TAVILY_API_KEY": "my_secret_key"})
    @patch("kosmo.tools.web_search.TavilyClient")
    def test_client_receives_api_key(self, mock_client_class):
        """Test that TavilyClient receives the API key."""
        mock_client = MagicMock()
        mock_client.search.return_value = {"results": []}
        mock_client_class.return_value = mock_client

        web_search("test")

        mock_client_class.assert_called_once_with(api_key="my_secret_key")


if __name__ == "__main__":
    unittest.main()
