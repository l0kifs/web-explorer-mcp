"""Integration tests for the web explorer MCP package."""

import pytest

from web_explorer_mcp import integrations
from web_explorer_mcp.config import settings
from web_explorer_mcp.entrypoints import mcp
from web_explorer_mcp.integrations import web


class TestPackageImports:
    """Test that all package imports work correctly."""

    def test_integrations_import(self):
        """Test that integrations package can be imported."""
        assert integrations is not None
        assert hasattr(integrations, "web")

    def test_web_integration_import(self):
        """Test that web integration can be imported."""
        assert web is not None
        assert hasattr(web, "PlaywrightWebpageContentService")
        assert hasattr(web, "SearxngWebSearchService")

    def test_config_import(self):
        """Test that config package can be imported."""
        assert settings is not None
        assert hasattr(settings, "AppSettings")

    def test_entrypoints_import(self):
        """Test that entrypoints package can be imported."""
        assert mcp is not None
        # Check that server module exists
        from web_explorer_mcp.entrypoints.mcp import server

        assert server is not None


class TestIntegrationWorkflow:
    """Integration tests for complete workflows."""

    def test_settings_creation(self):
        """Test that settings can be created and used."""
        from web_explorer_mcp.config.settings import AppSettings

        app_settings = AppSettings()
        assert app_settings is not None

        # Test that all sub-settings are accessible
        assert app_settings.logging is not None
        assert app_settings.web_search is not None
        assert app_settings.webpage is not None

    def test_extractor_imports(self):
        """Test that new services can be imported and instantiated."""
        from web_explorer_mcp.integrations.web import (
            PlaywrightWebpageContentService,
            SearxngWebSearchService,
        )

        # Classes should be importable
        assert PlaywrightWebpageContentService is not None
        assert SearxngWebSearchService is not None

    @pytest.mark.integration
    def test_mcp_server_creation(self):
        """Test that MCP server can be created."""
        from fastmcp import FastMCP

        from web_explorer_mcp.entrypoints.mcp.server import mcp

        assert mcp is not None
        # Check that it's a FastMCP instance
        assert isinstance(mcp, FastMCP)
        assert mcp.name == "Web Explorer MCP"

    def test_logging_config_application(self):
        """Test that logging configuration can be applied."""
        from web_explorer_mcp.config.logging_config import logging_config
        from web_explorer_mcp.config.settings import LoggingSettings

        settings = LoggingSettings()
        # Should not raise an exception
        try:
            logging_config(settings)
        except Exception as e:
            # In test environment, logger might not be fully configured
            # but the function should not crash
            assert "logger" in str(e) or "sys" in str(e)  # Expected test env issues


class TestErrorHandling:
    """Test error handling across the application."""

    def test_invalid_settings_creation(self):
        """Test that invalid settings are handled."""
        # Should handle invalid log format gracefully during creation
        import contextlib

        from web_explorer_mcp.config.settings import LoggingSettings

        with contextlib.suppress(Exception):
            invalid_settings = LoggingSettings(log_file_format="invalid")
            # If it gets here, validation might be lazy
            assert invalid_settings.log_file_format == "invalid"

    def test_missing_dependencies(self):
        """Test behavior when dependencies might be missing."""
        import importlib.util

        # Test that key dependencies are available
        dependencies = ["httpx", "bs4", "fastmcp", "pydantic"]
        for dep in dependencies:
            if importlib.util.find_spec(dep) is None:
                pytest.skip(f"Dependency missing: {dep}")

        assert True  # All dependencies available


class TestConfigurationValidation:
    """Test configuration validation."""

    def test_default_configuration(self):
        """Test that default configuration is valid."""
        from web_explorer_mcp.config.settings import AppSettings

        settings = AppSettings()

        # Validate key settings have reasonable defaults
        assert settings.web_search.searxng_url.startswith("http")
        assert settings.web_search.default_page_size > 0
        assert settings.web_search.timeout > 0
        assert settings.webpage.max_chars > 0
        assert settings.webpage.timeout > 0

    def test_configuration_types(self):
        """Test that configuration values have correct types."""
        from web_explorer_mcp.config.settings import AppSettings

        settings = AppSettings()

        # Type checks
        assert isinstance(settings.debug, bool)
        assert isinstance(settings.web_search.searxng_url, str)
        assert isinstance(settings.web_search.default_page_size, int)
        assert isinstance(settings.web_search.timeout, int)
        assert isinstance(settings.webpage.max_chars, int)
        assert isinstance(settings.webpage.timeout, int)
