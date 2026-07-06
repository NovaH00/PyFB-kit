from dataclasses import dataclass
from typing import Any

import httpx
from pydantic import ValidationError

@dataclass(frozen=True, slots=True)
class FacebookAPIError:
    message: str
    type: str
    code: int
    subcode: int | None
    fbtrace_id: str | None
    response: httpx.Response

    @classmethod
    def from_response(
        cls,
        response: httpx.Response,
    ) -> "FacebookAPIError":
        error = response.json()["error"]

        return cls(
            message=error["message"],
            type=error["type"],
            code=error["code"],
            subcode=error.get("error_subcode"),
            fbtrace_id=error.get("fbtrace_id"),
            response=response,
        )

@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """
    Represents a single validation issue.
    """

    location: tuple[str | int, ...]
    message: str
    code: str
    input: Any | None = None


@dataclass(frozen=True, slots=True)
class DataValidationError:
    """
    One or more validation issues encountered while validating data.
    """

    message: str
    issues: tuple[ValidationIssue, ...]

    @classmethod
    def from_pydantic_error(
        cls,
        error: ValidationError,
    ) -> DataValidationError:
        return cls(
            message="Data validation failed.",
            issues=tuple(
                ValidationIssue(
                    location=tuple(issue["loc"]),
                    message=issue["msg"],
                    code=issue["type"],
                    input=issue.get("input"),
                )
                for issue in error.errors()
            ),
        )

type SDKError = FacebookAPIError | DataValidationError
