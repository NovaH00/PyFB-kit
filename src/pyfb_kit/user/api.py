from collections.abc import AsyncIterator

import httpx
from pydantic import ValidationError
from returns.result import Result, Success, Failure

from pyfb_kit.graph import GraphClient, GraphConnection
from pyfb_kit.common.errors import (
    SDKError,
    FacebookAPIError,
    DataValidationError,
)
from pyfb_kit.page.models import Page

from .models import User


class UserAPI:
    """API for interacting with the authenticated Facebook user.

    Provides methods to retrieve user info and manage their pages.
    """

    def __init__(self, graph: GraphClient):
        self._graph = graph

    async def get(self) -> Result[User, SDKError]:
        """Retrieve the authenticated user's details."""
        return await self._graph.get(
            "/me",
            User,
            fields=["id", "name"],
        )

    async def get_pages(
        self,
        *,
        limit: int | None = None,
    ) -> Result[GraphConnection[Page], SDKError]:
        """Retrieve paginated pages owned by the authenticated user."""
        return await self._graph.get(
            "/me/accounts",
            GraphConnection[Page],
            params={"limit": limit} if limit is not None else None,
        )

    async def iter_pages(
        self,
        *,
        page_size: int | None = None,
    ) -> AsyncIterator[Result[Page, SDKError]]:
        """Iterate over all pages owned by the authenticated user as an async generator."""
        result = await self.get_pages(limit=page_size)

        if isinstance(result, Failure):
            yield result
            return

        connection = result.unwrap()

        while True:
            for page in connection.data:
                yield Success(page)

            next_url = (
                connection.paging.next
                if connection.paging is not None
                else None
            )

            if next_url is None:
                return

            async with httpx.AsyncClient() as client:
                response = await client.get(next_url)

            if response.is_error:
                yield Failure(FacebookAPIError.from_response(response))
                return

            try:
                connection = GraphConnection[Page].model_validate(
                    response.json()
                )
            except ValidationError as e:
                yield Failure(DataValidationError.from_pydantic_error(e))
                return
