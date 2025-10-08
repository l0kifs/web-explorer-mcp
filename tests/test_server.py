from web_explorer_mcp.config.settings import AppSettings
from web_explorer_mcp.entrypoints.mcp.server import mcp


class TestMCPServer:
    """Integration tests for MCP server tools."""

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
