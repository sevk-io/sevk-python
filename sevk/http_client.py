import json
from typing import Any, Mapping, Optional

import httpx

from . import __version__
from .exceptions import SevkError, _from_response
from .options import SevkOptions


class HttpClient:
    """Authenticated JSON transport used by the resource clients."""

    def __init__(self, api_key: str, options: SevkOptions) -> None:
        self.api_key = api_key
        self.base_url = options.base_url.rstrip("/")
        self.timeout = options.timeout
        self._client = httpx.Client(
            timeout=self.timeout,
            follow_redirects=False,
            headers={
                "Authorization": f"Bearer {self.api_key}" if self.api_key else "Bearer",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": f"sevk-python/{__version__}",
            },
        )

    def _handle_response(self, response: httpx.Response) -> Any:
        if not response.is_success:
            raise _from_response(response)

        if response.status_code == 204:
            return {}

        try:
            result = response.json()
        except ValueError as error:
            raise SevkError(
                "Expected a JSON response body but received empty or malformed JSON",
                status_code=response.status_code,
                code="INVALID_RESPONSE",
                response_body=response.text,
            ) from error
        if not isinstance(result, dict):
            raise SevkError(
                "Expected a JSON object response",
                status_code=response.status_code,
                code="INVALID_RESPONSE",
                response_body=response.text,
            )
        return result

    def get(self, path: str, params: Optional[Mapping[str, Any]] = None) -> Any:
        return self._request("GET", path, params=params)

    def post(
        self,
        path: str,
        data: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Any:
        return self._request("POST", path, data=data, headers=headers)

    def put(self, path: str, data: Optional[Mapping[str, Any]] = None) -> Any:
        return self._request("PUT", path, data=data)

    def patch(self, path: str, data: Optional[Mapping[str, Any]] = None) -> Any:
        return self._request("PATCH", path, data=data)

    def delete(self, path: str) -> Any:
        return self._request("DELETE", path)

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        data: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> Any:
        query = (
            {key: value for key, value in params.items() if value is not None}
            if params is not None
            else None
        )
        body = None
        if data is not None:
            try:
                body = json.dumps(
                    data, ensure_ascii=False, separators=(",", ":"), allow_nan=False
                ).encode("utf-8")
            except (TypeError, ValueError) as error:
                raise SevkError(str(error), code="SERIALIZATION_ERROR") from error

        try:
            response = self._client.request(
                method, self._url(path), params=query, content=body, headers=headers
            )
        except httpx.TimeoutException as error:
            raise SevkError(str(error), code="TIMEOUT") from error
        except httpx.RequestError as error:
            raise SevkError(str(error), code="NETWORK_ERROR") from error

        return self._handle_response(response)

    def close(self) -> None:
        self._client.close()

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"
