import json
from urllib.error import URLError

import pytest

from scripts.check_public_demo_gate import PUBLIC_OPERATIONS, Document, audit, origin

FRONTEND = "https://flowdeck.example.com"
BACKEND = "https://api.example.com"


def documents(mode="public_demo", extra_path=False, cors=FRONTEND):
    paths = {path: {method: {}} for method, path in PUBLIC_OPERATIONS}
    if extra_path:
        paths["/positions/futures/analyze"] = {"post": {}}
    payloads = {
        "/health": {"status": "ok", "service": "FlowDeck API"},
        "/api/info": {"environment": mode},
        "/openapi.json": {"paths": paths},
    }
    calls = []

    def fetch(url, frontend):
        calls.append(url)
        assert frontend == FRONTEND
        return Document(
            200,
            {"access-control-allow-origin": cors},
            json.dumps(payloads[url.removeprefix(BACKEND)]).encode(),
        )

    return fetch, calls


def test_public_contract_is_ready_for_review_not_automatic_release():
    fetch, calls = documents()
    checks = audit(BACKEND, FRONTEND, fetch)
    assert len(checks) == 4
    assert all(check.passed for check in checks)
    assert calls == [
        BACKEND + path for path in ["/health", "/api/info", "/openapi.json"]
    ]


@pytest.mark.parametrize(
    "options",
    [
        {"mode": "local"},
        {"mode": "unexpected"},
        {"extra_path": True},
        {"cors": "*"},
        {"cors": ""},
    ],
)
def test_release_gate_blocks_unsafe_or_unrecognized_deployments(options):
    fetch, _ = documents(**options)
    assert not all(check.passed for check in audit(BACKEND, FRONTEND, fetch))


@pytest.mark.parametrize(
    "response",
    [
        Document(302, {}, b""),
        Document(503, {}, b""),
        Document(200, {}, b"<html/>"),
        Document(200, {}, b"[]"),
        Document(200, {}, b"{}"),
    ],
)
def test_release_gate_does_not_treat_failed_or_malformed_responses_as_ready(response):
    assert not all(
        check.passed for check in audit(BACKEND, FRONTEND, lambda *_: response)
    )


def test_release_gate_handles_network_failure_without_stack_trace_or_success():
    def offline(*_):
        raise URLError("unavailable")

    checks = audit(BACKEND, FRONTEND, offline)
    assert len(checks) == 3
    assert all(not check.passed for check in checks)


@pytest.mark.parametrize(
    "value",
    [
        "http://api.example.com",
        "https://127.0.0.1",
        "https://localhost",
        "https://user:secret@api.example.com",
        "https://api.example.com/path",
        "https://api.example.com?token=secret",
        "https://api.example.com\n",
    ],
)
def test_release_gate_rejects_credential_and_non_public_origin_inputs(value):
    with pytest.raises(ValueError, match="HTTPS domain"):
        origin(value)
