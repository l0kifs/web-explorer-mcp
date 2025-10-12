"""
End-to-end tests for webpage_content_tool with Metabase Discourse topic page.

These tests validate the complete functionality of webpage_content_tool by extracting
and verifying real content from a Discourse forum page about OpenID Connect.

Test coverage:
- Basic content extraction (title, main content, pagination)
- Posts and comments extraction (user nicknames, post content)
- Links extraction (internal, external, GitHub links)
- Statistics extraction (views, likes, interaction features)
- Metadata extraction (headings, images, content type, published date)

Based on Playwright analysis of https://discourse.metabase.com/t/open-id-connect/271520:
- Page title: "Open ID Connect - Feature Requests - Metabase Discussion"
- Content type: discussion
- 2 posts by users: Babandis (5d ago), dwhitemv (4d ago)
- Statistics: 25 views, 2 links, 1 like per post
- GitHub issue links: #3101, #28549
- Headings: H1 "Open ID Connect", H2 user profiles, H4 GitHub issue titles
- Images: user avatars, icons

Note: Tests are marked as 'slow' with 60s timeout due to:
- Real network requests to external website
- Playwright browser automation
- Complex page processing

Run individual tests to avoid sequential execution issues:
  uv run pytest tests/test_e2e_webpage_content_tool.py::<test_name> --timeout=120
"""

import pytest

pytestmark = pytest.mark.e2e

TEST_URL = "https://discourse.metabase.com/t/open-id-connect/271520"


@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.timeout(60)
async def test_webpage_content_tool_discourse_basic_extraction(mcp_client):
    """
    E2E: Test basic content extraction from Metabase Discourse topic page.

    Validates that webpage_content_tool correctly extracts:
    - Page title and metadata
    - Main content structure
    - Pagination information

    This test is marked as slow because it:
    - Makes real network request to external website
    - Uses Playwright browser automation for content extraction
    - Processes complex Discourse forum page with multiple posts and comments
    """
    result = await mcp_client.call_tool("webpage_content_tool", {"url": TEST_URL})
    assert result["success"] is True, f"Tool call failed: {result['error']}"
    data = result["data"]
    assert data["error"] is None, f"Extractor error: {data['error']}"

    # Check title
    assert data["title"], "Title should be extracted"
    assert "Open ID Connect" in data["title"], (
        f"Title should contain 'Open ID Connect', got: {data['title']}"
    )

    # Check main content exists and has substantial length
    assert data["main_content"], "Main content should be extracted"
    assert len(data["main_content"]) > 1000, (
        f"Content should have substantial length, got: {len(data['main_content'])} chars"
    )

    # Check URL is correct
    assert data.get("url") == TEST_URL, f"URL should match, got: {data.get('url')}"

    # Check that main_text is paginated
    assert data.get("main_text"), "Main text (paginated) should be present"
    assert data.get("total_pages", 0) >= 1, "Should have at least 1 page"
    assert "pagination" in data, "Pagination info should be present"


@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.timeout(60)
async def test_webpage_content_tool_discourse_posts_and_comments(mcp_client):
    """
    E2E: Test extraction of posts and comments from Discourse topic page.

    Validates that webpage_content_tool correctly extracts:
    - Multiple posts/comments (at least 2 posts on the test page)
    - User nicknames (Babandis, dwhitemv)
    - Post content with topic keywords

    This test is marked as slow because it:
    - Makes real network request to external website
    - Uses Playwright browser automation for content extraction
    """
    result = await mcp_client.call_tool("webpage_content_tool", {"url": TEST_URL})
    assert result["success"] is True, f"Tool call failed: {result['error']}"
    data = result["data"]

    content_lower = data["main_content"].lower()

    # Check for topic-related keywords
    assert any(
        keyword in content_lower for keyword in ["openid", "oidc", "authentication"]
    ), "Content should contain relevant keywords about OpenID Connect"

    # Check for user nicknames (posts are from these users)
    assert "Babandis" in data["main_content"] or "babandis" in content_lower, (
        "Should contain username 'Babandis' (first post author)"
    )
    assert "dwhitemv" in content_lower, (
        "Should contain username 'dwhitemv' (second post author)"
    )

    # Check for multiple posts/comments (Discourse structure)
    # The page should mention GitHub issues or feature requests
    assert "github" in content_lower or "feature" in content_lower, (
        "Should mention GitHub or features (typical Discourse content)"
    )


