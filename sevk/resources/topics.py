from typing import List, Optional, TypedDict

from ._base import Resource
from .contacts import Contact
from .types import (
    AddContactsResponse,
    DeletedResponse,
    SearchPaginationParams,
    TopicContactRemovedResponse,
)


class _TopicRequired(TypedDict):
    id: str
    name: str
    description: Optional[str]
    audienceId: str
    createdAt: str
    updatedAt: str


class Topic(_TopicRequired, total=False):
    contactsCount: int
    subscribedContactsCount: int
    broadcastsCount: int


class TopicMutationResponse(_TopicRequired):
    """Create/update projection without aggregate counters."""


class _ListTopicsResponseRequired(TypedDict):
    items: List[Topic]


class ListTopicsResponse(_ListTopicsResponseRequired, total=False):
    total: int
    page: int
    totalPages: int
    hasMore: bool
    nextCursor: Optional[str]
    prevCursor: Optional[str]


class _CreateTopicParamsRequired(TypedDict):
    name: str


class CreateTopicParams(_CreateTopicParamsRequired, total=False):
    description: str


class UpdateTopicParams(TypedDict, total=False):
    name: str
    description: str


class ListTopicContactsParams(SearchPaginationParams, total=False):
    subscribed: bool


class _ListTopicContactsResponseRequired(TypedDict):
    items: List[Contact]


class ListTopicContactsResponse(_ListTopicContactsResponseRequired, total=False):
    total: int
    page: int
    totalPages: int
    hasMore: bool
    nextCursor: Optional[str]
    prevCursor: Optional[str]


class Topics(Resource):
    """Topics API resource"""

    def list(
        self,
        audience_id: str,
        params: Optional[SearchPaginationParams] = None,
    ) -> ListTopicsResponse:
        """List topics belonging to an audience with optional filtering."""
        return self._client.get(f"/audiences/{audience_id}/topics", params)

    def create(
        self, audience_id: str, data: CreateTopicParams
    ) -> TopicMutationResponse:
        """Create a subscription topic under an audience."""
        return self._client.post(f"/audiences/{audience_id}/topics", data)

    def get(self, topic_id: str) -> Topic:
        """Retrieve a topic by ID."""
        return self._client.get(f"/topics/{topic_id}")

    def update(self, topic_id: str, data: UpdateTopicParams) -> TopicMutationResponse:
        """Update a topic while preserving omitted fields."""
        return self._client.put(f"/topics/{topic_id}", data)

    def delete(self, topic_id: str) -> DeletedResponse:
        """Delete a topic without deleting its contacts or parent audience."""
        return self._client.delete(f"/topics/{topic_id}")

    def add_contacts(
        self, topic_id: str, contact_ids: List[str]
    ) -> AddContactsResponse:
        """Add contacts to a topic, ignoring existing memberships."""
        return self._client.post(
            f"/topics/{topic_id}/contacts",
            {"contactIds": contact_ids},
        )

    def remove_contact(
        self, topic_id: str, contact_id: str
    ) -> TopicContactRemovedResponse:
        """Remove a contact from the topic without deleting the contact."""
        return self._client.delete(f"/topics/{topic_id}/contacts/{contact_id}")

    def list_contacts(
        self,
        topic_id: str,
        params: Optional[ListTopicContactsParams] = None,
    ) -> ListTopicContactsResponse:
        """List contacts attached to a topic.

        Optional params: page, limit, after, before, search, and subscribed.
        """
        return self._client.get(f"/topics/{topic_id}/contacts", params)
