"""Read-only public API release gate. No uploads, generation, deletes or credentials."""

import argparse
import json
from dataclasses import asdict, dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

MAX_RESPONSE_BYTES = 512 * 1024
PUBLIC_OPERATIONS = {
    ("get", "/health"),
    ("get", "/capabilities"),
    ("get", "/api/info"),
    ("get", "/demo/sample-files"),
    ("post", "/demo/run"),
    ("get", "/runs"),
    ("get", "/runs/{run_id}"),
    ("get", "/runs/{run_id}/report"),
}
HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options", "trace"}


@dataclass(frozen=True)
class Document:
    status: int
    headers: dict[str, str]
    body: bytes


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    message: str


class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def origin(value: str) -> str:
    """Operator-supplied HTTPS domain, never a URL carrying credentials or a path."""
    try:
        parsed = urlsplit(value)
        valid = (
            parsed.scheme == "https"
            and parsed.hostname
            and "." in parsed.hostname
            and not parsed.username
            and not parsed.password
            and not parsed.query
            and not parsed.fragment
            and parsed.path in {"", "/"}
            and parsed.port in {None, 443}
            and not parsed.hostname.replace(".", "").isdigit()
            and not parsed.hostname.endswith((".local", ".internal", ".localhost"))
            and not any(ord(char) <= 32 or ord(char) == 127 for char in value)
            and not any(char in value for char in "\\@*?#")
        )
        if valid:
            return f"https://{parsed.hostname}"
    except ValueError:
        pass
    raise ValueError(
        "Use an exact HTTPS domain origin without credentials, path or query."
    )


def fetch_document(url: str, frontend_origin: str) -> Document:
    request = Request(
        url, headers={"Origin": frontend_origin, "Accept": "application/json"}
    )
    try:
        with build_opener(NoRedirects).open(request, timeout=25) as response:
            body = response.read(MAX_RESPONSE_BYTES + 1)
            if len(body) > MAX_RESPONSE_BYTES:
                raise ValueError("Response exceeds the read-only audit size limit.")
            return Document(
                response.status,
                {key.lower(): value for key, value in response.headers.items()},
                body,
            )
    except HTTPError as error:
        error.close()
        return Document(error.code, {}, b"")


def audit(backend_url: str, frontend_origin: str, fetch=fetch_document) -> list[Check]:
    backend = origin(backend_url)
    frontend = origin(frontend_origin)
    checks = []
    documents = {}
    for path in ["/health", "/api/info", "/openapi.json"]:
        try:
            document = fetch(backend + path, frontend)
            if document.status != 200:
                checks.append(
                    Check(
                        path, False, f"Expected HTTP 200; received {document.status}."
                    )
                )
                continue
            payload = json.loads(document.body)
            if not isinstance(payload, dict):
                raise TypeError("Expected JSON object")
            documents[path] = (payload, document)
        except (OSError, URLError, ValueError, TypeError):
            checks.append(
                Check(
                    path,
                    False,
                    "Unavailable or invalid response. Verify the host and retry; do not infer readiness.",
                )
            )

    if "/health" in documents:
        payload, _ = documents["/health"]
        ok = payload.get("status") == "ok" and payload.get("service") == "FlowDeck API"
        checks.append(
            Check(
                "health",
                ok,
                "FlowDeck health response verified."
                if ok
                else "Unexpected health contract.",
            )
        )
    if "/api/info" in documents:
        payload, document = documents["/api/info"]
        public = payload.get("environment") == "public_demo"
        checks.append(
            Check(
                "deployment_mode",
                public,
                "API declares public_demo."
                if public
                else "API does not declare public_demo. Do not promote a local-mode API.",
            )
        )
        cors = document.headers.get("access-control-allow-origin") == frontend
        checks.append(
            Check(
                "cors",
                cors,
                "Exact frontend origin allowed."
                if cors
                else "Expected exact frontend CORS origin, not wildcard or missing origin.",
            )
        )
    if "/openapi.json" in documents:
        payload, _ = documents["/openapi.json"]
        paths = payload.get("paths")
        valid = isinstance(paths, dict) and all(
            isinstance(item, dict) for item in paths.values()
        )
        operations = (
            {
                (method, path)
                for path, item in paths.items()
                for method in item
                if method in HTTP_METHODS
            }
            if valid
            else set()
        )
        matches = valid and operations == PUBLIC_OPERATIONS
        checks.append(
            Check(
                "public_contract",
                matches,
                "OpenAPI matches the synthetic public route contract."
                if matches
                else "OpenAPI is missing expected routes or exposes operations outside the public allowlist. Review the deployed build.",
            )
        )
    return checks


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend-url", required=True)
    parser.add_argument("--frontend-origin", required=True)
    args = parser.parse_args(argv)
    try:
        checks = audit(args.backend_url, args.frontend_origin)
    except ValueError as error:
        parser.error(str(error))
    passed = bool(checks) and all(check.passed for check in checks)
    print(
        json.dumps(
            {
                "status": "READY_FOR_MANUAL_REVIEW" if passed else "BLOCKED",
                "checks": [asdict(check) for check in checks],
                "limitations": "GET-only contract check, not proof of upload denial, security certification, indexing or full demo availability. Complete the manual deployment checklist.",
            },
            indent=2,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
