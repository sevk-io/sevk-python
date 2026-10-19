from typing import List, Literal, Optional, TypedDict

from ._base import Resource
from .broadcasts import BroadcastLifecycleStatus
from .emails import EmailStatus
from .types import DeletedResponse, JSONValue, PaginationParams

InboundEmailStatus = Literal["RECEIVED", "PROCESSED", "BOUNCED", "BLOCKED", "FAILED"]
InboundBlocklistType = Literal["EMAIL", "DOMAIN", "IP"]


class ListInboundParams(TypedDict, total=False):
    page: int
    limit: int
    after: str
    before: str
    search: str
    status: InboundEmailStatus
    domainId: str
    broadcastId: str
    isSpam: bool
    isVirus: bool


class _AddInboundBlocklistParamsRequired(TypedDict):
    type: InboundBlocklistType
    value: str


class AddInboundBlocklistParams(_AddInboundBlocklistParamsRequired, total=False):
    reason: Optional[str]


class InboundAttachment(TypedDict):
    id: str
    filename: str
    mimeType: str
    contentId: Optional[str]
    size: int
    createdAt: str


class _InboundReplyEmailRequired(TypedDict):
    id: str
    subject: Optional[str]
    to: Optional[str]


_InboundReplyEmailOptional = TypedDict(
    "_InboundReplyEmailOptional",
    {
        "messageId": Optional[str],
        "from": Optional[str],
        "status": EmailStatus,
        "createdAt": str,
        "broadcastId": Optional[str],
        "contactId": Optional[str],
    },
    total=False,
)


class InboundReplyEmail(_InboundReplyEmailRequired, _InboundReplyEmailOptional):
    pass


class _InboundReplyBroadcastRequired(TypedDict):
    id: str
    name: str


class InboundReplyBroadcast(_InboundReplyBroadcastRequired, total=False):
    subject: Optional[str]
    status: BroadcastLifecycleStatus
    createdAt: str


class InboundReplyEmailSummary(TypedDict):
    id: str
    subject: Optional[str]
    to: Optional[str]


class InboundReplyBroadcastSummary(TypedDict):
    id: str
    name: str


class InboundEmailSummary(TypedDict):
    id: str
    messageId: Optional[str]
    fromAddress: str
    toAddress: str
    subject: Optional[str]
    status: InboundEmailStatus
    isSpam: bool
    isVirus: bool
    spamScore: Optional[float]
    rawSize: int
    domainId: Optional[str]
    replyToEmailId: Optional[str]
    replyToBroadcastId: Optional[str]
    receivedAt: str
    createdAt: str
    replyToEmail: Optional[InboundReplyEmailSummary]
    replyToBroadcast: Optional[InboundReplyBroadcastSummary]


class _InboundEmailRequired(TypedDict):
    id: str
    fromAddress: str
    toAddress: str
    status: InboundEmailStatus
    isSpam: bool
    isVirus: bool
    rawSize: int
    domainId: Optional[str]
    receivedAt: str
    createdAt: str


class InboundEmail(_InboundEmailRequired, total=False):
    messageId: Optional[str]
    ccAddresses: List[str]
    subject: Optional[str]
    spamScore: Optional[float]
    inReplyTo: Optional[str]
    references: List[str]
    bodyText: Optional[str]
    bodyHtml: Optional[str]
    headers: JSONValue
    projectId: str
    processedAt: Optional[str]
    updatedAt: str
    attachments: List[InboundAttachment]
    replyToEmailId: Optional[str]
    replyToBroadcastId: Optional[str]
    replyToEmail: Optional[InboundReplyEmail]
    replyToBroadcast: Optional[InboundReplyBroadcast]


class _InboundListResponseRequired(TypedDict):
    items: List[InboundEmailSummary]


class InboundListResponse(_InboundListResponseRequired, total=False):
    total: int
    page: int
    totalPages: int
    hasMore: bool
    nextCursor: Optional[str]
    prevCursor: Optional[str]


