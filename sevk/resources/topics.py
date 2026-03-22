"""
Topics Resource
"""

from typing import Optional, Dict, Any, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import HttpClient


class Topics:
    """Topics API resource"""

    def __init__(self, client: "HttpClient"):
        self._client = client

    def list(self, audience_id: str) -> Dict[str, Any]:
        """List all topics for an audience"""
        return self._client.get(f"/audiences/{audience_id}/topics")

    def create(
        self,
        audience_id: str,
        name: str,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new topic"""
        data = {"name": name}
        if description is not None:
            data["description"] = description

        return self._client.post(f"/audiences/{audience_id}/topics", data)

    def get(self, audience_id: str, topic_id: str) -> Dict[str, Any]:
        """Get a topic by ID"""
        return self._client.get(f"/audiences/{audience_id}/topics/{topic_id}")

    def update(
        self,
        audience_id: str,
        topic_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update a topic"""
        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description

        return self._client.put(f"/audiences/{audience_id}/topics/{topic_id}", data)

    def delete(self, audience_id: str, topic_id: str) -> None:
        """Delete a topic"""
        self._client.delete(f"/audiences/{audience_id}/topics/{topic_id}")

    def add_contacts(self, audience_id: str, topic_id: str, contact_ids: List[str]) -> Dict[str, Any]:
        """Add contacts to a topic"""
        return self._client.post(
            f"/audiences/{audience_id}/topics/{topic_id}/contacts",
            {"contactIds": contact_ids}
        )

    def remove_contact(self, audience_id: str, topic_id: str, contact_id: str) -> None:
        """Remove a contact from a topic"""
        self._client.delete(f"/audiences/{audience_id}/topics/{topic_id}/contacts/{contact_id}")

    def list_contacts(
        self,
        audience_id: str,
        topic_id: str,
        page: Optional[int] = 1,
        limit: Optional[int] = 20,
    ) -> Dict[str, Any]:
        """List contacts for a topic

        Args:
            audience_id: The audience ID
            topic_id: The topic ID
            page: Page number (default 1)
            limit: Number of results per page (default 20)

        Returns:
            Dict with topic contacts
        """
        params = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit

        return self._client.get(
            f"/audiences/{audience_id}/topics/{topic_id}/contacts",
            params or None,
        )
