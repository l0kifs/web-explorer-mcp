"""Business logic interfaces and protocols."""

from typing import Protocol

from web_explorer_mcp.models.entities import SearchResponse, WebpageContent


class WebSearchService(Protocol):
    """Interface for web search operations."""

    async def search(
        self,
        query: str,
        page: int = 1,
        page_size: int = 5,
        timeout: int = 15,
    ) -> SearchResponse:
        """
        Perform web search.

        Args:
            query: Search query string
            page: Page number (1-based)
            page_size: Number of results per page
            timeout: Request timeout in seconds

        Returns:
            SearchResponse with results or error
        """
        ...


class WebpageContentService(Protocol):
    """Interface for webpage content extraction operations."""

    async def extract_content(
        self,
        url: str,
        raw_content: bool = False,
        timeout: int = 30,
        favor_precision: bool = True,
    ) -> WebpageContent:
        """
        Extract full content from webpage without pagination.

        This method extracts all available content from the page including
        text, links, images, metadata, and pagination information.
        Content pagination (character-based splitting) should be handled
        separately using the paginate_content utility function.

        Args:
            url: URL to extract content from
            raw_content: Return raw HTML if True
            timeout: Request timeout in seconds
            favor_precision: Favor precision over recall in content extraction

        Returns:
            WebpageContent with full extracted data or error
        """
        ...
