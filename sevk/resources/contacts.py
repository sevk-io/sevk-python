from typing import List, Literal, Optional, TypedDict

from ._base import Resource
from .activity import ActivityAction
from .types import DeletedResponse, JSONObject, JSONValue, PaginationParams

UnsubscribeSource = Literal["USER", "API", "ADMIN", "BOUNCE", "COMPLAINT"]


class _ContactRequired(TypedDict):
    id: str
    email: str
    subscribed: bool
    data: Optional[JSONObject]
    createdAt: str
    updatedAt: str
    projectId: str
    lastEventAt: Optional[str]
    unsubscribedAt: Optional[str]
    unsubscribedBy: Optional[UnsubscribeSource]
    resubscriptionLocked: bool
    bounceCount: int
    lastBouncedAt: Optional[str]


class Contact(_ContactRequired):
    pass


class _ListContactsResponseRequired(TypedDict):
    items: List[Contact]


class ListContactsResponse(_ListContactsResponseRequired, total=False):
    total: int
    page: int
    totalPages: int
    hasMore: bool
    nextCursor: Optional[str]
    prevCursor: Optional[str]


class _CreateContactParamsRequired(TypedDict):
    email: str


class CreateContactParams(_CreateContactParamsRequired, total=False):
    subscribed: bool
    data: JSONObject


class UpdateContactParams(TypedDict, total=False):
    email: str
    subscribed: bool
    data: Optional[JSONObject]


class ListContactsParams(TypedDict, total=False):
    page: int
    limit: int
    after: str
    before: str
    search: str
    excludeAudience: str
    subscribed: bool


class _BulkContactUpdateRequired(TypedDict):
    email: str


class BulkContactUpdate(_BulkContactUpdateRequired, total=False):
    subscribed: bool
    data: Optional[JSONObject]


class BulkUpdateContactsParams(TypedDict):
    contacts: List[BulkContactUpdate]


class BulkUpdateContactsResponse(TypedDict):
    updated: int
    notFound: int
    errors: List[str]
    updatedEmails: List[str]
    notFoundEmails: List[str]


class _BulkContactImportRequired(TypedDict):
    email: str


class BulkContactImport(_BulkContactImportRequired, total=False):
    subscribed: bool
    data: JSONObject


class _BulkImportContactsParamsRequired(TypedDict):
    contacts: List[BulkContactImport]


class BulkImportContactsParams(_BulkImportContactsParamsRequired, total=False):
    audienceId: str
    topicId: str


class ImportedContact(TypedDict):
    id: str
    email: str
    subscribed: bool


class BulkImportContactsResponse(TypedDict):
    created: int
    errors: List[str]
    contacts: List[ImportedContact]


class ContactActivityBroadcast(TypedDict):
    id: str
    name: Optional[str]


class ContactActivityEmail(TypedDict):
    id: str
    subject: Optional[str]


class ContactActivityItem(TypedDict):
    id: str
    action: ActivityAction
    description: Optional[str]
    createdAt: str
    userAgent: Optional[str]
    link: Optional[str]
    metadata: Optional[JSONValue]
    broadcast: Optional[ContactActivityBroadcast]
    email: Optional[ContactActivityEmail]


class _ContactActivityResponseRequired(TypedDict):
    items: List[ContactActivityItem]


class ContactActivityResponse(_ContactActivityResponseRequired, total=False):
    total: int
    page: int
    totalPages: int
    hasMore: bool
    nextCursor: Optional[str]
    prevCursor: Optional[str]


class Contacts(Resource):
    """Contacts API resource"""

    def list(self, params: Optional[ListContactsParams] = None) -> ListContactsResponse:
        """List contacts with optional pagination, search, and filters."""
        return self._client.get("/contacts", params)

    def create(self, data: CreateContactParams) -> Contact:
        """Create a contact and optionally attach custom metadata."""
        return self._client.post("/contacts", data)

    def get(self, contact_id: str) -> Contact:
        """Retrieve a contact by ID."""
        return self._client.get(f"/contacts/{contact_id}")

    def update(self, contact_id: str, data: UpdateContactParams) -> Contact:
        """Update a contact while preserving omitted fields."""
        return self._client.put(f"/contacts/{contact_id}", data)

    def delete(self, contact_id: str) -> DeletedResponse:
        """Delete a contact and remove its audience and topic memberships."""
        return self._client.delete(f"/contacts/{contact_id}")

    def bulk_update(self, data: BulkUpdateContactsParams) -> BulkUpdateContactsResponse:
        """Update contacts by email and report entries that were not found."""
        return self._client.put("/contacts/bulk-update", data)

    def bulk_import(self, data: BulkImportContactsParams) -> BulkImportContactsResponse:
        """Import contacts and optionally attach them to an audience or topic."""
        return self._client.post("/contacts/import", data)

    def activity(
        self,
        contact_id: str,
        params: Optional[PaginationParams] = None,
    ) -> ContactActivityResponse:
        """List delivery and engagement activity for a contact."""
        return self._client.get(f"/contacts/{contact_id}/activity", params)
