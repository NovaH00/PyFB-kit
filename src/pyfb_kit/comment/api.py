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
from pyfb_kit.common.models import GraphResponse
from pyfb_kit.common.models import Reaction
from pyfb_kit.user.models import User

from .models import Comment


class CommentAPI:
    """API for interacting with a single Facebook comment.

    Provides methods to read, update, delete, and interact with a comment
    and its sub-resources (replies, likes, reactions).
    """

    def __init__(
        self,
        graph: GraphClient,
        comment_id: str,
    ):
        self._graph = graph
        self._comment_id = comment_id

    async def get(self) -> Result[Comment, SDKError]:
        """Retrieve the comment's details."""
        return await self._graph.get(
            f"/{self._comment_id}",
            Comment,
            fields=["id", "message", "created_time", "from"],
        )

    async def update(
        self,
        *,
        message: str,
    ) -> Result[Comment, SDKError]:
        """Update the comment's message."""
        return await self._graph.post(
            f"/{self._comment_id}",
            Comment,
            data={"message": message},
        )

    async def delete(self) -> Result[GraphResponse, SDKError]:
        """Delete the comment."""
        return await self._graph.delete(
            f"/{self._comment_id}",
            GraphResponse,
        )

    async def get_replies(
        self,
        *,
        limit: int | None = None,
    ) -> Result[GraphConnection[Comment], SDKError]:
        """Retrieve paginated replies to this comment."""
        return await self._graph.get(
            f"/{self._comment_id}/comments",
            GraphConnection[Comment],
            params={"limit": limit} if limit is not None else None,
        )

    async def iter_replies(
        self,
        *,
        page_size: int | None = None,
    ) -> AsyncIterator[Result[Comment, SDKError]]:
        """Iterate over all replies to this comment as an async generator."""
        result = await self.get_replies(limit=page_size)

        if isinstance(result, Failure):
            yield result
            return

        connection = result.unwrap()

        while True:
            for reply in connection.data:
                yield Success(reply)

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

    async def create_reply(
        self,
        message: str,
    ) -> Result[Comment, SDKError]:
        """Create a reply to this comment."""
        return await self._graph.post(
            f"/{self._comment_id}/comments",
            Comment,
            data={"message": message},
        )

    async def get_likes(
        self,
        *,
        limit: int | None = None,
    ) -> Result[GraphConnection[User], SDKError]:
        """Retrieve paginated users who liked this comment."""
        return await self._graph.get(
            f"/{self._comment_id}/likes",
            GraphConnection[User],
            params={"limit": limit} if limit is not None else None,
        )

    async def like(self) -> Result[GraphResponse, SDKError]:
        """Like the comment as the authenticated user."""
        return await self._graph.post(
            f"/{self._comment_id}/likes",
            GraphResponse,
        )

    async def unlike(self) -> Result[GraphResponse, SDKError]:
        """Remove the authenticated user's like from this comment."""
        return await self._graph.delete(
            f"/{self._comment_id}/likes",
            GraphResponse,
        )

    async def get_reactions(
        self,
        *,
        limit: int | None = None,
    ) -> Result[GraphConnection[Reaction], SDKError]:
        """Retrieve paginated reactions on this comment."""
        return await self._graph.get(
            f"/{self._comment_id}/reactions",
            GraphConnection[Reaction],
            params={"limit": limit} if limit is not None else None,
        )

    async def iter_reactions(
        self,
        *,
        page_size: int | None = None,
    ) -> AsyncIterator[Result[Reaction, SDKError]]:
        """Iterate over all reactions on this comment as an async generator."""
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
