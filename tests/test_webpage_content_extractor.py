from unittest.mock import MagicMock, patch

from web_explorer_mcp.integrations.web.webpage_content_extractor import (
    webpage_content_extractor,
)


class TestWebpageContentExtractor:
    """Unit tests for webpage_content_extractor function."""

    @patch("web_explorer_mcp.integrations.web.webpage_content_extractor.httpx.Client")
    def test_basic_extraction(self, mock_client):
        """Test basic webpage content extraction."""
        # Mock the HTTP response
        mock_response = MagicMock()
        mock_response.text = """
        <html>
        <head><title>Test Page</title></head>
        <body>
        <p>This is a test paragraph.</p>
        <p>Another paragraph with content.</p>
        </body>
        </html>
        """
        mock_response.raise_for_status = MagicMock()
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        result = webpage_content_extractor("https://example.com")

        assert result["url"] == "https://example.com"
        assert result["title"] == "Test Page"
        assert "This is a test paragraph" in result["main_text"]
        assert result["error"] is None
        assert result["page"] == 1
        assert result["total_pages"] >= 1
        assert isinstance(result["has_next_page"], bool)

    @patch("web_explorer_mcp.integrations.web.webpage_content_extractor.httpx.Client")
    def test_pagination_first_page(self, mock_client):
        """Test pagination on first page."""
        # Create long content
        long_text = "A" * 200  # 200 characters
        mock_response = MagicMock()
        mock_response.text = f"<html><body><p>{long_text}</p></body></html>"
        mock_response.raise_for_status = MagicMock()
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        result = webpage_content_extractor("https://example.com", max_chars=100, page=1)

        assert result["page"] == 1
        assert result["total_pages"] == 2  # 200 chars / 100 = 2 pages
        assert result["has_next_page"] is True
        assert len(result["main_text"]) == 103  # 100 + "..."
        assert result["main_text"].endswith("...")

    @patch("web_explorer_mcp.integrations.web.webpage_content_extractor.httpx.Client")
    def test_pagination_last_page(self, mock_client):
        """Test pagination on last page."""
        long_text = "A" * 200
        mock_response = MagicMock()
        mock_response.text = f"<html><body><p>{long_text}</p></body></html>"
        mock_response.raise_for_status = MagicMock()
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        result = webpage_content_extractor("https://example.com", max_chars=100, page=2)

        assert result["page"] == 2
        assert result["total_pages"] == 2
        assert result["has_next_page"] is False
        assert len(result["main_text"]) == 100  # Exactly 100, no "..."
        assert not result["main_text"].endswith("...")

    @patch("web_explorer_mcp.integrations.web.webpage_content_extractor.httpx.Client")
    def test_pagination_page_out_of_range(self, mock_client):
        """Test pagination with page number beyond total pages."""
        short_text = "This is a longer text that exceeds the minimum length requirement for extraction."
        mock_response = MagicMock()
        mock_response.text = f"<html><body><p>{short_text}</p></body></html>"
        mock_response.raise_for_status = MagicMock()
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        result = webpage_content_extractor("https://example.com", max_chars=100, page=5)

        assert result["page"] == 5
        assert result["total_pages"] == 1  # Short text fits in 1 page
        assert result["has_next_page"] is False
        assert result["main_text"] == ""
        assert result["length"] == 0

    def test_invalid_page_number(self):
        """Test with invalid page number (less than 1)."""
        result = webpage_content_extractor("https://example.com", page=0)

        assert result["error"] == "Page number must be 1 or greater"
        assert result["page"] == 0

    def test_invalid_url(self):
        """Test with invalid URL."""
        result = webpage_content_extractor("")

        assert result["error"] == "A valid url (non-empty string) is required"

    @patch("web_explorer_mcp.integrations.web.webpage_content_extractor.httpx.Client")
    def test_article_body_and_main_text_separation(self, mock_client):
        """Test that article_body and main_text don't duplicate content."""
        # HTML with article containing paragraphs and additional content outside
        html_content = """
        <html>
        <body>
        <article>
        <h1>Article Title</h1>
        <p>This is content inside the article. It should appear in article_body.</p>
        <p>Another paragraph in the article with substantial content.</p>
        </article>
        <div class="sidebar">
        <p>This is sidebar content outside the article. It should appear in main_text.</p>
        </div>
        </body>
        </html>
        """
        mock_response = MagicMock()
        mock_response.text = html_content
        mock_response.raise_for_status = MagicMock()
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        result = webpage_content_extractor("https://example.com")

        # Check that article_body contains article content
        assert "Article Title" in result["article_body"]
        assert "This is content inside the article" in result["article_body"]
        assert "Another paragraph in the article" in result["article_body"]

        # Check that main_text contains only content outside article
        assert "sidebar content outside the article" in result["main_text"]
        assert "This is content inside the article" not in result["main_text"]

        # Check that they are separate
        assert result["article_body"] != result["main_text"]
        assert len(result["article_body"]) > 0
        assert len(result["main_text"]) > 0

    @patch("web_explorer_mcp.integrations.web.webpage_content_extractor.httpx.Client")
    def test_main_content_only_in_article_body(self, mock_client):
        """Test page with only article content - main_text should be empty."""
        html_content = """
        <html>
        <body>
        <article>
        <h1>Main Article</h1>
        <p>This is the main content of the article.</p>
        <p>More content in the same article.</p>
        </article>
        </body>
        </html>
        """
        mock_response = MagicMock()
        mock_response.text = html_content
        mock_response.raise_for_status = MagicMock()
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        result = webpage_content_extractor("https://example.com")

        assert "Main Article" in result["article_body"]
        assert "main content of the article" in result["article_body"]
        assert result["main_text"] == ""  # No content outside article

    @patch("web_explorer_mcp.integrations.web.webpage_content_extractor.httpx.Client")
    def test_no_article_content_only_main_text(self, mock_client):
        """Test page without article/main - all content goes to main_text."""
        html_content = """
        <html>
        <body>
        <div class="content">
        <h1>Page Title With Sufficient Length</h1>
        <p>This content is not in an article tag.</p>
        <p>More content outside semantic containers.</p>
        </div>
        </body>
        </html>
        """
        mock_response = MagicMock()
        mock_response.text = html_content
        mock_response.raise_for_status = MagicMock()
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        result = webpage_content_extractor("https://example.com")

        assert result["article_body"] == ""  # No article found
        assert "Page Title With Sufficient Length" in result["main_text"]
        assert "not in an article tag" in result["main_text"]

    @patch("web_explorer_mcp.integrations.web.webpage_content_extractor.httpx.Client")
    def test_main_element_instead_of_article(self, mock_client):
        """Test using main element instead of article."""
        html_content = """
        <html>
        <body>
        <main>
        <h1>Main Content</h1>
        <p>Content inside main element.</p>
        </main>
        <div>
        <p>Content outside main element.</p>
        </div>
        </body>
        </html>
        """
        mock_response = MagicMock()
        mock_response.text = html_content
        mock_response.raise_for_status = MagicMock()
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        result = webpage_content_extractor("https://example.com")

        assert "Main Content" in result["article_body"]
        assert "Content inside main element" in result["article_body"]
        assert "Content outside main element" in result["main_text"]
        assert "Content inside main element" not in result["main_text"]

    @patch("web_explorer_mcp.integrations.web.webpage_content_extractor.httpx.Client")
    def test_aria_hidden_removal(self, mock_client):
        """Test removal of aria-hidden elements."""
        html_content = """
        <html>
        <body>
        <div aria-hidden="true">Hidden content</div>
        <p>This is visible content that meets the minimum length requirement for extraction.</p>
        </body>
        </html>
        """
        mock_response = MagicMock()
        mock_response.text = html_content
        mock_response.raise_for_status = MagicMock()
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        result = webpage_content_extractor("https://example.com")

        assert "Hidden content" not in result["main_text"]
        assert (
            "This is visible content that meets the minimum length requirement"
            in result["main_text"]
        )

    @patch("web_explorer_mcp.integrations.web.webpage_content_extractor.httpx.Client")
    def test_style_hidden_removal(self, mock_client):
        """Test removal of elements with hidden styles."""
        html_content = """
        <html>
        <body>
        <div style="display: none;">Hidden content</div>
        <div style="visibility: hidden;">Also hidden</div>
        <p>This is visible content that meets the minimum length requirement for extraction.</p>
        </body>
        </html>
        """
        mock_response = MagicMock()
        mock_response.text = html_content
        mock_response.raise_for_status = MagicMock()
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        result = webpage_content_extractor("https://example.com")

        assert "Hidden content" not in result["main_text"]
        assert "Also hidden" not in result["main_text"]
        assert (
            "This is visible content that meets the minimum length requirement"
            in result["main_text"]
        )

    @patch("web_explorer_mcp.integrations.web.webpage_content_extractor.httpx.Client")
    def test_http_status_error(self, mock_client):
        """Test handling of HTTP status errors."""
        from httpx import HTTPStatusError

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = HTTPStatusError(
            "404 Client Error", request=MagicMock(), response=mock_response
        )
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        result = webpage_content_extractor("https://example.com")

        assert "HTTP error: 404" in result["error"]

    @patch("web_explorer_mcp.integrations.web.webpage_content_extractor.httpx.Client")
    def test_request_error(self, mock_client):
        """Test handling of request errors."""
        from httpx import RequestError

        mock_client.return_value.__enter__.return_value.get.side_effect = RequestError(
            "Network error"
        )

        result = webpage_content_extractor("https://example.com")

        assert "Connection error: Network error" in result["error"]

    @patch("web_explorer_mcp.integrations.web.webpage_content_extractor.httpx.Client")
    def test_parsing_error(self, mock_client):
        """Test handling of parsing errors."""
        mock_response = MagicMock()
        mock_response.text = "Invalid HTML content"
        mock_response.raise_for_status = MagicMock()
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        # Mock BeautifulSoup to raise an exception
        with patch(
            "web_explorer_mcp.integrations.web.webpage_content_extractor.BeautifulSoup"
        ) as mock_bs:
            mock_bs.side_effect = Exception("Parsing failed")

            result = webpage_content_extractor("https://example.com")

            assert "Parsing error: Parsing failed" in result["error"]
