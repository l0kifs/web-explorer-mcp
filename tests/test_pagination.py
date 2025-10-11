"""Unit tests for pagination utility function."""

import pytest

from web_explorer_mcp.business.services import paginate_content


class TestPaginateContent:
    """Test cases for paginate_content utility."""

    def test_empty_content(self):
        """Test pagination with empty content."""
        text, total_pages, has_next = paginate_content("", max_chars=100, page=1)

        assert text == ""
        assert total_pages == 0
        assert has_next is False

    def test_single_page_content(self):
        """Test content that fits in a single page."""
        content = "Short content"
        text, total_pages, has_next = paginate_content(content, max_chars=100, page=1)

        assert text == content
        assert total_pages == 1
        assert has_next is False

    def test_multi_page_content_first_page(self):
        """Test first page of multi-page content."""
        content = "A" * 250  # 250 chars
        text, total_pages, has_next = paginate_content(content, max_chars=100, page=1)

        assert len(text) == 103  # 100 chars + "..."
        assert text.endswith("...")
        assert total_pages == 3
        assert has_next is True

    def test_multi_page_content_middle_page(self):
        """Test middle page of multi-page content."""
        content = "A" * 250  # 250 chars
        text, total_pages, has_next = paginate_content(content, max_chars=100, page=2)

        assert len(text) == 103  # 100 chars + "..."
        assert text.endswith("...")
        assert total_pages == 3
        assert has_next is True

    def test_multi_page_content_last_page(self):
        """Test last page of multi-page content."""
        content = "A" * 250  # 250 chars
        text, total_pages, has_next = paginate_content(content, max_chars=100, page=3)

        assert len(text) == 50  # Remaining 50 chars
        assert not text.endswith("...")
        assert total_pages == 3
        assert has_next is False

    def test_exact_page_boundary(self):
        """Test content that exactly fills pages."""
        content = "A" * 200  # Exactly 2 pages of 100 chars
        text, total_pages, has_next = paginate_content(content, max_chars=100, page=1)

        assert len(text) == 103  # 100 chars + "..."
        assert total_pages == 2
        assert has_next is True

        text, total_pages, has_next = paginate_content(content, max_chars=100, page=2)
        assert len(text) == 100  # Exactly 100 chars
        assert total_pages == 2
        assert has_next is False

    def test_page_out_of_range(self):
        """Test requesting page beyond available pages."""
        content = "A" * 100
        text, total_pages, has_next = paginate_content(content, max_chars=100, page=5)

        assert text == ""
        assert total_pages == 1
        assert has_next is False

    def test_invalid_page_number(self):
        """Test with invalid page number (< 1)."""
        with pytest.raises(ValueError, match="Page number must be 1 or greater"):
            paginate_content("test content", max_chars=100, page=0)

        with pytest.raises(ValueError, match="Page number must be 1 or greater"):
            paginate_content("test content", max_chars=100, page=-1)

    def test_invalid_max_chars(self):
        """Test with invalid max_chars (< 1)."""
        with pytest.raises(ValueError, match="max_chars must be positive"):
            paginate_content("test content", max_chars=0, page=1)

        with pytest.raises(ValueError, match="max_chars must be positive"):
            paginate_content("test content", max_chars=-10, page=1)

    def test_default_max_chars(self):
        """Test with default max_chars parameter."""
        content = "A" * 10000  # Large content
        text, total_pages, has_next = paginate_content(content, max_chars=5000, page=1)

        assert len(text) == 5003  # 5000 + "..."
        assert total_pages == 2
        assert has_next is True

    def test_unicode_content(self):
        """Test pagination with unicode content."""
        content = "Привет мир! " * 50  # Unicode text
        text, total_pages, has_next = paginate_content(content, max_chars=100, page=1)

        assert len(text) <= 103  # Should not exceed max_chars + "..."
        assert total_pages > 0