class InboundStatsCounts(TypedDict):
    RECEIVED: int
    PROCESSED: int
    BOUNCED: int
    BLOCKED: int
    FAILED: int


class InboundStats(TypedDict):
    total: int
    counts: InboundStatsCounts
    received: int
    processed: int
    bounced: int
    blocked: int
    blocklistRejected: int
    spam: int
    failed: int


class InboundAttachmentDownload(TypedDict):
    url: str
    filename: str
    mimeType: str


class InboundRoute(TypedDict):
    id: str
    projectId: str
    name: str
    pattern: str
    target: str
    priority: int
    enabled: bool
    createdAt: str
    updatedAt: str


class _CreateInboundRouteParamsRequired(TypedDict):
    name: str
    pattern: str
    target: str


class CreateInboundRouteParams(_CreateInboundRouteParamsRequired, total=False):
    priority: int
    enabled: bool


class UpdateInboundRouteParams(TypedDict, total=False):
    name: str
    pattern: str
    target: str
    priority: int
    enabled: bool


class _InboundRoutesResponseRequired(TypedDict):
    items: List[InboundRoute]


class InboundRoutesResponse(_InboundRoutesResponseRequired, total=False):
    total: int
    page: int
    totalPages: int
    hasMore: bool
    nextCursor: Optional[str]
    prevCursor: Optional[str]


class InboundBlocklistEntry(TypedDict):
    id: str
    projectId: str
    type: InboundBlocklistType
    value: str
    reason: Optional[str]
    createdAt: str


class _InboundBlocklistResponseRequired(TypedDict):
    items: List[InboundBlocklistEntry]


class InboundBlocklistResponse(_InboundBlocklistResponseRequired, total=False):
    total: int
    page: int
    totalPages: int
    hasMore: bool
    nextCursor: Optional[str]
    prevCursor: Optional[str]


class _InboundQuotaRequired(TypedDict):
    projectId: str
    monthlyEmailsUsed: int
    resetAt: str
    createdAt: str
    updatedAt: str
    freeMonthlyInboundEmails: Optional[int]
    freeEmailsUsed: int
    inboundEmailPrice: float


class InboundQuota(_InboundQuotaRequired, total=False):
    monthlyEmailLimit: Optional[int]
    pausedAt: Optional[str]
    pausedReason: Optional[str]


class UpdateInboundQuotaParams(TypedDict, total=False):
    monthlyEmailLimit: Optional[int]


class InboundSecurityPlatform(TypedDict):
    maxAttachmentSizeCap: int


class _InboundSecurityConfigRequired(TypedDict):
    domainId: str
    dmarcStrict: bool
    spfRequired: bool
    spamThreshold: Optional[float]
    catchAllEnabled: bool
    acceptedRecipients: List[str]
    maxAttachmentSize: int
    allowedMimeTypes: List[str]
    platform: InboundSecurityPlatform


class InboundSecurityConfig(_InboundSecurityConfigRequired, total=False):
    id: str
    createdAt: str
    updatedAt: str


class UpdateInboundSecurityParams(TypedDict, total=False):
    dmarcStrict: bool
    spfRequired: bool
    spamThreshold: Optional[float]
    catchAllEnabled: bool
    acceptedRecipients: List[str]
    maxAttachmentSize: int
    allowedMimeTypes: List[str]


