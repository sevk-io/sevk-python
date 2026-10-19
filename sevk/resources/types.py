from typing import Dict, List, Literal, TypedDict, Union

JSONValue = Union[
    None,
    bool,
    int,
    float,
    str,
    List["JSONValue"],
    Dict[str, "JSONValue"],
]
JSONObject = Dict[str, JSONValue]


class PaginationParams(TypedDict, total=False):
    page: int
    limit: int
    after: str
    before: str


class SearchPaginationParams(PaginationParams, total=False):
    search: str


class DeletedResponse(TypedDict):
    id: str
    deleted: Literal[True]


class MembershipContact(TypedDict):
    id: str
    email: str
    subscribed: bool
    createdAt: str


class AddContactsResponse(TypedDict):
    added: int
    contacts: List[MembershipContact]


class AudienceContactRemovedResponse(TypedDict):
    audienceId: str
    contactId: str
    removed: Literal[True]


class TopicContactRemovedResponse(TypedDict):
    topicId: str
    contactId: str
    removed: Literal[True]
