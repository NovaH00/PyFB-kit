# PyFB-kit

Một thư viện Python bao ngoài Facebook Graph API cung cấp các trừu tượng thuận tiện để quản lý và kiểm duyệt các trang và bình luận trên Facebook.

## Cài đặt

Cài đặt gói bằng pip:

```bash
pip install pyfb-kit
```

Hoặc sử dụng uv (khuyến nghị):

```bash
uv add pyfb-kit
```

## Điều kiện tiên quyết

Trước khi sử dụng thư viện này, bạn cần có một mã truy cập người dùng dài hạn với các quyền thích hợp:

1. Tạo một ứng dụng Facebook Developer tại [developers.facebook.com/apps](https://developers.facebook.com/apps/)
2. Thêm các quyền sau vào ứng dụng của bạn:
   - `pages_manage_engagement`
   - `pages_read_engagement`
   - `pages_read_user_content`
   - `pages_show_list`
3. Tạo mã truy cập người dùng ngắn hạn thông qua Trình khám phá API với các quyền trên
4. Đổi mã này lấy mã dài hạn (có hiệu lực đến 60 ngày) bằng yêu cầu sau:

```python
import requests

params = {
    "grant_type": "fb_exchange_token",
    "client_id": "<MÃ_ỨNG_DỤNG_CỦA_BẠN>",
    "fb_exchange_token": "<MÃ_NGẮN_HẠN>",
    "client_secret": "<MẬT_KHẨU_ỨNG_DỤNG_CỦA_BẠN>",
}

response = requests.get("https://graph.facebook.com/v24.0/oauth/access_token", params=params)
long_lived_token = response.json()["access_token"]
```

## Sử dụng

### Thiết lập cơ bản

```python
from pyfb_kit import Client, Account, Post, Comment

# Khởi tạo client với mã truy cập người dùng dài hạn
client = Client(user_access_token="mã_truy_cập_dài_hạn_của_bạn")
```

### Quản lý tài khoản

Lấy tất cả các trang Facebook liên kết với tài khoản của bạn:

```python
# Lấy tất cả các tài khoản/trang có thể truy cập
accounts = client.get_accounts()

# In thông tin tài khoản
for account in accounts:
    print(f"Tên trang: {account.name}, ID: {account.id}")
```

### Làm việc với bài viết

Lấy bài viết từ một trang cụ thể:

```python
# Lấy bài viết từ một tài khoản cụ thể
first_account = accounts[0]
posts = client.get_posts(first_account)

# In thông tin bài viết
for post in posts:
    print(f"ID bài viết: {post.id}, Nội dung: {post.message[:50]}...")
```

### Quản lý bình luận

Tương tác với các bình luận trên bài viết:

```python
# Lấy bình luận từ một bài viết cụ thể
first_post = posts[0]
comments = client.get_comments(first_account, first_post)

# In thông tin bình luận
for comment in comments:
    print(f"Bình luận bởi {comment.from_info.name}: {comment.message[:50]}...")

# Đăng một bình luận mới trên bài viết
client.put_comment(first_account, first_post, "Đây là một bình luận mới!")

# Trả lời một bình luận hiện có
first_comment = comments[0]
client.reply_comment(first_account, first_comment, "Cảm ơn vì bình luận của bạn!")
```

### Các thao tác bình luận nâng cao

Lấy trả lời cho một bình luận cụ thể:

```python
# Lấy tất cả các trả lời cho một bình luận cụ thể
replies = client.get_comment_replies(first_account, first_comment)

for reply in replies:
    print(f"Trả lời bởi {reply.from_info.name}: {reply.message[:50]}...")
```