class Inbound(Resource):
    """Inbound API resource.

    Read inbound emails, manage per-project inbound settings (routes,
    blocklist, quota, security), and download attachments via
    short-lived URLs.

    Access via ``sevk.inbound``. Requires an API key with
    ``inbound:read``, ``inbound:write``, or ``inbound:delete``
    capabilities depending on the call.
    """

    def list(self, params: Optional[ListInboundParams] = None) -> InboundListResponse:
        """List received email with optional pagination and filtering."""
        return self._client.get("/inbound", params)

    def get(self, email_id: str) -> InboundEmail:
        """Retrieve a received email with parsed content and attachments."""
        return self._client.get(f"/inbound/{email_id}")

    def delete(self, email_id: str) -> DeletedResponse:
        """Delete a received email and its stored attachments."""
        return self._client.delete(f"/inbound/{email_id}")

    def stats(self, domain_id: Optional[str] = None) -> InboundStats:
        """Return inbound processing statistics, optionally for one domain."""
        params = {"domainId": domain_id} if domain_id else None

        return self._client.get("/inbound/stats", params)

    def download_attachment(
        self, email_id: str, attachment_id: str
    ) -> InboundAttachmentDownload:
        """Create a short-lived download URL for an inbound attachment."""
        return self._client.get(
            f"/inbound/{email_id}/attachments/{attachment_id}/download"
        )

    def list_routes(
        self, params: Optional[PaginationParams] = None
    ) -> InboundRoutesResponse:
        """List routing rules with optional offset or cursor pagination."""
        return self._client.get("/inbound-settings/routes", params)

    def get_route(self, route_id: str) -> InboundRoute:
        """Retrieve an inbound routing rule by ID."""
        return self._client.get(f"/inbound-settings/routes/{route_id}")

    def route_items(
        self, params: Optional[PaginationParams] = None
    ) -> List[InboundRoute]:
        return self.list_routes(params)["items"]

    def create_route(self, data: CreateInboundRouteParams) -> InboundRoute:
        """Create an inbound routing rule."""
        return self._client.post("/inbound-settings/routes", data)

    def update_route(
        self, route_id: str, data: UpdateInboundRouteParams
    ) -> InboundRoute:
        """Update an inbound routing rule while preserving omitted fields."""
        return self._client.put(f"/inbound-settings/routes/{route_id}", data)

    def delete_route(self, route_id: str) -> DeletedResponse:
        """Delete an inbound routing rule without deleting stored email."""
        return self._client.delete(f"/inbound-settings/routes/{route_id}")

    def list_blocklist(
        self, params: Optional[PaginationParams] = None
    ) -> InboundBlocklistResponse:
        """List blocked addresses with optional offset or cursor pagination."""
        return self._client.get("/inbound-settings/blocklist", params)

    def add_blocklist_entry(
        self, data: AddInboundBlocklistParams
    ) -> InboundBlocklistEntry:
        """Add an address to the inbound blocklist."""
        return self._client.post("/inbound-settings/blocklist", data)

    def blocklist_items(
        self, params: Optional[PaginationParams] = None
    ) -> List[InboundBlocklistEntry]:
        return self.list_blocklist(params)["items"]

    def remove_blocklist_entry(self, entry_id: str) -> DeletedResponse:
        """Remove an address from the inbound blocklist."""
        return self._client.delete(f"/inbound-settings/blocklist/{entry_id}")

    def get_quota(self) -> InboundQuota:
        """Return inbound quota settings and current usage counters."""
        return self._client.get("/inbound-settings/quota")

    def update_quota(self, data: UpdateInboundQuotaParams) -> InboundQuota:
        """Update the inbound monthly limit while preserving omitted fields."""
        return self._client.put("/inbound-settings/quota", data)

    def reset_quota(self) -> InboundQuota:
        """Clear a quota pause without resetting current-period usage."""
        return self._client.post("/inbound-settings/quota/reset")

    def get_security_config(self, domain_id: str) -> InboundSecurityConfig:
        """Return the effective inbound security settings for a domain."""
        return self._client.get(f"/inbound-settings/security/{domain_id}")

    def update_security_config(
        self, domain_id: str, data: UpdateInboundSecurityParams
    ) -> InboundSecurityConfig:
        """Update inbound security settings for a domain."""
        return self._client.put(f"/inbound-settings/security/{domain_id}", data)
