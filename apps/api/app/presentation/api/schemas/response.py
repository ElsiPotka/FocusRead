from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BaseAPIResponse(BaseModel):
    success: bool = Field(True, description="Request execution status")
    message: str | None = Field(None, description="Optional context message")


class MessageResponse(BaseAPIResponse):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"success": True, "message": "Book deleted"},
        }
    )


class APIResponse[T](BaseAPIResponse):
    data: T

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "success": True,
                "data": {"id": "01961f0e-...", "title": "The Great Gatsby"},
            },
        },
    )


class ListResponse[T](BaseAPIResponse):
    data: list[T]
    count: int = Field(..., description="Total items in list")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "success": True,
                "count": 2,
                "data": [
                    {"id": "01961f0e-...", "title": "Book A"},
                    {"id": "01961f0f-...", "title": "Book B"},
                ],
            },
        },
    )


class ErrorResponse(BaseAPIResponse):
    success: bool = Field(False, description="Always False for errors")
    error_code: str | None = Field(None, description="Machine-readable error code")
    detail: Any | None = Field(None, description="Validation errors or debug trace")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": False,
                "message": "Resource not found",
                "error_code": "NOT_FOUND",
                "detail": None,
            },
        }
    )
