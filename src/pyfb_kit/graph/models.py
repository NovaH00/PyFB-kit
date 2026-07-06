from typing import Any, BinaryIO, TYPE_CHECKING
from collections.abc import Mapping
from datetime import datetime

from pydantic import BaseModel

from pyfb_kit.common.models import GraphVersion

if TYPE_CHECKING:
    from .client import GraphClient

type QueryParams = Mapping[str, Any]
type FormData = Mapping[str, Any]
type RequestFiles = Mapping[str, BinaryIO | bytes]

class GraphCursor(BaseModel):
    before: str | None = None
    after: str | None = None

class GraphPaging(BaseModel):
    cursors: GraphCursor | None = None
    next: str | None = None
    previous: str | None = None

class GraphConnection[T](BaseModel):
    data: list[T]
    paging: GraphPaging | None = None


class GraphPage(BaseModel):
    id: str
    name: str
    access_token: str | None = None

    def graph(
        self,
        *,
        version: GraphVersion = GraphVersion.latest(),
    ) -> GraphClient:
        from .client import GraphClient
        if self.access_token is None:
            raise ValueError("Page has no access token.")

        return GraphClient(
            access_token=self.access_token,
            graph_version=version,
        )



class GraphComment(BaseModel):
    id: str
    message: str | None = None
    created_time: datetime | None = None
    from_: dict[str, str] | None = None
