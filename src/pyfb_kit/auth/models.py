from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from datetime import datetime

class GraphPermission(StrEnum):
    """Facebook Graph API OAuth permissions."""

    PublicProfile = "public_profile"
    """Basic profile information. This permission is granted by default."""

    Email = "email"
    """The user's primary email address."""

    UserFriends = "user_friends"
    """The user's friends who have also authorized your app."""

    PagesShowList = "pages_show_list"
    """List Facebook Pages the user can access or manage."""

    PagesReadEngagement = "pages_read_engagement"
    """Read Page metadata, posts, reactions, and other engagement data."""

    PagesReadUserContent = "pages_read_user_content"
    """Read user-generated content on a Page, such as visitor posts."""

    PagesManagePosts = "pages_manage_posts"
    """Create, edit, and delete posts on a Page."""

    PagesManageEngagement = "pages_manage_engagement"
    """Moderate Page comments and reactions."""

    PagesManageMetadata = "pages_manage_metadata"
    """Manage Page metadata, including webhook subscriptions."""

    PagesManageCta = "pages_manage_cta"
    """Manage a Page's call-to-action button."""

    PagesMessaging = "pages_messaging"
    """Send and receive Messenger messages on behalf of a Page."""

    InstagramBasic = "instagram_basic"
    """Read basic information for an Instagram Business or Creator account."""

    InstagramManageMessages = "instagram_manage_messages"
    """Read and reply to Instagram Direct Messages."""

    InstagramManageComments = "instagram_manage_comments"
    """Read, moderate, and reply to Instagram comments."""

    InstagramContentPublish = "instagram_content_publish"
    """Publish media to an Instagram Business account."""

    InstagramManageInsights = "instagram_manage_insights"
    """Read Instagram account insights and analytics."""

    AdsRead = "ads_read"
    """Read advertising accounts, campaigns, and performance data."""

    AdsManagement = "ads_management"
    """Create and manage advertising campaigns."""

    BusinessManagement = "business_management"
    """Manage Meta Business assets such as Pages, ad accounts, and users."""

    GroupsAccessMemberInfo = "groups_access_member_info"
    """Access information about members of Facebook Groups."""

    PublishVideo = "publish_video"
    """Publish videos or create live broadcasts."""


class GraphAuthType(StrEnum):
    """Facebook Login authorization flow modifiers."""

    Rerequest = "rerequest"
    """Ask again for permissions that the user previously declined."""

    Reauthorize = "reauthorize"
    """Force the user through the authorization flow again."""

    Reauthenticate = "reauthenticate"
    """Require the user to re-enter their Facebook credentials before continuing."""


@dataclass(slots=True, frozen=True)
class GraphAccessToken:
    access_token: str

@dataclass(slots=True, frozen=True)
class GraphTokenInfo:
    app_id: str
    application: str
    user_id: str | None
    token_type: str
    is_valid: bool
    expires_at: datetime | None
    issued_at: datetime | None
    scopes: tuple[GraphPermission, ...]
