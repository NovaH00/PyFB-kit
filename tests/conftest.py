from unittest.mock import AsyncMock
from datetime import datetime

import pytest
from returns.result import Success, Failure

from pyfb_kit.graph import GraphClient
from pyfb_kit.user.models import User
from pyfb_kit.page.models import Page
from pyfb_kit.post.models import Post
from pyfb_kit.comment.models import Comment
from pyfb_kit.common.models import (
    GraphResponse,
    Reaction,
    ReactionType,
)
from pyfb_kit.graph.models import (
    GraphConnection,
    GraphPaging,
    GraphCursor,
)
from pyfb_kit.common.errors import FacebookAPIError


SAMPLE_USER = User(id="1001", name="Test User")
SAMPLE_PAGE = Page(
    id="2001",
    name="Test Page",
    access_token="page_token_123",
    category="Test Category",
)
SAMPLE_POST = Post(
    id="2001_3001",
    created_time=datetime(2026, 3, 10, 8, 52, 40),
    message="Test post message",
    story=None,
)
SAMPLE_COMMENT = Comment(
    id="3001_4001",
    message="Test comment",
    created_time=datetime(2026, 3, 10, 8, 52, 51),
    author=SAMPLE_USER,
)
SAMPLE_REPLY = Comment(
    id="4001_5001",
    message="Test reply",
    created_time=datetime(2026, 3, 19, 10, 59, 13),
    author=SAMPLE_USER,
)
SAMPLE_REACTION = Reaction(
    id="6001",
    name="Test User",
    type=ReactionType.LIKE,
)
SAMPLE_RESPONSE = GraphResponse(success=True)


def success(result):
    return Success(result)


def empty_connection():
    return Success(GraphConnection(data=[], paging=None))


def single_item_connection(item):
    paging = GraphPaging(
        cursors=GraphCursor(before="before", after="after"),
        next=None,
        previous=None,
    )
    return Success(GraphConnection(data=[item], paging=paging))


def multi_page_first_connection(item):
    paging = GraphPaging(
        cursors=GraphCursor(before="before", after="after"),
        next="https://graph.facebook.com/v25.0/next?after=abc",
        previous=None,
    )
    return Success(GraphConnection(data=[item], paging=paging))


@pytest.fixture
def mock_graph():
    graph = AsyncMock(spec=GraphClient)
    graph.get = AsyncMock()
    graph.post = AsyncMock()
    graph.delete = AsyncMock()
    graph.put = AsyncMock()
    graph.patch = AsyncMock()
    return graph


@pytest.fixture
def fb_api_error():
    return FacebookAPIError(
        message="API error",
        type="OAuthException",
        code=100,
        subcode=None,
        fbtrace_id="abc123",
        response=AsyncMock(),
    )
