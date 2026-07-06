import pytest
from returns.result import Success, Failure

from pyfb_kit.user.api import UserAPI

from .conftest import SAMPLE_USER, SAMPLE_PAGE, success, single_item_connection


class TestUserAPIGet:
    async def test_success(self, mock_graph):
        mock_graph.get.return_value = success(SAMPLE_USER)
        api = UserAPI(mock_graph)
        result = await api.get()
        assert result == Success(SAMPLE_USER)
        mock_graph.get.assert_awaited_once_with(
            "/me", type(SAMPLE_USER), fields=["id", "name"]
        )

    async def test_failure(self, mock_graph, fb_api_error):
        mock_graph.get.return_value = Failure(fb_api_error)
        api = UserAPI(mock_graph)
        result = await api.get()
        assert isinstance(result, Failure)
        assert result.failure() is fb_api_error


class TestUserAPIGetPages:
    async def test_success(self, mock_graph):
        mock_graph.get.return_value = single_item_connection(SAMPLE_PAGE)
        api = UserAPI(mock_graph)
        result = await api.get_pages(limit=5)
        assert isinstance(result, Success)
        connection = result.unwrap()
        assert len(connection.data) == 1
        assert connection.data[0] == SAMPLE_PAGE

    async def test_no_limit(self, mock_graph):
        mock_graph.get.return_value = single_item_connection(SAMPLE_PAGE)
        api = UserAPI(mock_graph)
        result = await api.get_pages()
        assert isinstance(result, Success)
        mock_graph.get.assert_awaited_once()
        args, _ = mock_graph.get.call_args
        assert args[0] == "/me/accounts"


class TestUserAPIterPages:
    async def test_yields_pages(self, mock_graph):
        mock_graph.get.return_value = single_item_connection(SAMPLE_PAGE)
        api = UserAPI(mock_graph)
        items = [r async for r in api.iter_pages(page_size=5)]
        assert len(items) == 1
        assert items[0] == Success(SAMPLE_PAGE)

    async def test_handles_failure(self, mock_graph, fb_api_error):
        mock_graph.get.return_value = Failure(fb_api_error)
        api = UserAPI(mock_graph)
        items = [r async for r in api.iter_pages()]
        assert len(items) == 1
        assert items[0] == Failure(fb_api_error)
