from __future__ import annotations
import json
from collections.abc import Callable, Collection
from typing import Any, Literal
from pydantic import BaseModel, ValidationError
from returns.result import Result, Success, Failure
import httpx

from pyfb_kit.common.models import GraphVersion, APIUsage, UsageLimit
from pyfb_kit.common.errors import SDKError, FacebookAPIError, DataValidationError

from .models import (
    QueryParams,
    FormData,
    RequestFiles,
)

_USAGE_HEADERS = {
    "x-app-usage": "app",
    "x-page-usage": "page",
    "x-ad-account-usage": "ad_account",
}

class GraphClient:
    def __init__(
        self,
        access_token: str,
        graph_version: GraphVersion = GraphVersion.latest(),
        on_usage: Callable[[APIUsage], None] | None = None,
    ):
        self._access_token = access_token
        self._version = graph_version
        self._on_usage = on_usage
        self._httpx_client = httpx.AsyncClient(
            base_url=f"https://graph.facebook.com/{self._version.value}"
        )

    def _emit_usage(self, response: httpx.Response) -> None:
        if self._on_usage is None:
            return

        usage_dict: dict[str, UsageLimit | None] = {}
        for header, key in _USAGE_HEADERS.items():
            value = response.headers.get(header)
            if value is not None:
                try:
                    data = json.loads(value)
                    usage_dict[key] = UsageLimit.model_validate(data)
                except Exception:
                    usage_dict[key] = None
            else:
                usage_dict[key] = None

        usage = APIUsage(**usage_dict)
        self._on_usage(usage)

    def _build_query(
        self,
        *,
        fields: Collection[str] | None,
        params: QueryParams | None,
    ) -> dict[str, Any]:
        query = dict(params or {})
        query["access_token"] = self._access_token
        if fields:
            query["fields"] = ",".join(fields)

        return query

    @staticmethod
    def _normalize_path(path: str) -> str:
        return "/" + path.lstrip("/")

    async def request(
        self,
        method: Literal["GET", "POST", "DELETE", "PUT", "PATCH"],
        path: str,
        *,
        fields: Collection[str] | None = None,
        params: QueryParams | None = None,
        data: FormData | None = None,
        files: RequestFiles | None = None,
    ) -> httpx.Response:
        query = self._build_query(
            fields=fields,
            params=params,
        )

        response = await self._httpx_client.request(
            method=method,
            url=self._normalize_path(path),
            params=query,
            data=data,
            files=files,
        )

        self._emit_usage(response)
        return response

    async def get[T: BaseModel](
        self,
        path: str,
        response_model: type[T],
        *,
        fields: Collection[str] | None = None,
        params: QueryParams | None = None
    ) -> Result[T, SDKError]:

        response = await self.request(
            method="GET",
            path=path,
            fields=fields,
            params=params
        )

        if response.is_error:
            return Failure(FacebookAPIError.from_response(response))

        payload = response.json()

        try:
            return Success(response_model.model_validate(payload))
        except ValidationError as e:
            return Failure(DataValidationError.from_pydantic_error(e))


    async def post[T: BaseModel](
        self,
        path: str,
        response_model: type[T],
        *,
        fields: Collection[str] | None = None,
        params: QueryParams | None = None,
        data: FormData | None = None,
        files: RequestFiles | None = None
    ) -> Result[T, SDKError]:

        response = await self.request(
            method="POST",
            path=path,
            fields=fields,
            params=params,
            data=data,
            files=files
        )

        if response.is_error:
            return Failure(FacebookAPIError.from_response(response))

        payload = response.json()

        try:
            return Success(response_model.model_validate(payload))
        except ValidationError as e:
            return Failure(DataValidationError.from_pydantic_error(e))


    async def delete[T: BaseModel](
        self,
        path: str,
        response_model: type[T],
        *,
        fields: Collection[str] | None = None,
        params: QueryParams | None = None
    ) -> Result[T, SDKError]:

        response = await self.request(
            method="DELETE",
            path=path,
            fields=fields,
            params=params
        )

        if response.is_error:
            return Failure(FacebookAPIError.from_response(response))

        data = response.json()

        try:
            return Success(response_model.model_validate(data))
        except ValidationError as e:
            return Failure(DataValidationError.from_pydantic_error(e))

    async def put[T: BaseModel](
        self,
        path: str,
        response_model: type[T],
        *,
        fields: Collection[str] | None = None,
        params: QueryParams | None = None,
        data: FormData | None = None,
        files: RequestFiles | None = None
    ) -> Result[T, SDKError]:

        response = await self.request(
            method="PUT",
            path=path,
            fields=fields,
            params=params,
            data=data,
            files=files
        )

        if response.is_error:
            return Failure(FacebookAPIError.from_response(response))

        payload = response.json()

        try:
            return Success(response_model.model_validate(payload))
        except ValidationError as e:
            return Failure(DataValidationError.from_pydantic_error(e))

    async def patch[T: BaseModel](
        self,
        path: str,
        response_model: type[T],
        *,
        fields: Collection[str] | None = None,
        params: QueryParams | None = None,
        data: FormData | None = None,
        files: RequestFiles | None = None
    ) -> Result[T, SDKError]:

        response = await self.request(
            method="PATCH",
            path=path,
            fields=fields,
            params=params,
            data=data,
            files=files
        )

        if response.is_error:
            return Failure(FacebookAPIError.from_response(response))

        payload = response.json()

        try:
            return Success(response_model.model_validate(payload))
        except ValidationError as e:
            return Failure(DataValidationError.from_pydantic_error(e))
