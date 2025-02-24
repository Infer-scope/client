import os
import ssl
from typing import Dict, Any, Union, Type
from uuid import UUID

import httpx
from attr import evolve
from attrs import define, field

from inferscope.models import ArtifactPack, DataDescription, StoredArtifact, Project
from inferscope.models.interactive_base import InteractiveBaseModel

BASE_URl = "https://app.inferscope.tech/api"


def _get_token() -> str:
    if "INFERSCOPE_TOKEN" in os.environ:
        return os.environ["INFERSCOPE_TOKEN"]
    token_file_path = os.path.expanduser("~/.inferscope/token")
    if os.path.exists(token_file_path):
        with open(token_file_path, "r") as f:
            return f.read().strip()
    return ""


@define
class HTTPClient:
    """A Client which has been authenticated for use on secured endpoints

    The following are accepted as keyword arguments and will be used to construct httpx Clients internally:

        ``base_url``: The base URL for the API, all requests are made to a relative path to this URL

        ``cookies``: A dictionary of cookies to be sent with every request

        ``headers``: A dictionary of headers to be sent with every request

        ``timeout``: The maximum amount of a time a request can take. API functions will raise
        httpx.TimeoutException if this is exceeded.

        ``verify_ssl``: Whether or not to verify the SSL certificate of the API server. This should be True in production,
        but can be set to False for testing purposes.

        ``follow_redirects``: Whether or not to follow redirects. Default value is False.

        ``httpx_args``: A dictionary of additional arguments to be passed to the ``httpx.Client`` and ``httpx.AsyncClient`` constructor.


    Attributes:
        raise_on_unexpected_status: Whether or not to raise an errors.UnexpectedStatus if the API returns a
            status code that was not documented in the source OpenAPI document. Can also be provided as a keyword
            argument to the constructor.
        token: The token to use for authentication
        prefix: The prefix to use for the Authorization header
        _auth_header_name: The name of the Authorization header
    """

    raise_on_unexpected_status: bool = field(default=False, kw_only=True)

    _cookies: Dict[str, str] = field(factory=dict, kw_only=True, alias="cookies")
    _headers: Dict[str, str] = field(factory=dict, kw_only=True, alias="headers")
    _timeout: Union[httpx.Timeout, None] = field(
        default=None, kw_only=True, alias="timeout"
    )
    _verify_ssl: Union[str, bool, ssl.SSLContext] = field(
        default=True, kw_only=True, alias="verify_ssl"
    )
    _follow_redirects: bool = field(
        default=False, kw_only=True, alias="follow_redirects"
    )
    _httpx_args: Dict[str, Any] = field(factory=dict, kw_only=True, alias="httpx_args")
    _client: Union[httpx.Client, None] = field(default=None, init=False)
    _async_client: Union[httpx.AsyncClient, None] = field(default=None, init=False)

    token: str
    _base_url: str = field(alias="base_url", default=BASE_URl)
    prefix: str = field(default="Bearer")
    _auth_header_name: str = field(init=False, default="Authorization")

    def with_headers(self, headers: Dict[str, str]) -> "HTTPClient":
        """Get a new client matching this one with additional headers"""
        if self._client is not None:
            self._client.headers.update(headers)
        if self._async_client is not None:
            self._async_client.headers.update(headers)
        return evolve(self, headers={**self._headers, **headers})

    def with_cookies(self, cookies: Dict[str, str]) -> "HTTPClient":
        """Get a new client matching this one with additional cookies"""
        if self._client is not None:
            self._client.cookies.update(cookies)
        if self._async_client is not None:
            self._async_client.cookies.update(cookies)
        return evolve(self, cookies={**self._cookies, **cookies})

    def with_timeout(self, timeout: httpx.Timeout) -> "HTTPClient":
        """Get a new client matching this one with a new timeout (in seconds)"""
        if self._client is not None:
            self._client.timeout = timeout
        if self._async_client is not None:
            self._async_client.timeout = timeout
        return evolve(self, timeout=timeout)

    def set_httpx_client(self, client: httpx.Client) -> "HTTPClient":
        """Manually the underlying httpx.Client

        **NOTE**: This will override any other settings on the client, including cookies, headers, and timeout.
        """
        self._client = client
        return self

    def get_httpx_client(self) -> httpx.Client:
        """Get the underlying httpx.Client, constructing a new one if not previously set"""
        if self._client is None:
            self._headers[self._auth_header_name] = (
                f"{self.prefix} {self.token}" if self.prefix else self.token
            )
            self._client = httpx.Client(
                base_url=self._base_url,
                cookies=self._cookies,
                headers=self._headers,
                timeout=self._timeout,
                verify=self._verify_ssl,
                follow_redirects=self._follow_redirects,
                **self._httpx_args,
            )
        return self._client

    def __enter__(self) -> "HTTPClient":
        """Enter a context manager for self.client—you cannot enter twice (see httpx docs)"""
        self.get_httpx_client().__enter__()
        return self

    def __exit__(self, *args: Any, **kwargs: Any) -> None:
        """Exit a context manager for internal httpx.Client (see httpx docs)"""
        self.get_httpx_client().__exit__(*args, **kwargs)

    def set_async_httpx_client(self, async_client: httpx.AsyncClient) -> "HTTPClient":
        """Manually the underlying httpx.AsyncClient

        **NOTE**: This will override any other settings on the client, including cookies, headers, and timeout.
        """
        self._async_client = async_client
        return self

    def get_async_httpx_client(self) -> httpx.AsyncClient:
        """Get the underlying httpx.AsyncClient, constructing a new one if not previously set"""
        if self._async_client is None:
            self._headers[self._auth_header_name] = (
                f"{self.prefix} {self.token}" if self.prefix else self.token
            )
            self._async_client = httpx.AsyncClient(
                base_url=self._base_url,
                cookies=self._cookies,
                headers=self._headers,
                timeout=self._timeout,
                verify=self._verify_ssl,
                follow_redirects=self._follow_redirects,
                **self._httpx_args,
            )
        return self._async_client

    async def __aenter__(self) -> "HTTPClient":
        """Enter a context manager for underlying httpx.AsyncClient—you cannot enter twice (see httpx docs)"""
        await self.get_async_httpx_client().__aenter__()
        return self

    async def __aexit__(self, *args: Any, **kwargs: Any) -> None:
        """Exit a context manager for underlying httpx.AsyncClient (see httpx docs)"""
        await self.get_async_httpx_client().__aexit__(*args, **kwargs)


