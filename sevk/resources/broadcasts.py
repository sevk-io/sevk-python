"""
Broadcasts Resource
"""

from typing import Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import HttpClient


class Broadcasts:
    """Broadcasts API resource"""

    def __init__(self, client: "HttpClient"):
        self._client = client

    def list(
        self,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List all broadcasts"""
        params = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        if search is not None:
            params["search"] = search

        return self._client.get("/broadcasts", params or None)

    def get(self, broadcast_id: str) -> Dict[str, Any]:
        """Get a broadcast by ID"""
        return self._client.get(f"/broadcasts/{broadcast_id}")

    def create(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new broadcast"""
        return self._client.post("/broadcasts", params)

    def update(self, broadcast_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a broadcast"""
        return self._client.put(f"/broadcasts/{broadcast_id}", params)

    def delete(self, broadcast_id: str) -> None:
        """Delete a broadcast"""
        self._client.delete(f"/broadcasts/{broadcast_id}")

    def send(self, broadcast_id: str) -> Dict[str, Any]:
        """Send a broadcast"""
        return self._client.post(f"/broadcasts/{broadcast_id}/send")

    def cancel(self, broadcast_id: str) -> Dict[str, Any]:
        """Cancel a broadcast"""
        return self._client.post(f"/broadcasts/{broadcast_id}/cancel")

    def send_test(self, broadcast_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send a test broadcast"""
        return self._client.post(f"/broadcasts/{broadcast_id}/test", params)

    def get_analytics(self, broadcast_id: str) -> Dict[str, Any]:
        """Get analytics for a broadcast"""
        return self._client.get(f"/broadcasts/{broadcast_id}/analytics")

    def get_status(self, broadcast_id: str) -> Dict[str, Any]:
        """Get status for a broadcast

        Args:
            broadcast_id: The broadcast ID

        Returns:
            Dict with broadcast status
        """
        return self._client.get(f"/broadcasts/{broadcast_id}/status")

    def get_emails(
        self,
        broadcast_id: str,
        page: Optional[int] = 1,
        limit: Optional[int] = 20,
    ) -> Dict[str, Any]:
        """Get emails for a broadcast

        Args:
            broadcast_id: The broadcast ID
            page: Page number (default 1)
            limit: Number of results per page (default 20)

        Returns:
            Dict with broadcast emails
        """
        params = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit

        return self._client.get(f"/broadcasts/{broadcast_id}/emails", params or None)

    def estimate_cost(self, broadcast_id: str) -> Dict[str, Any]:
        """Estimate cost for a broadcast

        Args:
            broadcast_id: The broadcast ID

        Returns:
            Dict with cost estimate
        """
        return self._client.get(f"/broadcasts/{broadcast_id}/estimate-cost")

    def list_active(self) -> Dict[str, Any]:
        """List active broadcasts

        Returns:
            Dict with active broadcasts
        """
        return self._client.get("/broadcasts/active")
