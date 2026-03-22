"""
Events Resource
"""

from typing import Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import HttpClient


class Events:
    """Events API resource"""

    def __init__(self, client: "HttpClient"):
        self._client = client

    def list(
        self,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        category: Optional[str] = None,
        type: Optional[str] = None,
        days: Optional[int] = None,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List events

        Args:
            page: Page number
            limit: Number of results per page
            category: Filter by category
            type: Filter by type
            days: Filter by number of days
            search: Search query

        Returns:
            Dict with events data
        """
        params = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        if category is not None:
            params["category"] = category
        if type is not None:
            params["type"] = type
        if days is not None:
            params["days"] = days
        if search is not None:
            params["search"] = search

        return self._client.get("/events", params or None)

    def stats(self) -> Dict[str, Any]:
        """Get event statistics

        Returns:
            Dict with event statistics
        """
        return self._client.get("/events/stats")
