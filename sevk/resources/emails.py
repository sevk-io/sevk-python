from typing import Any, Dict, List, Literal, Mapping, Optional, TypedDict, Union, cast

from ..markup import render
from ._base import Resource

EmailStatus = Literal[
    "PENDING",
    "SCHEDULED",
    "SENT",
    "DELIVERED",
    "BOUNCED",
    "OPENED",
    "COMPLAINT",
    "FAILED",
    "SUPPRESSED",
    "CANCELLED",
]
EmailType = Literal["MARKETING", "TRANSACTIONAL"]


class _EmailAttachmentRequired(TypedDict):
    filename: str
    content: str
    content_type: str


class EmailAttachment(_EmailAttachmentRequired, total=False):
    """Email attachment structure.

    ``filename``, ``content``, and ``content_type`` are required. Set ``cid``
    for inline images referenced from the HTML body via
    ``<img src="cid:...">``.
    """

    cid: str


class EmailTracking(TypedDict, total=False):
    """Per-email tracking overrides. When a field is omitted, the sending
    domain's default applies."""

    open: bool
    click: bool


class _SendEmailOptional(TypedDict, total=False):
    html: Optional[str]
    text: Optional[str]
    markup: str
    reply_to: Union[str, List[str]]
    cc: Union[str, List[str]]
    bcc: Union[str, List[str]]
    attachments: List[EmailAttachment]
    tracking: EmailTracking
    headers: Dict[str, str]


_SendEmailRequired = TypedDict(
    "_SendEmailRequired",
    {
        "from": str,
        "to": Union[str, List[str]],
        "subject": str,
    },
)

_SendBulkEmailRequired = TypedDict(
    "_SendBulkEmailRequired",
    {
        "from": str,
        "to": str,
        "subject": str,
    },
)


class _SendEmailScheduledOptional(TypedDict, total=False):
    scheduled_at: str


class SendEmailParams(
    _SendEmailRequired,
    _SendEmailOptional,
    _SendEmailScheduledOptional,
):
    pass


class SendBulkEmailParams(_SendBulkEmailRequired, _SendEmailOptional):
    pass


class UpdateScheduledEmailParams(TypedDict):
    scheduled_at: str


class ScheduledEmailMutationResponse(TypedDict):
    id: str


class SendOptions(TypedDict, total=False):
    idempotency_key: str


class SendSingleEmailResponse(TypedDict):
    id: str


class SendMultipleEmailResponse(TypedDict):
    ids: List[str]


SendEmailResponse = Union[SendSingleEmailResponse, SendMultipleEmailResponse]


class BulkEmailError(TypedDict):
    index: int
    email: str
    error: str


class _SendBulkEmailResponseRequired(TypedDict):
    success: int
    failed: int
    ids: List[str]


class SendBulkEmailResponse(_SendBulkEmailResponseRequired, total=False):
    errors: List[BulkEmailError]


_EmailRequired = TypedDict(
    "_EmailRequired",
    {
        "id": str,
        "messageId": Optional[str],
        "providerMessageId": Optional[str],
        "from": Optional[str],
        "to": Optional[str],
        "subject": Optional[str],
        "body": Optional[str],
        "text": Optional[str],
        "status": EmailStatus,
        "type": EmailType,
        "userAgent": Optional[str],
        "contactId": Optional[str],
        "broadcastId": Optional[str],
        "broadcastVariantId": Optional[str],
        "projectId": str,
        "openedAt": Optional[str],
        "clickedAt": Optional[str],
        "unsubscribedAt": Optional[str],
        "scheduledAt": Optional[str],
        "cancelledAt": Optional[str],
        "createdAt": str,
        "updatedAt": str,
    },
)


class Email(_EmailRequired):
    pass


def _to_wire(params: Mapping[str, Any]) -> Dict[str, Any]:
    """Render markup to html locally and strip the markup key before sending."""
    if not isinstance(params, Mapping):
        return cast(Dict[str, Any], params)

    payload = dict(params)
    markup = payload.pop("markup", None)
    if "scheduled_at" in payload:
        payload["scheduledAt"] = payload.pop("scheduled_at")

    if markup:
        payload["html"] = render(markup)

    attachments = payload.get("attachments")

    if isinstance(attachments, list):
        payload["attachments"] = [
            {
                ("contentType" if key == "content_type" else key): value
                for key, value in attachment.items()
            }
            if isinstance(attachment, dict)
            else attachment
            for attachment in attachments
        ]

    return payload


def _idempotency_headers(
    options: Optional[SendOptions],
) -> Optional[Dict[str, str]]:
    if not options:
        return None

    key = options.get("idempotency_key")

    if key is None:
        return None

    return {"Idempotency-Key": str(key)}


class Emails(Resource):
    """Emails API resource"""

    def send(
        self,
        params: SendEmailParams,
        options: Optional[SendOptions] = None,
    ) -> SendEmailResponse:
        """Send one transactional email, rendering local markup when supplied."""
        wire = _to_wire(params)
        return self._client.post(
            "/emails",
            wire,
            headers=_idempotency_headers(options),
        )

    def get(self, email_id: str) -> Email:
        """Retrieve a sent email and its current delivery state."""
        return self._client.get(f"/emails/{email_id}")

    def update(
        self,
        email_id: str,
        params: UpdateScheduledEmailParams,
    ) -> ScheduledEmailMutationResponse:
        """Move an unattempted scheduled email to a new delivery time."""
        return self._client.patch(
            f"/emails/{email_id}",
            {
                ("scheduledAt" if key == "scheduled_at" else key): value
                for key, value in params.items()
            },
        )

    def cancel(self, email_id: str) -> ScheduledEmailMutationResponse:
        """Cancel an unattempted scheduled email."""
        return self._client.post(f"/emails/{email_id}/cancel")

    def send_bulk(
        self,
        emails: List[SendBulkEmailParams],
        options: Optional[SendOptions] = None,
    ) -> SendBulkEmailResponse:
        """Send up to 100 transactional emails and return per-request results."""
        wire_emails = (
            [_to_wire(email) for email in emails]
            if isinstance(emails, (list, tuple))
            else emails
        )

        return self._client.post(
            "/emails/bulk",
            {"emails": wire_emails},
            headers=_idempotency_headers(options),
        )
