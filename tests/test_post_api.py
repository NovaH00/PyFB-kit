import pytest
from returns.result import Success, Failure

from pyfb_kit.post.api import PostAPI

from .conftest import (
    SAMPLE_POST,
    SAMPLE_COMMENT,
    SAMPLE_REACTION,
    SAMPLE_RESPONSE,
    success,
    single_item_connection,
)


class TestPostAPIGet:
    async def test_success(self, mock_graph):
        mock_graph.get.return_value = success(SAMPLE_POST)
        api = PostAPI(mock_graph, post_id="2001_3001")
        result = await api.get()
        assert result == Success(SAMPLE_POST)
        mock_graph.get.assert_awaited_once_with(
            "/2001_3001", type(SAMPLE_POST),
            fields=["id", "message", "created_time", "story"],
        )


class TestPostAPIUpdate:
    async def test_success(self, mock_graph):
        mock_graph.post.return_value = success(SAMPLE_POST)
        api = PostAPI(mock_graph, post_id="2001_3001")
        result = await api.update(message="Updated")
        assert result == Success(SAMPLE_POST)
        mock_graph.post.assert_awaited_once_with(
            "/2001_3001", type(SAMPLE_POST), data={"message": "Updated"},
        )


class TestPostAPIDelete:
    async def test_success(self, mock_graph):
        mock_graph.delete.return_value = success(SAMPLE_RESPONSE)
        api = PostAPI(mock_graph, post_id="2001_3001")
        result = await api.delete()
        assert result == Success(SAMPLE_RESPONSE)
        mock_graph.delete.assert_awaited_once_with(
            "/2001_3001", type(SAMPLE_RESPONSE),
        )


class TestPostAPIGetComments:
    async def test_success(self, mock_graph):
        mock_graph.get.return_value = single_item_connection(SAMPLE_COMMENT)
        api = PostAPI(mock_graph, post_id="2001_3001")
        result = await api.get_comments(limit=5)
        assert isinstance(result, Success)
        assert result.unwrap().data[0] == SAMPLE_COMMENT


class TestPostAPIterComments:
    async def test_yields_comments(self, mock_graph):
        mock_graph.get.return_value = single_item_connection(SAMPLE_COMMENT)
        api = PostAPI(mock_graph, post_id="2001_3001")
        items = [r async for r in api.iter_comments(page_size=5)]
        assert len(items) == 1
        assert items[0] == Success(SAMPLE_COMMENT)

    async def test_handles_failure(self, mock_graph, fb_api_error):
        mock_graph.get.return_value = Failure(fb_api_error)
        api = PostAPI(mock_graph, post_id="2001_3001")
        items = [r async for r in api.iter_comments()]
        assert len(items) == 1
        assert items[0] == Failure(fb_api_error)


class TestPostAPICreateComment:
    async def test_success(self, mock_graph):
        mock_graph.post.return_value = success(SAMPLE_COMMENT)
        api = PostAPI(mock_graph, post_id="2001_3001")
        result = await api.create_comment(message="Nice post!")
        assert result == Success(SAMPLE_COMMENT)
        mock_graph.post.assert_awaited_once_with(
            "/2001_3001/comments", type(SAMPLE_COMMENT),
            data={"message": "Nice post!"},
        )


class TestPostAPIGetReactions:
    async def test_success(self, mock_graph):
        mock_graph.get.return_value = single_item_connection(SAMPLE_REACTION)
        api = PostAPI(mock_graph, post_id="2001_3001")
        result = await api.get_reactions(limit=5)
        assert isinstance(result, Success)
        assert result.unwrap().data[0] == SAMPLE_REACTION


class TestPostAPIterReactions:
    async def test_yields_reactions(self, mock_graph):
        mock_graph.get.return_value = single_item_connection(SAMPLE_REACTION)
        api = PostAPI(mock_graph, post_id="2001_3001")
        items = [r async for r in api.iter_reactions(page_size=5)]
        assert len(items) == 1
        assert items[0] == Success(SAMPLE_REACTION)

    async def test_handles_failure(self, mock_graph, fb_api_error):
        mock_graph.get.return_value = Failure(fb_api_error)
        api = PostAPI(mock_graph, post_id="2001_3001")
        items = [r async for r in api.iter_reactions()]
        assert len(items) == 1
        assert items[0] == Failure(fb_api_error)


class TestPostAPILike:
    async def test_success(self, mock_graph):
        mock_graph.post.return_value = success(SAMPLE_RESPONSE)
        api = PostAPI(mock_graph, post_id="2001_3001")
        result = await api.like()
        assert result == Success(SAMPLE_RESPONSE)
        mock_graph.post.assert_awaited_once_with(
            "/2001_3001/likes", type(SAMPLE_RESPONSE),
        )


class TestPostAPIUnlike:
    async def test_success(self, mock_graph):
        mock_graph.delete.return_value = success(SAMPLE_RESPONSE)
        api = PostAPI(mock_graph, post_id="2001_3001")
        result = await api.unlike()
        assert result == Success(SAMPLE_RESPONSE)
        mock_graph.delete.assert_awaited_once_with(
            "/2001_3001/likes", type(SAMPLE_RESPONSE),
        )
