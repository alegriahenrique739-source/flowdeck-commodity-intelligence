import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
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
from backend.app.security.boundary import DemoAdmission, PublicDemoBoundary
from backend.app.security.config import DeploymentPolicy
from backend.app.security.public_runs import PublicDemoRegistry
from backend.app.services.workflows.run_registry import PROJECT_ROOT

DEFAULT_ALLOWED_ORIGINS = (
    "http://localhost:3000",
    "http://127.0.0.1:3000",
)


def _allowed_origins_from_env() -> list[str]:
    configured = os.getenv("FLOWDECK_ALLOWED_ORIGINS")
    if not configured:
        return list(DEFAULT_ALLOWED_ORIGINS)
    return [origin.strip() for origin in configured.split(",") if origin.strip()]


async def http_exception_handler(_request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


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
                "details": {"errors": jsonable_encoder(exc.errors())},
                "errors": jsonable_encoder(exc.errors()),
            }
        },
    )


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
                "details": {"errors": jsonable_encoder(exc.errors())},
                "errors": jsonable_encoder(exc.errors()),
            }
        },
    )


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


def create_app(*, project_root=PROJECT_ROOT) -> FastAPI:
    origins = _allowed_origins_from_env()
    policy = DeploymentPolicy.from_env(origins)
    application = FastAPI(
        title="FlowDeck API",
        version="0.1.0",
        description=(
            "Synthetic public demo API. No uploads or private portfolios. "
            "Generation is bounded per process; all demo runs are shared."
            if policy.is_public_demo
            else "Local API for FlowDeck commodity trading intelligence workflows, "
            "including oil futures validation, Brent/WTI curve analytics, "
            "position exposure, hedge simulation, stress P&L and Excel reporting."
        ),
        contact={"name": "FlowDeck Product Team"},
    )
    application.state.deployment_policy = policy
    application.state.run_registry = (
        PublicDemoRegistry(project_root, policy.public_max_runs)
        if policy.is_public_demo
        else None
    )
    if policy.is_public_demo:
        application.add_middleware(PublicDemoBoundary, admission=DemoAdmission())
    # CORS surrounds boundary responses so allowed frontends see clean 403/429 errors.
    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )
    for exception, handler in (
        (HTTPException, http_exception_handler),
        (RequestValidationError, request_validation_exception_handler),
        (ValidationError, pydantic_validation_exception_handler),
        (Exception, unexpected_exception_handler),
    ):
        application.add_exception_handler(exception, handler)

    selected = [health, capabilities, info, demo, runs]
    if not policy.is_public_demo:
        selected.extend(
            [
                market_data,
                curves,
                positions,
                exposure,
                hedging,
                risk,
                reports,
            ]
        )
    for route in selected:
        application.include_router(route.router)

    if policy.is_public_demo:
        original_openapi = application.openapi

        def public_openapi():
            schema = original_openapi()
            schema["x-flowdeck-deployment"] = {
                "mode": "public_demo",
                "uploads": "disabled",
                "storage": "synthetic-only separate directory",
                "max_stored_runs": policy.public_max_runs,
                "max_active_generations": 1,
                "generation_start_interval_seconds": 5,
                "limits_scope": "single process",
            }
            for path in schema["paths"].values():
                for operation in path.values():
                    if isinstance(operation, dict) and "responses" in operation:
                        for status, description in (
                            ("400", "Invalid query or request body not allowed"),
                            ("403", "Outside public demo scope"),
                            ("408", "Request did not complete"),
                            ("414", "Query too long"),
                        ):
                            operation["responses"].setdefault(
                                status,
                                {
                                    "description": description,
                                    "content": {
                                        "application/json": {
                                            "schema": {
                                                "$ref": "#/components/schemas/ErrorEnvelope"
                                            }
                                        }
                                    },
                                },
                            )
            for status, description in (
                (
                    "429",
                    "Generation busy or global start interval; Retry-After supplied",
                ),
                ("503", "Public demo storage full; operator review required"),
            ):
                schema["paths"]["/demo/run"]["post"]["responses"][status] = {
                    "description": description,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ErrorEnvelope"}
                        }
                    },
                }
            return schema

        application.openapi = public_openapi
    return application


app = create_app()
