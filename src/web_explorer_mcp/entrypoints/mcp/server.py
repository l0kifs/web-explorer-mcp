import asyncio
import importlib.metadata
import signal
from typing import Any

from fastmcp import FastMCP
from loguru import logger

from web_explorer_mcp.config.logging_config import logging_config
from web_explorer_mcp.config.settings import AppSettings
from web_explorer_mcp.entrypoints.mcp.dependencies import create_web_explorer_service

mcp = FastMCP("Web Explorer MCP")

settings = AppSettings()
web_explorer_service = create_web_explorer_service(settings)


async def shutdown_handler(signum, loop):
    """Handle shutdown signals gracefully."""
    logger.info(f"Received signal {signum}, shutting down...")
    try:
        # Stop the playwright service gracefully
        playwright_service = getattr(web_explorer_service, "_playwright_service", None)
        if playwright_service and hasattr(playwright_service, "stop"):
            await playwright_service.stop()
        logger.info("Playwright service stopped successfully")
    except Exception as e:
        logger.error(f"Error stopping playwright service: {e}")

    # Stop the event loop
    loop.stop()


@mcp.tool()
async def web_search_tool(
    query: str, page: int = 1, page_size: int | None = None
) -> dict[str, Any]:
    """
    Perform web search using SearxNG instance.

    This tool searches the web using a local SearxNG instance and returns
    structured search results. It provides title, description, and URL for
    each result with support for pagination. The tool handles errors gracefully
    and returns them in the response rather than raising exceptions.

    Parameters
    ----------
    query : str
        The search query string. Must be non-empty and will be trimmed of
        leading/trailing whitespace. Examples: "python programming",
        "machine learning tutorials", "fastapi documentation".

    page : int, optional
        Page number for pagination, starting from 1. Each page contains
        `page_size` results. Defaults to 1 (first page).

    page_size : int, optional
        Maximum number of results to return per page. If not provided,
        uses the default from application settings. Must be positive.

    Returns
    -------
    dict
        A dictionary containing search results and metadata:
        - query: str - The original search query
        - page: int - The requested page number
        - page_size: int - Results per page
        - total_results: int - Total number of results found by SearxNG
        - results: list[dict] - Search results, each containing:
          - title: str - Result title
          - description: str - Result description/content
          - url: str - Result URL
        - error: str | None - Error message if search failed, None on success

    Examples
    --------
    >>> web_search_tool("python asyncio", page=1, page_size=3)
    {
        'query': 'python asyncio',
        'page': 1,
        'page_size': 3,
        'total_results': 42,
        'results': [
            {
                'title': 'asyncio — Asynchronous I/O',
                'description': 'The asyncio package provides infrastructure...',
                'url': 'https://docs.python.org/3/library/asyncio.html'
            }
        ],
        'error': None
    }

    Notes
    -----
    - Requires a running SearxNG instance at the configured URL
    - The SearxNG URL is configured via application settings
    - Connection errors, timeouts, and HTTP errors are handled gracefully
    - Results are limited by client-side pagination after receiving the response
    - Empty or whitespace-only queries will return an error
    """
    logger.info(
        f"Web search tool called with query='{query}', page={page}, page_size={page_size}"
    )

    # Use default page size from settings if not provided
    if page_size is None:
        page_size = settings.web_search.default_page_size

    result = await web_explorer_service.search_web(
        query=query,
        page=page,
        page_size=page_size,
    )

    # Convert SearchResponse to dict format for backward compatibility
    if result.error:
        return {
            "query": result.query,
            "page": result.page,
            "page_size": result.page_size,
            "total_results": 0,
            "results": [],
            "error": result.error,
        }
    else:
        return {
            "query": result.query,
            "page": result.page,
            "page_size": result.page_size,
            "total_results": result.total_results,
            "results": [
                {
                    "title": r.title,
                    "description": r.description,
                    "url": r.url,
                }
                for r in result.results
            ],
            "error": None,
        }


