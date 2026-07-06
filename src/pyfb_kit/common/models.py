from enum import StrEnum

from pydantic import BaseModel


class GraphVersion(StrEnum):
    V25_0 = "v25.0"
    V24_0 = "v24.0"

    @classmethod
    def latest(cls) -> GraphVersion:
        return cls.V25_0


class GraphResponse(BaseModel):
    success: bool


class ReactionType(StrEnum):
    LIKE = "LIKE"
    LOVE = "LOVE"
    WOW = "WOW"
    HAHA = "HAHA"
    SAD = "SAD"
    ANGRY = "ANGRY"


class Reaction(BaseModel):
    id: str
    name: str | None = None
    type: ReactionType | None = None


class UsageLimit(BaseModel):
    call_count: int
    total_cputime: float
    total_time: float


class APIUsage(BaseModel):
    app: UsageLimit | None = None
    page: UsageLimit | None = None
    ad_account: UsageLimit | None = None
