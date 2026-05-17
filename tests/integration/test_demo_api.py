from decimal import Decimal
from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_demo_sample_files_returns_expected_files() -> None:
    response = client.get("/demo/sample-files")

    assert response.status_code == 200
    payload = response.json()
    assert (
        payload["market_data_file"]
        == "data/sample/market_data/valid_brent_wti_futures.csv"
    )
    assert (
        payload["futures_positions_file"]
        == "data/sample/positions/valid_futures_positions.csv"
    )
    assert (
        payload["physical_cargoes_file"]
        == "data/sample/positions/valid_physical_cargoes.csv"
    )
    assert "Synthetic" in payload["note"]


def test_demo_run_returns_run_id_and_summary() -> None:
    response = client.post("/demo/run")

    assert response.status_code == 200
    payload = response.json()
    assert payload["run_id"].startswith("FD-RUN-")
    assert payload["status"] == "SUCCESS"
    assert payload["summary"]["number_of_curves"] == 2
    assert payload["summary"]["number_of_net_exposure_buckets"] > 0
    assert Decimal(str(payload["summary"]["total_net_exposure_bbl"]))
    assert payload["report_url"] == f"/runs/{payload['run_id']}/report"
    assert payload["run_detail_url"] == f"/runs/{payload['run_id']}"
    assert "Synthetic demo data only." in payload["assumptions"]


def test_demo_run_creates_metadata_and_report() -> None:
    response = client.post("/demo/run")

    assert response.status_code == 200
    run_id = response.json()["run_id"]
    run_dir = PROJECT_ROOT / "runs" / run_id
    assert (run_dir / "run_metadata.json").exists()
    assert (run_dir / "flowdeck_report.xlsx").exists()


def test_demo_run_report_url_downloads_workbook() -> None:
    response = client.post("/demo/run")
    payload = response.json()

    report_response = client.get(payload["report_url"])

    assert report_response.status_code == 200
    assert report_response.headers["content-type"] == (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert report_response.content.startswith(b"PK")


def test_demo_run_rejects_invalid_target_hedge_ratio() -> None:
    response = client.post("/demo/run", params={"target_hedge_ratio": "1.5"})

    assert response.status_code == 400
    assert response.json()["detail"]["error_code"] == "DEMO_RUN_VALIDATION_ERROR"


def test_demo_run_rejects_invalid_stress_scenario() -> None:
    response = client.post("/demo/run", params={"stress_scenario": "BAD_SCENARIO"})

    assert response.status_code == 400
    assert response.json()["detail"]["error_code"] == "REQUEST_VALIDATION_ERROR"


def test_openapi_includes_demo_endpoints() -> None:
    schema = client.get("/openapi.json").json()

    assert "/demo/sample-files" in schema["paths"]
    assert "/demo/run" in schema["paths"]
