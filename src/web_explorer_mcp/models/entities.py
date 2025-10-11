"""Core entities and data models for the web explorer application."""

from typing import Any

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    """Represents a single web search result."""

    title: str = Field(..., description="Title of the search result")
    description: str = Field(..., description="Description or content snippet")
    url: str = Field(..., description="URL of the result")


class SearchResponse(BaseModel):
    """Response from a web search operation."""

    query: str = Field(..., description="Original search query")
    page: int = Field(..., description="Page number requested")
    page_size: int = Field(..., description="Number of results per page")
    total_results: int = Field(..., description="Total number of results found")
    results: list[SearchResult] = Field(
        default_factory=list, description="List of search results"
    )
    error: str | None = Field(None, description="Error message if operation failed")


class WebpageHeading(BaseModel):
    """Represents a heading with hierarchical level."""

    level: int = Field(..., description="Heading level (1-6)")
    text: str = Field(..., description="Text content of the heading")


class WebpageLink(BaseModel):
    """Represents a link from a webpage."""

    url: str = Field(..., description="URL of the link")
    text: str = Field("", description="Link text")
    type: str = Field(
        "internal", description="Link type (internal, external, file, image, etc.)"
    )


class WebpageImage(BaseModel):
    """Represents an image from a webpage."""

    url: str = Field(..., description="Image URL")
    alt: str = Field("", description="Alt text")
    title: str = Field("", description="Title attribute")


class WebpageContent(BaseModel):
    """Extracted content from a webpage.

    This model provides comprehensive webpage data extraction including
    metadata, structured content, links, images, and pagination information.
    """

    # Original URL
    url: str = Field(..., description="Original URL")

    # Basic metadata
    title: str = Field("", description="Page title")
    description: str = Field("", description="Meta description or page description")
    author: str = Field("", description="Page author (from meta tags)")
    published_date: str = Field("", description="Publication date (from meta tags)")

    # Content
    main_content: str = Field(
        "", description="Main text content with inline annotations"
    )

    # Structured data
    links: list[WebpageLink] = Field(
        default_factory=list, description="Extracted links"
    )
    images: list[WebpageImage] = Field(
        default_factory=list, description="Extracted images"
    )
    headings: list[WebpageHeading] = Field(
        default_factory=list, description="Heading structure with levels"
    )

    # Metadata and classification
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata (og, twitter, etc.)"
    )
    content_type: str = Field(
        "webpage", description="Content type (article, discussion, code, etc.)"
    )

    # Pagination info
    pagination: dict[str, Any] = Field(
        default_factory=dict,
        description="Pagination information from the page (next_page, prev_page, etc.)",
    )

    # Status and statistics
    length: int = Field(0, description="Length of main_content in characters")
    error: str | None = Field(None, description="Error message if extraction failed")
