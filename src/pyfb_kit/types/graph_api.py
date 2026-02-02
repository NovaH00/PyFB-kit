from typing import Annotated, Any

type Response = Annotated[
    dict[str, Any],
    "Raw Facebook Graph API response object returned by get_connections()."
]

type Data = Annotated[
    list[dict[str, Any]],
    "List of raw Facebook Graph API objects extracted from the 'data' field."
]

