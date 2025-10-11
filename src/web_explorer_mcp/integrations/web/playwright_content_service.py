import re
import time
from typing import TypedDict
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Comment
from loguru import logger
from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)

from web_explorer_mcp.business.interfaces import WebpageContentService
from web_explorer_mcp.config.settings import PlaywrightSettings
from web_explorer_mcp.models.entities import WebpageContent


class HeadingDict(TypedDict):
    """Type definition for heading dictionary."""

    level: int
    text: str


class PlaywrightWebpageContentService(WebpageContentService):
    """Webpage content extraction service using Playwright for JavaScript rendering."""

    def __init__(self, settings: PlaywrightSettings):
        """Initialize the Playwright service with settings."""
        self.settings = settings
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None

    async def _ensure_browser(self) -> None:
        """Ensure browser is initialized in remote mode."""
        # Connect to remote Playwright server via WebSocket
        if self._browser is None:
            if self._playwright is None:
                self._playwright = await async_playwright().start()

            assert self.settings.connection_url is not None
            logger.info(
                f"Connecting to remote Playwright server at {self.settings.connection_url}"
            )
            self._browser = await self._playwright.chromium.connect(
                self.settings.connection_url
            )
            logger.info("Successfully connected to remote Playwright server")

        if self._context is None:
            self._context = await self._browser.new_context(
                viewport={
                    "width": self.settings.viewport_width,
                    "height": self.settings.viewport_height,
                },
                user_agent=self.settings.user_agent,
                locale="en-US",
                timezone_id="America/New_York",
                extra_http_headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
                    "Cache-Control": "max-age=0",
                },
            )

    async def _get_page(self) -> Page:
        """Get a new page from the browser context."""
        await self._ensure_browser()
        assert self._context is not None  # Ensured by _ensure_browser
        return await self._context.new_page()

    # Elements to remove (boilerplate, navigation, etc.)
    REMOVE_SELECTORS = [
        "script",
        "style",
        "noscript",
        "iframe",
        "nav",
        "header",
        "footer",
        ".nav",
        ".navigation",
        ".menu",
        ".sidebar",
        ".advertisement",
        ".ad",
        ".ads",
        ".cookie-banner",
        ".cookie-notice",
        ".social-share",
        ".related-articles",
        ".recommended",
        ".breadcrumb",
        "[role='banner']",
        "[role='navigation']",
        "[role='complementary']",
    ]

    # Selectors that should NOT be removed (forum posts, discussions)
    PRESERVE_SELECTORS = [
        'article[id^="post_"]',  # Discourse posts (e.g., post_1, post_2)
        ".topic-post",  # Forum posts
        ".comment",  # Comments
        ".reply",  # Replies
        "article[data-post-id]",  # Posts with data attributes
    ]

    # Content container selectors (ordered by priority)
    CONTENT_SELECTORS = [
        "article",
        "main",
        '[role="main"]',
        ".main-content",
        ".content",
        "#main",
        "#content",
        ".post-content",
        ".entry-content",
        ".article-content",
        ".page-content",
    ]

    def _clean_html(
        self, soup: BeautifulSoup, remove_boilerplate: bool = True
    ) -> BeautifulSoup:
        """
        Remove unwanted elements from HTML.

        Args:
            soup: BeautifulSoup object
            remove_boilerplate: Whether to remove boilerplate elements

        Returns:
            Cleaned BeautifulSoup object
        """
        if not remove_boilerplate:
            return soup

        # Estimate HTML size to choose cleaning strategy
        html_size = len(str(soup))
        logger.debug(f"HTML size: {html_size} bytes")

        # For large pages (>1MB), use simplified fast cleaning to avoid performance issues
        use_fast_cleaning = html_size > 1_000_000

        if use_fast_cleaning:
            logger.debug("Using fast cleaning mode for large page")
            return self._clean_html_fast(soup)
        else:
            logger.debug("Using thorough cleaning mode for normal page")
            return self._clean_html_thorough(soup)

    def _clean_html_fast(self, soup: BeautifulSoup) -> BeautifulSoup:
        """
        Fast HTML cleaning for large pages - only removes critical elements.

        Args:
            soup: BeautifulSoup object

        Returns:
            Cleaned BeautifulSoup object
        """
        # Remove comments
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        # Only remove elements that definitely should go, without complex preserve logic
        # This is O(n) instead of O(n*m) for large pages
        critical_tags = ["script", "style", "noscript", "iframe"]
        for tag_name in critical_tags:
            for element in soup.find_all(tag_name):
                element.decompose()

        # Remove navigation/header/footer only if NOT inside article tags
        # This preserves forum/discussion structure
        nav_tags = ["nav", "header", "footer"]
        for tag_name in nav_tags:
            for element in soup.find_all(tag_name):
                # Don't remove if inside article (preserve forum structure)
                if not element.find_parent("article"):
                    element.decompose()

        return soup

    def _clean_html_thorough(self, soup: BeautifulSoup) -> BeautifulSoup:
        """
        Thorough HTML cleaning for normal pages - removes boilerplate with preserve logic.

        Args:
            soup: BeautifulSoup object

        Returns:
            Cleaned BeautifulSoup object
        """
        # Remove comments
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        # Pre-build set of preserved elements and their descendants
        # This is much faster than checking for each element individually
        preserved_elements = set()
        for preserve_selector in self.PRESERVE_SELECTORS:
            for elem in soup.select(preserve_selector):
                preserved_elements.add(elem)
                # Add all descendants to preserved set
                for descendant in elem.descendants:
                    if hasattr(descendant, "name") and descendant.name:
                        preserved_elements.add(descendant)

        # Also preserve all article elements
        for article in soup.find_all("article"):
            preserved_elements.add(article)
            for descendant in article.descendants:
                if hasattr(descendant, "name") and descendant.name:
                    preserved_elements.add(descendant)

        # Remove unwanted elements, but preserve forum posts/comments
        for selector in self.REMOVE_SELECTORS:
            for element in soup.select(selector):
                # Quick check if element is in preserved set or has preserved parent
                if element in preserved_elements:
                    continue

                # Check if any parent is preserved
                should_preserve = False
                parent = element.parent
                while parent and parent.name:
                    if parent in preserved_elements:
                        should_preserve = True
                        break
                    parent = parent.parent

                if not should_preserve:
                    element.decompose()

        # Remove empty elements (only for thorough cleaning)
        for tag in soup.find_all():
            if not tag.get_text(strip=True) and not tag.find_all(
                ["img", "video", "audio"]
            ):
                tag.decompose()

        return soup

    def _find_main_content(self, soup: BeautifulSoup):
        """
        Find main content container using heuristics.

        For forum/discussion pages (like Discourse), returns a container
        that includes all posts. For other pages, returns the main content area.

        Args:
            soup: BeautifulSoup object

        Returns:
            Main content element or body
        """
        # Special handling for forum/discussion pages (e.g., Discourse)
        # Check for multiple posts in a thread using Discourse-specific selectors
        posts = soup.select('article[id^="post_"]')
        if len(posts) > 1:
            # Find common parent that contains all posts
            common_parent = posts[0].parent
            while common_parent and not all(
                post in common_parent.descendants for post in posts
            ):
                common_parent = common_parent.parent

            if common_parent:
                logger.debug(
                    f"Found discussion thread with {len(posts)} posts, using common parent"
                )
                return common_parent

        # Try known content selectors
        for selector in self.CONTENT_SELECTORS:
            content = soup.select_one(selector)
            if content:
                logger.debug(f"Found main content using selector: {selector}")
                return content

        # Fallback: find largest text block
        candidates = []
        for tag in soup.find_all(["div", "section", "article"]):
            text_length = len(tag.get_text(strip=True))
            if text_length > 200:  # Minimum length threshold
                candidates.append((text_length, tag))

        if candidates:
            candidates.sort(reverse=True)
            logger.debug(f"Found main content by text length: {candidates[0][0]} chars")
            return candidates[0][1]

        # Last resort: return body
        logger.debug("Using body as main content")
        return soup.body if soup.body else soup

    async def _extract_js_metadata(self, page: Page) -> dict:
        """
        Extract metadata from JavaScript (OpenGraph, JSON-LD, etc.).

        Args:
            page: Playwright page instance

        Returns:
            Dictionary with extracted metadata
        """
        try:
            js_data = await page.evaluate("""
                () => {
                    const data = {
                        meta: {},
                        jsonLd: [],
                    };
                    
                    // Extract meta tags
                    document.querySelectorAll('meta').forEach(meta => {
                        const property = meta.getAttribute('property') || meta.getAttribute('name');
                        const content = meta.getAttribute('content');
                        if (property && content) {
                            data.meta[property] = content;
                        }
                    });
                    
                    // Extract JSON-LD data
                    document.querySelectorAll('script[type="application/ld+json"]').forEach(script => {
                        try {
                            const jsonData = JSON.parse(script.textContent);
                            data.jsonLd.push(jsonData);
                        } catch (e) {
                            // Ignore parsing errors
                        }
                    });
                    
                    return data;
                }
            """)
            return js_data
        except Exception as e:
            logger.debug(f"Failed to extract JS metadata: {e}")
            return {"meta": {}, "jsonLd": []}

    def _extract_pagination_info(self, soup: BeautifulSoup, base_url: str) -> dict:
        """
        Extract pagination information from the page.

        Args:
            soup: BeautifulSoup object
            base_url: Base URL for resolving relative links

        Returns:
            Dictionary with pagination data
        """
        pagination = {
            "has_pagination": False,
            "current_page": None,
            "total_pages": None,
            "next_page": None,
            "prev_page": None,
            "all_pages": [],
        }

        # Common pagination selectors
        pagination_selectors = [
            ".pagination",
            ".paging",
            ".pager",
            ".page-navigation",
            ".page-nav",
            'nav[aria-label="Pagination"]',
            'nav[aria-label="Page navigation"]',
            'nav[aria-label*="pagination"]',
            'nav[aria-label*="paging"]',
            '[role="navigation"][aria-label*="pagination"]',
            "nav.pagination",
            "div.pagination",
            "ul.pagination",
            ".paginator",
            ".pages",
        ]

        pagination_container = None
        for selector in pagination_selectors:
            pagination_container = soup.select_one(selector)
            if pagination_container:
                logger.debug(f"Found pagination using selector: {selector}")
                break

        if not pagination_container:
            return pagination

        pagination["has_pagination"] = True

        # Extract next page link
        next_keywords = ["next", "next page", "older", "→", "›", "»"]
        for link in pagination_container.find_all("a", href=True):
            link_text = link.get_text(strip=True).lower()
            link_title = (link.get("title") or "").lower()
            link_aria = (link.get("aria-label") or "").lower()

            if any(
                keyword in link_text or keyword in link_title or keyword in link_aria
                for keyword in next_keywords
            ):
                href = link.get("href")
                if isinstance(href, str):
                    pagination["next_page"] = urljoin(base_url, href)
                    logger.debug(f"Found next page: {pagination['next_page']}")
                break

        # Extract previous page link
        prev_keywords = ["prev", "previous", "newer", "←", "‹", "«"]
        for link in pagination_container.find_all("a", href=True):
            link_text = link.get_text(strip=True).lower()
            link_title = (link.get("title") or "").lower()
            link_aria = (link.get("aria-label") or "").lower()

            if any(
                keyword in link_text or keyword in link_title or keyword in link_aria
                for keyword in prev_keywords
            ):
                href = link.get("href")
                if isinstance(href, str):
                    pagination["prev_page"] = urljoin(base_url, href)
                    logger.debug(f"Found prev page: {pagination['prev_page']}")
                break

        # Extract current page and all page links
        current_indicators = []
        for elem in pagination_container.find_all(class_=True):
            classes = elem.get("class")
            if (
                classes
                and isinstance(classes, list)
                and any(c in ["active", "current", "selected"] for c in classes)
            ):
                current_indicators.append(elem)

        for indicator in current_indicators:
            text = indicator.get_text(strip=True)
            if text.isdigit():
                pagination["current_page"] = int(text)
                break

        # Extract all page numbers
        page_links = pagination_container.find_all("a", href=True)
        for link in page_links:
            text = link.get_text(strip=True)
            if text.isdigit():
                page_num = int(text)
                href = link.get("href")
                if isinstance(href, str):
                    page_url = urljoin(base_url, href)
                    if page_url not in [p["url"] for p in pagination["all_pages"]]:
                        pagination["all_pages"].append(
                            {"page": page_num, "url": page_url}
                        )

        # Try to determine total pages
        if pagination["all_pages"]:
            pagination["total_pages"] = max(p["page"] for p in pagination["all_pages"])

        # Look for "Page X of Y" pattern
        page_info_text = pagination_container.get_text()
        page_pattern = re.search(r"page\s+(\d+)\s+of\s+(\d+)", page_info_text.lower())
        if page_pattern:
            pagination["current_page"] = int(page_pattern.group(1))
            pagination["total_pages"] = int(page_pattern.group(2))

        return pagination

    def _extract_text_content(self, content, base_url: str) -> str:
        """
        Extract clean text from content with inline links and images.

        Args:
            content: BeautifulSoup element
            base_url: Base URL for resolving relative URLs

        Returns:
            Clean text content with inline [link](url) and [image: alt](url) annotations
        """
        # Process links inline
        for link in content.find_all("a", href=True):
            href_value = link.get("href")
            if not isinstance(href_value, str):
                continue

            href = str(href_value)
            if href.startswith("#") or href.startswith("javascript:"):
                continue

            full_url = urljoin(base_url, href)
            text = link.get_text(strip=True)

            # Replace link with markdown-style annotation
            if text:
                link.replace_with(f"{text} [→ {full_url}]")
            else:
                link.replace_with(f"[link: {full_url}]")

        # Process images inline
        for img in content.find_all("img"):
            src = img.get("src") or img.get("data-src")
            if not src:
                continue

            full_url = urljoin(base_url, str(src))
            alt = img.get("alt", "")

            # Replace image with annotation
            if alt:
                img.replace_with(f"[image: {alt} @ {full_url}]")
            else:
                img.replace_with(f"[image @ {full_url}]")

        # Remove script, style, and other non-content tags that might have been missed
        for tag in content.find_all(["script", "style", "noscript"]):
            tag.decompose()

        # Get text with proper spacing - use space separator to avoid breaking words
        text = content.get_text(separator=" ", strip=True)

        # Normalize whitespace: collapse multiple spaces, remove excessive newlines
        # Split by newlines first to preserve paragraph structure
        lines = []
        for line in text.split("\n"):
            # Normalize spaces within each line
            line = " ".join(line.split())
            if line:  # Skip empty lines
                lines.append(line)

        # Join with double newlines for readability
        return "\n\n".join(lines)

    def _detect_content_type(self, url: str, soup: BeautifulSoup) -> str:
        """
        Detect content type based on URL and page structure.

        Args:
            url: Page URL
            soup: BeautifulSoup object

        Returns:
            Content type string
        """
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        # Check by domain
        if "github.com" in domain or "gitlab.com" in domain:
            return "code"
        elif "linkedin.com" in domain:
            return "profile"
        elif "wikipedia.org" in domain:
            return "article"
        elif "discourse" in domain or "forum" in domain:
            return "discussion"
        elif "stackoverflow.com" in domain:
            return "qa"

        # Check by structure
        if soup.select_one("article"):
            return "article"
        elif soup.select_one('[itemtype*="Person"]'):
            return "profile"
        elif soup.select_one(".repository-content"):
            return "code"

        return "webpage"

    async def _close_browser(self) -> None:
        """Close browser context (keep browser connection alive for reuse)."""
        # Only close context if it exists, keep browser connection alive
        if self._context:
            await self._context.close()
            self._context = None

    def _extract_links(self, content, base_url: str) -> list[dict[str, str]]:
        """
        Extract links from content.

        Args:
            content: BeautifulSoup element with content
            base_url: Base URL for resolving relative links

        Returns:
            List of link dictionaries
        """
        links = []
        seen_urls = set()

        for link in content.find_all("a", href=True):
            href_value = link.get("href")
            if not isinstance(href_value, str):
                continue

            href = str(href_value)
            text = link.get_text(strip=True)

            # Skip anchors and javascript
            if href.startswith("#") or href.startswith("javascript:"):
                continue

            # Resolve relative URLs
            full_url = urljoin(base_url, href)

            # Avoid duplicates
            if full_url in seen_urls:
                continue
            seen_urls.add(full_url)

            links.append(
                {"url": full_url, "text": text, "type": self._classify_link(full_url)}
            )

        return links

    def _classify_link(self, url: str) -> str:
        """
        Classify link type based on URL.

        Args:
            url: URL to classify

        Returns:
            Link type (external, internal, file, etc.)
        """
        parsed = urlparse(url)
        path_lower = parsed.path.lower()

        if path_lower.endswith(
            (".pdf", ".doc", ".docx", ".xls", ".xlsx", ".zip", ".tar.gz")
        ):
            return "file"
        elif path_lower.endswith((".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp")):
            return "image"
        elif parsed.netloc in ("github.com", "gitlab.com", "bitbucket.org"):
            return "code"
        elif parsed.netloc in ("twitter.com", "linkedin.com", "facebook.com"):
            return "social"
        elif parsed.netloc:
            return "external"
        else:
            return "internal"

    def _extract_images(self, content, base_url: str) -> list[dict[str, str]]:
        """
        Extract images from content.

        Args:
            content: BeautifulSoup element with content
            base_url: Base URL for resolving relative URLs

        Returns:
            List of image dictionaries
        """
        images = []
        seen_urls = set()

        for img in content.find_all("img"):
            src = img.get("src") or img.get("data-src")
            if not src:
                continue

            # Resolve relative URLs
            full_url = urljoin(base_url, str(src))

            # Avoid duplicates
            if full_url in seen_urls:
                continue
            seen_urls.add(full_url)

            images.append(
                {
                    "url": full_url,
                    "alt": img.get("alt", ""),
                    "title": img.get("title", ""),
                }
            )

        return images

    def _extract_headings(self, content) -> list[HeadingDict]:
        """
        Extract headings structure.

        Args:
            content: BeautifulSoup element with content

        Returns:
            List of heading dictionaries with 'level' (int) and 'text' (str)
        """
        headings: list[HeadingDict] = []

        for heading in content.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
            text = heading.get_text(strip=True)
            if text:
                level: int = int(heading.name[1])
                headings.append({"level": level, "text": text})

        return headings

    async def extract_content(
        self,
        url: str,
        raw_content: bool = False,
        timeout: int = 30,
        favor_precision: bool = True,
    ) -> WebpageContent:
        """
        Extract full content from webpage using Playwright for JavaScript rendering.

        This method extracts all available content without character-based pagination.
        Use the paginate_content() utility function separately if needed.

        Args:
            url: URL to extract content from
            raw_content: Return raw HTML if True
            timeout: Request timeout in seconds
            favor_precision: Favor precision over recall in content extraction

        Returns:
            WebpageContent with full extracted data or error
        """
        from web_explorer_mcp.models.entities import (
            WebpageHeading,
            WebpageImage,
            WebpageLink,
        )

        result = WebpageContent(
            url=url,
            title="",
            description="",
            author="",
            published_date="",
            main_content="",
            headings=[],
            links=[],
            images=[],
            metadata={},
            content_type="webpage",
            pagination={},
            length=0,
            error=None,
        )

        if not url or not isinstance(url, str):
            result.error = "A valid url (non-empty string) is required"
            return result

        logger.info(
            f"Starting Playwright webpage content extraction: url='{url}', raw_content={raw_content}, timeout={timeout}s"
        )

        page_instance = None
        start_time = time.time()
        try:
            page_instance = await self._get_page()

            # Add anti-detection script before navigation
            await page_instance.add_init_script("""
                // Override the navigator.webdriver flag
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => false,
                });
                
                // Override navigator.plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                
                // Override navigator.languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
                
                // Add chrome object
                window.chrome = {
                    runtime: {},
                };
                
                // Override permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            """)

            # Navigate with anti-bot detection handling
            # Use shorter timeout and don't wait for everything to load
            logger.debug(
                f"Starting page.goto() with timeout={timeout}s, wait_until='domcontentloaded'"
            )
            try:
                await page_instance.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=timeout * 1000,
                )
                logger.debug("page.goto() completed successfully")
            except Exception as e:
                # If navigation times out, log but continue - page might be partially loaded
                logger.warning(f"Navigation timeout or error (continuing anyway): {e}")

            # Quick check for anti-bot challenges (reduced from 3s to 1s)
            await page_instance.wait_for_timeout(1000)

            # Check if we hit a challenge
            page_content = await page_instance.content()
            if (
                "just a moment" in page_content.lower()
                or "checking your browser" in page_content.lower()
            ):
                logger.info("Detected anti-bot challenge, waiting for completion...")
                await page_instance.wait_for_timeout(
                    3000
                )  # Only wait extra if challenge detected

            # Wait for full load with shorter timeout - but don't fail if it times out
            try:
                await page_instance.wait_for_load_state(
                    self.settings.wait_for_load_state,
                    timeout=5000,  # Further reduced from 10s to 5s
                )
            except Exception as e:
                logger.debug(f"Load state timeout (continuing anyway): {e}")
                # Continue anyway - page might still be usable

            # Simulate human-like interaction (optional, only if not timed out)
            try:
                await page_instance.mouse.move(100, 100)
                await page_instance.wait_for_timeout(200)  # Reduced from 300ms to 200ms
            except Exception as e:
                logger.debug(f"Mouse simulation failed (continuing anyway): {e}")

            # Additional wait for dynamic content (reduced from 2s to 0.5s)
            await page_instance.wait_for_timeout(500)

            logger.debug("Getting page HTML content...")
            html = await page_instance.content()
            logger.debug(f"Got HTML content: {len(html)} characters")

            if raw_content:
                result.main_content = html
                result.length = len(html)
            else:
                # Extract JS metadata first
                logger.debug("Extracting JS metadata...")
                js_metadata = await self._extract_js_metadata(page_instance)
                logger.debug(f"JS metadata extracted: {len(js_metadata)} items")

                # Parse HTML with BeautifulSoup
                logger.debug("Parsing HTML with BeautifulSoup...")
                soup = BeautifulSoup(html, "html.parser")
                logger.debug("BeautifulSoup parsing completed")

                # Detect content type
                logger.debug("Detecting content type...")
                content_type = self._detect_content_type(url, soup)
                logger.debug(f"Detected content type: {content_type}")
                result.content_type = content_type

                # Extract pagination info BEFORE cleaning (needs navigation elements)
                logger.debug("Extracting pagination info...")
                pagination_info = self._extract_pagination_info(soup, url)
                logger.debug(
                    f"Pagination info extracted: {pagination_info.get('has_pagination')}"
                )
                if pagination_info.get("has_pagination"):
                    logger.info(
                        f"Detected pagination: current={pagination_info.get('current_page')}, "
                        f"total={pagination_info.get('total_pages')}, "
                        f"next={bool(pagination_info.get('next_page'))}, "
                        f"prev={bool(pagination_info.get('prev_page'))}"
                    )
                result.pagination = pagination_info

                # Clean HTML and find main content
                logger.debug("Cleaning HTML...")
                cleaned_soup = self._clean_html(soup, remove_boilerplate=True)
                logger.debug("HTML cleaned")

                logger.debug("Finding main content...")
                main_content = self._find_main_content(cleaned_soup)
                logger.debug("Main content found")

                # Extract structured data BEFORE modifying DOM
                logger.debug("Extracting links...")
                links_data = self._extract_links(main_content, url)
                logger.debug(f"Extracted {len(links_data)} links")

                logger.debug("Extracting images...")
                images_data = self._extract_images(main_content, url)
                logger.debug(f"Extracted {len(images_data)} images")

                logger.debug("Extracting headings...")
                headings_data = self._extract_headings(main_content)
                logger.debug(f"Extracted {len(headings_data)} headings")

                # Convert to Pydantic models
                from web_explorer_mcp.models.entities import (
                    WebpageHeading,
                    WebpageImage,
                    WebpageLink,
                )

                logger.debug("Converting to Pydantic models...")
                result.links = [WebpageLink(**link) for link in links_data]
                result.images = [WebpageImage(**img) for img in images_data]
                result.headings = [WebpageHeading(**h) for h in headings_data]
                logger.debug("Pydantic models created")

                # Extract text content with inline links and images
                # Make a copy to avoid modifying the original
                import copy

                logger.debug("Extracting text content...")
                main_content_copy = copy.copy(main_content)
                markdown_content = self._extract_text_content(main_content_copy, url)
                logger.debug(
                    f"Text content extracted: {len(markdown_content)} characters"
                )

                # Extract metadata with fallbacks to JS data
                logger.debug("Extracting metadata...")
                title = ""
                if soup.title and soup.title.string:
                    title = soup.title.string.strip()
                elif js_metadata.get("meta", {}).get("og:title"):
                    title = js_metadata["meta"]["og:title"]
                else:
                    og_title = soup.find("meta", property="og:title")
                    if og_title:
                        content = og_title.get("content")
                        if isinstance(content, str):
                            title = content.strip()
                    else:
                        h1 = soup.find("h1")
                        if h1:
                            title = h1.get_text(strip=True)
                result.title = title

                description = ""
                if js_metadata.get("meta", {}).get("og:description"):
                    description = js_metadata["meta"]["og:description"]
                else:
                    meta_desc = soup.find("meta", attrs={"name": "description"})
                    if meta_desc:
                        content = meta_desc.get("content")
                        if isinstance(content, str):
                            description = content.strip()
                    else:
                        og_desc = soup.find("meta", property="og:description")
                        if og_desc:
                            content = og_desc.get("content")
                            if isinstance(content, str):
                                description = content.strip()
                result.description = description

                # Extract author
                author = ""
                if js_metadata.get("meta", {}).get("article:author"):
                    author = js_metadata["meta"]["article:author"]
                else:
                    author_meta = soup.find("meta", attrs={"name": "author"})
                    if author_meta:
                        content = author_meta.get("content")
                        if isinstance(content, str):
                            author = content.strip()
                result.author = author

                # Extract published date
                published_date = ""
                if js_metadata.get("meta", {}).get("article:published_time"):
                    published_date = js_metadata["meta"]["article:published_time"]
                else:
                    date_meta = soup.find("meta", property="article:published_time")
                    if date_meta:
                        content = date_meta.get("content")
                        if isinstance(content, str):
                            published_date = content.strip()
                result.published_date = published_date

                # Store metadata
                result.metadata = js_metadata.get("meta", {})

                # Set content
                logger.debug("Setting final content...")
                result.main_content = markdown_content or ""
                result.length = len(result.main_content)
                logger.debug("Content extraction completed")

            elapsed_time = time.time() - start_time
            logger.info(
                f"Playwright webpage content extraction completed successfully in {elapsed_time:.2f}s: "
                f"extracted {len(result.main_content)} chars, "
                f"{len(result.links)} links, {len(result.images)} images, "
                f"{len(result.headings)} headings"
            )

        except TimeoutError as e:
            elapsed_time = time.time() - start_time
            result.error = (
                f"Playwright extraction timeout after {elapsed_time:.2f}s: {str(e)}"
            )
            logger.error(
                f"Timeout extracting content from {url} after {elapsed_time:.2f}s: {e}"
            )
        except Exception as e:
            elapsed_time = time.time() - start_time
            result.error = (
                f"Playwright extraction error after {elapsed_time:.2f}s: {str(e)}"
            )
            logger.exception(
                f"Unexpected error extracting content from {url} after {elapsed_time:.2f}s"
            )
        finally:
            if page_instance:
                await page_instance.close()

        return result

    async def stop(self) -> None:
        """Stop the browser completely - call this on application shutdown."""
        if self._context:
            await self._context.close()
            self._context = None
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
