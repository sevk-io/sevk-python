from typing import Optional, TypedDict

from ._base import Resource


class OutboundQuota(TypedDict):
    projectId: str
    monthlyEmailLimit: Optional[int]
    adminMonthlyEmailLimit: Optional[int]
    effectiveMonthlyEmailLimit: Optional[int]
    monthlyEmailsUsed: int
    limitEmailsUsed: int
    monthlyRemaining: Optional[int]
    rateLimit: Optional[int]
    resetAt: str
    pausedAt: Optional[str]
    pausedReason: Optional[str]
    createdAt: str
    updatedAt: str
    freeMonthlyEmails: Optional[int]
    freeEmailsUsed: int
    emailPrice: float


class UpdateOutboundQuotaParams(TypedDict):
    monthlyEmailLimit: Optional[int]


class Outbound(Resource):
    """Outbound resource. Read and adjust the project's monthly outbound
    sending cap, and pause / resume transactional sending.

    Pause affects ``POST /emails``, ``POST /emails/bulk``, and SMTP relay.
    Broadcasts run on a separate balance check and are NOT affected.

    Access via ``sevk.outbound``. Requires an API key with ``outbound:read``
    for ``get_quota``, or ``outbound:write`` for the others.
    """

    def get_quota(self) -> OutboundQuota:
        """Return outbound quota settings and current usage counters."""
        return self._client.get("/outbound-settings/quota")

    def update_quota(self, data: UpdateOutboundQuotaParams) -> OutboundQuota:
        """Update the monthly cap and clear a cap-exhausted pause when possible."""
        return self._client.put("/outbound-settings/quota", data)

    def reset_quota(self) -> OutboundQuota:
        """Clear an outbound pause while preserving usage and the configured cap."""
        return self._client.post("/outbound-settings/quota/reset")

    def reset_limit(self) -> OutboundQuota:
        """Reset custom-limit usage while preserving the cap and monthly usage."""
        return self._client.post("/outbound-settings/quota/reset-limit")

    def pause_quota(self) -> OutboundQuota:
        """Pause transactional sending until ``reset_quota`` is called."""
        return self._client.post("/outbound-settings/quota/pause")
