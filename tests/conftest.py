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


# Test markers
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
