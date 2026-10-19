from typing import Optional, TypedDict

from ._base import Resource


class FreeEmailUsage(TypedDict):
    current: int
    limit: Optional[int]
    remaining: int


class InboundUsage(TypedDict):
    emailsCount: int
    monthlyEmailLimit: Optional[int]
    monthlyEmailsUsed: int
    monthlyRemaining: Optional[int]
    resetAt: Optional[str]
    pausedAt: Optional[str]
    pausedReason: Optional[str]
    freeEmails: FreeEmailUsage


class OutboundUsage(TypedDict):
    monthlyEmailLimit: Optional[int]
    adminMonthlyEmailLimit: Optional[int]
    effectiveMonthlyEmailLimit: Optional[int]
    monthlyEmailsUsed: int
    limitEmailsUsed: int
    monthlyRemaining: Optional[int]
    rateLimit: Optional[int]
    resetAt: Optional[str]
    pausedAt: Optional[str]
    pausedReason: Optional[str]
    freeEmails: FreeEmailUsage


class _ProjectUsageRequired(TypedDict):
    id: str
    name: str
    audienceLimit: Optional[int]
    contactLimit: Optional[int]
    broadcastLimit: Optional[int]
    domainLimit: Optional[int]
    webhookLimit: Optional[int]
    storageLimit: Optional[str]
    storageUsed: str
    monthlyOutboundEmailLimit: Optional[int]
    outboundRateLimit: Optional[int]
    audiencesCount: int
    contactsCount: int
    broadcastsCount: int
    monthlyBroadcastsUsed: int
    domainsCount: int
    webhooksCount: int
    inboundEmailsCount: int
    inbound: InboundUsage
    outbound: OutboundUsage
    freeMonthlyOutboundEmails: Optional[int]
    freeMonthlyInboundEmails: Optional[int]


class ProjectUsage(_ProjectUsageRequired, total=False):
    balance: str
    outboundEmailPrice: str
    inboundEmailPrice: str


class Usage(Resource):
    """Reads project limits, resource counts, and current email usage."""

    def get(self) -> ProjectUsage:
        """Return current limits and inbound and outbound usage."""
        return self._client.get("/limits")
