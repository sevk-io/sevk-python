from typing import List, Literal, Optional, TypedDict

from .emails import EmailStatus, EmailType

BroadcastLifecycleStatus = Literal[
    "DRAFT",
    "SCHEDULED",
    "STARTING",
    "SENDING",
    "SENT",
    "FAILED",
    "CANCELLING",
    "CANCELLED",
]
BroadcastStyle = Literal["HTML", "MARKUP"]
BroadcastTargetType = Literal["ALL", "AUDIENCE", "TOPIC", "SEGMENT"]
BroadcastWinnerMetric = Literal["OPEN_RATE", "CLICK_RATE"]
BroadcastABTestStatus = Literal[
    "SCHEDULED",
    "TESTING",
    "EVALUATING",
    "ROLLING_OUT",
    "COMPLETED",
    "FAILED",
]
BroadcastWarningType = Literal["FAILED_EMAILS"]


class BroadcastStatusWarning(TypedDict):
    type: BroadcastWarningType
    message: str
    failedCount: int


class BroadcastStatusProgress(TypedDict):
    percentage: float
    emailsSent: int
    totalContacts: int
    pendingEmails: int
    estimatedTimeRemaining: Optional[str]


class BroadcastStatusSchedule(TypedDict):
    scheduledAt: Optional[str]
    timeUntilSend: int
    willSendIn: str
    isPastDue: bool


class BroadcastStatusCompletion(TypedDict):
    completedAt: Optional[str]
    totalEmailsSent: int
    successRate: float


class _BroadcastStatusResponseRequired(TypedDict):
    id: str
    name: str
    status: BroadcastLifecycleStatus
    totalContacts: int
    emailsSent: int
    failedEmails: int
    pendingEmails: int
    createdAt: str
    sentAt: Optional[str]
    completedAt: Optional[str]
    scheduledAt: Optional[str]


class BroadcastStatusResponse(_BroadcastStatusResponseRequired, total=False):
    sendingStartedAt: str
    step: str
    stepLabel: str
    stepIndex: int
    stepTotal: int
    stepProgress: float
    warning: BroadcastStatusWarning
    progress: BroadcastStatusProgress
    schedule: BroadcastStatusSchedule
    completion: BroadcastStatusCompletion


class ListBroadcastsParams(TypedDict, total=False):
    page: int
    limit: int
    after: str
    before: str
    search: str
    status: BroadcastLifecycleStatus


class _AbTestConfigInputRequired(TypedDict):
    testPercent: int
    evalAfterMinutes: int


class AbTestConfigInput(_AbTestConfigInputRequired, total=False):
    winnerMetric: BroadcastWinnerMetric


class _VariantInputRequired(TypedDict):
    label: str


class VariantInput(_VariantInputRequired, total=False):
    subject: str
    body: str
    fromName: str


class _CreateBroadcastParamsRequired(TypedDict):
    name: str
    subject: str
    senderName: str
    domainId: str


class CreateBroadcastParams(_CreateBroadcastParamsRequired, total=False):
    body: str
    style: BroadcastStyle
    targetType: BroadcastTargetType
    audienceId: str
    topicId: str
    segmentId: str
    email: str
    replyTo: str
    replyToInbound: bool
    scheduledAt: str
    includeListUnsubscribeHeader: bool
    openTracking: Optional[bool]
    clickTracking: Optional[bool]
    variants: List[VariantInput]
    abTest: AbTestConfigInput


class UpdateBroadcastParams(TypedDict, total=False):
    name: str
    subject: str
    body: str
    style: BroadcastStyle
    targetType: BroadcastTargetType
    audienceId: Optional[str]
    topicId: Optional[str]
    segmentId: Optional[str]
    email: str
    senderName: str
    replyTo: Optional[str]
    replyToInbound: bool
    domainId: str
    scheduledAt: Optional[str]
    includeListUnsubscribeHeader: bool
    openTracking: Optional[bool]
    clickTracking: Optional[bool]
    variants: Optional[List[VariantInput]]
    abTest: Optional[AbTestConfigInput]


class _BroadcastRecipientEstimateParamsRequired(TypedDict):
    targetType: BroadcastTargetType


class BroadcastRecipientEstimateParams(
    _BroadcastRecipientEstimateParamsRequired, total=False
):
    audienceId: str
    topicId: str
    segmentId: str


class BroadcastRecipientEstimate(TypedDict):
    count: int


class BroadcastCostEstimate(TypedDict):
    estimatedCost: float
    emailPrice: float
    contactCount: int
    currentBalance: float
    hasSufficientBalance: bool
    shortfall: float
    freeEmailsAvailable: int
    freeEmailsToUse: int
    paidEmailsCount: int


class BroadcastVariant(TypedDict):
    id: str
    broadcastId: str
    label: str
    subject: Optional[str]
    body: Optional[str]
    fromName: Optional[str]
    totalContacts: int
    sentCount: int
    failedCount: int
    deliveredCount: int
    openedCount: int
    clickedCount: int
    bouncedCount: int
    complainedCount: int
    unsubscribedCount: int
    isWinner: bool
    createdAt: str
    updatedAt: str


