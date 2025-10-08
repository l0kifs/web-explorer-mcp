from unittest.mock import MagicMock, patch

from web_explorer_mcp.integrations.web.web_search_extractor import web_search_extractor


class TestWebSearchExtractor:
    """Unit tests for web_search_extractor function."""

    @patch("web_explorer_mcp.integrations.web.web_search_extractor.httpx.Client")
    def test_successful_search(self, mock_client):
        """Test successful web search with valid results."""
        # Mock SearxNG response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [
                {
                    "title": "Python Programming",
                    "content": "Learn Python programming",
                    "url": "https://python.org",
                },
                {
                    "title": "Python Tutorial",
                    "content": "Python tutorial for beginners",
                    "url": "https://tutorial.python.org",
                },
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        result = web_search_extractor("python programming")

        assert result["query"] == "python programming"
        assert result["page"] == 1
        assert result["page_size"] == 5
        assert result["total_results"] == 2
        assert len(result["results"]) == 2
        assert result["results"][0]["title"] == "Python Programming"
        assert result["results"][0]["description"] == "Learn Python programming"
        assert result["results"][0]["url"] == "https://python.org"
        assert result["error"] is None

    @patch("web_explorer_mcp.integrations.web.web_search_extractor.httpx.Client")
    def test_empty_query(self, mock_client):
        """Test search with empty query."""
        result = web_search_extractor("")

        assert result["error"] == "Search query must be a non-empty string"
        assert result["query"] == ""
        assert result["results"] == []
        assert result["total_results"] == 0
        # Ensure no HTTP request was made
        mock_client.assert_not_called()

    @patch("web_explorer_mcp.integrations.web.web_search_extractor.httpx.Client")
    def test_whitespace_only_query(self, mock_client):
        """Test search with whitespace-only query."""
        result = web_search_extractor("   ")

        assert result["error"] == "Search query must be a non-empty string"
        assert result["query"] == "   "
        assert result["results"] == []
        mock_client.assert_not_called()

    def test_invalid_page_number(self):
        """Test search with invalid page number."""
        result = web_search_extractor("test", page=0)

        assert result["error"] == "Page number must be greater than 0"
        assert result["page"] == 0

    def test_invalid_page_size(self):
        """Test search with invalid page size."""
        result = web_search_extractor("test", page_size=0)

        assert result["error"] == "Page size must be greater than 0"
        assert result["page_size"] == 0

    @patch("web_explorer_mcp.integrations.web.web_search_extractor.httpx.Client")
    def test_connection_error(self, mock_client):
        """Test handling of connection errors."""
        from httpx import ConnectError

        mock_client.return_value.__enter__.return_value.get.side_effect = ConnectError(
            "Connection failed"
        )

        result = web_search_extractor("test query")

        assert "Cannot connect to SearxNG" in result["error"]
        assert result["results"] == []
        assert result["total_results"] == 0

    @patch("web_explorer_mcp.integrations.web.web_search_extractor.httpx.Client")
    def test_http_error(self, mock_client):
        """Test handling of HTTP errors."""
        from httpx import HTTPStatusError

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = HTTPStatusError(
            "404 Client Error", request=MagicMock(), response=mock_response
        )
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        result = web_search_extractor("test query")

        assert "HTTP error from SearxNG: 404" in result["error"]
        assert result["results"] == []
        assert result["total_results"] == 0

    @patch("web_explorer_mcp.integrations.web.web_search_extractor.httpx.Client")
    def test_timeout_error(self, mock_client):
        """Test handling of timeout errors."""
        from httpx import TimeoutException

        mock_client.return_value.__enter__.return_value.get.side_effect = (
            TimeoutException("Request timeout")
        )

        result = web_search_extractor("test query")

        assert "Request timeout after 15 seconds" in result["error"]
        assert result["results"] == []
        assert result["total_results"] == 0

    @patch("web_explorer_mcp.integrations.web.web_search_extractor.httpx.Client")
    def test_custom_searxng_url(self, mock_client):
        """Test search with custom SearxNG URL."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status = MagicMock()
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        custom_url = "http://custom-searxng:8080"
        web_search_extractor("test", searxng_url=custom_url)

        # Verify the correct URL was constructed
        mock_client.return_value.__enter__.return_value.get.assert_called_once()
        call_args = mock_client.return_value.__enter__.return_value.get.call_args
        assert call_args[0][0] == f"{custom_url}/search"

    @patch("web_explorer_mcp.integrations.web.web_search_extractor.httpx.Client")
    def test_pagination(self, mock_client):
        """Test search with pagination."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [
                {
                    "title": "Result 1",
                    "content": "Content 1",
                    "url": "http://example1.com",
                },
                {
                    "title": "Result 2",
                    "content": "Content 2",
                    "url": "http://example2.com",
                },
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        result = web_search_extractor("test", page=2, page_size=2)

        assert result["page"] == 2
        assert result["page_size"] == 2
        # Verify pagination parameters in request
        call_args = mock_client.return_value.__enter__.return_value.get.call_args
        params = call_args[1]["params"]
        assert params["pageno"] == 2

    @patch("web_explorer_mcp.integrations.web.web_search_extractor.httpx.Client")
    def test_client_side_pagination(self, mock_client):
        """Test client-side pagination when SearxNG returns more results than requested."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [
                {
                    "title": f"Result {i}",
                    "content": f"Content {i}",
                    "url": f"http://example{i}.com",
                }
                for i in range(1, 11)  # 10 results
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        result = web_search_extractor("test", page_size=3)

        assert (
            len(result["results"]) == 3
        )  # Only 3 results returned despite 10 available
        assert result["total_results"] == 10  # But total shows all available
        assert result["results"][0]["title"] == "Result 1"
        assert result["results"][2]["title"] == "Result 3"

    @patch("web_explorer_mcp.integrations.web.web_search_extractor.httpx.Client")
    def test_empty_results(self, mock_client):
        """Test search that returns no results."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status = MagicMock()
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        result = web_search_extractor("nonexistent query")

        assert result["total_results"] == 0
        assert result["results"] == []
        assert result["error"] is None

    @patch("web_explorer_mcp.integrations.web.web_search_extractor.httpx.Client")
    def test_malformed_response(self, mock_client):
        """Test handling of malformed JSON response."""
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status = MagicMock()
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        result = web_search_extractor("test")

        assert "Search error" in result["error"]
        assert result["results"] == []
        assert result["total_results"] == 0

    @patch("web_explorer_mcp.integrations.web.web_search_extractor.httpx.Client")
    def test_result_formatting(self, mock_client):
        """Test that results are properly formatted."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [
                {
                    "title": "Test Title",
                    "content": "Test description with content",
                    "url": "https://example.com/test",
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        result = web_search_extractor("test")

        expected_result = {
            "title": "Test Title",
            "description": "Test description with content",
            "url": "https://example.com/test",
        }
        assert result["results"][0] == expected_result

    @patch("web_explorer_mcp.integrations.web.web_search_extractor.httpx.Client")
    def test_query_stripping(self, mock_client):
        """Test that query is properly stripped of whitespace."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status = MagicMock()
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        result = web_search_extractor("  test query  ")

        # Verify the stripped query was used in the request
        call_args = mock_client.return_value.__enter__.return_value.get.call_args
        params = call_args[1]["params"]
        assert params["q"] == "test query"
        assert result["query"] == "  test query  "  # Original query preserved in result
