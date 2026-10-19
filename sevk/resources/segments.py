from typing import List, Literal, Optional, TypedDict

from ._base import Resource
from .types import DeletedResponse, JSONObject, JSONValue, SearchPaginationParams

SegmentOperator = Literal["AND", "OR"]
SegmentRuleOperator = Literal[
    "equals",
    "notEquals",
    "contains",
    "notContains",
    "startsWith",
    "endsWith",
    "greaterThan",
    "lessThan",
    "greaterOrEqual",
    "lessOrEqual",
    "isEmpty",
    "isNotEmpty",
    "in",
    "notIn",
]


class _SegmentRuleRequired(TypedDict):
    field: str
    operator: SegmentRuleOperator
    value: JSONValue


class SegmentRule(_SegmentRuleRequired, total=False):
    groupId: str
    groupOperator: SegmentOperator


class SegmentGroup(TypedDict):
    id: str
    operator: SegmentOperator


class _CreateSegmentParamsRequired(TypedDict):
    name: str
    rules: List[SegmentRule]
    operator: SegmentOperator


class CreateSegmentParams(_CreateSegmentParamsRequired, total=False):
    limitToTopics: List[str]
    groups: List[SegmentGroup]


class _PreviewSegmentParamsRequired(TypedDict):
    rules: List[SegmentRule]
    operator: SegmentOperator


class PreviewSegmentParams(_PreviewSegmentParamsRequired, total=False):
    limitToTopics: List[str]
    groups: List[SegmentGroup]


class UpdateSegmentParams(TypedDict, total=False):
    name: str
    rules: List[SegmentRule]
    operator: SegmentOperator
    limitToTopics: List[str]
    groups: List[SegmentGroup]


class Segment(TypedDict):
    id: str
    name: str
    rules: List[SegmentRule]
    operator: SegmentOperator
    limitToTopics: List[str]
    groups: Optional[List[SegmentGroup]]
    audienceId: str
    createdAt: str
    updatedAt: str
    lastRunAt: Optional[str]
    lastRunCount: Optional[int]


class _ListSegmentsResponseRequired(TypedDict):
    items: List[Segment]


class ListSegmentsResponse(_ListSegmentsResponseRequired, total=False):
    total: int
    page: int
    totalPages: int
    hasMore: bool
    nextCursor: Optional[str]
    prevCursor: Optional[str]


class SegmentPreviewContact(TypedDict):
    id: str
    email: str
    subscribed: bool
    data: Optional[JSONObject]
    createdAt: str


class PreviewSegmentResponse(TypedDict):
    count: int
    contacts: List[SegmentPreviewContact]


class CalculateSegmentResponse(TypedDict):
    count: int
    segmentId: str
    segmentName: str
    lastRunAt: str


class Segments(Resource):
    """Segments API resource"""

    def list(
        self,
        audience_id: str,
        params: Optional[SearchPaginationParams] = None,
    ) -> ListSegmentsResponse:
        """List segments belonging to an audience with optional filtering."""
        return self._client.get(f"/audiences/{audience_id}/segments", params)

    def create(self, audience_id: str, data: CreateSegmentParams) -> Segment:
        """Create a saved contact segment under an audience."""
        return self._client.post(f"/audiences/{audience_id}/segments", data)

    def preview(
        self, audience_id: str, data: PreviewSegmentParams
    ) -> PreviewSegmentResponse:
        """Evaluate segment rules and return matches without saving them."""
        return self._client.post(f"/audiences/{audience_id}/segments/preview", data)

    def get(self, segment_id: str) -> Segment:
        """Retrieve a saved segment by ID."""
        return self._client.get(f"/segments/{segment_id}")

    def update(self, segment_id: str, data: UpdateSegmentParams) -> Segment:
        """Update a segment while preserving omitted fields."""
        return self._client.put(f"/segments/{segment_id}", data)

    def delete(self, segment_id: str) -> DeletedResponse:
        """Delete a segment without deleting any contacts."""
        return self._client.delete(f"/segments/{segment_id}")

    def calculate(self, segment_id: str) -> CalculateSegmentResponse:
        """Recalculate and return the current matching contact count."""
        return self._client.get(f"/segments/{segment_id}/calculate")
