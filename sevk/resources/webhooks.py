"""
Webhooks Resource
"""

from typing import Optional, Dict, Any, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import HttpClient


class Webhooks:
    """Webhooks API resource"""

    def __init__(self, client: "HttpClient"):
        self._client = client

    def list(self) -> Dict[str, Any]:
        """List all webhooks

        Returns:
            Dict with webhooks data
        """
        return self._client.get("/webhooks")

    def get(self, webhook_id: str) -> Dict[str, Any]:
        """Get a webhook by ID

        Args:
            webhook_id: The webhook ID

        Returns:
            Dict with webhook data
        """
        return self._client.get(f"/webhooks/{webhook_id}")

    def create(
        self,
        url: str,
        events: List[str],
        enabled: bool = True,
    ) -> Dict[str, Any]:
        """Create a new webhook

        Args:
            url: The webhook URL
            events: List of event types to subscribe to
            enabled: Whether the webhook is enabled (default True)

        Returns:
            Dict with created webhook data
        """
        data = {
            "url": url,
            "events": events,
            "enabled": enabled,
        }

        return self._client.post("/webhooks", data)

    def update(self, webhook_id: str, **kwargs: Any) -> Dict[str, Any]:
        """Update a webhook

        Args:
            webhook_id: The webhook ID
            **kwargs: Fields to update (url, events, enabled)

        Returns:
            Dict with updated webhook data
        """
        return self._client.put(f"/webhooks/{webhook_id}", kwargs)

    def delete(self, webhook_id: str) -> None:
        """Delete a webhook

        Args:
            webhook_id: The webhook ID
        """
        self._client.delete(f"/webhooks/{webhook_id}")

    def test(self, webhook_id: str) -> Dict[str, Any]:
        """Test a webhook

        Args:
            webhook_id: The webhook ID

        Returns:
            Dict with test result
        """
        return self._client.post(f"/webhooks/{webhook_id}/test")

    def list_events(self) -> Dict[str, Any]:
        """List available webhook events

        Returns:
            Dict with available events
        """
        return self._client.get("/webhooks/events")