@define
class Client:
    token: str = field(default=_get_token())
    server_url: Union[str, None] = field(kw_only=True, default=None)
    _httpx_client: HTTPClient = field()

    _artifacts_service_clients: dict[UUID, HTTPClient] = field(
        kw_only=True, factory=dict
    )

    @_httpx_client.default
    def _httpx_client_creator(self):
        if self.server_url:
            return HTTPClient(self.token, base_url=self.server_url)
        return HTTPClient(self.token)

    def get_artifact_service_http_client_for_project(
        self, project_id: UUID
    ) -> HTTPClient:
        from inferscope.models import ProjectProperties

        client = self._artifacts_service_clients.get(project_id)
        if client is not None:
            return client
        httpx_client = self._httpx_client.get_httpx_client()
        project_props_result = httpx_client.get(f"project/{project_id}/properties")
        project_props_result.raise_for_status()
        project_props = ProjectProperties.model_validate_json(
            project_props_result.content
        )

        client = HTTPClient(self.token, base_url=project_props.artifact_service_api_url)
        self._artifacts_service_clients[project_id] = client
        return client

    def add(self, entity: InteractiveBaseModel) -> InteractiveBaseModel:
        httpx_client = self._httpx_client.get_httpx_client()
        from json import loads

        result = httpx_client.post(
            entity.entity_create_url, json=loads(entity.model_dump_json())
        )
        result.raise_for_status()
        return type(entity).model_validate_json(result.content)

    def get(
        self, cls: Type[InteractiveBaseModel], entity_id: Union[str, UUID]
    ) -> InteractiveBaseModel:
        httpx_client = self._httpx_client.get_httpx_client()
        result = httpx_client.get(cls.entity_url(entity_id))
        result.raise_for_status()
        return cls.model_validate_json(result.content)

    def _artifact_httpx_for_project(self, project_id: UUID) -> httpx.Client:
        artifact_client = self.get_artifact_service_http_client_for_project(project_id)
        return artifact_client.get_httpx_client()

    def create_artifact_package(self, parent_project_id: UUID) -> UUID:
        http_client = self._artifact_httpx_for_project(parent_project_id)
        empty_pack = ArtifactPack(owner_project_uid=parent_project_id)
        result = http_client.post(
            "artifact_pack", json=empty_pack.model_dump(mode="json")
        )
        result.raise_for_status()
        return UUID(result.json())

    def upload_file_to_artifact_pack(
        self,
        parent_project_id: UUID,
        artifact_pack_id: UUID,
        path: str,
        blob: Union[bytes, str, None] = None,
        data_description: Union[DataDescription, None] = None,
    ) -> StoredArtifact:
        http_client = self._artifact_httpx_for_project(parent_project_id)
        from io import BytesIO

        if isinstance(blob, str):
            blob = blob.encode("utf-8")
        result = http_client.put(
            f"artifact_pack/{artifact_pack_id}/{path}", data=BytesIO(blob)
        )
        result.raise_for_status()
        result = StoredArtifact.model_validate(result.json())
        if data_description is not None:
            result.data_description = data_description
            patch_result = http_client.patch(
                f"artifact_pack/{artifact_pack_id}", json=result.model_dump(mode="json")
            )
            patch_result.raise_for_status()
            result = StoredArtifact.model_validate(patch_result.json())
        return result

    def get_default_project(self) -> Project:
        httpx_client = self._httpx_client.get_httpx_client()
        result = httpx_client.get("project/default")
        result.raise_for_status()
        return Project.model_validate_json(result.content)
