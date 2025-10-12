from typing import Literal

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LoggingSettings(BaseModel):
    console_log_level: str = Field(default="INFO", description="Console logging level")
    log_to_console: bool = Field(
        default=False, description="Enable logging to console (stdout)"
    )
    file_log_level: str = Field(default="INFO", description="File logging level")
    log_to_file: bool = Field(default=True, description="Enable logging to file")
    log_file_path: str = Field(default="app.log", description="Path to the log file")
    log_file_format: str = Field(
        default="text", description="Log file format: 'text' or 'json'"
    )


class WebSearchSettings(BaseModel):
    searxng_url: str = Field(
        default="http://127.0.0.1:9011",
        description="Base URL for SearxNG search engine",
    )
    default_page_size: int = Field(
        default=5, description="Default number of search results per page"
    )
    timeout: int = Field(default=15, description="HTTP request timeout in seconds")


class WebpageContentSettings(BaseModel):
    max_chars: int = Field(
        default=5000, description="Default maximum characters for extracted main text"
    )
    timeout: int = Field(
        default=15, description="HTTP request timeout in seconds for webpage fetching"
    )


class PlaywrightSettings(BaseModel):
    connection_url: str | None = Field(
        default="http://127.0.0.1:9012",
        description="Remote Playwright server WebSocket URL (e.g., ws://127.0.0.1:9012/). If set, connects to remote server instead of local browser",
    )
    headless: bool = Field(default=True, description="Run browser in headless mode")
    browser: str = Field(
        default="chromium",
        description="Browser to use: 'chromium', 'firefox', or 'webkit'",
    )
    timeout: int = Field(default=30, description="Page load timeout in seconds")
    wait_for_load_state: Literal["load", "domcontentloaded", "networkidle"] = Field(
        default="load",
        description="Wait condition: 'load', 'domcontentloaded', 'networkidle'",
    )
    viewport_width: int = Field(default=1280, description="Browser viewport width")
    viewport_height: int = Field(default=720, description="Browser viewport height")
    user_agent: str = Field(
        default="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        description="User agent string for the browser",
    )
    large_page_threshold_bytes: int = Field(
        default=50_000,
        description="HTML size threshold in bytes for switching to fast cleaning mode (default: 500KB)",
    )


# Top-level settings class
class AppSettings(BaseSettings):
    debug: bool = Field(default=False, description="Enable debug mode")

    logging: LoggingSettings = Field(
        default_factory=lambda: LoggingSettings(), description="Logging configuration"
    )
    web_search: WebSearchSettings = Field(
        default_factory=lambda: WebSearchSettings(),
        description="Web search configuration",
    )
    webpage: WebpageContentSettings = Field(
        default_factory=lambda: WebpageContentSettings(),
        description="Configuration for webpage content extractor",
    )
    playwright: PlaywrightSettings = Field(
        default_factory=lambda: PlaywrightSettings(),
        description="Configuration for Playwright browser automation",
    )

    model_config = SettingsConfigDict(
        env_prefix="WEB_EXPLORER_MCP_",
        env_nested_delimiter="_",
        case_sensitive=False,
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
    )
