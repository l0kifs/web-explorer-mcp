"""Business logic services for web exploration operations."""

from web_explorer_mcp.business.interfaces import WebpageContentService, WebSearchService
from web_explorer_mcp.models.entities import SearchResponse, WebpageContent


def paginate_content(
    content: str, max_chars: int = 5000, page: int = 1
) -> tuple[str, int, bool]:
    """
    Paginate text content by character count.

    This utility function splits content into pages based on character count.
    It's used separately from extraction to allow full content extraction
    followed by optional pagination.

    Args:
        content: Full text content to paginate
        max_chars: Maximum characters per page
        page: Page number (1-based)

    Returns:
        Tuple of (page_text, total_pages, has_next_page):
        - page_text: Content for the requested page (with "..." if truncated)
        - total_pages: Total number of pages
        - has_next_page: Whether there are more pages after this one

    Raises:
        ValueError: If page < 1 or max_chars < 1
    """
    if page < 1:
        raise ValueError("Page number must be 1 or greater")
    if max_chars < 1:
        raise ValueError("max_chars must be positive")

    total_chars = len(content)
    if total_chars == 0:
        return ("", 0, False)

    # Calculate total pages (ceiling division)
    total_pages = (total_chars + max_chars - 1) // max_chars
    has_next_page = page < total_pages

    # If page exceeds total pages, return empty
    if page > total_pages:
        return ("", total_pages, False)

    # Extract page content
    start_idx = (page - 1) * max_chars
    end_idx = min(page * max_chars, total_chars)
    page_text = content[start_idx:end_idx]

    # Add continuation indicator if not the last page
    if has_next_page:
        page_text += "..."

    return (page_text, total_pages, has_next_page)


class WebExplorerService:
    """Main service for web exploration operations."""

    def __init__(
        self,
        search_service: WebSearchService,
        content_service: WebpageContentService,
    ):
        self._search_service = search_service
        self._content_service = content_service

    async def search_web(
        self,
        query: str,
        page: int = 1,
        page_size: int | None = None,
    ) -> SearchResponse:
        """
        Search the web using the configured search service.

        Args:
            query: Search query
            page: Page number (1-based)
            page_size: Results per page (uses default if None)

        Returns:
            SearchResponse with results
        """
        if page_size is None:
            page_size = 5  # Default from settings

        return await self._search_service.search(
            query=query,
            page=page,
            page_size=page_size,
        )

    async def extract_webpage_content(
        self,
        url: str,
        raw_content: bool = False,
        timeout: int = 30,
    ) -> WebpageContent:
        """
        Extract full content from a webpage using Playwright.

        This method extracts all available content without pagination.
        Use paginate_content() separately if you need to split the content.

        Args:
            url: URL to extract from
            raw_content: Return raw HTML if True
            timeout: Request timeout in seconds

        Returns:
            WebpageContent with full extracted data
        """
        return await self._content_service.extract_content(
            url=url,
            raw_content=raw_content,
            timeout=timeout,
        )
