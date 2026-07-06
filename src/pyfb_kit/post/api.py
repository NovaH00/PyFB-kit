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
from pyfb_kit.common.models import GraphResponse, Reaction
from pyfb_kit.comment.models import Comment

from .models import Post


class PostAPI:
    """API for interacting with a single Facebook post.

    Provides methods to read, update, delete, and interact with a post
    and its sub-resources (comments, reactions, likes).
    """

    def __init__(
        self,
        graph: GraphClient,
        post_id: str,
    ):
        self._graph = graph
        self._post_id = post_id

    async def get(
        self,
    ) -> Result[Post, SDKError]:
        """Retrieve the post's details."""
        return await self._graph.get(
            f"/{self._post_id}",
            Post,
            fields=["id", "message", "created_time", "story"],
        )

    async def update(
        self,
        *,
        message: str,
    ) -> Result[Post, SDKError]:
        """Update the post's message."""
        return await self._graph.post(
            f"/{self._post_id}",
            Post,
            data={"message": message},
        )

    async def delete(
        self,
    ) -> Result[GraphResponse, SDKError]:
        """Delete the post."""
        return await self._graph.delete(
            f"/{self._post_id}",
            GraphResponse,
        )

    async def get_comments(
        self,
        *,
        limit: int | None = None,
    ) -> Result[GraphConnection[Comment], SDKError]:
        """Retrieve paginated comments on this post."""
        return await self._graph.get(
            f"/{self._post_id}/comments",
            GraphConnection[Comment],
            params={"limit": limit} if limit is not None else None,
        )

    async def iter_comments(
        self,
        *,
        page_size: int | None = None,
    ) -> AsyncIterator[Result[Comment, SDKError]]:
        """Iterate over all comments on this post as an async generator."""
        result = await self.get_comments(limit=page_size)

        if isinstance(result, Failure):
            yield result
            return

        connection = result.unwrap()

        while True:
            for comment in connection.data:
                yield Success(comment)

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
                connection = GraphConnection[Comment].model_validate(
                    response.json()
                )
            except ValidationError as e:
                yield Failure(DataValidationError.from_pydantic_error(e))
                return

    async def create_comment(
        self,
        message: str,
    ) -> Result[Comment, SDKError]:
        """Create a comment on this post."""
        return await self._graph.post(
            f"/{self._post_id}/comments",
            Comment,
            data={"message": message},
        )

    async def get_reactions(
        self,
        *,
        limit: int | None = None,
    ) -> Result[GraphConnection[Reaction], SDKError]:
        """Retrieve paginated reactions on this post."""
        return await self._graph.get(
            f"/{self._post_id}/reactions",
            GraphConnection[Reaction],
            params={"limit": limit} if limit is not None else None,
        )

    async def iter_reactions(
        self,
        *,
        page_size: int | None = None,
    ) -> AsyncIterator[Result[Reaction, SDKError]]:
        """Iterate over all reactions on this post as an async generator."""
        result = await self.get_reactions(limit=page_size)

        if isinstance(result, Failure):
            yield result
            return

        connection = result.unwrap()

        while True:
            for reaction in connection.data:
                yield Success(reaction)

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
                connection = GraphConnection[Reaction].model_validate(
                    response.json()
                )
            except ValidationError as e:
                yield Failure(DataValidationError.from_pydantic_error(e))
                return

    async def like(
        self,
    ) -> Result[GraphResponse, SDKError]:
        """Like the post as the authenticated user."""
        return await self._graph.post(
            f"/{self._post_id}/likes",
            GraphResponse,
        )

    async def unlike(
        self,
    ) -> Result[GraphResponse, SDKError]:
        """Remove the authenticated user's like from this post."""
        return await self._graph.delete(
            f"/{self._post_id}/likes",
            GraphResponse,
        )
