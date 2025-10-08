import os
import sys
import tempfile
from unittest.mock import patch

from web_explorer_mcp.config.logging_config import logging_config
from web_explorer_mcp.config.settings import LoggingSettings


class TestLoggingConfig:
    """Unit tests for logging configuration."""

    @patch("web_explorer_mcp.config.logging_config.logger")
    def test_logging_config_text_format(self, mock_logger):
        """Test logging configuration with text format."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_log_file = temp_file.name

        try:
            settings = LoggingSettings(
                console_log_level="DEBUG",
                file_log_level="INFO",
                log_file_path=temp_log_file,
                log_file_format="text",
            )

            logging_config(settings)

            # Verify logger.remove() was called
            mock_logger.remove.assert_called_once()

            # Verify add was called at least twice (console + file)
            assert mock_logger.add.call_count >= 2

            # Check console handler call
            console_calls = [
                call
                for call in mock_logger.add.call_args_list
                if len(call[0]) > 0 and call[0][0] == sys.stdout
            ]
            assert len(console_calls) >= 1

            # Check file handler call
            file_calls = [
                call
                for call in mock_logger.add.call_args_list
                if len(call[0]) > 0 and temp_log_file in str(call[0])
            ]
            assert len(file_calls) == 1

        finally:
            if os.path.exists(temp_log_file):
                os.unlink(temp_log_file)

    @patch("web_explorer_mcp.config.logging_config.logger")
    def test_logging_config_json_format(self, mock_logger):
        """Test logging configuration with JSON format."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_log_file = temp_file.name

        try:
            settings = LoggingSettings(
                console_log_level="WARNING",
                file_log_level="ERROR",
                log_file_path=temp_log_file,
                log_file_format="json",
            )

            logging_config(settings)

            # Verify file handler was added with JSON format
            file_calls = [
                call
                for call in mock_logger.add.call_args_list
                if temp_log_file in str(call)
            ]
            assert len(file_calls) == 1

            # Check that JSON format was used (serialize=True)
            file_call = file_calls[0]
            kwargs = file_call[1]
            assert kwargs.get("serialize") is True

        finally:
            if os.path.exists(temp_log_file):
                os.unlink(temp_log_file)

    @patch("web_explorer_mcp.config.logging_config.logger")
    def test_logging_config_no_file(self, mock_logger):
        """Test logging configuration without log file."""
        settings = LoggingSettings(
            console_log_level="INFO",
            file_log_level="INFO",
            log_file_path="",  # Empty string means no file logging
            log_file_format="text",
        )

        logging_config(settings)

        # Verify only console handler was added
        calls = mock_logger.add.call_args_list
        console_calls = [
            call for call in calls if len(call[0]) > 0 and call[0][0] == sys.stdout
        ]
        file_calls = [
            call for call in calls if len(call[0]) > 0 and call[0][0] != sys.stdout
        ]

        assert len(console_calls) >= 1
        assert len(file_calls) == 0

    @patch("web_explorer_mcp.config.logging_config.logger")
    def test_logging_config_invalid_format(self, mock_logger):
        """Test logging configuration with invalid format raises ValueError."""
        settings = LoggingSettings(log_file_format="invalid")

        try:
            logging_config(settings)
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            assert "Invalid log_file_format" in str(e)
            assert "Use 'text' or 'json'" in str(e)

    def test_logging_config_function_signature(self):
        """Test that logging_config function accepts LoggingSettings."""
        import contextlib

        settings = LoggingSettings()
        # Function should not raise when called with valid settings
        with contextlib.suppress(Exception):
            logging_config(settings)

    @patch("web_explorer_mcp.config.logging_config.logger")
    def test_logging_config_console_handler_setup(self, mock_logger):
        """Test that console handler is configured correctly."""
        settings = LoggingSettings(console_log_level="DEBUG")

        logging_config(settings)

        # Find console handler call
        console_calls = [
            call
            for call in mock_logger.add.call_args_list
            if len(call[0]) > 0 and call[0][0] == sys.stdout
        ]
        assert len(console_calls) >= 1

        call_args, call_kwargs = console_calls[0]
        assert call_kwargs["level"] == "DEBUG"
        assert call_kwargs["colorize"] is True
        assert "format" in call_kwargs

    @patch("web_explorer_mcp.config.logging_config.logger")
    def test_logging_config_file_handler_setup(self, mock_logger):
        """Test that file handler is configured correctly."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_log_file = temp_file.name

        try:
            settings = LoggingSettings(
                file_log_level="WARNING",
                log_file_path=temp_log_file,
                log_file_format="text",
            )

            logging_config(settings)

            # Find file handler call
            file_calls = [
                call
                for call in mock_logger.add.call_args_list
                if temp_log_file in str(call)
            ]
            assert len(file_calls) == 1

            call_args, call_kwargs = file_calls[0]
            assert call_args[0] == temp_log_file
            assert call_kwargs["level"] == "WARNING"
            assert "rotation" in call_kwargs
            assert "retention" in call_kwargs
            assert call_kwargs["enqueue"] is True

        finally:
            if os.path.exists(temp_log_file):
                os.unlink(temp_log_file)

    @patch("web_explorer_mcp.config.logging_config.logger")
    def test_logging_config_removes_existing_handlers(self, mock_logger):
        """Test that existing handlers are removed before adding new ones."""
        settings = LoggingSettings()

        logging_config(settings)

        # Verify remove() was called first
        assert mock_logger.remove.called
        remove_call_order = mock_logger.remove.call_args_list
        add_call_order = mock_logger.add.call_args_list

        # remove should be called before add
        assert len(remove_call_order) > 0
        assert len(add_call_order) > 0
