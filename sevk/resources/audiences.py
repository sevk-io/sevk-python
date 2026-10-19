from typing import List, Literal, Optional, TypedDict

from ._base import Resource
from .contacts import Contact
from .types import (
    AddContactsResponse,
    AudienceContactRemovedResponse,
    DeletedResponse,
    SearchPaginationParams,
)

AudienceVisibility = Literal["PUBLIC", "PRIVATE"]


class _CreateAudienceParamsRequired(TypedDict):
    name: str


class CreateAudienceParams(_CreateAudienceParamsRequired, total=False):
    description: str
    visibility: AudienceVisibility


class UpdateAudienceParams(TypedDict, total=False):
    name: str
    description: str
    visibility: AudienceVisibility


class _AudienceRequired(TypedDict):
    id: str
    name: str
    description: Optional[str]
    visibility: AudienceVisibility
    projectId: str
    createdAt: str
    updatedAt: str


class Audience(_AudienceRequired, total=False):
    contactsCount: int
    subscribedContactsCount: int
    broadcastsCount: int
    topicsCount: int
    segmentsCount: int


class AudienceMutationResponse(_AudienceRequired):
    """Create/update projection without aggregate counters."""


class _ListAudiencesResponseRequired(TypedDict):
    items: List[Audience]


class ListAudiencesResponse(_ListAudiencesResponseRequired, total=False):
    total: int
    page: int
    totalPages: int
    hasMore: bool
    nextCursor: Optional[str]
    prevCursor: Optional[str]


class ListAudienceContactsParams(SearchPaginationParams, total=False):
    subscribed: bool
    excludeTopicId: str


class _ListAudienceContactsResponseRequired(TypedDict):
    items: List[Contact]


class ListAudienceContactsResponse(_ListAudienceContactsResponseRequired, total=False):
    total: int
    page: int
    totalPages: int
    hasMore: bool
    nextCursor: Optional[str]
    prevCursor: Optional[str]


class Audiences(Resource):
    """Audiences API resource"""

    def list(
        self, params: Optional[SearchPaginationParams] = None
    ) -> ListAudiencesResponse:
        """List audiences with optional pagination and search."""
        return self._client.get("/audiences", params)

    def create(self, data: CreateAudienceParams) -> AudienceMutationResponse:
        """Create an audience for organizing contacts, topics, and segments."""
        return self._client.post("/audiences", data)

    def get(self, audience_id: str) -> Audience:
        """Retrieve an audience by ID."""
        return self._client.get(f"/audiences/{audience_id}")

    def update(
        self, audience_id: str, data: UpdateAudienceParams
    ) -> AudienceMutationResponse:
        """Update an audience while preserving omitted fields."""
        return self._client.put(f"/audiences/{audience_id}", data)

    def delete(self, audience_id: str) -> DeletedResponse:
        """Delete an audience without deleting its contacts."""
        return self._client.delete(f"/audiences/{audience_id}")

    def add_contacts(
        self, audience_id: str, contact_ids: List[str]
    ) -> AddContactsResponse:
        """Add contacts to an audience, ignoring existing memberships."""
        return self._client.post(
            f"/audiences/{audience_id}/contacts",
            {"contactIds": contact_ids},
        )

    def remove_contact(
        self, audience_id: str, contact_id: str
    ) -> AudienceContactRemovedResponse:
        """Remove a contact from the audience without deleting the contact."""
        return self._client.delete(f"/audiences/{audience_id}/contacts/{contact_id}")

    def list_contacts(
        self,
        audience_id: str,
        params: Optional[ListAudienceContactsParams] = None,
    ) -> ListAudienceContactsResponse:
        """List contacts attached to an audience with optional filtering."""
        return self._client.get(f"/audiences/{audience_id}/contacts", params)
