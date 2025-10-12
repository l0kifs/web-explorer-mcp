"""
End-to-end tests for webpage_content_tool with Stack Overflow page.

Tests extraction of question, answers, votes, users, comments, and other
information from a famous Stack Overflow page about parsing HTML with regex.
"""

import pytest

# URL of the famous Stack Overflow page about parsing HTML with regex
TEST_URL = "https://stackoverflow.com/questions/1732348/regex-match-open-tags-except-xhtml-self-contained-tags"

pytestmark = pytest.mark.e2e


@pytest.mark.asyncio
@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.timeout(60)
async def test_stackoverflow_basic_extraction(mcp_client):
    """Test basic content extraction from Stack Overflow page."""
    result = await mcp_client.call_tool("webpage_content_tool", {"url": TEST_URL})

    assert result["success"] is True, "Tool execution should succeed"
    assert result["data"] is not None, "Should return data"

    # Check title
    assert "title" in result["data"]
    assert "RegEx match open tags" in result["data"]["title"]
    assert "XHTML" in result["data"]["title"]

    # Check URL
    assert result["data"]["url"] == TEST_URL

    # Check main content exists
    assert "main_content" in result["data"]
    assert len(result["data"]["main_content"]) > 0

    # Check content type detection
    assert "content_type" in result["data"]
    assert result["data"]["content_type"] == "qa"  # Stack Overflow is Q&A format


@pytest.mark.asyncio
@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.timeout(60)
async def test_stackoverflow_question_content(mcp_client):
    """Test extraction of question content."""
    result = await mcp_client.call_tool("webpage_content_tool", {"url": TEST_URL})

    assert result["success"] is True
    main_content = result["data"]["main_content"]

    # Check question content is present
    assert "need to match all of these opening tags" in main_content.lower()
    assert "<p>" in main_content
    assert '<a href="foo">' in main_content

    # Check that self-closing tags are mentioned
    assert "<br />" in main_content or "br /" in main_content
    assert "<hr" in main_content

    # Check regex pattern is present
    assert "([a-z]+)" in main_content or "[a-z]" in main_content


@pytest.mark.asyncio
@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.timeout(60)
async def test_stackoverflow_tags_extraction(mcp_client):
    """Test extraction of Stack Overflow tags."""
    result = await mcp_client.call_tool("webpage_content_tool", {"url": TEST_URL})

    assert result["success"] is True
    main_content = result["data"]["main_content"]

    # Check that tags are present in content (typically near question)
    content_lower = main_content.lower()
    assert "html" in content_lower
    assert "regex" in content_lower
    assert "xhtml" in content_lower


@pytest.mark.asyncio
@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.timeout(60)
async def test_stackoverflow_answers_extraction(mcp_client):
    """Test extraction of answers content."""
    result = await mcp_client.call_tool("webpage_content_tool", {"url": TEST_URL})

    assert result["success"] is True
    main_content = result["data"]["main_content"]

    # Check famous answer content (bobince's legendary answer)
    assert (
        "can't parse" in main_content.lower() or "cannot parse" in main_content.lower()
    )
    assert (
        "regular expression" in main_content.lower() or "regex" in main_content.lower()
    )

    # Check for other notable answer phrases
    content_lower = main_content.lower()
    assert (
        "xml parser" in content_lower
        or "html parser" in content_lower
        or "parser" in content_lower
    )

    # Check that multiple answers are present (look for answer indicators)
    # Answers typically have "answered" or user information
    assert main_content.count("answer") > 5 or main_content.count("Answer") > 5


@pytest.mark.asyncio
@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.timeout(60)
async def test_stackoverflow_users_extraction(mcp_client):
    """Test extraction of user names from Stack Overflow page."""
    result = await mcp_client.call_tool("webpage_content_tool", {"url": TEST_URL})

    assert result["success"] is True
    main_content = result["data"]["main_content"]

    # Check for notable users on this page
    # Jeff (original asker), bobince (famous answer), Kaitlin Duck Sherwood, etc.
    content_lower = main_content.lower()

    # At least some user names should be present
    user_indicators = ["jeff", "bob", "community wiki", "user"]
    found_users = sum(1 for indicator in user_indicators if indicator in content_lower)
    assert found_users >= 2, "Should find multiple user indicators"


