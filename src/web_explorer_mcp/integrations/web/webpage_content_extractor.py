import re
from typing import Any

import httpx
from bs4 import BeautifulSoup, FeatureNotFound
from loguru import logger


def webpage_content_extractor(
    url: str, max_chars: int = 5000, timeout: int = 15, page: int = 1
) -> dict[str, Any]:
    """
    Extracts and cleans webpage content for a given URL.

    Returns a dictionary with: url, title, main_text, meta_description, article_body,
    headers (list), length, error, page, total_pages, has_next_page.

    Parameters
    ----------
    url : str
        URL of the webpage to fetch and extract.
    max_chars : int, optional
        Maximum characters per page for main_text (default 5000).
    timeout : int, optional
        HTTP request timeout in seconds (default 15).
    page : int, optional
        Page number to return (default 1). Pagination is applied to main_text.

    Notes
    -----
    - Uses httpx and BeautifulSoup to fetch and parse HTML
    - Errors are returned in the `error` field instead of raising
    - meta_description: Page description from meta tags
    - article_body: Primary content from semantic HTML tags (article/main/post-body)
    - main_text: Complementary content from other p/li/td elements (excludes article_body areas)
    - Pagination: main_text is split into pages of max_chars each
    """

    result = {
        "url": url,
        "title": None,
        "main_text": None,
        "meta_description": None,
        "article_body": None,
        "headers": [],
        "length": 0,
        "error": None,
        "page": page,
        "total_pages": 0,
        "has_next_page": False,
    }

    if not url or not isinstance(url, str):
        result["error"] = "A valid url (non-empty string) is required"
        return result

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
    }

    try:
        with httpx.Client(
            timeout=timeout, follow_redirects=True, headers=headers
        ) as client:
            resp = client.get(url)
            resp.raise_for_status()
            html = resp.text

        try:
            soup = BeautifulSoup(html, "lxml")
        except FeatureNotFound:
            logger.warning("lxml parser not available, falling back to html.parser")
            soup = BeautifulSoup(html, "html.parser")

        # Remove unwanted tags (extended list)
        for tag in soup(
            [
                "script",
                "style",
                "noscript",
                "iframe",
                "footer",
                "header",
                "nav",
                "aside",
                "button",
                "form",
                "svg",
            ]
        ):
            tag.decompose()
        for tag in soup.find_all(attrs={"aria-hidden": "true"}):
            tag.decompose()
        for tag in soup.find_all(style=True):
            style = tag.get("style", "")
            if style and ("display:none" in style or "visibility:hidden" in style):
                tag.decompose()

        # Title
        title = soup.title.string.strip() if soup.title and soup.title.string else None
        result["title"] = title

        # Meta description
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if not meta_desc:
            meta_desc = soup.find("meta", property="og:description")
        meta_description = meta_desc.get("content", "").strip() if meta_desc else ""
        result["meta_description"] = meta_description

        # Headers
        headers_list = []
        for h in soup.find_all(["h1", "h2", "h3"]):
            text = h.get_text(strip=True)
            if text:
                headers_list.append({"tag": h.name, "text": text})
        result["headers"] = headers_list

        # Semantic content detection (article/main) - primary content
        article_body = ""
        article = (
            soup.find("article") or soup.find("main") or soup.find(class_="post-body")
        )
        if article:
            # For article_body, include shorter texts like titles (min 10 chars)
            article_min_length = 10
            article_texts = [
                p.get_text(strip=True)
                for p in article.find_all(
                    ["p", "li", "td", "h1", "h2", "h3", "h4", "h5", "h6"]
                )
                if len(p.get_text(strip=True)) > article_min_length
            ]
            article_body = "\n".join(article_texts)
        result["article_body"] = article_body

        # Main text from p, li, td - complementary content (excluding article/main areas)
        min_text_length = 20
        main_blocks = []
        for tag in soup.find_all(["p", "li", "td", "h1", "h2", "h3", "h4", "h5", "h6"]):
            # Skip content that's already in article_body to avoid duplication
            if (
                article
                and tag.find_parent(["article", "main"])
                or tag.find_parent(class_="post-body")
            ):
                continue
            text = tag.get_text(separator=" ", strip=True)
            if text and len(text) > min_text_length:
                main_blocks.append(text)

        main_text = "\n".join(main_blocks)
        # Improved text cleaning
        main_text = re.sub(
            r"\s+", " ", main_text
        )  # Replace any whitespace with single space
        main_text = re.sub(r"\n\s*\n", "\n\n", main_text)  # Normalize paragraphs
        main_text = main_text.strip()

        # Pagination logic
        total_chars = len(main_text)
        total_pages = (total_chars + max_chars - 1) // max_chars  # Ceiling division
        result["total_pages"] = total_pages
        result["has_next_page"] = page < total_pages

        if page < 1:
            result["error"] = "Page number must be 1 or greater"
            return result
        if page > total_pages:
            result["main_text"] = ""
            result["length"] = 0
            return result

        start_idx = (page - 1) * max_chars
        end_idx = min(page * max_chars, total_chars)
        page_text = main_text[start_idx:end_idx]
        if page < total_pages:
            page_text += "..."

        result["main_text"] = page_text
        result["length"] = len(page_text)

        return result

    except httpx.HTTPStatusError as e:
        status = e.response.status_code if e.response is not None else "?"
        result["error"] = f"HTTP error: {status}"
        logger.error(f"HTTP error fetching {url}: {status}")
        return result
    except httpx.RequestError as e:
        result["error"] = f"Connection error: {str(e)}"
        logger.error(f"Request error fetching {url}: {str(e)}")
        return result
    except Exception as e:
        result["error"] = f"Parsing error: {str(e)}"
        logger.exception(f"Unexpected error parsing {url}")
        return result
