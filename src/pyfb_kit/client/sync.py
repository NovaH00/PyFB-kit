from typing import Any, cast
from collections.abc import Iterator

import facebook
from facebook import GraphAPI

from ..models import (
    Account,
    Post,
    Comment
)

from ..types.graph_api import (
    Response,
    Data,
)

class Client:
    """
    Synchronous client for interacting with the Facebook Graph API.

    Provides methods to manage Facebook pages, posts, and comments.
    """

    def __init__(self, user_access_token: str):
        """
        Initialize the client with a user access token.

        Args:
            user_access_token: A valid Facebook user access token with appropriate permissions
        """
        self._user_access_token: str = user_access_token

    def _get_data(
        self,
        graph: facebook.GraphAPI,
        id: str,
        connection_name: str,
        **kwargs: Any
    ) -> Data:
        """
        Internal method to retrieve paginated data from the Facebook Graph API.

        This method handles pagination automatically by following the cursors in the response
        and concatenating all pages to produce a single data response.

        Args:
            graph: An initialized GraphAPI instance
            id: The ID of the object to query (e.g., user ID, page ID, post ID)
            connection_name: The connection name to query (e.g., "posts", "comments", "accounts")
            **kwargs: Additional parameters to pass to the Graph API call

        Returns:
            A list of raw Facebook Graph API objects extracted from the 'data' field
        """
        all_data: Data = []
        
        while True:
            # Request the current page
            res = graph.get_connections( # pyright: ignore
                id,
                connection_name,
                **kwargs
            ) 
            res = cast(Response, res)

            current_data: Data = res.get("data") # pyright: ignore
            
            if current_data:
                all_data.extend(current_data)

            # Check for the next page cursor ('after')
            # Facebook Structure: {'paging': {'cursors': {'after': '...'}}}
            try:
                paging = res.get("paging", None)
                if not paging: break
                    
                cursors = paging.get("cursors")
                if not cursors: break
                    
                after = cursors.get("after")
                if not after: break
                
                # Update kwargs with the 'after' cursor for the next iteration
                kwargs["after"] = after
                
            except (AttributeError, TypeError):
                # If the response structure is unexpected, stop pagination
                break
                
        return all_data 

    def get_accounts(self) -> list[Account]:
        """
        Retrieve all Facebook accounts/pages associated with the authenticated user.

        This method fetches all Facebook pages that the user has access to, along with
        their access tokens and other metadata.

        Returns:
            A list of Account objects representing the Facebook pages accessible to the user
        """
        accounts: Data = self._get_data(
            graph=GraphAPI(self._user_access_token),
            id="me",
            connection_name="accounts"
        )

        return [
            Account.model_validate(acc)
            for acc in accounts
        ]
    
    def get_posts(self, account: Account) -> list[Post]:
        """
        Retrieve all posts from a specific Facebook page/account.

        This method fetches all posts from the given Facebook page, including their
        content, creation time, and attachments.

        Args:
            account: Account object containing the access token and ID for the Facebook page

        Returns:
            A list of Post objects representing the posts on the Facebook page
        """
        posts: Data = self._get_data(
            graph=GraphAPI(account.access_token),
            id=account.id,
            connection_name="posts",
            fields="id,message,created_time,attachments{media,type,subattachments}",
        )

        return [
            Post.model_validate(p)
            for p in posts
        ]
    
    def get_comments(self, account: Account, post: Post) -> list[Comment]:
        """
        Retrieve all comments for a given post using the account's access token.

        Args:
            account: Account object containing the access token for the Facebook page
            post: Post object containing the post information

        Returns:
            A list of Comment objects representing the comments on the post
        """
        comments: Data = self._get_data(
            graph=GraphAPI(account.access_token),
            id=post.id,
            connection_name="comments",
            fields="id,from,message,created_time,like_count,parent"
        )

        return [
            Comment.model_validate(comment)
            for comment in comments
        ]

    def put_comment(self, account: Account, post: Post, message: str) -> None:
        """
        Post a direct comment on a post using the account's access token.

        Args:
            account: Account object containing the access token for the Facebook page
            post: Post object containing the post information
            message: The message content for the comment

        Returns:
            None
        """
        graph = GraphAPI(account.access_token)

        # Use the Facebook Graph API to post a comment on the specific post
        _ = graph.put_object( # pyright: ignore
            parent_object=post.id,
            connection_name="comments",
            message=message
        )

    def reply_comment(self, account: Account, comment: Comment, reply_message: str) -> None:
        """
        Reply to a specific comment using the account's access token.
        This creates a reply to the given comment.

        Args:
            account: Account object containing the access token for the Facebook page
            comment: Comment object representing the comment to reply to
            reply_message: The message content for the reply

        Returns:
            None
        """
        graph = GraphAPI(account.access_token)

        # Use the Facebook Graph API to reply to the specific comment
        _ = graph.put_object( # pyright: ignore
            parent_object=comment.id,
            connection_name="comments",
            message=reply_message
        )

    def get_comment_replies(self, account: Account, comment: Comment) -> list[Comment]:
        """
        Retrieve all replies to a specific comment using the account's access token.

        Args:
            account: Account object containing the access token for the Facebook page
            comment: Comment object representing the parent comment whose replies are to be retrieved

        Returns:
            A list of Comment objects representing the replies to the given comment
        """
        replies: Data = self._get_data(
            graph=GraphAPI(account.access_token),
            id=comment.id,
            connection_name="comments",
            fields="id,from,message,created_time,like_count,parent"
        )

        return [
            Comment.model_validate(reply)
            for reply in replies
        ]

    # TODO: Add hide/unhide comments methods
