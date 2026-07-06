from __future__ import annotations
from datetime import datetime, UTC
from returns.result import Result, Success, Failure
from collections.abc import Collection
from urllib.parse import urlencode
import httpx

from pyfb_kit.common.errors import FacebookAPIError
from pyfb_kit.common.models import GraphVersion

from .models import GraphPermission, GraphAuthType, GraphAccessToken, GraphTokenInfo

class FacebookClient:
    def __init__(
        self,
        *,
        app_id: str,
        app_secret: str,
        redirect_url: str,
        graph_version: GraphVersion = GraphVersion.latest()
    ):
        self._app_id = app_id
        self._app_secret = app_secret
        self._redirect_url = redirect_url
        self._version = graph_version

        self._oauth_base_url = "https://www.facebook.com"
        self._graph_base_url = "https://graph.facebook.com"
        self._httpx_client = httpx.AsyncClient(
            base_url=f"{self._graph_base_url}/{self._version.value}"
        )

    def get_oauth_url(
        self,
        state: str,
        *,
        scope: Collection[GraphPermission] | None = None,
        auth_type: GraphAuthType | None = None
    ) -> str:
        """
        Construct the Facebook Login OAuth URL.

        Args:
            redirect_url: The OAuth callback URL registered for the application.
            state: An opaque value used to prevent CSRF attacks.
            scope (Optional): The permissions to request from the user.
            auth_type (Optional): Controls how Facebook handles the authorization flow.

        Returns:
            The OAuth authorization URL.
        """
        params: dict[str, str] = {
            "client_id": self._app_id,
            "redirect_uri": self._redirect_url,
            "state": state,
            "response_type": "code",
        }

        if scope:
            # We sort the permissions to keep the URL consistent
            params["scope"] = ",".join(
                permission.value
                for permission in sorted(scope, key=lambda p: p.value)
            )

        if auth_type is not None:
            params["auth_type"] = auth_type.value

        return f"{self._oauth_base_url}/{self._version.value}/dialog/oauth?{urlencode(params)}"

    async def exchange_short_lived_token(
        self,
        code: str,
    ) -> Result[GraphAccessToken, FacebookAPIError]:
        """
        Exchange an OAuth authorization code for a short-lived access token.

        Args:
            code: The authorization code returned by Facebook.

        Returns:
            The short-lived access token.
        """

        response = await self._httpx_client.get(
            "/oauth/access_token",
            params={
                "client_id": self._app_id,
                "client_secret": self._app_secret,
                "redirect_uri": self._redirect_url,
                "code": code,
            },
        )

        if response.is_error:
            return Failure(
                FacebookAPIError.from_response(response)
            )

        data = response.json()

        return Success(
            GraphAccessToken(access_token=data["access_token"])
        )

    async def exchange_long_lived_token(
        self,
        access_token: str,
    ) -> Result[GraphAccessToken, FacebookAPIError]:
        """
        Exchange a short-lived user access token for a long-lived user access token.

        Args:
            access_token: A valid short-lived user access token.

        Returns:
            The long-lived user access token.
        """

        response = await self._httpx_client.get(
            "/oauth/access_token",
            params={
                "grant_type": "fb_exchange_token",
                "client_id": self._app_id,
                "client_secret": self._app_secret,
                "fb_exchange_token": access_token,
            },
        )

        if response.is_error:
            return Failure(
                FacebookAPIError.from_response(response)
            )

        data = response.json()

        return Success(
            GraphAccessToken(access_token=data["access_token"])
        )

    async def exchange_code_for_long_lived_token(
        self,
        code: str
    ) -> Result[GraphAccessToken, FacebookAPIError]:
        """
        Exchange an authorization code for a long-lived user access token.
        """
        result = await self.exchange_short_lived_token(code)

        if isinstance(result, Success):
            return await self.exchange_long_lived_token(
                result.unwrap().access_token
            )
        else:
            return result

    async def debug_token(
        self,
        access_token: str,
    ) -> Result[GraphTokenInfo, FacebookAPIError]:
        """
        Inspect an access token.

        Args:
            access_token: The user or page access token to inspect.

        Returns:
            Information about the access token.
        """

        response = await self._httpx_client.get(
            "/debug_token",
            params={
                "input_token": access_token,
                "access_token": f"{self._app_id}|{self._app_secret}",
            },
        )

        if response.is_error:
            return Failure(
                FacebookAPIError.from_response(response)
            )
        data = response.json()["data"]

        def parse_timestamp(value: int | None) -> datetime | None:
            if not value:
                return None

            return datetime.fromtimestamp(value, UTC)

        scopes = tuple(
            GraphPermission(scope)
            for scope in data["scopes"]
        )
        return Success(GraphTokenInfo(
            app_id=data["app_id"],
            application=data["application"],
            user_id=data.get("user_id"),
            token_type=data["type"],
            is_valid=data["is_valid"],
            expires_at=parse_timestamp(data.get("expires_at")),
            issued_at=parse_timestamp(data.get("issued_at")),
            scopes=scopes,
        ))
