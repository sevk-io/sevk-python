from types import TracebackType
from typing import Optional, Type

from .http_client import HttpClient
from .options import SevkOptions
from .resources.activity import Activity
from .resources.audiences import Audiences
from .resources.broadcasts import Broadcasts
from .resources.contacts import Contacts
from .resources.domains import Domains
from .resources.emails import Emails
from .resources.inbound import Inbound
from .resources.markup import Markup
from .resources.outbound import Outbound
from .resources.segments import Segments
from .resources.subscriptions import Subscriptions
from .resources.templates import Templates
from .resources.topics import Topics
from .resources.usage import Usage
from .resources.webhooks import Webhooks


class Sevk:
    """
    sevk API Client

    Usage:
        sevk = Sevk("sevk_your_api_key")
        contacts = sevk.contacts.list()
    """

    def __init__(self, api_key: str, options: Optional[SevkOptions] = None) -> None:
        """Create an API client and expose its resource clients as attributes."""
        if options is None:
            options = SevkOptions()

        self._client = HttpClient(api_key, options)

        self.contacts = Contacts(self._client)
        self.audiences = Audiences(self._client)
        self.templates = Templates(self._client)
        self.broadcasts = Broadcasts(self._client)
        self.domains = Domains(self._client)
        self.topics = Topics(self._client)
        self.segments = Segments(self._client)
        self.subscriptions = Subscriptions(self._client)
        self.emails = Emails(self._client)
        self.webhooks = Webhooks(self._client)
        self.activity = Activity(self._client)
        self.inbound = Inbound(self._client)
        self.outbound = Outbound(self._client)
        self.usage = Usage(self._client)
        self.markup = Markup()

    def close(self) -> None:
        """Release connections held by the API client."""
        self._client.close()

    def __enter__(self) -> "Sevk":
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self.close()
