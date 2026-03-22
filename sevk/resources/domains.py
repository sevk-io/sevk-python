"""
Domains Resource
"""

from typing import Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import HttpClient


class Domains:
    """Domains API resource"""

    def __init__(self, client: "HttpClient"):
        self._client = client

    def list(self, verified: Optional[bool] = None) -> Dict[str, Any]:
        """List all domains"""
        params = {}
        if verified is not None:
            params["verified"] = verified

        return self._client.get("/domains", params or None)

    def get(self, domain_id: str) -> Dict[str, Any]:
        """Get a domain by ID"""
        return self._client.get(f"/domains/{domain_id}")

    def create(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new domain

        Args:
            params: Dictionary containing domain parameters:
                - name: Domain name (e.g., "example.com")

        Returns:
            Dict with created domain data
        """
        return self._client.post("/domains", params)

    def update(
        self,
        domain_id: str,
        email: Optional[str] = None,
        from_: Optional[str] = None,
        sender_name: Optional[str] = None,
        click_tracking: Optional[bool] = None,
        open_tracking: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Update a domain

        Args:
            domain_id: The domain ID to update
            email: Email address
            from_: From address
            sender_name: Sender name
            click_tracking: Enable click tracking
            open_tracking: Enable open tracking

        Returns:
            Dict with updated domain data
        """
        data = {}
        if email is not None:
            data["email"] = email
        if from_ is not None:
            data["from"] = from_
        if sender_name is not None:
            data["senderName"] = sender_name
        if click_tracking is not None:
            data["clickTracking"] = click_tracking
        if open_tracking is not None:
            data["openTracking"] = open_tracking

        return self._client.put(f"/domains/{domain_id}", data)

    def delete(self, domain_id: str) -> Dict[str, Any]:
        """Delete a domain by ID

        Args:
            domain_id: The domain ID to delete

        Returns:
            Dict with deletion confirmation
        """
        return self._client.delete(f"/domains/{domain_id}")

    def verify(self, domain_id: str) -> Dict[str, Any]:
        """Verify a domain by ID

        Args:
            domain_id: The domain ID to verify

        Returns:
            Dict with verification status
        """
        return self._client.post(f"/domains/{domain_id}/verify")

    def get_dns_records(self, domain_id: str) -> Dict[str, Any]:
        """Get DNS records for a domain

        Args:
            domain_id: The domain ID

        Returns:
            Dict with DNS records
        """
        return self._client.get(f"/domains/{domain_id}/dns-records")

    def get_regions(self) -> Dict[str, Any]:
        """Get available domain regions

        Returns:
            Dict with available regions
        """
        return self._client.get("/domains/regions")
