"""
sevk SDK exception classes.

Maps the API's error envelope onto a typed exception hierarchy. The base
``SevkError`` extends ``Exception`` so existing ``except Exception`` callers
keep working.

The API emits two envelope shapes:

- Handled errors: ``{ "statusCode", "code", "message" }`` plus optional
  ``details`` and, for ``VALIDATION_ERROR``, ``fields: { field: [str, ...] }``
- Unhandled failures: ``{ "error": "Internal Server Error", "message" }``
"""

from typing import Any, Dict, List, Optional


class SevkError(Exception):
    """Base class for every error raised by the sevk SDK."""

    def __init__(
        self,
        message: str,
        status_code: int = 0,
        code: str = "UNKNOWN_ERROR",
        response_body: Optional[Any] = None,
        details: Optional[Any] = None,
        fields: Optional[Dict[str, List[str]]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.response_body = response_body
        self.details = details
        self.fields: Dict[str, List[str]] = fields or {}

    def __str__(self) -> str:
        return f"[{self.status_code} {self.code}] {self.message}"


class BadRequestError(SevkError):
    """HTTP 400 - request was rejected by a domain or precondition guard."""


class UnauthorizedError(SevkError):
    """HTTP 401 - missing, malformed, or revoked API key."""


class ForbiddenError(SevkError):
    """HTTP 403 - key authenticated but lacks the required capability."""


class NotFoundError(SevkError):
    """HTTP 404 - resource does not exist in this project."""


class ConflictError(SevkError):
    """HTTP 409 - uniqueness constraint already satisfied by another row."""


class RateLimitError(SevkError):
    """HTTP 429 - per-key or per-project rate limit hit."""

    def __init__(
        self,
        message: str,
        status_code: int = 429,
        code: str = "TOO_MANY_REQUESTS",
        response_body: Optional[Any] = None,
        retry_after: Optional[int] = None,
        details: Optional[Any] = None,
        fields: Optional[Dict[str, List[str]]] = None,
    ):
        super().__init__(message, status_code, code, response_body, details, fields)
        self.retry_after = retry_after


class ValidationError(SevkError):
    """Request input rejected by the API."""

    def __init__(
        self,
        message: str,
        status_code: int = 422,
        code: str = "VALIDATION_ERROR",
        response_body: Optional[Any] = None,
        fields: Optional[Dict[str, List[str]]] = None,
        details: Optional[Any] = None,
    ):
        super().__init__(message, status_code, code, response_body, details, fields)


class InternalServerError(SevkError):
    """HTTP 5xx - unexpected server failure. Retry with backoff."""


_MAX_RETRY_AFTER_SECONDS = 2_147_483_647


def _parse_retry_after(value: Optional[str]) -> Optional[int]:
    if value is None:
        return None
    normalized = value.strip()
    if not normalized.isascii() or not normalized.isdigit():
        return None
    seconds = int(normalized)
    return seconds if seconds <= _MAX_RETRY_AFTER_SECONDS else None


def _from_response(response: Any) -> SevkError:
    """Inspect a ``httpx.Response`` (or anything with ``status_code``,
    ``headers``, ``json()``, ``text``) and build the right ``SevkError``.

    Handles both error envelopes documented above. Falls back to a generic
    ``SevkError`` when the body is not JSON.
    """
    status_code = getattr(response, "status_code", 0)

    decode_failed = object()
    body: Any = decode_failed
    try:
        body = response.json()
    except Exception:
        pass
    raw_text = getattr(response, "text", "")
    response_body = raw_text if body is decode_failed else body

    payload: Dict[str, Any] = {}
    if isinstance(body, dict):
        if isinstance(body.get("error"), dict):
            payload = body["error"]
        else:
            payload = body

    raw_code = payload.get("code")
    code = raw_code if isinstance(raw_code, str) and raw_code else "UNKNOWN_ERROR"
    raw_message = payload.get("message")
    text_message = (
        body.strip()
        if isinstance(body, str) and body.strip()
        else raw_text.strip()
        if body is decode_failed and isinstance(raw_text, str) and raw_text.strip()
        else None
    )
    message = (
        raw_message
        if isinstance(raw_message, str) and raw_message
        else text_message or f"HTTP {status_code}"
    )
    details = payload.get("details")

    fields_raw = payload.get("fields")
    fields: Dict[str, List[str]] = {}
    if isinstance(fields_raw, dict):
        for key, value in fields_raw.items():
            if isinstance(value, list):
                fields[str(key)] = [str(v) for v in value]
            else:
                fields[str(key)] = [str(value)]

    if status_code == 422 or (
        status_code == 400 and (code == "VALIDATION_ERROR" or fields)
    ):
        return ValidationError(
            message=message,
            status_code=status_code or 422,
            code=code or "VALIDATION_ERROR",
            response_body=response_body,
            fields=fields,
            details=details,
        )

    if status_code == 400:
        return BadRequestError(
            message, status_code, code or "BAD_REQUEST", response_body, details, fields
        )
    if status_code == 401:
        return UnauthorizedError(
            message, status_code, code or "UNAUTHORIZED", response_body, details, fields
        )
    if status_code == 403:
        return ForbiddenError(
            message, status_code, code or "FORBIDDEN", response_body, details, fields
        )
    if status_code == 404:
        return NotFoundError(
            message, status_code, code or "NOT_FOUND", response_body, details, fields
        )
    if status_code == 409:
        return ConflictError(
            message, status_code, code or "CONFLICT", response_body, details, fields
        )
    if status_code == 429:
        retry_after_header = None
        headers = getattr(response, "headers", None)
        if headers is not None:
            try:
                retry_after_header = headers.get("Retry-After") or headers.get(
                    "retry-after"
                )
            except Exception:
                retry_after_header = None
        return RateLimitError(
            message=message,
            status_code=status_code,
            code=code or "TOO_MANY_REQUESTS",
            response_body=response_body,
            retry_after=_parse_retry_after(retry_after_header),
            details=details,
            fields=fields,
        )
    if status_code >= 500:
        return InternalServerError(
            message,
            status_code,
            code or "INTERNAL_SERVER_ERROR",
            response_body,
            details,
            fields,
        )

    return SevkError(message, status_code, code, response_body, details, fields)


__all__ = [
    "SevkError",
    "BadRequestError",
    "UnauthorizedError",
    "ForbiddenError",
    "NotFoundError",
    "ConflictError",
    "RateLimitError",
    "ValidationError",
    "InternalServerError",
]
