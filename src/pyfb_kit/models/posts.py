from typing import Any
from datetime import datetime
from pydantic import BaseModel, Field, model_validator


class Image(BaseModel):
    src: str = Field(..., description="Direct URL to the image hosted by Facebook")
    width: int = Field(..., description="Width of the image in pixels")
    height: int = Field(..., description="Height of the image in pixels")


class Attachments(BaseModel):
    images: list[Image] | None = Field(None, description="List of images attached to the post, if any")
    # TODO: Add other attachment types here (videos, links, etc.)

class Post(BaseModel):
    """
    Normalized DTO for a Facebook Page post.

    IMPORTANT:
    This model expects the raw input to include attachment data from the
    Facebook Graph API. When querying posts, you MUST request the following
    fields for validation and normalization to work correctly:

        ...get_connections(
            account_id,
            "posts",
            fields="id,message,created_time,attachments{media,type,subattachments}"
        )

    If `attachments` or `attachments.media.image` are missing from the
    response, `attachments.images` will be set to None.
    """
    id: str = Field(..., description="Unique identifier of the Facebook post")
    created_time: datetime = Field(..., description="Timestamp when the post was created (ISO-8601)")
    message: str | None = Field(None, description="Text content of the post")
    attachments: Attachments | None = Field(None, description="Normalized attachments associated with the post")

    @model_validator(mode="before")
    @classmethod
    def extract_facebook_payload(cls, raw: dict[str, Any]):
        images: list[Image] = []

        for att in raw.get("attachments", {}).get("data", []):
            if att.get("type") != "photo":
                continue

            image = att.get("media", {}).get("image")
            if not image:
                continue

            images.append(
                Image(
                    src=image["src"],
                    width=image["width"],
                    height=image["height"],
                )
            )

        return {
            "id": raw["id"],
            "created_time": raw["created_time"],
            "message": raw.get("message"),
            "attachments": {"images": images} if images else None,
        }

