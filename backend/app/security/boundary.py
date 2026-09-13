import asyncio
import math
import re
import threading
import time
from urllib.parse import parse_qs

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from backend.app.services.demo.demo_schemas import DemoStressScenario

RUN_PATH = re.compile(r"/runs/FD-RUN-[0-9]{8}-[0-9]{6}-[A-F0-9]{6}(?:/report)?")
READ_PATHS = frozenset(
    {
        "/health",
        "/capabilities",
        "/api/info",
        "/demo/sample-files",
        "/runs",
        "/docs",
        "/docs/oauth2-redirect",
        "/redoc",
        "/openapi.json",
    }
)
RATIO = re.compile(r"(?:0(?:\.[0-9]{1,8})?|1(?:\.0{1,8})?)")


def public_route_allowed(method: str, path: str) -> bool:
    return (method == "POST" and path == "/demo/run") or (
        method == "GET" and (path in READ_PATHS or RUN_PATH.fullmatch(path) is not None)
    )


class DemoAdmission:
    """One active generator and a global start interval per process, not per IP."""

    def __init__(self, interval: float = 5.0, clock=None):
        self.interval = interval
        self.clock = clock or time.monotonic
        self.lock = threading.Lock()
        self.active = False
        self.last_started: float | None = None

    def enter(self) -> tuple[str, int] | None:
        with self.lock:
            now = self.clock()
            if self.active:
                return "PUBLIC_DEMO_BUSY", 5
            if (
                self.last_started is not None
                and now - self.last_started < self.interval
            ):
                return "PUBLIC_DEMO_RATE_LIMIT", max(
                    1, math.ceil(self.interval - (now - self.last_started))
                )
            self.active = True
            self.last_started = now
            return None

    def leave(self):
        with self.lock:
            self.active = False


class PublicDemoBoundary:
    """Reject non-demo requests before FastAPI resolves dependencies or reads forms."""

    def __init__(self, app: ASGIApp, admission: DemoAdmission):
        self.app = app
        self.admission = admission

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "websocket":
            await send({"type": "websocket.close", "code": 1008})
            return
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def secure_send(message):
            if message["type"] == "http.response.start":
                headers = [
                    (k, v)
                    for k, v in message.get("headers", [])
                    if k.lower()
                    not in {
                        b"cache-control",
                        b"x-content-type-options",
                        b"referrer-policy",
                        b"x-robots-tag",
                    }
                ]
                message = {
                    **message,
                    "headers": headers
                    + [
                        (b"cache-control", b"no-store"),
                        (b"x-content-type-options", b"nosniff"),
                        (b"referrer-policy", b"no-referrer"),
                        (b"x-robots-tag", b"noindex, nofollow"),
                    ],
                }
            await send(message)

        async def reject(
            status: int, code: str, message: str, retry: int | None = None
        ):
            response = JSONResponse(
                status_code=status,
                content={
                    "detail": {
                        "error_code": code,
                        "message": message,
                        "error": message,
                        "details": None,
                    }
                },
                headers={"Retry-After": str(retry)} if retry else None,
            )
            await response(scope, receive, secure_send)

        path = scope.get("path", "")
        if not public_route_allowed(scope["method"], path):
            await reject(
                403,
                "PUBLIC_DEMO_ONLY",
                "This API is restricted to synthetic demo workflows. Upload and local analytics routes are unavailable.",
            )
            return
        query = scope.get("query_string", b"")
        if len(query) > 2048:
            await reject(414, "PUBLIC_QUERY_TOO_LARGE", "The demo query is too long.")
            return
        if path == "/demo/run":
            try:
                values = parse_qs(
                    query.decode("ascii"),
                    keep_blank_values=True,
                    max_num_fields=2,
                    encoding="ascii",
                    errors="strict",
                )
                valid = (
                    not values.keys() - {"target_hedge_ratio", "stress_scenario"}
                    and all(len(v) == 1 for v in values.values())
                    and RATIO.fullmatch(values.get("target_hedge_ratio", ["0.80"])[0])
                    is not None
                    and values.get("stress_scenario", ["PARALLEL_DOWN_5"])[0]
                    in {s.value for s in DemoStressScenario}
                )
            except (ValueError, UnicodeError):
                valid = False
            if not valid:
                await reject(
                    400,
                    "PUBLIC_DEMO_QUERY_INVALID",
                    "Use a hedge ratio from 0 to 1 with at most 8 decimal places and a supported demo scenario; repeated or extra parameters are not allowed.",
                )
                return

        lengths = [
            v for k, v in scope.get("headers", []) if k.lower() == b"content-length"
        ]
        if lengths and lengths != [b"0"]:
            await reject(
                400,
                "PUBLIC_BODY_NOT_ALLOWED",
                "Public demo requests do not accept files or request bodies. Use query parameters.",
            )
            return
        # No permitted endpoint needs a body. Check the stream too, not just its header.
        try:
            async with asyncio.timeout(5):
                while True:
                    message = await receive()
                    if message["type"] == "http.disconnect":
                        return
                    if message.get("body"):
                        await reject(
                            400,
                            "PUBLIC_BODY_NOT_ALLOWED",
                            "Public demo requests do not accept files or request bodies. Use query parameters.",
                        )
                        return
                    if not message.get("more_body", False):
                        break
        except TimeoutError:
            await reject(
                408,
                "PUBLIC_REQUEST_TIMEOUT",
                "The demo request did not complete in time.",
            )
            return

        replayed = False

        async def replay():
            nonlocal replayed
            if not replayed:
                replayed = True
                return {"type": "http.request", "body": b"", "more_body": False}
            return await receive()

        generation = scope["method"] == "POST"
        if generation:
            limit = self.admission.enter()
            if limit:
                code, seconds = limit
                await reject(
                    429,
                    code,
                    "Demo generation is temporarily limited. Retry shortly.",
                    seconds,
                )
                return
        try:
            await self.app(scope, replay, secure_send)
        finally:
            if generation:
                self.admission.leave()
