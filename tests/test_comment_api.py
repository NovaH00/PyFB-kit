import pytest
from returns.result import Success, Failure

from pyfb_kit.comment.api import CommentAPI

from .conftest import (
    SAMPLE_COMMENT,
    SAMPLE_REPLY,
    SAMPLE_REACTION,
    SAMPLE_RESPONSE,
    SAMPLE_USER,
    success,
    single_item_connection,
)


class TestCommentAPIGet:
    async def test_success(self, mock_graph):
        mock_graph.get.return_value = success(SAMPLE_COMMENT)
        api = CommentAPI(mock_graph, comment_id="3001_4001")
        result = await api.get()
        assert result == Success(SAMPLE_COMMENT)
        mock_graph.get.assert_awaited_once_with(
            "/3001_4001", type(SAMPLE_COMMENT),
            fields=["id", "message", "created_time", "from"],
        )


class TestCommentAPIUpdate:
    async def test_success(self, mock_graph):
        mock_graph.post.return_value = success(SAMPLE_COMMENT)
        api = CommentAPI(mock_graph, comment_id="3001_4001")
        result = await api.update(message="Updated comment")
        assert result == Success(SAMPLE_COMMENT)
        mock_graph.post.assert_awaited_once_with(
            "/3001_4001", type(SAMPLE_COMMENT),
            data={"message": "Updated comment"},
        )


class TestCommentAPIDelete:
    async def test_success(self, mock_graph):
        mock_graph.delete.return_value = success(SAMPLE_RESPONSE)
        api = CommentAPI(mock_graph, comment_id="3001_4001")
        result = await api.delete()
        assert result == Success(SAMPLE_RESPONSE)
        mock_graph.delete.assert_awaited_once_with(
            "/3001_4001", type(SAMPLE_RESPONSE),
        )


class TestCommentAPIGetReplies:
    async def test_success(self, mock_graph):
        mock_graph.get.return_value = single_item_connection(SAMPLE_REPLY)
        api = CommentAPI(mock_graph, comment_id="3001_4001")
        result = await api.get_replies(limit=5)
        assert isinstance(result, Success)
        assert result.unwrap().data[0] == SAMPLE_REPLY


class TestCommentAPIterReplies:
    async def test_yields_replies(self, mock_graph):
        mock_graph.get.return_value = single_item_connection(SAMPLE_REPLY)
        api = CommentAPI(mock_graph, comment_id="3001_4001")
        items = [r async for r in api.iter_replies(page_size=5)]
        assert len(items) == 1
        assert items[0] == Success(SAMPLE_REPLY)

    async def test_handles_failure(self, mock_graph, fb_api_error):
        mock_graph.get.return_value = Failure(fb_api_error)
        api = CommentAPI(mock_graph, comment_id="3001_4001")
        items = [r async for r in api.iter_replies()]
        assert len(items) == 1
        assert items[0] == Failure(fb_api_error)


class TestCommentAPICreateReply:
    async def test_success(self, mock_graph):
        mock_graph.post.return_value = success(SAMPLE_COMMENT)
        api = CommentAPI(mock_graph, comment_id="3001_4001")
        result = await api.create_reply(message="Great point!")
        assert result == Success(SAMPLE_COMMENT)
        mock_graph.post.assert_awaited_once_with(
            "/3001_4001/comments", type(SAMPLE_COMMENT),
            data={"message": "Great point!"},
        )


class TestCommentAPIGetLikes:
    async def test_success(self, mock_graph):
        mock_graph.get.return_value = single_item_connection(SAMPLE_USER)
        api = CommentAPI(mock_graph, comment_id="3001_4001")
        result = await api.get_likes(limit=5)
        assert isinstance(result, Success)
        assert result.unwrap().data[0] == SAMPLE_USER


class TestCommentAPILike:
    async def test_success(self, mock_graph):
        mock_graph.post.return_value = success(SAMPLE_RESPONSE)
        api = CommentAPI(mock_graph, comment_id="3001_4001")
        result = await api.like()
        assert result == Success(SAMPLE_RESPONSE)
        mock_graph.post.assert_awaited_once_with(
            "/3001_4001/likes", type(SAMPLE_RESPONSE),
        )


class TestCommentAPIUnlike:
    async def test_success(self, mock_graph):
        mock_graph.delete.return_value = success(SAMPLE_RESPONSE)
        api = CommentAPI(mock_graph, comment_id="3001_4001")
        result = await api.unlike()
        assert result == Success(SAMPLE_RESPONSE)
        mock_graph.delete.assert_awaited_once_with(
            "/3001_4001/likes", type(SAMPLE_RESPONSE),
        )


class TestCommentAPIGetReactions:
    async def test_success(self, mock_graph):
        mock_graph.get.return_value = single_item_connection(SAMPLE_REACTION)
        api = CommentAPI(mock_graph, comment_id="3001_4001")
        result = await api.get_reactions(limit=5)
        assert isinstance(result, Success)
        assert result.unwrap().data[0] == SAMPLE_REACTION


class TestCommentAPIterReactions:
    async def test_yields_reactions(self, mock_graph):
        mock_graph.get.return_value = single_item_connection(SAMPLE_REACTION)
        api = CommentAPI(mock_graph, comment_id="3001_4001")
        items = [r async for r in api.iter_reactions(page_size=5)]
        assert len(items) == 1
        assert items[0] == Success(SAMPLE_REACTION)

    async def test_handles_failure(self, mock_graph, fb_api_error):
        mock_graph.get.return_value = Failure(fb_api_error)
        api = CommentAPI(mock_graph, comment_id="3001_4001")
        items = [r async for r in api.iter_reactions()]
        assert len(items) == 1
        assert items[0] == Failure(fb_api_error)