@mcp.tool()
async def webpage_content_tool(
    url: str,
    max_chars: int | None = None,
    page: int = 1,
    raw_content: bool = False,
) -> dict[str, Any]:
    """
    Extract and clean webpage content for a provided URL.

    This tool extracts full content from webpages using Playwright with JavaScript rendering.
    Content is automatically paginated for display if it exceeds max_chars.

    Parameters
    ----------
    url: str
        The URL to fetch and extract.
    max_chars: int, optional
        Maximum characters per page to include in the main text. If not provided,
        5000 characters are used. Pagination is applied to main_content only.
    page: int, optional
        Page number to return (default 1). Pagination is applied to main_content
        for readability, but full content is always extracted.
    raw_content: bool, optional
        If True, return raw HTML content without processing. Defaults to False.

    Returns
    -------
    dict
        The extractor output with comprehensive webpage data:
        - url: Original URL
        - title: Page title
        - description: Meta description
        - author: Page author (from meta tags)
        - published_date: Publication date
        - main_content: Full extracted text with inline link/image annotations
        - main_text: Paginated content for display (controlled by max_chars and page parameters)
        - headings: Heading structure with levels
        - links: Extracted links with URLs and types
        - images: Extracted images with URLs and alt text
        - metadata: Additional metadata (OpenGraph, Twitter cards, etc.)
        - content_type: Detected content type (article, discussion, code, etc.)
        - pagination: Site pagination info (next_page, prev_page, etc.)
        - length: Length of displayed content (paginated text length)
        - error: Error message if extraction failed
        - page: Current display page number
        - total_pages: Total display pages
        - has_next_page: Whether there are more display pages

    Examples
    --------
    - webpage_content_tool("https://example.com") - Extract with default settings
    - webpage_content_tool("https://example.com", max_chars=1000) - Get concise content
    - webpage_content_tool("https://example.com", page=2) - Get next page of content
    - webpage_content_tool("https://example.com", raw_content=True) - Get raw HTML

    Notes
    -----
    - Pagination applies to main_text field for display purposes
    - Full untruncated content is always available in main_content field
    - Uses Playwright for JavaScript rendering and accurate content extraction
    """
    logger.info(
        f"Webpage content tool called with url='{url}', max_chars={max_chars}, page={page}, raw_content={raw_content}"
    )

    if max_chars is None:
        max_chars = settings.webpage.max_chars

    # Extract full content
    result = await web_explorer_service.extract_webpage_content(
        url=url,
        raw_content=raw_content,
    )

    # Apply pagination for display if requested
    from web_explorer_mcp.business.services import paginate_content

    paginated_text = result.main_content
    display_length = len(result.main_content)
    current_page = page
    total_pages = 0
    has_next = False

    try:
        paginated_text, total_pages, has_next = paginate_content(
            result.main_content, max_chars=max_chars, page=page
        )
        display_length = len(paginated_text)
    except ValueError as e:
        result.error = str(e)
        paginated_text = ""
        display_length = 0
        total_pages = 0
        has_next = False

    # Convert WebpageContent to dict format
    return {
        "url": result.url,
        "title": result.title,
        "description": result.description,
        "author": result.author,
        "published_date": result.published_date,
        "main_content": result.main_content,  # Full content
        "main_text": paginated_text,  # Paginated for display
        "headings": [{"level": h.level, "text": h.text} for h in result.headings],
        "links": [
            {"url": link.url, "text": link.text, "type": link.type}
            for link in result.links
        ],
        "images": [
            {"url": img.url, "alt": img.alt, "title": img.title}
            for img in result.images
        ],
        "metadata": result.metadata,
        "content_type": result.content_type,
        "pagination": result.pagination,
        "length": display_length,
        "error": result.error,
        "page": current_page,
        "total_pages": total_pages,
        "has_next_page": has_next,
    }


def main():
    """Entry point for the MCP server."""
    logging_config(settings.logging)
    version = importlib.metadata.version("web_explorer_mcp")
    logger.info(f"Starting Web Explorer MCP version {version}")
    logger.info(
        f"Configuration loaded: debug={settings.debug}, searxng_url={settings.web_search.searxng_url}"
    )

    # Setup signal handlers for graceful shutdown
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(
            sig, lambda s=sig: asyncio.create_task(shutdown_handler(s, loop))
        )

    try:
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    finally:
        # Ensure cleanup happens
        try:
            playwright_service = getattr(
                web_explorer_service, "_playwright_service", None
            )
            if playwright_service and hasattr(playwright_service, "stop"):
                loop.run_until_complete(playwright_service.stop())
        except Exception as e:
            logger.error(f"Error during final cleanup: {e}")
        loop.close()


if __name__ == "__main__":
    main()
