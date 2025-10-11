"""Unit tests for WebExplorerService."""

from unittest.mock import AsyncMock

import pytest

from web_explorer_mcp.business.services import WebExplorerService
from web_explorer_mcp.models.entities import SearchResponse, WebpageContent


class TestWebExplorerService:
    """Test cases for WebExplorerService."""

    @pytest.fixture
    def mock_search_service(self):
        """Mock WebSearchService."""
        service = AsyncMock()
        service.search.return_value = SearchResponse(
            query="test query",
            page=1,
            page_size=5,
            total_results=10,
            results=[],
            error=None,
        )
        return service

    @pytest.fixture
    def mock_content_service(self):
        """Mock WebpageContentService."""
        service = AsyncMock()
        service.extract_content.return_value = WebpageContent(
            url="https://example.com",
            title="Test Page",
            description="Test description",
            author="Test Author",
            published_date="2025-01-01",
            main_content="Test content",
            headings=[],
            links=[],
            images=[],
            metadata={},
            content_type="article",
            pagination={},
            length=100,
            error=None,
        )
        return service

    @pytest.fixture
    def web_explorer_service(self, mock_search_service, mock_content_service):
        """WebExplorerService instance with mocked dependencies."""
        return WebExplorerService(
            search_service=mock_search_service,
            content_service=mock_content_service,
        )

    @pytest.mark.asyncio
    async def test_search_web_with_default_page_size(
        self, web_explorer_service, mock_search_service
    ):
        """Test search_web with default page size."""
        result = await web_explorer_service.search_web(query="test query")

        assert result.query == "test query"
        assert result.page == 1
        assert result.page_size == 5
        mock_search_service.search.assert_called_once_with(
            query="test query", page=1, page_size=5
        )

    @pytest.mark.asyncio
    async def test_search_web_with_custom_page_size(
        self, web_explorer_service, mock_search_service
    ):
        """Test search_web with custom page size."""
        # Configure mock to return different response for custom parameters
        mock_search_service.search.return_value = SearchResponse(
            query="test query",
            page=2,
            page_size=10,
            total_results=20,
            results=[],
            error=None,
        )

        result = await web_explorer_service.search_web(
            query="test query", page=2, page_size=10
        )

        assert result.query == "test query"
        assert result.page == 2
        assert result.page_size == 10
        mock_search_service.search.assert_called_once_with(
            query="test query", page=2, page_size=10
        )

    @pytest.mark.asyncio
    async def test_extract_webpage_content_with_defaults(
        self, web_explorer_service, mock_content_service
    ):
        """Test extract_webpage_content with default parameters."""
        result = await web_explorer_service.extract_webpage_content(
            url="https://example.com"
        )

        assert result.url == "https://example.com"
        assert result.title == "Test Page"
        mock_content_service.extract_content.assert_called_once_with(
            url="https://example.com",
            raw_content=False,
            timeout=30,
        )

    @pytest.mark.asyncio
    async def test_extract_webpage_content_with_custom_params(
        self, web_explorer_service, mock_content_service
    ):
        """Test extract_webpage_content with custom parameters."""
        result = await web_explorer_service.extract_webpage_content(
            url="https://example.com",
            raw_content=True,
            timeout=60,
        )

        assert result.url == "https://example.com"
        mock_content_service.extract_content.assert_called_once_with(
            url="https://example.com",
            raw_content=True,
            timeout=60,
        )

    @pytest.mark.asyncio
    async def test_search_web_error_propagation(
        self, mock_search_service, mock_content_service
    ):
        """Test that search errors are propagated correctly."""
        mock_search_service.search.return_value = SearchResponse(
            query="error query",
            page=1,
            page_size=5,
            total_results=0,
            results=[],
            error="Search failed",
        )

        service = WebExplorerService(mock_search_service, mock_content_service)
        result = await service.search_web(query="error query")

        assert result.error == "Search failed"
        assert result.total_results == 0

    @pytest.mark.asyncio
    async def test_extract_content_error_propagation(
        self, mock_search_service, mock_content_service
    ):
        """Test that content extraction errors are propagated correctly."""
        mock_content_service.extract_content.return_value = WebpageContent(
            url="https://error.com",
            title="",
            description="",
            author="",
            published_date="",
            main_content="",
            headings=[],
            links=[],
            images=[],
            metadata={},
            content_type="webpage",
            pagination={},
            length=0,
            error="Extraction failed",
        )

        service = WebExplorerService(mock_search_service, mock_content_service)
        result = await service.extract_webpage_content(url="https://error.com")

        assert result.error == "Extraction failed"
        assert result.url == "https://error.com"