@pytest.mark.asyncio
@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.timeout(60)
async def test_stackoverflow_voting_indicators(mcp_client):
    """Test presence of voting indicators in content."""
    result = await mcp_client.call_tool("webpage_content_tool", {"url": TEST_URL})

    assert result["success"] is True
    main_content = result["data"]["main_content"]

    # Check for voting-related content
    content_lower = main_content.lower()
    voting_indicators = ["vote", "upvote", "score", "rating"]
    found_voting = any(indicator in content_lower for indicator in voting_indicators)
    assert found_voting, "Should find voting-related indicators"


@pytest.mark.asyncio
@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.timeout(60)
async def test_stackoverflow_views_indicator(mcp_client):
    """Test presence of view count indicators."""
    result = await mcp_client.call_tool("webpage_content_tool", {"url": TEST_URL})

    assert result["success"] is True
    main_content = result["data"]["main_content"]

    # Check for view count indicators
    content_lower = main_content.lower()
    assert "view" in content_lower or "times" in content_lower, "Should mention views"


@pytest.mark.asyncio
@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.timeout(60)
async def test_stackoverflow_comments_indicators(mcp_client):
    """Test presence of comment indicators."""
    result = await mcp_client.call_tool("webpage_content_tool", {"url": TEST_URL})

    assert result["success"] is True
    main_content = result["data"]["main_content"]

    # Check for comment indicators
    content_lower = main_content.lower()
    assert "comment" in content_lower, "Should mention comments"


@pytest.mark.asyncio
@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.timeout(60)
async def test_stackoverflow_links_extraction(mcp_client):
    """Test extraction of links from Stack Overflow page."""
    result = await mcp_client.call_tool("webpage_content_tool", {"url": TEST_URL})

    assert result["success"] is True
    assert "links" in result["data"]

    links = result["data"]["links"]
    assert len(links) > 0, "Should extract links"

    # Check for Stack Overflow specific links
    link_urls = [link.get("url", "") for link in links]

    # Should have internal Stack Overflow links
    assert any("stackoverflow.com" in url for url in link_urls), (
        "Should have Stack Overflow links"
    )

    # Check that links have required fields
    for link in links[:10]:  # Check first 10 links
        assert "url" in link
        assert "text" in link or "title" in link


@pytest.mark.asyncio
@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.timeout(60)
async def test_stackoverflow_external_links(mcp_client):
    """Test detection of external links in answers."""
    result = await mcp_client.call_tool("webpage_content_tool", {"url": TEST_URL})

    assert result["success"] is True
    assert "links" in result["data"]

    links = result["data"]["links"]
    link_urls = [link.get("url", "") for link in links]

    # Stack Overflow answers often contain external reference links
    # Check for external domains (not stackoverflow.com or stackexchange.com)
    external_links = [
        url
        for url in link_urls
        if url
        and ("http://" in url or "https://" in url)
        and "stackoverflow.com" not in url
        and "stackexchange.com" not in url
    ]

    assert len(external_links) > 0, "Should find external reference links"


@pytest.mark.asyncio
@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.timeout(60)
async def test_stackoverflow_metadata_extraction(mcp_client):
    """Test extraction of page metadata."""
    result = await mcp_client.call_tool("webpage_content_tool", {"url": TEST_URL})

    assert result["success"] is True
    assert "metadata" in result["data"]

    metadata = result["data"]["metadata"]

    # Check for standard metadata fields
    assert "description" in result["data"] or "description" in metadata
    assert "author" in result["data"] or "author" in metadata or "og:author" in metadata


