from pydantic import BaseModel


class Page(BaseModel):
    id: str
    name: str
    access_token: str | None = None
    category: str | None = None
