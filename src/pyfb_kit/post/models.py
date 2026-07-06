from datetime import datetime

from pydantic import BaseModel

class Post(BaseModel):
    id: str
    created_time: datetime
    message: str | None = None
    story: str | None = None