class BroadcastAbTest(TypedDict):
    id: str
    broadcastId: str
    testPercent: int
    evalAfterMinutes: int
    winnerMetric: BroadcastWinnerMetric
    status: BroadcastABTestStatus
    scheduledEvalAt: Optional[str]
    winnerVariantId: Optional[str]
    evaluatedAt: Optional[str]
    createdAt: str
    updatedAt: str


class BroadcastAudienceRef(TypedDict):
    id: str
    name: str
    contactsCount: int
    subscribedContactsCount: int
    broadcastsCount: int
    topicsCount: int
    segmentsCount: int


class BroadcastTopicRef(TypedDict):
    id: str
    name: str
    contactsCount: int
    subscribedContactsCount: int
    broadcastsCount: int


class BroadcastSegmentRef(TypedDict):
    id: str
    name: str


class BroadcastDomainRef(TypedDict):
    id: str
    domain: str
    senderName: Optional[str]
    verified: bool


class _BroadcastRequired(TypedDict):
    id: str
    name: str
    subject: str
    body: str
    style: BroadcastStyle
    status: BroadcastLifecycleStatus
    targetType: BroadcastTargetType
    audienceId: Optional[str]
    topicId: Optional[str]
    segmentId: Optional[str]
    email: Optional[str]
    senderName: Optional[str]
    domainId: Optional[str]
    scheduledAt: Optional[str]
    sentAt: Optional[str]
    completedAt: Optional[str]
    projectId: str
    createdAt: str
    updatedAt: str
    audience: Optional[BroadcastAudienceRef]
    topic: Optional[BroadcastTopicRef]
    segment: Optional[BroadcastSegmentRef]
    domain: Optional[BroadcastDomainRef]


class BroadcastBase(_BroadcastRequired, total=False):
    replyTo: Optional[str]
    replyToInbound: bool
    delivered: Optional[str]
    includeListUnsubscribeHeader: bool
    openTracking: Optional[bool]
    clickTracking: Optional[bool]


class _BroadcastSummaryRequired(BroadcastBase):
    estimatedCost: Optional[str]
    actualCost: Optional[str]


class BroadcastSummary(_BroadcastSummaryRequired, total=False):
    totalContacts: int
    sentCount: int
    failedCount: int
    deliveredCount: int
    openedCount: int
    clickedCount: int
    bouncedCount: int
    complainedCount: int
    unsubscribedCount: int


class BroadcastWithVariants(BroadcastBase):
    variants: List[BroadcastVariant]
    abTest: Optional[BroadcastAbTest]


class BroadcastUpdate(BroadcastBase, total=False):
    """Update response; experiment fields are present when the mutation touched them."""

    variants: List[BroadcastVariant]
    abTest: Optional[BroadcastAbTest]


class Broadcast(BroadcastSummary):
    variants: List[BroadcastVariant]
    abTest: Optional[BroadcastAbTest]


class BroadcastEmailContact(TypedDict):
    id: Optional[str]
    email: str


class _BroadcastEmailRequired(TypedDict):
    id: str
    to: str
    subject: str
    status: EmailStatus
    type: EmailType


class BroadcastEmail(_BroadcastEmailRequired, total=False):
    messageId: Optional[str]
    openedAt: Optional[str]
    clickedAt: Optional[str]
    unsubscribedAt: Optional[str]
    createdAt: str
    contact: BroadcastEmailContact


class _ListBroadcastsResponseRequired(TypedDict):
    items: List[BroadcastSummary]


class ListBroadcastsResponse(_ListBroadcastsResponseRequired, total=False):
    total: int
    page: int
    totalPages: int
    hasMore: bool
    nextCursor: Optional[str]
    prevCursor: Optional[str]


class _ListBroadcastEmailsResponseRequired(TypedDict):
    items: List[BroadcastEmail]


class ListBroadcastEmailsResponse(_ListBroadcastEmailsResponseRequired, total=False):
    total: int
    page: int
    totalPages: int
    hasMore: bool
    nextCursor: Optional[str]
    prevCursor: Optional[str]


class BroadcastAnalytics(TypedDict):
    totalEmails: int
    sentEmails: int
    deliveredEmails: int
    openedEmails: int
    clickedEmails: int
    totalClicks: int
    bouncedEmails: int
    failedEmails: int
    unsubscribedEmails: int
    deliveryRate: float
    openRate: float
    clickRate: float
    bounceRate: float
    unsubscribeRate: float


class CancelBroadcastResponse(TypedDict):
    broadcast: BroadcastSummary
    cancelledJobs: int


class TestBroadcastParams(TypedDict):
    emails: List[str]


class TestBroadcastOptions(TypedDict, total=False):
    idempotency_key: str


class TestBroadcastResponse(TypedDict):
    testEmails: int
    message: str


class ActiveBroadcastABTest(TypedDict):
    status: BroadcastABTestStatus
    scheduledEvalAt: Optional[str]
    testPercent: int


class ActiveBroadcast(TypedDict):
    id: str
    name: str
    status: BroadcastLifecycleStatus
    sentCount: int
    failedCount: int
    totalContacts: int
    scheduledAt: Optional[str]
    abTest: Optional[ActiveBroadcastABTest]


class ActiveBroadcastsResponse(TypedDict):
    items: List[ActiveBroadcast]
    total: int
