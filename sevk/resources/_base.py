from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..http_client import HttpClient


class Resource:
    def __init__(self, client: "HttpClient") -> None:
        self._client = client
