from typing import Dict, List, Literal, Optional, TypedDict

from ._base import Resource
from .types import DeletedResponse, PaginationParams

WebhookEventType = Literal[
    "email.sent",
    "email.delivered",
    "email.opened",
    "email.clicked",
    "email.bounced",
    "email.complained",
    "email.rejected",
    "email.delayed",
    "email.rendering_failed",
    "contact.subscribed",
    "contact.unsubscribed",
    "broadcast.started",
    "broadcast.finished",
    "email.received",
]
WebhookCategory = Literal["email", "subscription", "broadcast"]


class _CreateWebhookParamsRequired(TypedDict):
    url: str
    events: List[WebhookEventType]


class CreateWebhookParams(_CreateWebhookParamsRequired, total=False):
    enabled: bool


class UpdateWebhookParams(TypedDict, total=False):
    url: str
    events: List[WebhookEventType]
    enabled: bool


class WebhookEventDefinition(TypedDict):
    name: str
    description: str
    category: WebhookCategory


class WebhookEventsResponse(TypedDict):
    items: List[WebhookEventType]
    events: Dict[str, WebhookEventDefinition]


class _WebhookCommonRequired(TypedDict):
    id: str
    url: str
    enabled: bool
    projectId: str
    events: List[WebhookEventType]
    failureCount: int
    lastFailureAt: Optional[str]
    lastDeliveryAt: Optional[str]
    disabledAt: Optional[str]
    createdAt: str
    updatedAt: str


class Webhook(_WebhookCommonRequired):
    # Masked placeholder (••••••••) or None.
    secret: Optional[str]


class CreatedWebhook(_WebhookCommonRequired):
    # One-time usable signing secret, always prefixed with whsec_.
    secret: str


class _ListWebhooksResponseRequired(TypedDict):
    items: List[Webhook]
    availableEvents: Dict[str, WebhookEventDefinition]


class ListWebhooksResponse(_ListWebhooksResponseRequired, total=False):
    total: int
    page: int
    totalPages: int
    hasMore: bool
    nextCursor: Optional[str]
    prevCursor: Optional[str]


class TestWebhookResponse(TypedDict):
    success: bool
    status: int
    statusText: str
    message: str


class RotateWebhookResponse(TypedDict):
    id: str
    secret: str


class Webhooks(Resource):
    """Webhooks API resource"""

    def list(self, params: Optional[PaginationParams] = None) -> ListWebhooksResponse:
        """List configured webhooks and their recent delivery health."""
        return self._client.get("/webhooks", params)

    def get(self, webhook_id: str) -> Webhook:
        """Retrieve a webhook and its recent delivery state."""
        return self._client.get(f"/webhooks/{webhook_id}")

    def create(self, data: CreateWebhookParams) -> CreatedWebhook:
        """Create a webhook and return the usable whsec_ secret exactly once."""
        return self._client.post("/webhooks", data)

    def update(self, webhook_id: str, data: UpdateWebhookParams) -> Webhook:
        """Update a webhook while preserving omitted fields."""
        return self._client.put(f"/webhooks/{webhook_id}", data)

    def delete(self, webhook_id: str) -> DeletedResponse:
        """Delete a webhook and stop future deliveries to its URL."""
        return self._client.delete(f"/webhooks/{webhook_id}")

    def test(self, webhook_id: str) -> TestWebhookResponse:
        """Send a test event and return the delivery result."""
        return self._client.post(f"/webhooks/{webhook_id}/test")

    def rotate(self, webhook_id: str) -> RotateWebhookResponse:
        return self._client.post(f"/webhooks/{webhook_id}/rotate")

    def events(self) -> WebhookEventsResponse:
        """List event names that can be assigned to a webhook."""
        return self._client.get("/webhooks/events")
