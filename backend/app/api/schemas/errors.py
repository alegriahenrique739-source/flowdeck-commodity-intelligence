from __future__ import annotations

from typing import Any

from pydantic import Field

from backend.app.api.schemas.common import ApiModel


class ErrorResponse(ApiModel):
    error_code: str = Field(..., examples=["VALIDATION_ERROR"])
    message: str = Field(..., examples=["Validation failed."])
    details: Any | None = Field(default=None)


class ErrorEnvelope(ApiModel):
    detail: ErrorResponse


class ValidationErrorDetail(ApiModel):
    valid: bool = Field(default=False, examples=[False])
    row_count: int = Field(default=0, examples=[0])
    errors: list[Any] = Field(default_factory=list)
    error_code: str = Field(default="VALIDATION_ERROR")
    message: str = Field(default="Validation failed.")
    details: Any | None = None


class ValidationErrorEnvelope(ApiModel):
    detail: ValidationErrorDetail


ERROR_RESPONSES = {
    400: {
        "model": ErrorEnvelope,
        "description": "Request validation or input validation failed.",
        "content": {
            "application/json": {
                "example": {
                    "detail": {
                        "error_code": "VALIDATION_ERROR",
                        "message": "Validation failed.",
                        "details": {"errors": ["price must be positive"]},
                    }
                }
            }
        },
    },
    500: {
        "model": ErrorEnvelope,
        "description": "Unexpected internal service error.",
        "content": {
            "application/json": {
                "example": {
                    "detail": {
                        "error_code": "INTERNAL_ERROR",
                        "message": "Internal server error.",
                        "details": None,
                    }
                }
            }
        },
    },
}

