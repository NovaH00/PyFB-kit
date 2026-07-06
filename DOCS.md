# Reference

## GraphClient

The core HTTP client for the Facebook Graph API. Every domain API receives a `GraphClient` instance.

```python
from pyfb_kit import GraphClient
from pyfb_kit.common import GraphVersion

graph = GraphClient(
    access_token="your_token",
    graph_version=GraphVersion.latest(),
    on_usage=None,  # optional callback for rate-limit tracking
)
```

### Methods

Each method returns `Result[T, SDKError]` where `T` is the provided response model.

```python
await graph.get(path, response_model, *, fields=None, params=None)
await graph.post(path, response_model, *, fields=None, params=None, data=None, files=None)
await graph.delete(path, response_model, *, fields=None, params=None)
await graph.put(path, response_model, *, fields=None, params=None, data=None, files=None)
await graph.patch(path, response_model, *, fields=None, params=None, data=None, files=None)
await graph.request(method, path, *, fields=None, params=None, data=None, files=None)
```

- `path` — relative path like `"/me"` or `"/{post_id}/comments"`
- `response_model` — a Pydantic model class (or `GraphConnection[T]` for paginated endpoints)
- `fields` — optional `Collection[str]` for field selection
- `params` — optional query parameters (`Mapping[str, Any]`)
- `data` — optional form data (`Mapping[str, Any]`)
- `files` — optional file uploads (`Mapping[str, BinaryIO | bytes]`)

### Usage Tracking

Pass an `on_usage` callback to monitor API rate limits:

```python
from pyfb_kit import APIUsage

def on_usage(usage: APIUsage):
    if usage.app and usage.app.call_count > 80:
        log.warning("Approaching rate limit")
    if usage.page:
        print(f"Page usage: {usage.page}")

graph = GraphClient(token, on_usage=on_usage)
```

`APIUsage` contains optional `app`, `page`, and `ad_account` fields, each of type `UsageLimit | None`:

```python
from pyfb_kit import UsageLimit

class UsageLimit(BaseModel):
    call_count: int
    total_cputime: float
    total_time: float
```

The callback fires on every `GraphClient.request()` call, including pagination requests.

---

## UserAPI

```python
from pyfb_kit.user import UserAPI

user_api = UserAPI(graph)
```

| Method | Returns | Description |
|---|---|---|
| `get()` | `Result[User, SDKError]` | Authenticated user's profile |
| `get_pages(*, limit)` | `Result[GraphConnection[Page], SDKError]` | Pages owned by the user |
| `iter_pages(*, page_size)` | `AsyncIterator[Result[Page, SDKError]]` | Async generator over all pages |

### User model

```python
from pyfb_kit.user import User

class User(BaseModel):
    id: str
    name: str
```

---

## PageAPI

```python
from pyfb_kit.page import PageAPI

page_api = PageAPI(graph, page_id="me")
```

| Method | Returns | Description |
|---|---|---|
| `get()` | `Result[Page, SDKError]` | Page details (id, name, category, access_token) |
| `create_post(*, message)` | `Result[Post, SDKError]` | Create a new post on the page's feed |
| `get_posts(*, limit)` | `Result[GraphConnection[Post], SDKError]` | Page's own posts |
| `iter_posts(*, page_size)` | `AsyncIterator[Result[Post, SDKError]]` | Async generator over all posts |

### Page model

```python
from pyfb_kit.page import Page

class Page(BaseModel):
    id: str
    name: str
    access_token: str | None = None
    category: str | None = None
```

---

## PostAPI

```python
from pyfb_kit.post import PostAPI

post_api = PostAPI(graph, post_id)
```

| Method | Returns | Description |
|---|---|---|
| `get()` | `Result[Post, SDKError]` | Post details |
| `update(*, message)` | `Result[Post, SDKError]` | Update the post's message |
| `delete()` | `Result[GraphResponse, SDKError]` | Delete the post |
| `get_comments(*, limit)` | `Result[GraphConnection[Comment], SDKError]` | Comments on the post |
| `iter_comments(*, page_size)` | `AsyncIterator[Result[Comment, SDKError]]` | Async generator over all comments |
| `create_comment(message)` | `Result[Comment, SDKError]` | Create a comment |
| `get_reactions(*, limit)` | `Result[GraphConnection[Reaction], SDKError]` | Reactions on the post |
| `iter_reactions(*, page_size)` | `AsyncIterator[Result[Reaction, SDKError]]` | Async generator over all reactions |
| `like()` | `Result[GraphResponse, SDKError]` | Like the post |
| `unlike()` | `Result[GraphResponse, SDKError]` | Unlike the post |

### Post model

```python
from pyfb_kit.post import Post

class Post(BaseModel):
    id: str
    created_time: datetime
    message: str | None = None
    story: str | None = None
```

---

## CommentAPI

