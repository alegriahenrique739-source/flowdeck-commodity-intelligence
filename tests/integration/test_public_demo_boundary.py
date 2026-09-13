import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.main import create_app
from backend.app.security.boundary import DemoAdmission, PublicDemoBoundary
from backend.app.security.public_runs import PublicDemoRegistry, PublicDemoStorageFull
from backend.app.services.workflows import (
    LocalRunRegistry,
    RunMetadata,
    RunOutputFiles,
    RunStatus,
    RunType,
)

ORIGIN = "https://flowdeck-demo.example"
RUN = "FD-RUN-20260912-120000-ABC123"


@pytest.fixture
def public_app(monkeypatch, tmp_path):
    monkeypatch.setenv("FLOWDECK_DEPLOYMENT_MODE", "public_demo")
    monkeypatch.setenv("FLOWDECK_ALLOWED_ORIGINS", ORIGIN)
    monkeypatch.setenv("FLOWDECK_ENABLE_LOCAL_IMPORTS", "false")
    monkeypatch.setenv("FLOWDECK_PUBLIC_MAX_RUNS", "100")
    return create_app(project_root=tmp_path)


@pytest.fixture
def client(public_app):
    with TestClient(public_app, raise_server_exceptions=False) as http:
        yield http


def metadata(run_id=RUN, **updates):
    return RunMetadata(
        run_id=run_id,
        run_type=RunType.DEMO_WORKFLOW,
        status=RunStatus.SUCCESS,
        created_at=datetime(2026, 9, 12, tzinfo=UTC),
        **updates,
    )


@pytest.mark.parametrize(
    "path",
    [
        "/market-data/validate",
        "/curves/build",
        "/positions/futures/analyze",
        "/positions/physical/analyze",
        "/exposure/net",
        "/hedging/simulate",
        "/risk/stress",
        "/reports/excel",
        "/desk/analyze",
        "/desk/report",
        "/intake/inspect",
        "/intake/prepare",
        "/intake/report",
        "/portfolio/analyze",
        "/portfolio/report",
        "/pricing/review",
        "/pricing/report",
        "/reconciliation/review",
        "/reconciliation/report",
        "/future-route",
    ],
)
def test_public_mode_denies_all_non_demo_workflows(client, path, monkeypatch):
    monkeypatch.setenv("FLOWDECK_ENABLE_LOCAL_IMPORTS", "true")
    response = client.post(
        path, content=b"not-even-valid-multipart", headers={"Origin": ORIGIN}
    )
    assert response.status_code == 403
    assert response.json()["detail"]["error_code"] == "PUBLIC_DEMO_ONLY"
    assert response.headers["access-control-allow-origin"] == ORIGIN
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-robots-tag"] == "noindex, nofollow"


def test_real_demo_run_metadata_report_and_local_isolation(
    public_app, client, tmp_path
):
    local = LocalRunRegistry(runs_root=tmp_path / "runs", project_root=tmp_path)
    local.create_run_dir(RUN)
    local.write_metadata(metadata(notes="LOCAL_PRIVATE_SENTINEL"))
    response = client.post(
        "/demo/run?target_hedge_ratio=0.80&stress_scenario=PARALLEL_DOWN_5"
    )
    assert response.status_code == 200, response.text
    result = response.json()
    run_id = result["run_id"]
    assert result["status"] == "SUCCESS"
    assert result["summary"]["number_of_curves"] == 2
    root = tmp_path / "runs" / "public-demo" / run_id
    assert (root / "run_metadata.json").is_file() and (
        root / "flowdeck_report.xlsx"
    ).is_file()
    listed = client.get("/runs").json()
    assert listed["count"] == 1 and listed["runs"][0]["run_id"] == run_id
    assert client.get(f"/runs/{RUN}").status_code == 404
    assert client.get(f"/runs/{RUN}/report").status_code == 404
    detail = client.get(result["run_detail_url"])
    assert detail.status_code == 200 and str(tmp_path) not in detail.text
    report = client.get(result["report_url"])
    assert report.status_code == 200 and report.content.startswith(b"PK")
    assert "spreadsheetml.sheet" in report.headers["content-type"]
    assert report.headers["cache-control"] == "no-store"
    assert report.headers["x-content-type-options"] == "nosniff"
    assert report.headers["x-robots-tag"] == "noindex, nofollow"
    assert "attachment" in report.headers["content-disposition"]
    assert "LOCAL_PRIVATE_SENTINEL" not in detail.text + json.dumps(listed)


