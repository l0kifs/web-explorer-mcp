"""
End-to-end tests for Web Explorer MCP server using MCP client.

These tests verify the complete functionality of the MCP server by making
actual client calls through the FastMCP Client with in-memory transport.
"""

import pytest

pytestmark = pytest.mark.e2e


@pytest.mark.asyncio
async def test_server_ping(mcp_client):
    """Test that server responds to ping requests."""
    result = await mcp_client.ping()
    assert result is True, "Server should respond to ping"


@pytest.mark.asyncio
async def test_list_tools(mcp_client):
    """Test listing available tools on the server."""
    tools = await mcp_client.list_tools()

    # Verify we have tools
    assert len(tools) > 0, "Server should have at least one tool"

    # Verify expected tools are present
    tool_names = [tool["name"] for tool in tools]
    assert "web_search_tool" in tool_names, "web_search_tool should be available"
    assert "webpage_content_tool" in tool_names, (
        "webpage_content_tool should be available"
    )

    # Verify tool structure
    for tool in tools:
        assert "name" in tool, "Tool should have a name"
        assert "description" in tool, "Tool should have a description"
        assert "inputSchema" in tool, "Tool should have an input schema"


@pytest.mark.asyncio
async def test_list_resources(mcp_client):
    """Test listing available resources on the server."""
    resources = await mcp_client.list_resources()

    # Server may or may not have resources - just verify the call works
    assert isinstance(resources, list), "Should return a list of resources"


@pytest.mark.asyncio
async def test_list_prompts(mcp_client):
    """Test listing available prompts on the server."""
    prompts = await mcp_client.list_prompts()

    # Server may or may not have prompts - just verify the call works
    assert isinstance(prompts, list), "Should return a list of prompts"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_web_search_tool_basic(mcp_client):
    """Test basic web search tool functionality."""
    result = await mcp_client.call_tool(
        "web_search_tool", {"query": "python programming", "page": 1, "page_size": 3}
    )

    # Check basic structure
    assert result["success"] is True, "Tool call should succeed"
    assert result["error"] is None, "Should not have an error"

    data = result["data"]
    assert "query" in data, "Response should include query"
    assert data["query"] == "python programming", "Query should match input"
    assert "page" in data, "Response should include page number"
    assert "page_size" in data, "Response should include page size"
    assert "results" in data, "Response should include results"
    assert "error" in data, "Response should include error field"


@pytest.mark.asyncio
async def test_web_search_tool_empty_query(mcp_client):
    """Test web search tool with empty query."""
    result = await mcp_client.call_tool("web_search_tool", {"query": ""})

    # Empty query should be handled gracefully
    data = result["data"]
    assert "error" in data or "query" in data, "Should handle empty query"


@pytest.mark.asyncio
async def test_web_search_tool_pagination(mcp_client):
    """Test web search tool pagination parameters."""
    result = await mcp_client.call_tool(
        "web_search_tool", {"query": "fastmcp", "page": 2, "page_size": 5}
    )

    assert result["success"] is True, "Tool call should succeed"
    data = result["data"]
    assert data["page"] == 2, "Page number should be 2"
    assert data["page_size"] == 5, "Page size should be 5"


@pytest.mark.asyncio
async def test_webpage_content_tool_structure(mcp_client):
    """Test webpage content tool returns proper structure (mocked data)."""
    # For e2e tests, we test the tool call structure, not actual web scraping
    # Actual web scraping with Playwright is tested in integration tests
    result = await mcp_client.call_tool(
        "webpage_content_tool",
        {"url": "data:text/html,<html><body><h1>Test</h1><p>Content</p></body></html>"},
    )

    # Tool should execute and return proper structure
    assert result["success"] is True, "Tool call should succeed"
    data = result["data"]

    # Verify response structure (without requiring specific content)
    assert "url" in data, "Response should include URL"
    assert "title" in data, "Response should include title"
    assert "main_content" in data, "Response should include main content"
    assert "main_text" in data, "Response should include paginated text"
    assert "headings" in data, "Response should include headings"
    assert "links" in data, "Response should include links"
    assert "images" in data, "Response should include images"
    assert "metadata" in data, "Response should include metadata"
    assert "error" in data, "Response should include error field"


