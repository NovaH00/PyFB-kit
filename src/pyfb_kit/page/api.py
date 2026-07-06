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
from pyfb_kit.post.models import Post

from .models import Page


class PageAPI:
    """API for interacting with a Facebook Page.

    Provides methods to manage a page and its posts.
    """

    def __init__(
        self,
        graph: GraphClient,
        page_id: str = "me",
    ):
        self._graph = graph
        self._page_id = page_id

    async def get(self) -> Result[Page, SDKError]:
        """Retrieve the page's details."""
        return await self._graph.get(
            f"/{self._page_id}",
            Page,
            fields=["id", "name", "category", "access_token"],
        )

    async def create_post(
        self,
        message: str,
    ) -> Result[Post, SDKError]:
        """Create a new post on this page's feed."""
        return await self._graph.post(
            f"/{self._page_id}/feed",
            Post,
            data={"message": message},
        )

    async def get_posts(
        self,
        *,
        limit: int | None = None,
    ) -> Result[GraphConnection[Post], SDKError]:
        """Retrieve paginated posts from this page."""
        return await self._graph.get(
            f"/{self._page_id}/posts",
            GraphConnection[Post],
            params={"limit": limit} if limit is not None else None,
        )

    async def iter_posts(
        self,
        *,
        page_size: int | None = None,
    ) -> AsyncIterator[Result[Post, SDKError]]:
        """Iterate over all posts from this page as an async generator."""
        result = await self.get_posts(limit=page_size)

        if isinstance(result, Failure):
            yield result
            return

        connection = result.unwrap()

        while True:
            for post in connection.data:
                yield Success(post)

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
                connection = GraphConnection[Post].model_validate(
                    response.json()
                )
            except ValidationError as e:
                yield Failure(DataValidationError.from_pydantic_error(e))
                return
