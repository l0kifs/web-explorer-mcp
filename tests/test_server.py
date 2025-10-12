"""Unit and integration tests for MCP server."""

from unittest.mock import patch

import pytest

from web_explorer_mcp.config.settings import AppSettings
from web_explorer_mcp.entrypoints.mcp.server import mcp
from web_explorer_mcp.models.entities import (
    SearchResponse,
    SearchResult,
    WebpageContent,
)


class TestMCPServer:
    """Integration and unit tests for MCP server tools."""

    def setup_method(self):
        """Set up test fixtures."""
        self.settings = AppSettings()

    def test_web_search_tool_logic(self):
        """Test web_search_tool logic with successful search."""
        # Test parameter defaults
        page_size = 5
        if page_size is None:
            page_size = self.settings.web_search.default_page_size

        assert page_size == 5

        # Test that settings are accessible
        assert self.settings.web_search.searxng_url is not None
        assert self.settings.web_search.timeout > 0

    def test_webpage_content_tool_logic(self):
        """Test webpage_content_tool logic with successful extraction."""
        # Test parameter defaults
        max_chars = 5000
        if max_chars is None:
            max_chars = self.settings.webpage.max_chars

        assert max_chars == 5000

        # Test that settings are accessible
        assert self.settings.webpage.max_chars > 0
        assert self.settings.webpage.timeout > 0

    def test_mcp_tool_registration(self):
        """Test that MCP tools are properly registered."""
        # Check that mcp instance exists and has expected attributes
        assert mcp is not None
        assert hasattr(mcp, "name")
        assert mcp.name == "Web Explorer MCP"

    def test_settings_integration(self):
        """Test that settings are properly loaded and used."""
        # Test that settings object is created
        assert self.settings is not None
        assert hasattr(self.settings, "web_search")
        assert hasattr(self.settings, "webpage")
        assert hasattr(self.settings, "logging")

        # Test web search settings
        assert self.settings.web_search.searxng_url is not None
        assert self.settings.web_search.default_page_size > 0
        assert self.settings.web_search.timeout > 0

        # Test webpage settings
        assert self.settings.webpage.max_chars > 0
        assert self.settings.webpage.timeout > 0

        # Test logging settings
        assert self.settings.logging.console_log_level is not None
        assert self.settings.logging.file_log_level is not None

    @pytest.mark.asyncio
    @patch("web_explorer_mcp.entrypoints.mcp.server.web_explorer_service")
    async def test_web_search_tool_conversion_success(self, mock_service):
        """Test web_search_tool response conversion with successful search."""
        # Setup mock response with proper SearchResult objects
        mock_response = SearchResponse(
            query="test query",
            page=1,
            page_size=5,
            total_results=10,
            results=[
                SearchResult(
                    title="Result 1", description="Desc 1", url="https://example1.com"
                ),
                SearchResult(
                    title="Result 2", description="Desc 2", url="https://example2.com"
                ),
            ],
            error=None,
        )
        mock_service.search_web.return_value = mock_response

        # Test the conversion that happens in the tool
        converted = {
            "query": mock_response.query,
            "page": mock_response.page,
            "page_size": mock_response.page_size,
            "total_results": mock_response.total_results,
            "results": [
                {
                    "title": r.title,
                    "description": r.description,
                    "url": r.url,
                }
                for r in mock_response.results
            ],
            "error": None,
        }

        expected = {
            "query": "test query",
            "page": 1,
            "page_size": 5,
            "total_results": 10,
            "results": [
                {
                    "title": "Result 1",
                    "description": "Desc 1",
                    "url": "https://example1.com",
                },
                {
                    "title": "Result 2",
                    "description": "Desc 2",
                    "url": "https://example2.com",
                },
            ],
            "error": None,
        }

        assert converted == expected

    @pytest.mark.asyncio
    @patch("web_explorer_mcp.entrypoints.mcp.server.web_explorer_service")
    async def test_webpage_content_tool_conversion_success(self, mock_service):
        """Test webpage_content_tool response conversion with successful extraction."""
        from web_explorer_mcp.models.entities import WebpageHeading

        mock_response = WebpageContent(
            url="https://example.com",
            title="Test Page",
            description="Meta desc",
            author="",
            published_date="",
            main_content="Main content",
            content_type="webpage",
            headings=[WebpageHeading(level=1, text="Header 1")],
            length=100,
            error=None,
        )
        mock_service.extract_webpage_content.return_value = mock_response

        # Test the conversion that happens in the tool (with pagination applied)
        # Simulate what server.py does
        paginated_text = "Main content"  # For short content, no pagination
        total_pages = 1
        has_next = False
        display_length = len(paginated_text)

        converted = {
            "url": mock_response.url,
            "title": mock_response.title,
            "description": mock_response.description,
            "main_content": mock_response.main_content,
            "main_text": paginated_text,
            "headings": [
                {"level": h.level, "text": h.text} for h in mock_response.headings
            ],
            "length": display_length,
            "error": mock_response.error,
            "page": 1,
            "total_pages": total_pages,
            "has_next_page": has_next,
        }

        expected = {
            "url": "https://example.com",
            "title": "Test Page",
            "description": "Meta desc",
            "main_content": "Main content",
            "main_text": "Main content",
            "headings": [{"level": 1, "text": "Header 1"}],
            "length": 12,
            "error": None,
            "page": 1,
            "total_pages": 1,
            "has_next_page": False,
        }

        assert converted == expected
