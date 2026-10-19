from typing import Optional, TypedDict, Union

from ._base import Resource
from .types import JSONObject


class _SubscribeParamsRequired(TypedDict):
    email: str


class SubscribeParams(_SubscribeParamsRequired, total=False):
    audienceId: str
    data: JSONObject


class UnsubscribeParams(TypedDict, total=False):
    email: str
    contactId: str
    broadcastId: str


class SubscriptionContact(TypedDict):
    id: str
    email: str
    subscribed: bool


class SubscriptionContactWithData(SubscriptionContact):
    data: Optional[JSONObject]


class SubscriptionAudience(TypedDict):
    id: str
    name: str


class AlreadySubscribedResponse(TypedDict):
    contact: SubscriptionContact
    alreadySubscribed: bool
    message: str


class AudienceSubscribedResponse(TypedDict):
    contact: SubscriptionContactWithData
    audience: Optional[SubscriptionAudience]


SubscribeResponse = Union[AlreadySubscribedResponse, AudienceSubscribedResponse]


class _UnsubscribeResponseRequired(TypedDict):
    contact: SubscriptionContact


class UnsubscribeResponse(_UnsubscribeResponseRequired, total=False):
    alreadyUnsubscribed: bool


class Subscriptions(Resource):
    """Subscriptions API resource"""

    def subscribe(self, data: SubscribeParams) -> SubscribeResponse:
        """Subscribe a contact and optionally add it to an audience."""
        return self._client.post("/subscriptions/subscribe", data)

    def unsubscribe(self, data: UnsubscribeParams) -> UnsubscribeResponse:
        """Globally unsubscribe a contact and optionally attribute the action."""
        return self._client.post("/subscriptions/unsubscribe", data)