@pytest.mark.parametrize(
    "path",
    ["/health", "/api/info", "/runs", "/openapi.json", "/docs", f"/runs/{RUN}/report"],
)
def test_public_api_documents_and_missing_reports_are_noindex(client, path):
    response = client.get(path)
    assert response.headers["x-robots-tag"] == "noindex, nofollow"


def test_local_api_headers_are_unchanged(monkeypatch, tmp_path):
    monkeypatch.setenv("FLOWDECK_DEPLOYMENT_MODE", "local")
    with TestClient(create_app(project_root=tmp_path)) as http:
        assert "x-robots-tag" not in http.get("/health").headers


def test_public_openapi_contains_only_public_contract(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert set(schema["paths"]) == {
        "/health",
        "/capabilities",
        "/api/info",
        "/demo/sample-files",
        "/demo/run",
        "/runs",
        "/runs/{run_id}",
        "/runs/{run_id}/report",
    }
    assert schema["x-flowdeck-deployment"]["mode"] == "public_demo"
    assert {"429", "503"} <= schema["paths"]["/demo/run"]["post"]["responses"].keys()
    assert client.get("/api/info").json()["environment"] == "public_demo"
    assert client.get("/health").json()["status"] == "ok"
    assert client.get("/docs").status_code == 200
    assert client.get("/redoc").status_code == 200
    assert (
        client.get("/demo/sample-files")
        .json()["market_data_file"]
        .startswith("data/sample/")
    )


@pytest.mark.parametrize(
    "method,path",
    [
        ("POST", "/health"),
        ("DELETE", f"/runs/{RUN}"),
        ("PUT", "/demo/run"),
        ("POST", "/demo/run/"),
        ("POST", "/demo//run"),
        ("GET", "/runs/UNKNOWN"),
        ("GET", "/runs/%2e%2e%2fREADME.md"),
        ("GET", "/runs/%252e%252e%252fREADME.md"),
    ],
)
def test_method_and_path_variants_do_not_escape_boundary(client, method, path):
    assert client.request(method, path).status_code == 403


@pytest.mark.parametrize(
    "query",
    [
        "target_hedge_ratio=2",
        "target_hedge_ratio=-1",
        "target_hedge_ratio=NaN",
        "target_hedge_ratio=1e-999999999",
        "target_hedge_ratio=0.123456789",
        "target_hedge_ratio=0.8&target_hedge_ratio=1",
        "stress_scenario=BAD",
        "book=PRIVATE",
        "target_hedge_ratio=",
        "stress_scenario=%FF",
    ],
)
def test_public_generation_query_is_small_and_unambiguous(client, query):
    response = client.post("/demo/run?" + query)
    assert response.status_code == 400, response.text
    assert response.json()["detail"]["error_code"] == "PUBLIC_DEMO_QUERY_INVALID"


def test_large_query_and_posted_body_are_rejected(client):
    assert client.get("/runs?extra=" + "x" * 2049).status_code == 414
    for path, method in [("/demo/run", "POST"), ("/health", "GET")]:
        response = client.request(method, path, content=b"private payload")
        assert response.status_code == 400
        assert "private payload" not in response.text


def test_rate_limit_and_cors_rejection(client):
    assert client.post("/demo/run").status_code == 200
    limited = client.post(
        "/demo/run", headers={"Origin": ORIGIN, "X-Forwarded-For": "1.2.3.4"}
    )
    assert limited.status_code == 429
    assert int(limited.headers["retry-after"]) >= 1
    assert limited.headers["access-control-allow-origin"] == ORIGIN
    assert (
        "access-control-allow-origin"
        not in client.get(
            "/health", headers={"Origin": "https://untrusted.example"}
        ).headers
    )
    preflight = client.options(
        "/demo/run", headers={"Origin": ORIGIN, "Access-Control-Request-Method": "POST"}
    )
    assert preflight.status_code == 200
    assert preflight.headers.get("access-control-allow-credentials") is None


def test_full_storage_returns_controlled_error_without_deleting(
    public_app, client, tmp_path
):
    registry = public_app.state.run_registry
    registry.max_runs = 1
    registry.create_run_dir(RUN)
    (registry.run_dir(RUN) / "keep.txt").write_text("synthetic operator fixture")
    response = client.post("/demo/run")
    assert response.status_code == 503
    assert response.json()["detail"]["error_code"] == "PUBLIC_DEMO_STORAGE_FULL"
    assert (
        registry.run_dir(RUN) / "keep.txt"
    ).read_text() == "synthetic operator fixture"
    with pytest.raises(PublicDemoStorageFull):
        registry.create_run_dir("FD-RUN-20260912-120001-ABC124")


@pytest.mark.parametrize("exception", [RuntimeError, ValueError])
def test_public_failed_metadata_does_not_publish_raw_exceptions(
    public_app, client, monkeypatch, exception
):
    from backend.app.services.demo import demo_runner

    def fail(*_args, **_kwargs):
        raise exception("PRIVATE_PATH_AND_DIAGNOSTIC")

    monkeypatch.setattr(demo_runner, "load_market_data_csv", fail)
    response = client.post("/demo/run")
    assert response.status_code == 500 and "PRIVATE_PATH" not in response.text
    listed = client.get("/runs")
    assert listed.json()["runs"][0]["status"] == "FAILED"
    assert "PRIVATE_PATH" not in listed.text
    run_id = listed.json()["runs"][0]["run_id"]
    assert "PRIVATE_PATH" not in client.get(f"/runs/{run_id}").text
    assert (
        "PRIVATE_PATH"
        not in public_app.state.run_registry.metadata_path(run_id).read_text()
    )


def test_corrupt_mismatched_and_oversize_metadata_is_ignored(public_app, client):
    registry = public_app.state.run_registry
    registry.create_run_dir(RUN)
    file = registry.metadata_path(RUN)
    for content in (
        "invalid json",
        "x" * 65537,
        metadata(run_id="FD-RUN-20260912-120001-ABC124").model_dump_json(),
    ):
        file.write_text(content)
        assert client.get("/runs").json() == {"runs": [], "count": 0}
        assert client.get(f"/runs/{RUN}").status_code == 404


def test_missing_and_unsafe_metadata_report_path_cannot_read_outside(
    public_app, client, tmp_path
):
    registry = public_app.state.run_registry
    registry.create_run_dir(RUN)
    outside = tmp_path / "private.xlsx"
    outside.write_bytes(b"PRIVATE_WORKBOOK")
    registry.metadata_path(RUN).write_text(
        metadata(
            output_files=RunOutputFiles(excel_report_path=str(outside))
        ).model_dump_json()
    )
    response = client.get(f"/runs/{RUN}/report")
    assert response.status_code == 404
    assert b"PRIVATE_WORKBOOK" not in response.content
    assert str(outside) not in client.get(f"/runs/{RUN}").text


@pytest.mark.parametrize(
    "name,value",
    [
        ("FLOWDECK_DEPLOYMENT_MODE", "public-demo-typo"),
        ("FLOWDECK_ENABLE_LOCAL_IMPORTS", "true"),
        ("FLOWDECK_ENABLE_LOCAL_IMPORTS", "typo"),
        ("FLOWDECK_ALLOWED_ORIGINS", "*"),
        ("FLOWDECK_ALLOWED_ORIGINS", ""),
        ("FLOWDECK_ALLOWED_ORIGINS", "http://insecure.example"),
        ("FLOWDECK_ALLOWED_ORIGINS", "https://user:pass@example.com"),
        ("FLOWDECK_ALLOWED_ORIGINS", "https://example.com/path"),
        ("FLOWDECK_ALLOWED_ORIGINS", "https://example.com/?x=1"),
        ("FLOWDECK_ALLOWED_ORIGINS", "https://*.example.com"),
        ("FLOWDECK_PUBLIC_MAX_RUNS", "0"),
        ("FLOWDECK_PUBLIC_MAX_RUNS", "1001"),
        ("FLOWDECK_PUBLIC_MAX_RUNS", "not-a-number"),
    ],
)
def test_unsafe_public_configuration_fails_closed(
    public_app, monkeypatch, tmp_path, name, value
):
    monkeypatch.setenv(name, value)
    with pytest.raises(ValueError):
        create_app(project_root=tmp_path)


def test_default_local_mode_preserves_existing_routes_and_store(monkeypatch, tmp_path):
    monkeypatch.delenv("FLOWDECK_DEPLOYMENT_MODE", raising=False)
    monkeypatch.setenv("FLOWDECK_ALLOWED_ORIGINS", "http://localhost:3000")
    app = create_app(project_root=tmp_path)
    assert app.state.deployment_policy.mode == "local"
    assert app.state.run_registry is None
    with TestClient(app) as client:
        assert "/market-data/validate" in client.get("/openapi.json").json()["paths"]
        assert client.get("/api/info").json()["environment"] == "local"


def test_denied_route_never_reads_or_parses_body():
    async def scenario():
        messages = []

        async def fail(*_args):
            raise AssertionError("Denied request reached body/application")

        async def send(message):
            messages.append(message)

        await PublicDemoBoundary(fail, DemoAdmission())(
            {"type": "http", "method": "POST", "path": "/reports/excel", "headers": []},
            fail,
            send,
        )
        assert messages[0]["status"] == 403

    asyncio.run(scenario())


def test_streamed_body_rejected_even_with_false_zero_content_length():
    async def scenario():
        messages = []

        async def fail(*_args):
            raise AssertionError("Body reached application")

        async def receive():
            return {
                "type": "http.request",
                "body": b"PRIVATE_UPLOAD",
                "more_body": True,
            }

        async def send(message):
            messages.append(message)

        await PublicDemoBoundary(fail, DemoAdmission())(
            {
                "type": "http",
                "method": "POST",
                "path": "/demo/run",
                "headers": [(b"content-length", b"0")],
            },
            receive,
            send,
        )
        assert messages[0]["status"] == 400
        assert b"PRIVATE_UPLOAD" not in messages[1]["body"]

    asyncio.run(scenario())


def test_concurrent_generation_is_rejected_and_slot_released():
    async def scenario():
        started, release = asyncio.Event(), asyncio.Event()
        calls = 0
        responses = []

        async def application(scope, receive, send):
            nonlocal calls
            calls += 1
            started.set()
            await release.wait()
            raise RuntimeError("synthetic failure")

        async def receive():
            return {"type": "http.request", "body": b"", "more_body": False}

        async def send(message):
            responses.append(message)

        admission = DemoAdmission(clock=lambda: 100)
        middleware = PublicDemoBoundary(application, admission)
        scope = {"type": "http", "method": "POST", "path": "/demo/run", "headers": []}
        first = asyncio.create_task(middleware(scope, receive, send))
        await started.wait()
        await middleware(scope, receive, send)
        assert calls == 1 and responses[0]["status"] == 429
        assert b"PUBLIC_DEMO_BUSY" in responses[1]["body"]
        release.set()
        with pytest.raises(RuntimeError):
            await first
        assert admission.active is False
        admission.clock = lambda: 106
        assert admission.enter() is None
        admission.leave()

    asyncio.run(scenario())


def test_linked_paths_are_rejected_without_reading_them(public_app, client, tmp_path):
    registry = public_app.state.run_registry
    registry.create_run_dir(RUN)
    external = tmp_path / "external.json"
    external.write_text(metadata(notes="PRIVATE_SENTINEL").model_dump_json())
    try:
        registry.metadata_path(RUN).symlink_to(external)
    except OSError:
        pytest.skip(
            "Host does not permit symlink creation; resolver checks are covered separately."
        )
    assert client.get("/runs").json()["count"] == 0
    assert client.get(f"/runs/{RUN}").status_code == 404


def test_resolved_path_escape_is_rejected_without_symlink_privileges(
    tmp_path, monkeypatch
):
    registry = PublicDemoRegistry(tmp_path, 2)
    real_resolve = Path.resolve
    target = registry.run_dir(RUN)

    def redirect(path, *args, **kwargs):
        return (
            tmp_path / "external"
            if path == target
            else real_resolve(path, *args, **kwargs)
        )

    monkeypatch.setattr(Path, "resolve", redirect)
    with pytest.raises(ValueError, match="Linked public run"):
        registry.run_dir(RUN)