@pytest.mark.asyncio
async def test_webpage_content_tool_with_max_chars(mcp_client):
    """Test webpage content extraction with max_chars limit."""
    result = await mcp_client.call_tool(
        "webpage_content_tool", {"url": "https://example.com", "max_chars": 500}
    )

    assert result["success"] is True, "Tool call should succeed"
    data = result["data"]
    assert "main_text" in data, "Response should include paginated text"
    # The paginated text should respect the max_chars limit
    assert data["page"] == 1, "Should return first page by default"


@pytest.mark.asyncio
async def test_webpage_content_tool_pagination(mcp_client):
    """Test webpage content extraction with pagination."""
    result = await mcp_client.call_tool(
        "webpage_content_tool",
        {"url": "https://example.com", "max_chars": 100, "page": 1},
    )

    assert result["success"] is True, "Tool call should succeed"
    data = result["data"]
    assert "page" in data, "Response should include current page"
    assert "total_pages" in data, "Response should include total pages"
    assert "has_next_page" in data, "Response should include has_next_page flag"


@pytest.mark.asyncio
async def test_webpage_content_tool_raw_content(mcp_client):
    """Test webpage content extraction with raw HTML."""
    result = await mcp_client.call_tool(
        "webpage_content_tool", {"url": "https://example.com", "raw_content": True}
    )

    assert result["success"] is True, "Tool call should succeed"
    data = result["data"]
    # Raw content should still have basic structure
    assert "url" in data, "Response should include URL"
    assert "main_content" in data, "Response should include content"


@pytest.mark.asyncio
async def test_webpage_content_tool_invalid_url(mcp_client):
    """Test webpage content tool with invalid URL."""
    result = await mcp_client.call_tool(
        "webpage_content_tool",
        {"url": "https://this-domain-definitely-does-not-exist-12345.com"},
    )

    # Should handle error gracefully
    data = result["data"]
    # Either the tool succeeds with an error in data, or the call itself reports error
    if result["success"]:
        assert data.get("error") is not None, "Should have error for invalid URL"
    else:
        assert result["error"] is not None, "Should report error for invalid URL"


@pytest.mark.asyncio
async def test_call_nonexistent_tool(mcp_client):
    """Test calling a tool that doesn't exist."""
    result = await mcp_client.call_tool("nonexistent_tool", {"param": "value"})

    assert result["success"] is False, "Should fail for nonexistent tool"
    assert result["error"] is not None, "Should have error message"


@pytest.mark.asyncio
async def test_web_search_tool_missing_required_param(mcp_client):
    """Test web search tool with missing required parameter."""
    result = await mcp_client.call_tool("web_search_tool", {})

    # Should fail or handle gracefully
    assert result["success"] is False or "error" in result["data"], (
        "Should handle missing required parameter"
    )


@pytest.mark.asyncio
async def test_multiple_tool_calls_sequential(mcp_client):
    """Test making multiple tool calls in sequence."""
    # First call - list tools
    tools = await mcp_client.list_tools()
    assert len(tools) > 0, "Should have tools"

    # Second call - web search
    result1 = await mcp_client.call_tool(
        "web_search_tool", {"query": "python", "page_size": 2}
    )
    assert result1["success"] is True, "First search should succeed"

    # Third call - another web search
    result2 = await mcp_client.call_tool(
        "web_search_tool", {"query": "fastmcp", "page_size": 2}
    )
    assert result2["success"] is True, "Second search should succeed"

    # Verify queries are different
    assert result1["data"]["query"] != result2["data"]["query"], (
        "Different queries should be processed correctly"
    )


@pytest.mark.asyncio
async def test_client_connection_lifecycle(mcp_client):
    """Test that client maintains connection throughout the test."""
    # Ping at start
    result1 = await mcp_client.ping()
    assert result1 is True, "Initial ping should succeed"

    # Do some work
    tools = await mcp_client.list_tools()
    assert len(tools) > 0, "Should be able to list tools"

    # Ping again
    result2 = await mcp_client.ping()
    assert result2 is True, "Second ping should succeed"