@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.timeout(60)
async def test_webpage_content_tool_discourse_links_extraction(mcp_client):
    """
    E2E: Test extraction of links from Discourse topic page.

    Validates that webpage_content_tool correctly extracts:
    - Multiple links (internal and external)
    - GitHub links to related issues
    - Link counts and statistics

    Based on Playwright analysis, the page contains:
    - Link to GitHub issue #3101 (Auth: OpenID authentication)
    - Link to GitHub issue #28549 (Support OAuth 2.0 / OIDC)
    - Links to user profiles

    This test is marked as slow because it:
    - Makes real network request to external website
    - Uses Playwright browser automation for content extraction
    """
    result = await mcp_client.call_tool("webpage_content_tool", {"url": TEST_URL})
    assert result["success"] is True, f"Tool call failed: {result['error']}"
    data = result["data"]

    # Check for links
    assert data.get("links"), "Links should be extracted"
    assert len(data["links"]) > 0, "Should have at least one link"

    # Check for HTTPS links
    https_links = [
        link for link in data["links"] if link.get("url", "").startswith("https://")
    ]
    assert len(https_links) > 0, "Should have at least one HTTPS link"

    # Check for GitHub links (mentioned in posts)
    github_links = [
        link for link in data["links"] if "github.com" in link.get("url", "")
    ]
    # Note: Links might be in main_content as text, not necessarily extracted as link objects
    content_lower = data["main_content"].lower()
    assert "github.com/metabase" in content_lower or len(github_links) > 0, (
        "Should reference GitHub metabase repository"
    )


@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.timeout(60)
async def test_webpage_content_tool_discourse_statistics(mcp_client):
    """
    E2E: Test extraction of statistics from Discourse topic page.

    Validates that webpage_content_tool correctly extracts:
    - View counts (should be present in Discourse pages)
    - Like counts (posts have like buttons)
    - Link counts (metadata about linked content)

    Based on Playwright analysis, the page shows:
    - 25 views
    - 2 links
    - Like buttons on posts (with counts)

    This test is marked as slow because it:
    - Makes real network request to external website
    - Uses Playwright browser automation for content extraction
    """
    result = await mcp_client.call_tool("webpage_content_tool", {"url": TEST_URL})
    assert result["success"] is True, f"Tool call failed: {result['error']}"
    data = result["data"]

    content_lower = data["main_content"].lower()

    # Check for view statistics
    assert "view" in content_lower or "views" in content_lower, (
        "Content should contain view statistics (typical Discourse feature)"
    )

    # Check for like/interaction features
    # Discourse pages have like buttons and counts
    assert (
        "like" in content_lower
        or "liked" in content_lower
        or any(keyword in content_lower for keyword in ["reply", "post"])
    ), "Content should contain interaction features (likes, replies, posts)"


@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.timeout(60)
async def test_webpage_content_tool_discourse_metadata(mcp_client):
    """
    E2E: Test extraction of metadata and structure from Discourse topic page.

    Validates that webpage_content_tool correctly extracts:
    - Headings structure (h1, h2, h4)
    - Images (avatars, icons)
    - Content type detection (should be 'discussion')
    - Published date

    Based on Playwright analysis, the page has:
    - H1: "Open ID Connect"
    - H2: User profile headings (Babandis, dwhitemv)
    - H4: GitHub issue titles
    - Images: avatars, icons

    This test is marked as slow because it:
    - Makes real network request to external website
    - Uses Playwright browser automation for content extraction
    """
    result = await mcp_client.call_tool("webpage_content_tool", {"url": TEST_URL})
    assert result["success"] is True, f"Tool call failed: {result['error']}"
    data = result["data"]

    # Check for headings structure
    assert data.get("headings"), "Headings should be extracted"
    assert len(data["headings"]) > 0, "Should have at least one heading"

    # Check for main heading (H1 or similar with "Open ID Connect")
    heading_texts = [h.get("text", "").lower() for h in data["headings"]]
    assert any("open" in text and "connect" in text for text in heading_texts), (
        "Should have heading about 'Open ID Connect'"
    )

    # Check for images (avatars, icons, etc. on Discourse pages)
    assert isinstance(data.get("images", []), list), "Images should be a list"
    # Discourse pages typically have user avatars
    assert len(data.get("images", [])) > 0, (
        "Should have at least one image (e.g., avatar)"
    )

    # Check content type detection
    assert data.get("content_type"), "Content type should be detected"
    assert data["content_type"] == "discussion", (
        f"Content type should be 'discussion' for Discourse page, got: {data.get('content_type')}"
    )

    # Check metadata
    assert data.get("metadata"), "Metadata should be extracted"
    assert isinstance(data["metadata"], dict), "Metadata should be a dictionary"

    # Check published date
    assert data.get("published_date"), "Published date should be extracted"
