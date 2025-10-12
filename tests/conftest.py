"""Pytest configuration and fixtures for web-explorer-mcp tests."""

import pytest


@pytest.fixture
def sample_html():
    """Sample HTML content for testing webpage extraction."""
    return """
    <html>
    <head>
        <title>Test Page Title</title>
        <meta name="description" content="Test page description">
    </head>
    <body>
        <header>
            <h1>Main Header</h1>
        </header>
        <article>
            <h2>Article Title</h2>
            <p>This is content inside an article. It should be extracted as article_body.</p>
            <p>More article content with sufficient length for extraction.</p>
        </article>
        <aside>
            <p>This is sidebar content outside the article.</p>
        </aside>
        <footer>
            <p>Footer content that should be ignored.</p>
        </footer>
    </body>
    </html>
    """


@pytest.fixture
def mock_search_response():
    """Mock response data for web search testing."""
    return {
        "query": "test search",
        "page": 1,
        "page_size": 5,
        "total_results": 3,
        "results": [
            {
                "title": "Test Result 1",
                "description": "Description for test result 1",
                "url": "https://example1.com",
            },
            {
                "title": "Test Result 2",
                "description": "Description for test result 2",
                "url": "https://example2.com",
            },
            {
                "title": "Test Result 3",
                "description": "Description for test result 3",
                "url": "https://example3.com",
            },
        ],
        "error": None,
    }


@pytest.fixture
def mock_webpage_response():
    """Mock response data for webpage content extraction testing."""
    return {
        "url": "https://example.com",
        "title": "Example Page",
        "main_text": "This is the main content of the page.",
        "meta_description": "Example page description",
        "article_body": "Article content from semantic HTML",
        "headers": [
            {"tag": "h1", "text": "Main Header"},
            {"tag": "h2", "text": "Sub Header"},
        ],
        "length": 35,
        "error": None,
        "page": 1,
        "total_pages": 1,
        "has_next_page": False,
    }


@pytest.fixture
def app_settings():
    """Application settings fixture."""
    from web_explorer_mcp.config.settings import AppSettings

    return AppSettings()


@pytest.fixture(autouse=True)
def reset_logger():
    """Reset logger between tests to avoid state pollution."""
    from loguru import logger

    logger.remove()  # Clear all handlers
    yield
    logger.remove()  # Clean up after test


@pytest.fixture(scope="function")
async def mcp_client():
    """
    MCP client fixture for e2e testing.

    Provides a connected MCP client instance using in-memory transport.
    Automatically connects before test and disconnects after.

    Scope: function - each test gets its own isolated client instance
    to avoid state pollution and resource conflicts between tests.

    IMPORTANT: This fixture also ensures proper cleanup of Playwright resources
    by closing the browser context after each test to prevent WebSocket connection
    issues and resource leaks between sequential test runs.
    """
    from tests.mcp_client import MCPClient
    from web_explorer_mcp.entrypoints.mcp.server import mcp, web_explorer_service

    client = MCPClient(mcp)
    await client.connect()

    try:
        yield client
    finally:
        # Disconnect MCP client
        await client.disconnect()

        # Critical: Fully stop Playwright service to prevent connection reuse issues
        # This ensures each test starts with a completely fresh Playwright instance
        # including new browser connection, context, and page
        try:
            content_service = web_explorer_service._content_service  # type: ignore
            if hasattr(content_service, "stop"):
                await content_service.stop()  # type: ignore
                import logging

                logging.info("Playwright service stopped successfully after test")
        except Exception as e:
            # Log but don't fail the test on cleanup errors
            import logging

            logging.warning(f"Error stopping Playwright service: {e}")


# Test markers
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "e2e: mark test as end-to-end test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
