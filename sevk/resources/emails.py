"""
Emails Resource
"""

from typing import Optional, Dict, Any, List, TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from ..client import HttpClient


class EmailAttachment(TypedDict):
    """Email attachment structure"""
    filename: str  # File name (e.g., "invoice.pdf")
    content: str  # Base64 encoded file content
    contentType: str  # MIME type (e.g., "application/pdf", "image/png")


class Emails:
    """Emails API resource"""

    def __init__(self, client: "HttpClient"):
        self._client = client

    def send(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send a transactional email

        Args:
            params: Dictionary containing email parameters:
                - from: Sender email address
                - to: Recipient email address
                - subject: Email subject
                - html: HTML content (optional)
                - text: Plain text content (optional)
                - reply_to: Reply-to address (optional)
                - cc: CC recipients (optional)
                - bcc: BCC recipients (optional)
                - attachments: List of attachment dicts (optional, max 10, max 10MB total)
                    Each attachment should have:
                    - filename: str
                    - content: str (base64 encoded)
                    - contentType: str

        Returns:
            Dict with 'id' or 'ids' key

        Example:
            >>> # Send with HTML
            >>> sevk.emails.send({
            ...     'to': 'user@example.com',
            ...     'subject': 'Hello',
            ...     'html': '<h1>Hello World</h1>'
            ... })

            >>> # Send with attachments
            >>> sevk.emails.send({
            ...     'to': 'user@example.com',
            ...     'subject': 'Invoice',
            ...     'html': '<p>Please find your invoice attached.</p>',
            ...     'attachments': [{
            ...         'filename': 'invoice.pdf',
            ...         'content': base64_content,
            ...         'contentType': 'application/pdf'
            ...     }]
            ... })
        """
        return self._client.post("/emails", params)

    def get(self, email_id: str) -> Dict[str, Any]:
        """Get an email by ID

        Args:
            email_id: The email ID to retrieve

        Returns:
            Dict with email data
        """
        return self._client.get(f"/emails/{email_id}")

    def send_bulk(self, emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Send multiple emails in bulk

        Args:
            emails: List of email parameter dictionaries (max 100)
                Each email dict should contain the same parameters as send()

        Returns:
            Dict with:
                - success: int (number of successfully queued emails)
                - failed: int (number of failed emails)
                - ids: List[str] (IDs of successfully queued emails)
                - errors: List[Dict] (optional, details of failed emails)

        Example:
            >>> result = sevk.emails.send_bulk([
            ...     {
            ...         'to': 'user1@example.com',
            ...         'subject': 'Hello',
            ...         'html': '<h1>Hello User 1</h1>'
            ...     },
            ...     {
            ...         'to': 'user2@example.com',
            ...         'subject': 'Invoice',
            ...         'html': '<p>Your invoice</p>',
            ...         'attachments': [{
            ...             'filename': 'invoice.pdf',
            ...             'content': base64_content,
            ...             'contentType': 'application/pdf'
            ...         }]
            ...     }
            ... ])
            >>> print(f"Success: {result['success']}, Failed: {result['failed']}")
        """
        return self._client.post("/emails/bulk", {"emails": emails})
