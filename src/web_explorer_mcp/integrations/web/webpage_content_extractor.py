import re
from typing import Any

import httpx
from bs4 import BeautifulSoup, FeatureNotFound
from loguru import logger


def webpage_content_extractor(
    url: str, max_chars: int = 5000, timeout: int = 15
) -> dict[str, Any]:
    """
    Extracts and cleans webpage content for a given URL.

    Returns a dictionary with: url, title, main_text, headers (list), length, error.

    Parameters
    ----------
    url : str
        URL of the webpage to fetch and extract.
    max_chars : int, optional
        Maximum characters to return for main_text (default 5000).
    timeout : int, optional
        HTTP request timeout in seconds (default 15).

    Notes
    -----
    - Uses httpx and BeautifulSoup to fetch and parse HTML
    - Errors are returned in the `error` field instead of raising
    """

    result = {
        "url": url,
        "title": None,
        "main_text": None,
        "headers": [],
        "length": 0,
        "error": None,
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

        # Remove unwanted tags
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

        # Headers
        headers_list = []
        for h in soup.find_all(["h1", "h2", "h3"]):
            text = h.get_text(strip=True)
            if text:
                headers_list.append({"tag": h.name, "text": text})
        result["headers"] = headers_list

        # Main text from p, li, td
        main_blocks = []
        for tag in soup.find_all(["p", "li", "td"]):
            text = tag.get_text(separator=" ", strip=True)
            if text and len(text) > 30:
                main_blocks.append(text)

        main_text = "\n".join(main_blocks)
        main_text = re.sub(r"\n+", "\n", main_text)
        main_text = re.sub(r"\s+", " ", main_text)
        main_text = main_text.strip()

        if len(main_text) > max_chars:
            main_text = main_text[:max_chars] + "..."

        result["main_text"] = main_text
        result["length"] = len(main_text)

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
