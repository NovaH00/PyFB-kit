from datetime import datetime

from pydantic import BaseModel, Field

from pyfb_kit.user.models import User

class Comment(BaseModel):
    id: str
    message: str | None = None
    created_time: datetime | None = None
    author: User | None = Field(None, alias="from")
