# pyfb-kit

A modern, async Python SDK for the Facebook Graph API.

## Installation

```bash
uv add pyfb-kit
```

## Authentication

Before making API calls, you need an access token. Use the built-in OAuth client:

```python
from pyfb_kit import FacebookClient, GraphPermission
from returns.result import Success, Failure

client = FacebookClient(
    app_id="your_app_id",
    app_secret="your_app_secret",
    redirect_url="http://localhost:8080/callback",
)

url = client.get_oauth_url(
    "my_state",
    scope=[GraphPermission.PublicProfile, GraphPermission.PagesShowList],
)

# 1. Direct the user to `url` in their browser.
# 2. Facebook will redirect them to your redirect_url with a `?code=...` parameter.
# 3. Capture that `code` value and pass it here:

token_result = await client.exchange_code_for_long_lived_token(code)
match token_result:
    case Success(token):
        access_token = token.access_token
    case Failure(e):
        print(f"Auth failed: {e}")
```

## Quick Start

```python
import asyncio
from returns.result import Success, Failure
from pyfb_kit import GraphClient
from pyfb_kit.user import UserAPI

async def main():
    graph = GraphClient("your_access_token")

    user_api = UserAPI(graph)
    match await user_api.get():
        case Success(user):
            print(user)
        case Failure(e):
            print(f"Error: {e}")

asyncio.run(main())
```

## Usage

### User API — get info and pages

```python
from returns.result import Success, Failure
from pyfb_kit import GraphClient
from pyfb_kit.user import UserAPI

graph = GraphClient("user_token")
user_api = UserAPI(graph)

match await user_api.get():
    case Success(user):
        print(user)
    case Failure(e):
        print(f"Error: {e}")

match await user_api.get_pages(limit=10):
    case Success(connection):
        print(connection.data)
    case Failure(e):
        print(f"Error: {e}")

async for result in user_api.iter_pages():
    match result:
        case Success(page):
            print(page)
        case Failure(e):
            print(f"Error: {e}")
```

### Page API — manage a page and its posts

```python
from returns.result import Success, Failure
from pyfb_kit import GraphClient
from pyfb_kit.page import PageAPI

graph = GraphClient("page_token")
page_api = PageAPI(graph, page_id="your_page_id")

match await page_api.get():
    case Success(page):
        print(page)
    case Failure(e):
        print(f"Error: {e}")

match await page_api.create_post(message="Hello!"):
    case Success(post):
        print(post)
    case Failure(e):
        print(f"Error: {e}")

async for result in page_api.iter_posts(page_size=5):
    match result:
        case Success(post):
            print(post)
        case Failure(e):
            print(f"Error: {e}")
```

### Post API — read, update, delete, interact

```python
from returns.result import Success, Failure
from pyfb_kit import GraphClient
from pyfb_kit.post import PostAPI

graph = GraphClient("page_token")
post_api = PostAPI(graph, post_id="post_id_123")

match await post_api.get():
    case Success(post):
        print(post)
    case Failure(e):
        print(f"Error: {e}")

match await post_api.get_comments(limit=10):
    case Success(connection):
        print(connection.data)
    case Failure(e):
        print(f"Error: {e}")

match await post_api.like():
    case Success(response):
        print(f"Liked: {response.success}")
    case Failure(e):
        print(f"Error: {e}")
```

### Comment API — replies, likes, reactions

```python
from returns.result import Success, Failure
from pyfb_kit import GraphClient
from pyfb_kit.comment import CommentAPI

graph = GraphClient("page_token")
comment_api = CommentAPI(graph, comment_id="comment_id_456")

match await comment_api.get():
    case Success(comment):
        print(comment)
    case Failure(e):
        print(f"Error: {e}")

match await comment_api.get_replies():
    case Success(connection):
        print(connection.data)
    case Failure(e):
        print(f"Error: {e}")

match await comment_api.create_reply(message="Thanks!"):
    case Success(reply):
        print(reply)
    case Failure(e):
        print(f"Error: {e}")
```

## Error Handling

This library uses `returns` result types instead of exceptions. Every API method returns `Result[T, SDKError]` — it's either `Success(value)` or `Failure(error)`. You must explicitly handle both cases:

```python
from returns.result import Result, Success, Failure
from pyfb_kit import SDKError

match await post_api.get():
    case Success(post):
        print(post)
    case Failure(e):
        print(f"Error: {e}")
```

Or use functional methods like `.map()`, `.alt()`, `.unwrap()`:

```python
post = await post_api.get()
post.map(lambda p: print(p)).alt(lambda e: print(e))
```

Iterators yield `Result[T, SDKError]` for each item — check each one:

```python
async for result in page_api.iter_posts():
    match result:
        case Success(post):
            ...
        case Failure(e):
            ...
```

## API Reference

Full documentation is in [DOCS.md](./DOCS.md).

## Testing

```bash
uv run pytest
```
