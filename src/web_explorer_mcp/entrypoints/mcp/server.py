from typing import Any

from fastmcp import FastMCP

from web_explorer_mcp.config.settings import AppSettings
from web_explorer_mcp.integrations.web.web_search_extractor import web_search_extractor
from web_explorer_mcp.integrations.web.webpage_content_extractor import (
    webpage_content_extractor,
)

mcp = FastMCP("Web Explorer MCP")

settings = AppSettings()


@mcp.tool()
def web_search_tool(
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
    # Use default page size from settings if not provided
    if page_size is None:
        page_size = settings.web_search.default_page_size

    return web_search_extractor(
        query=query,
        searxng_url=settings.web_search.searxng_url,
        page=page,
        page_size=page_size,
        timeout=settings.web_search.timeout,
    )


@mcp.tool()
def webpage_content_tool(url: str, max_chars: int | None = None) -> dict[str, Any]:
    """
    Extract and clean webpage content for a provided URL.

    Parameters
    ----------
    url: str
        The URL to fetch and extract.
    max_chars: int, optional
        Maximum characters to include in the main text. If not provided,
        5000 characters are used.

    Returns
    -------
    dict
        The extractor output: url, title, main_text, headers, length, error
    """
    if max_chars is None:
        max_chars = settings.webpage.max_chars

    return webpage_content_extractor(
        url=url, max_chars=max_chars, timeout=settings.webpage.timeout
    )


def main():
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