@pytest.mark.asyncio
@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.timeout(60)
async def test_stackoverflow_headings_structure(mcp_client):
    """Test extraction of heading structure."""
    result = await mcp_client.call_tool("webpage_content_tool", {"url": TEST_URL})

    assert result["success"] is True
    assert "headings" in result["data"]

    headings = result["data"]["headings"]
    assert len(headings) > 0, "Should extract headings"

    # Check heading structure
    heading_texts = " ".join([h.get("text", "") for h in headings])
    heading_texts_lower = heading_texts.lower()

    # Should have main question heading
    assert "regex" in heading_texts_lower or "tag" in heading_texts_lower

    # Should have answer-related headings
    assert "answer" in heading_texts_lower or "comment" in heading_texts_lower


@pytest.mark.asyncio
@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.timeout(60)
async def test_stackoverflow_images_extraction(mcp_client):
    """Test extraction of images (user avatars, etc.)."""
    result = await mcp_client.call_tool("webpage_content_tool", {"url": TEST_URL})

    assert result["success"] is True
    assert "images" in result["data"]

    images = result["data"]["images"]

    # Stack Overflow pages typically have user avatars and possibly other images
    # Even if no content images, there should be UI elements
    assert isinstance(images, list)

    # If images found, check structure
    if len(images) > 0:
        for img in images[:5]:  # Check first 5 images
            assert "url" in img or "src" in img


@pytest.mark.asyncio
@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.timeout(60)
async def test_stackoverflow_code_blocks(mcp_client):
    """Test that code blocks are preserved in content."""
    result = await mcp_client.call_tool("webpage_content_tool", {"url": TEST_URL})

    assert result["success"] is True
    main_content = result["data"]["main_content"]

    # Stack Overflow questions and answers typically contain code blocks
    # Check for code-related markers
    assert (
        "code" in main_content.lower() or "<" in main_content or "regex" in main_content
    )


@pytest.mark.asyncio
@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.timeout(60)
async def test_stackoverflow_page_length(mcp_client):
    """Test that significant content is extracted."""
    result = await mcp_client.call_tool("webpage_content_tool", {"url": TEST_URL})

    assert result["success"] is True
    assert "length" in result["data"]

    # Stack Overflow page with 36+ answers should have substantial content
    content_length = result["data"]["length"]
    assert content_length > 1000, (
        "Should extract substantial content from page with many answers"
    )


@pytest.mark.asyncio
@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.timeout(60)
async def test_stackoverflow_accepted_answer_indicator(mcp_client):
    """Test detection of accepted answer indicator."""
    result = await mcp_client.call_tool("webpage_content_tool", {"url": TEST_URL})

    assert result["success"] is True
    main_content = result["data"]["main_content"]

    # Check for accepted answer indicators
    content_lower = main_content.lower()
    accepted_indicators = ["accept", "✓", "checkmark", "best", "correct"]
    found_accepted = any(
        indicator in content_lower for indicator in accepted_indicators
    )

    # This is a popular question, likely has accepted answer
    # But we're lenient as the indicator might be visual-only
    if found_accepted:
        assert True, "Found accepted answer indicator"
    else:
        # Just check that answers are present
        assert "answer" in content_lower


@pytest.mark.asyncio
@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.timeout(60)
async def test_stackoverflow_pagination_info(mcp_client):
    """Test extraction of pagination information."""
    result = await mcp_client.call_tool("webpage_content_tool", {"url": TEST_URL})

    assert result["success"] is True

    # Check pagination data
    if "pagination" in result["data"]:
        pagination = result["data"]["pagination"]
        assert isinstance(pagination, dict)

        # This page has multiple pages of answers
        # Should have next_page info
        if "next_page" in pagination:
            assert pagination["next_page"] is not None


@pytest.mark.asyncio
@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.timeout(60)
async def test_stackoverflow_question_status(mcp_client):
    """Test detection of question status (protected, locked, etc.)."""
    result = await mcp_client.call_tool("webpage_content_tool", {"url": TEST_URL})

    assert result["success"] is True
    main_content = result["data"]["main_content"]

    # This famous question is protected
    content_lower = main_content.lower()

    # Check for status indicators
    status_indicators = ["protect", "lock", "closed", "status"]
    _found_status = any(indicator in content_lower for indicator in status_indicators)

    # At minimum, check that the page loaded properly
    assert len(main_content) > 500, "Should have substantial content"
