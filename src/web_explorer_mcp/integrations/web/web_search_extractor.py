from typing import Any

import httpx
from loguru import logger


def web_search_extractor(
    query: str,
    searxng_url: str = "http://127.0.0.1:8080",
    page: int = 1,
    page_size: int = 5,
    timeout: int = 15,
) -> dict[str, Any]:
    """
    Performs web search using local SearxNG API.

    Returns a structured dictionary with search results including title,
    description, and URL for each result. Supports pagination.

    Parameters
    ----------
    query : str
        Search query string. Must be non-empty.
    searxng_url : str, optional
        Base URL of the SearxNG instance. Defaults to "http://127.0.0.1:8080".
    page : int, optional
        Page number starting from 1. Defaults to 1.
    page_size : int, optional
        Number of results per page. Defaults to 5.
    timeout : int, optional
        Request timeout in seconds. Defaults to 15.

    Returns
    -------
    dict[str, Any]
        A dictionary containing:
        - query: str - The original search query
        - page: int - The page number
        - page_size: int - Results per page
        - total_results: int - Total number of results found
        - results: list[dict] - List of search results, each containing:
          - title: str - Result title
          - description: str - Result description/content
          - url: str - Result URL
        - error: str | None - Error message if any occurred

    Examples
    --------
    >>> web_search_extractor("python programming", page=1, page_size=3)
    {
        'query': 'python programming',
        'page': 1,
        'page_size': 3,
        'total_results': 15,
        'results': [
            {
                'title': 'Python Programming Language',
                'description': 'Official Python website...',
                'url': 'https://python.org'
            }
        ],
        'error': None
    }

    Notes
    -----
    - Requires a running SearxNG instance at the specified URL
    - Returns error messages in the 'error' field instead of raising exceptions
    - Pagination is handled client-side by limiting the returned results
    - All HTTP errors and connection issues are caught and returned as error messages
    """
    result = {
        "query": query,
        "page": page,
        "page_size": page_size,
        "total_results": 0,
        "results": [],
        "error": None,
    }

    # Validate input
    if not query or not isinstance(query, str) or not query.strip():
        result["error"] = "Search query must be a non-empty string"
        return result

    if page < 1:
        result["error"] = "Page number must be greater than 0"
        return result

    if page_size < 1:
        result["error"] = "Page size must be greater than 0"
        return result

    # Construct SearxNG search URL
    searxng_search_url = f"{searxng_url.rstrip('/')}/search"

    try:
        # Parameters for SearxNG API
        search_params = {"q": query.strip(), "format": "json", "pageno": page}

        logger.debug(f"Performing SearxNG search: {query}, page {page}")

        with httpx.Client(timeout=timeout) as client:
            response = client.get(searxng_search_url, params=search_params)
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
                    {
                        "title": res.get("title", ""),
                        "description": res.get("content", ""),
                        "url": res.get("url", ""),
                    }
                )

            result["total_results"] = len(searxng_results)
            result["results"] = formatted_results

            logger.debug(
                f"Found {len(formatted_results)} results out of {len(searxng_results)} total"
            )

        return result

    except httpx.ConnectError:
        result["error"] = (
            f"Cannot connect to SearxNG ({searxng_url}). Make sure the service is running."
        )
        logger.error(f"Connection error to SearxNG at {searxng_url}")
        return result
    except httpx.HTTPStatusError as e:
        result["error"] = f"HTTP error from SearxNG: {e.response.status_code}"
        logger.error(f"HTTP error from SearxNG: {e.response.status_code}")
        return result
    except httpx.TimeoutException:
        result["error"] = f"Request timeout after {timeout} seconds"
        logger.error("Timeout error for SearxNG request")
        return result
    except Exception as e:
        result["error"] = f"Search error: {str(e)}"
        logger.error(f"Unexpected error during search: {str(e)}")
        return result
