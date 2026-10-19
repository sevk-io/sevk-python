"""
Verifier for sevk webhook deliveries.

sevk uses the Svix-compatible signature scheme (`svix-id`, `svix-timestamp`,
`svix-signature` headers), so this helper or the official `svix` package can
be used. sevk issues canonical ``whsec_`` base64 secrets that can be passed
directly to either verifier.
"""

import base64
import binascii
import hmac
import json
import time
from hashlib import sha256
from typing import Any, Mapping, Optional, Union

TOLERANCE_SECONDS = 5 * 60


class WebhookVerificationError(Exception):
    pass


class WebhookVerifier:
    def __init__(self, secret: str) -> None:
        """Prepare a verifier with the signing secret issued for a webhook."""
        if not secret:
            raise WebhookVerificationError("Webhook secret is required")

        if secret.startswith("whsec_"):
            try:
                self._key = base64.b64decode(secret[len("whsec_") :], validate=True)
            except (binascii.Error, ValueError) as exc:
                raise WebhookVerificationError("Invalid base64 secret") from exc
            if not self._key:
                raise WebhookVerificationError("Invalid base64 secret")
        else:
            self._key = secret.encode("utf-8")

    def verify(
        self, payload: Union[str, bytes], headers: Mapping[str, Optional[str]]
    ) -> Any:
        """Verify the delivery signature and timestamp, then parse its JSON payload."""
        msg_id = _header(headers, "svix-id")
        msg_timestamp = _header(headers, "svix-timestamp")
        msg_signature = _header(headers, "svix-signature")

        if not msg_id or not msg_timestamp or not msg_signature:
            raise WebhookVerificationError("Missing required svix headers")

        if not msg_timestamp.isascii() or not msg_timestamp.isdigit():
            raise WebhookVerificationError("Invalid timestamp header")
        try:
            timestamp = int(msg_timestamp)
        except ValueError as exc:
            raise WebhookVerificationError("Invalid timestamp header") from exc

        now = int(time.time())

        if timestamp < now - TOLERANCE_SECONDS or timestamp > now + TOLERANCE_SECONDS:
            raise WebhookVerificationError("Timestamp outside tolerance window")

        payload_bytes = payload.encode("utf-8") if isinstance(payload, str) else payload
        to_sign = f"{msg_id}.{msg_timestamp}.".encode("utf-8") + payload_bytes
        digest = hmac.new(self._key, to_sign, sha256).digest()
        expected = "v1," + base64.b64encode(digest).decode("ascii")

        for candidate in msg_signature.split(" "):
            if candidate.isascii() and hmac.compare_digest(candidate, expected):
                try:
                    return json.loads(payload)
                except json.JSONDecodeError as exc:
                    raise WebhookVerificationError("Invalid JSON payload") from exc

        raise WebhookVerificationError("Signature mismatch")


def _header(headers: Mapping[str, Optional[str]], name: str) -> Optional[str]:
    for key, value in headers.items():
        normalized = str(key).lower()
        if normalized.startswith("http_"):
            normalized = normalized[len("http_") :]
        normalized = normalized.replace("_", "-")
        if normalized == name and value is not None:
            return value

    return None
