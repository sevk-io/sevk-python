import os

import pytest

from sevk import Sevk, SevkOptions

API_KEY = os.environ.get("SEVK_API_KEY")
FROM = os.environ.get("SEVK_TEST_FROM")
TO = os.environ.get("SEVK_TEST_TO")


@pytest.mark.skipif(
    not (API_KEY and FROM and TO),
    reason="SEVK_API_KEY, SEVK_TEST_FROM and SEVK_TEST_TO are required",
)
def test_sends_a_markup_email_through_the_sevk_api() -> None:
    assert API_KEY and FROM and TO
    base_url = os.environ.get("SEVK_BASE_URL") or SevkOptions().base_url
    with Sevk(API_KEY, SevkOptions(base_url=base_url)) as client:
        response = client.emails.send(
            {
                "from": FROM,
                "to": TO,
                "subject": "Sevk SDK send test",
                "markup": "<section><paragraph>Hello from the Sevk Python SDK</paragraph></section>",
            }
        )
    identifier = dict(response).get("id")
    assert isinstance(identifier, str)
    assert identifier
