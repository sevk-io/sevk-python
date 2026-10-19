from typing import Optional

from ._base import Resource
from .broadcast_types import (
    AbTestConfigInput,
    ActiveBroadcast,
    ActiveBroadcastABTest,
    ActiveBroadcastsResponse,
    Broadcast,
    BroadcastAbTest,
    BroadcastABTestStatus,
    BroadcastAnalytics,
    BroadcastAudienceRef,
    BroadcastBase,
    BroadcastCostEstimate,
    BroadcastDomainRef,
    BroadcastEmail,
    BroadcastEmailContact,
    BroadcastLifecycleStatus,
    BroadcastRecipientEstimate,
    BroadcastRecipientEstimateParams,
    BroadcastSegmentRef,
    BroadcastStatusCompletion,
    BroadcastStatusProgress,
    BroadcastStatusResponse,
    BroadcastStatusSchedule,
    BroadcastStatusWarning,
    BroadcastStyle,
    BroadcastSummary,
    BroadcastTargetType,
    BroadcastTopicRef,
    BroadcastUpdate,
    BroadcastVariant,
    BroadcastWarningType,
    BroadcastWinnerMetric,
    BroadcastWithVariants,
    CancelBroadcastResponse,
    CreateBroadcastParams,
    ListBroadcastEmailsResponse,
    ListBroadcastsParams,
    ListBroadcastsResponse,
    TestBroadcastOptions,
    TestBroadcastParams,
    TestBroadcastResponse,
    UpdateBroadcastParams,
    VariantInput,
)
from .types import DeletedResponse, PaginationParams

__all__ = [
    "AbTestConfigInput",
    "ActiveBroadcast",
    "ActiveBroadcastABTest",
    "ActiveBroadcastsResponse",
    "Broadcast",
    "BroadcastBase",
    "BroadcastABTestStatus",
    "BroadcastAbTest",
    "BroadcastAnalytics",
    "BroadcastAudienceRef",
    "BroadcastCostEstimate",
    "BroadcastDomainRef",
    "BroadcastEmail",
    "BroadcastEmailContact",
    "BroadcastLifecycleStatus",
    "BroadcastRecipientEstimate",
    "BroadcastRecipientEstimateParams",
    "BroadcastSummary",
    "BroadcastUpdate",
    "BroadcastWithVariants",
    "BroadcastSegmentRef",
    "BroadcastStatusCompletion",
    "BroadcastStatusProgress",
    "BroadcastStatusResponse",
    "BroadcastStatusSchedule",
    "BroadcastStatusWarning",
    "BroadcastStyle",
    "BroadcastTargetType",
    "BroadcastTopicRef",
    "BroadcastVariant",
    "BroadcastWarningType",
    "BroadcastWinnerMetric",
    "Broadcasts",
    "CancelBroadcastResponse",
    "CreateBroadcastParams",
    "ListBroadcastEmailsResponse",
    "ListBroadcastsParams",
    "ListBroadcastsResponse",
    "TestBroadcastParams",
    "TestBroadcastOptions",
    "TestBroadcastResponse",
    "UpdateBroadcastParams",
    "VariantInput",
]


class Broadcasts(Resource):
    """Compose, schedule, send, and inspect broadcast campaigns."""

    def list(
        self, params: Optional[ListBroadcastsParams] = None
    ) -> ListBroadcastsResponse:
        """List broadcasts with optional pagination, search, and status filters."""
        return self._client.get("/broadcasts", params)

    def get(self, broadcast_id: str) -> Broadcast:
        """Retrieve a broadcast by ID and include its delivery state."""
        return self._client.get(f"/broadcasts/{broadcast_id}")

    def create(self, data: CreateBroadcastParams) -> BroadcastWithVariants:
        """Create a draft or scheduled broadcast for a target group."""
        return self._client.post("/broadcasts", data)

    def update(self, broadcast_id: str, data: UpdateBroadcastParams) -> BroadcastUpdate:
        """Update a broadcast while preserving omitted fields."""
        return self._client.put(f"/broadcasts/{broadcast_id}", data)

    def delete(self, broadcast_id: str) -> DeletedResponse:
        """Delete a broadcast that has not been sent."""
        return self._client.delete(f"/broadcasts/{broadcast_id}")

    def send(self, broadcast_id: str) -> BroadcastSummary:
        """Queue a prepared broadcast for delivery."""
        return self._client.post(f"/broadcasts/{broadcast_id}/send")

    def cancel(self, broadcast_id: str) -> CancelBroadcastResponse:
        """Cancel a broadcast when its state still allows cancellation."""
        return self._client.post(f"/broadcasts/{broadcast_id}/cancel")

    def test(
        self,
        broadcast_id: str,
        data: TestBroadcastParams,
        options: Optional[TestBroadcastOptions] = None,
    ) -> TestBroadcastResponse:
        """Send the broadcast to test recipients without starting the campaign."""
        key = options.get("idempotency_key") if options else None
        headers = {"Idempotency-Key": key} if key is not None else None
        return self._client.post(f"/broadcasts/{broadcast_id}/test", data, headers)

    def analytics(self, broadcast_id: str) -> BroadcastAnalytics:
        """Return aggregate delivery and engagement analytics."""
        return self._client.get(f"/broadcasts/{broadcast_id}/analytics")

    def status(self, broadcast_id: str) -> BroadcastStatusResponse:
        """Return live scheduling and delivery progress."""
        return self._client.get(f"/broadcasts/{broadcast_id}/status")

    def emails(
        self,
        broadcast_id: str,
        params: Optional[PaginationParams] = None,
    ) -> ListBroadcastEmailsResponse:
        """List email deliveries created for a broadcast."""
        return self._client.get(f"/broadcasts/{broadcast_id}/emails", params)

    def estimate_cost(self, broadcast_id: str) -> BroadcastCostEstimate:
        """Estimate delivery cost without sending the broadcast."""
        return self._client.get(f"/broadcasts/{broadcast_id}/estimate-cost")

    def estimate_recipients(
        self, params: BroadcastRecipientEstimateParams
    ) -> BroadcastRecipientEstimate:
        """Resolve the subscribed recipient count for a target."""
        return self._client.post("/broadcasts/estimate-recipients", params)

    def active(self) -> ActiveBroadcastsResponse:
        """List broadcasts that are scheduled or processing."""
        return self._client.get("/broadcasts/active")
