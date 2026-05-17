import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from backend.app.api.routes import (
    capabilities,
    curves,
    demo,
    exposure,
    health,
    hedging,
    info,
    market_data,
    positions,
    reports,
    risk,
    runs,
)

DEFAULT_ALLOWED_ORIGINS = (
    "http://localhost:3000",
    "http://127.0.0.1:3000",
)


def _allowed_origins_from_env() -> list[str]:
    configured = os.getenv("FLOWDECK_ALLOWED_ORIGINS")
    if not configured:
        return list(DEFAULT_ALLOWED_ORIGINS)
    return [origin.strip() for origin in configured.split(",") if origin.strip()]


app = FastAPI(
    title="FlowDeck API",
    version="0.1.0",
    description=(
        "Local API for FlowDeck commodity trading intelligence workflows, "
        "including oil futures validation, Brent/WTI curve analytics, "
        "position exposure, hedge simulation, stress P&L and Excel reporting."
    ),
    contact={"name": "FlowDeck Product Team"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins_from_env(),
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    _request: Request, exc: RequestValidationError
):
    return JSONResponse(
        status_code=400,
        content={
            "detail": {
                "error": "Invalid request.",
                "error_code": "REQUEST_VALIDATION_ERROR",
                "message": "Invalid request.",
                "details": {"errors": exc.errors()},
                "errors": exc.errors(),
            }
        },
    )


@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(
    _request: Request, exc: ValidationError
):
    return JSONResponse(
        status_code=400,
        content={
            "detail": {
                "error": "Validation failed.",
                "error_code": "VALIDATION_ERROR",
                "message": "Validation failed.",
                "details": {"errors": exc.errors()},
                "errors": exc.errors(),
            }
        },
    )


@app.exception_handler(Exception)
async def unexpected_exception_handler(_request: Request, _exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "detail": {
                "error": "Internal server error.",
                "error_code": "INTERNAL_ERROR",
                "message": "Internal server error.",
                "details": None,
            }
        },
    )


app.include_router(health.router)
app.include_router(capabilities.router)
app.include_router(info.router)
app.include_router(demo.router)
app.include_router(market_data.router)
app.include_router(curves.router)
app.include_router(positions.router)
app.include_router(exposure.router)
app.include_router(hedging.router)
app.include_router(risk.router)
app.include_router(reports.router)
app.include_router(runs.router)
