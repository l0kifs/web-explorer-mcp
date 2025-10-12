"""Web search service implementation using SearxNG."""

import httpx
from loguru import logger

from web_explorer_mcp.business.interfaces import WebSearchService
from web_explorer_mcp.models.entities import SearchResponse, SearchResult


class SearxngWebSearchService(WebSearchService):
    """Web search service implementation using SearxNG."""

    def __init__(self, searxng_url: str = "http://127.0.0.1:9011"):
        self.searxng_url = searxng_url

    async def search(
        self,
        query: str,
        page: int = 1,
        page_size: int = 5,
        timeout: int = 15,
    ) -> SearchResponse:
        """
        Perform web search using SearxNG.

        Args:
            query: Search query string
            page: Page number (1-based)
            page_size: Number of results per page
            timeout: Request timeout in seconds

        Returns:
            SearchResponse with results or error
        """
        result = SearchResponse(
            query=query,
            page=page,
            page_size=page_size,
            total_results=0,
            results=[],
            error=None,
        )

        # Validate input
        if not query or not isinstance(query, str) or not query.strip():
            result.error = "Search query must be a non-empty string"
            return result

        if page < 1:
            result.error = "Page number must be greater than 0"
            return result

        if page_size < 1:
            result.error = "Page size must be greater than 0"
            return result

        logger.info(
            f"Starting web search: query='{query.strip()}', searxng_url='{self.searxng_url}', page={page}, page_size={page_size}, timeout={timeout}s"
        )

        # Construct SearxNG search URL
        searxng_search_url = f"{self.searxng_url.rstrip('/')}/search"

        try:
            # Parameters for SearxNG API
            search_params = {"q": query.strip(), "format": "json", "pageno": page}

            logger.debug(f"Performing SearxNG search: {query}, page {page}")

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(searxng_search_url, params=search_params)
                response.raise_for_status()

                search_data = response.json()

                # Extract results from SearxNG response
                searxng_results = search_data.get("results", [])

                # Apply client-side pagination
                start_idx = 0
                end_idx = min(len(searxng_results), page_size)
                paged_results = searxng_results[start_idx:end_idx]

                # Format results
                formatted_results = []
                for res in paged_results:
                    formatted_results.append(
                        SearchResult(
                            title=res.get("title", ""),
                            description=res.get("content", ""),
                            url=res.get("url", ""),
                        )
                    )

                result.total_results = len(searxng_results)
                result.results = formatted_results

                logger.info(
                    f"Web search completed successfully: found {len(searxng_results)} total results, returned {len(formatted_results)} for page {page}"
                )

        except httpx.ConnectError:
            result.error = f"Cannot connect to SearxNG ({self.searxng_url}). Make sure the service is running."
            logger.error(f"Connection error to SearxNG at {self.searxng_url}")
        except httpx.HTTPStatusError as e:
            result.error = f"HTTP error from SearxNG: {e.response.status_code}"
            logger.error(f"HTTP error from SearxNG: {e.response.status_code}")
        except httpx.TimeoutException:
            result.error = f"Request timeout after {timeout} seconds"
            logger.error("Timeout error for SearxNG request")
        except Exception as e:
            result.error = f"Search error: {str(e)}"
            logger.error(f"Unexpected error during search: {str(e)}")

        return result
