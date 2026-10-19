from typing import Any, Dict, List, Literal, Optional, TypedDict, Union

from ._base import Resource

ActivityEventType = Literal["EMAIL", "SUBSCRIPTION"]
ActivityAction = Literal[
    "REQUESTED",
    "SENT",
    "DELIVERED",
    "OPENED",
    "CLICKED",
    "BOUNCED",
    "COMPLAINT",
    "FAILED",
    "SUBSCRIBED",
    "UNSUBSCRIBED",
    "DELAYED",
    "REJECTED",
]
ActivityCategory = Literal["EMAIL", "SUBSCRIPTION", "all"]


class ActivityItem(TypedDict):
    id: str
    eventType: ActivityEventType
    action: ActivityAction
    description: Optional[str]
    emailId: Optional[str]
    emailSubject: Optional[str]
    contactId: Optional[str]
    contactEmail: Optional[str]
    broadcastId: Optional[str]
    broadcastName: Optional[str]
    link: Optional[str]
    userAgent: Optional[str]
    metadata: Optional[str]
    createdAt: str


class ListActivityParams(TypedDict, total=False):
    page: int
    limit: int
    after: str
    before: str
    category: ActivityCategory
    type: List[ActivityAction]
    days: int
    search: str


class ActivityOffsetPage(TypedDict):
    items: List[ActivityItem]
    total: int
    page: int
    totalPages: int


class ActivityCursorPage(TypedDict):
    items: List[ActivityItem]
    hasMore: bool
    nextCursor: Optional[str]
    prevCursor: Optional[str]


ListActivityResponse = Union[ActivityOffsetPage, ActivityCursorPage]


class ActivityRates(TypedDict):
    open: float
    click: float
    bounce: float
    delivery: float


class ActivityStatsResponse(TypedDict):
    totalEmails: int
    sentEmails: int
    deliveredEmails: int
    openedEmails: int
    clickedEmails: int
    bouncedEmails: int
    marketingEmails: int
    transactionalEmails: int
    rates: ActivityRates


class Activity(Resource):
    """Activity API resource"""

    def list(self, params: Optional[ListActivityParams] = None) -> ListActivityResponse:
        """List project activity with optional pagination and filtering."""
        wire: Optional[Dict[str, Any]] = dict(params) if params else None
        if wire and isinstance(wire.get("type"), list):
            wire["type"] = ",".join(wire["type"])
        return self._client.get("/activity", wire)

    def stats(self) -> ActivityStatsResponse:
        """Return aggregate counts and rates for recent project activity."""
        return self._client.get("/activity/stats")
