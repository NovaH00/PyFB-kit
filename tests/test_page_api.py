import pytest
from returns.result import Success, Failure

from pyfb_kit.page.api import PageAPI

from .conftest import SAMPLE_PAGE, SAMPLE_POST, success, single_item_connection


class TestPageAPIGet:
    async def test_success(self, mock_graph):
        mock_graph.get.return_value = success(SAMPLE_PAGE)
        api = PageAPI(mock_graph, page_id="2001")
        result = await api.get()
        assert result == Success(SAMPLE_PAGE)
        mock_graph.get.assert_awaited_once_with(
            "/2001", type(SAMPLE_PAGE),
            fields=["id", "name", "category", "access_token"],
        )

    async def test_success_with_default_page_id(self, mock_graph):
        mock_graph.get.return_value = success(SAMPLE_PAGE)
        api = PageAPI(mock_graph)
        result = await api.get()
        assert result == Success(SAMPLE_PAGE)
        mock_graph.get.assert_awaited_once_with(
            "/me", type(SAMPLE_PAGE),
            fields=["id", "name", "category", "access_token"],
        )


class TestPageAPICreatePost:
    async def test_success(self, mock_graph):
        mock_graph.post.return_value = success(SAMPLE_POST)
        api = PageAPI(mock_graph, page_id="2001")
        result = await api.create_post(message="New post")
        assert result == Success(SAMPLE_POST)
        mock_graph.post.assert_awaited_once_with(
            "/2001/feed", type(SAMPLE_POST), data={"message": "New post"},
        )


class TestPageAPIGetPosts:
    async def test_success(self, mock_graph):
        mock_graph.get.return_value = single_item_connection(SAMPLE_POST)
        api = PageAPI(mock_graph, page_id="2001")
        result = await api.get_posts(limit=10)
        assert isinstance(result, Success)
        connection = result.unwrap()
        assert connection.data[0] == SAMPLE_POST


class TestPageAPIterPosts:
    async def test_yields_posts(self, mock_graph):
        mock_graph.get.return_value = single_item_connection(SAMPLE_POST)
        api = PageAPI(mock_graph, page_id="2001")
        items = [r async for r in api.iter_posts(page_size=10)]
        assert len(items) == 1
        assert items[0] == Success(SAMPLE_POST)

    async def test_handles_failure(self, mock_graph, fb_api_error):
        mock_graph.get.return_value = Failure(fb_api_error)
        api = PageAPI(mock_graph, page_id="2001")
        items = [r async for r in api.iter_posts()]
        assert len(items) == 1
        assert items[0] == Failure(fb_api_error)
