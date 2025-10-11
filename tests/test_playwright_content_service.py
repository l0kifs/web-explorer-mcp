"""Unit tests for PlaywrightWebpageContentService."""

from unittest.mock import AsyncMock, patch

import pytest

from web_explorer_mcp.config.settings import PlaywrightSettings
from web_explorer_mcp.integrations.web.playwright_content_service import (
    PlaywrightWebpageContentService,
)
from web_explorer_mcp.models.entities import WebpageContent


class TestPlaywrightWebpageContentService:
    """Unit tests for PlaywrightWebpageContentService."""

    @pytest.fixture
    def settings(self):
        """Create settings instance for testing."""
        return PlaywrightSettings()

    @pytest.fixture
    def service(self, settings):
        """Create service instance for testing."""
        return PlaywrightWebpageContentService(settings)

    @pytest.mark.asyncio
    async def test_invalid_url(self, service):
        """Test handling of invalid URL."""
        result = await service.extract_content("")

        assert isinstance(result, WebpageContent)
        assert result.url == ""
        assert result.error == "A valid url (non-empty string) is required"
        assert result.main_content == ""

    @pytest.mark.asyncio
    async def test_playwright_error_handling(self, service):
        """Test error handling when Playwright fails."""
        mock_page = AsyncMock()
        mock_page.add_init_script = AsyncMock()
        mock_page.goto = AsyncMock(side_effect=Exception("Browser error"))
        mock_page.close = AsyncMock()

        mock_context = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)

        mock_browser = AsyncMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)

        mock_playwright = AsyncMock()
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)

        with patch(
            "web_explorer_mcp.integrations.web.playwright_content_service.async_playwright"
        ) as mock_async_playwright:
            mock_async_playwright.return_value.start = AsyncMock(
                return_value=mock_playwright
            )

            result = await service.extract_content("https://example.com")

            assert isinstance(result, WebpageContent)
            assert result.url == "https://example.com"
            assert result.error is not None
            assert "Playwright extraction error" in result.error
            assert result.main_content == ""
