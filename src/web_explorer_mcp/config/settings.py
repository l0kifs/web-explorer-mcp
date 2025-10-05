from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LoggingSettings(BaseModel):
    console_log_level: str = Field(default="INFO", description="Console logging level")
    file_log_level: str = Field(default="INFO", description="File logging level")
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

    model_config = SettingsConfigDict(
        env_prefix="WEB_EXPLORER_MCP_",
        env_nested_delimiter="_",
        case_sensitive=False,
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
    )
