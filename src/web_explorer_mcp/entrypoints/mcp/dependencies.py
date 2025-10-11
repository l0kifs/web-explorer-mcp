"""Dependency injection composition for MCP server."""

from web_explorer_mcp.business.services import WebExplorerService
from web_explorer_mcp.config.settings import AppSettings
from web_explorer_mcp.integrations.web.playwright_content_service import (
    PlaywrightWebpageContentService,
)
from web_explorer_mcp.integrations.web.searxng_search_service import (
    SearxngWebSearchService,
)


def create_web_explorer_service(settings: AppSettings) -> WebExplorerService:
    """
    Create WebExplorerService with concrete implementations.

    Args:
        settings: Application settings

    Returns:
        Configured WebExplorerService instance
    """
    search_service = SearxngWebSearchService(
        searxng_url=settings.web_search.searxng_url,
    )

    content_service = PlaywrightWebpageContentService(settings.playwright)

    return WebExplorerService(
        search_service=search_service,
        content_service=content_service,
    )
