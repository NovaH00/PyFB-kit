from typing import Any
from datetime import datetime
from pydantic import BaseModel, Field, model_validator


class From(BaseModel):
    id: str = Field(..., description="ID of the user who made the comment")
    name: str = Field(..., description="Name of the user who made the comment")


class Comment(BaseModel):
    """
    Normalized DTO for a Facebook comment.

    IMPORTANT:
    This model expects the raw input to include comment data from the
    Facebook Graph API. When querying comments, you MUST request the following
    fields for validation and normalization to work correctly:

        ...get_connections(
            post_id,
            "comments",
            fields="id,from,message,created_time,like_count,parent"
        )

    If required fields are missing from the response, validation will fail.
    """
    id: str = Field(..., description="Unique identifier of the Facebook comment")
    message: str = Field(..., description="Text content of the comment")
    created_time: datetime = Field(..., description="Timestamp when the comment was created (ISO-8601)")
    from_info: From = Field(..., alias="from", description="Information about the user who made the comment")
    like_count: int = Field(default=0, description="Number of likes on the comment")
    parent_id: str | None = Field(None, description="ID of the parent comment if this is a reply, otherwise None")

    @model_validator(mode="before")
    @classmethod
    def extract_facebook_payload(cls, raw: dict[str, Any]):
        return {
            "id": raw["id"],
            "message": raw["message"],
            "created_time": raw["created_time"],
            "from": {
                "id": raw["from"]["id"],
                "name": raw["from"]["name"]
            },
            "like_count": raw.get("like_count", 0),
            "parent_id": raw.get("parent", {}).get("id") if raw.get("parent") else None
        }
