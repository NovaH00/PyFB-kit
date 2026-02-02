[Tiếng Việt](README-vi.md)
# PyFB-kit

A Python wrapper for the Facebook Graph API that provides convenient abstractions for managing and moderating Facebook pages and comments.

## Installation

Install the package using pip:

```bash
pip install pyfb-kit
```

Or using uv (recommended):

```bash
uv add pyfb-kit
```

## Prerequisites

Before using this library, you need to obtain a long-lived user access token with the appropriate permissions:

1. Create a Facebook developer application at [developers.facebook.com/apps](https://developers.facebook.com/apps/)
2. Add the following permissions to your application:
   - `pages_manage_engagement`
   - `pages_read_engagement`
   - `pages_read_user_content`
   - `pages_show_list`
3. Generate a short-lived user access token via the Graph API Explorer with the above permissions
4. Exchange it for a long-lived token (valid for up to 60 days) using the following request:

```python
import requests

params = {
    "grant_type": "fb_exchange_token",
    "client_id": "<YOUR_APP_ID>",
    "fb_exchange_token": "<SHORT_LIVED_TOKEN>",
    "client_secret": "<YOUR_APP_SECRET>",
}

response = requests.get("https://graph.facebook.com/v24.0/oauth/access_token", params=params)
long_lived_token = response.json()["access_token"]
```

## Usage

### Basic Setup

```python
from pyfb_kit import Client, Account, Post, Comment

# Initialize the client with your user access token
client = Client(user_access_token="your_long_lived_token_here")
```

### Managing Accounts

Retrieve all Facebook pages associated with your account:

```python
# Get all accessible accounts/pages
accounts = client.get_accounts()

# Print account information
for account in accounts:
    print(f"Page Name: {account.name}, ID: {account.id}")
```

### Working with Posts

Fetch posts from a specific page:

```python
# Get posts from a specific account
first_account = accounts[0]
posts = client.get_posts(first_account)

# Print post information
for post in posts:
    print(f"Post ID: {post.id}, Message: {post.message[:50]}...")
```

### Comment Management

Interact with comments on posts:

```python
# Get comments from a specific post
first_post = posts[0]
comments = client.get_comments(first_account, first_post)

# Print comment information
for comment in comments:
    print(f"Comment by {comment.from_info.name}: {comment.message[:50]}...")

# Post a new comment on a post
client.put_comment(first_account, first_post, "This is a new comment!")

# Reply to an existing comment
first_comment = comments[0]
client.reply_comment(first_account, first_comment, "Thanks for your comment!")
```

### Advanced Comment Operations

Retrieve replies to a specific comment:

```python
# Get all replies to a specific comment
replies = client.get_comment_replies(first_account, first_comment)

for reply in replies:
    print(f"Reply by {reply.from_info.name}: {reply.message[:50]}...")
```