```python
from pyfb_kit.comment import CommentAPI

comment_api = CommentAPI(graph, comment_id)
```

| Method | Returns | Description |
|---|---|---|
| `get()` | `Result[Comment, SDKError]` | Comment details |
| `update(*, message)` | `Result[Comment, SDKError]` | Update the comment's message |
| `delete()` | `Result[GraphResponse, SDKError]` | Delete the comment |
| `get_replies(*, limit)` | `Result[GraphConnection[Comment], SDKError]` | Replies to the comment |
| `iter_replies(*, page_size)` | `AsyncIterator[Result[Comment, SDKError]]` | Async generator over all replies |
| `create_reply(message)` | `Result[Comment, SDKError]` | Reply to the comment |
| `get_likes(*, limit)` | `Result[GraphConnection[User], SDKError]` | Users who liked the comment |
| `like()` | `Result[GraphResponse, SDKError]` | Like the comment |
| `unlike()` | `Result[GraphResponse, SDKError]` | Unlike the comment |
| `get_reactions(*, limit)` | `Result[GraphConnection[Reaction], SDKError]` | Reactions on the comment |
| `iter_reactions(*, page_size)` | `AsyncIterator[Result[Reaction, SDKError]]` | Async generator over all reactions |

### Comment model

```python
from pyfb_kit.comment import Comment
from pydantic import Field

class Comment(BaseModel):
    id: str
    message: str | None = None
    created_time: datetime | None = None
    author: User | None = Field(None, alias="from")
```

The `author` field maps from the JSON key `"from"` via pydantic alias.

---

## Models

### GraphConnection

A generic paginated response wrapper used by all list endpoints.

```python
from pyfb_kit import GraphConnection, GraphPaging

class GraphConnection[T](BaseModel):
    data: list[T]
    paging: GraphPaging | None = None
```

### GraphPaging / GraphCursor

```python
from pyfb_kit import GraphCursor, GraphPaging

class GraphCursor(BaseModel):
    before: str | None = None
    after: str | None = None

class GraphPaging(BaseModel):
    cursors: GraphCursor | None = None
    next: str | None = None
    previous: str | None = None
```

### GraphResponse

Returned by simple mutation endpoints (like, unlike, delete).

```python
from pyfb_kit import GraphResponse

class GraphResponse(BaseModel):
    success: bool
```

### Reaction / ReactionType

```python
from pyfb_kit import Reaction, ReactionType

class ReactionType(StrEnum):
    LIKE = "LIKE"
    LOVE = "LOVE"
    WOW = "WOW"
    HAHA = "HAHA"
    SAD = "SAD"
    ANGRY = "ANGRY"

class Reaction(BaseModel):
    id: str
    name: str | None = None
    type: ReactionType | None = None
```

### GraphVersion

```python
from pyfb_kit import GraphVersion

class GraphVersion(StrEnum):
    V25_0 = "v25.0"
    V24_0 = "v24.0"

    @classmethod
    def latest(cls) -> GraphVersion: ...
```

---

## Error Handling

All API methods return `Result[T, SDKError]` where `SDKError = FacebookAPIError | DataValidationError`.

Always unwrap or match on the result:

```python
from returns.result import Result, Success, Failure
from pyfb_kit import SDKError, FacebookAPIError, DataValidationError

match await post_api.get():
    case Success(post):
        print(post)
    case Failure(FacebookAPIError() as e):
        print(f"Facebook error {e.code}: {e.message}")
    case Failure(DataValidationError() as e):
        print(f"Validation error: {e.message}")
```

Or use `.map()` / `.alt()` for functional chaining.

---

## Pagination

List endpoints return `GraphConnection[T]`, closing the page. For unbounded iteration, use the `iter_*` methods:

```python
# Manual pagination
page = await post_api.get_comments(limit=10)
for comment in page.unwrap().data:
    print(comment)
# Follow next_url from page.unwrap().paging.next

# Async generator (automatic pagination)
async for comment in post_api.iter_comments(page_size=10):
    match comment:
        case Success(c):
            print(c)
        case Failure(e):
            print(f"Error: {e}")
```

Pagination internally follows `paging.next` URLs via `httpx`. The `on_usage` callback fires for each page request.

---

## Auth Module

```python
from pyfb_kit import FacebookClient, GraphPermission, GraphAccessToken
```

| Method | Returns | Description |
|---|---|---|
| `get_oauth_url(state, scope)` | `str` | Build a Facebook login URL |
| `exchange_code_for_long_lived_token(code)` | `Result[GraphAccessToken, SDKError]` | Exchange code for a long-lived token |

```python
class GraphAccessToken(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
```

### Permissions

```python
class GraphPermission(StrEnum):
    PublicProfile = "public_profile"
    PagesManageEngagement = "pages_manage_engagement"
    PagesReadEngagement = "pages_read_engagement"
    PagesShowList = "pages_show_list"
    # ...
```
