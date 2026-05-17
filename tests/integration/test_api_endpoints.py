from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
MARKET_DIR = PROJECT_ROOT / "data" / "sample" / "market_data"
POSITIONS_DIR = PROJECT_ROOT / "data" / "sample" / "positions"


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "FlowDeck API",
        "version": "0.1.0",
    }


def test_capabilities_endpoint() -> None:
    response = client.get("/capabilities")

    assert response.status_code == 200
    payload = response.json()
    assert payload["commodities"] == ["BRENT", "WTI"]
    assert "excel_export" in payload["modules"]


def test_api_info_endpoint() -> None:
    response = client.get("/api/info")

    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "FlowDeck API"
    assert payload["environment"] == "local"
    assert payload["docs_url"] == "/docs"
    assert "http://localhost:3000" in payload["frontend_expected_origin_examples"]


def test_cors_allows_localhost_frontend_origin() -> None:
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_market_data_validation_with_valid_csv() -> None:
    response = client.post(
        "/market-data/validate",
        files={"file": _csv_file(MARKET_DIR / "valid_brent_wti_futures.csv")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["valid"] is True
    assert payload["row_count"] == 6
    assert len(payload["preview_rows"]) > 0


def test_market_data_validation_with_invalid_csv() -> None:
    response = client.post(
        "/market-data/validate",
        files={"file": _csv_file(MARKET_DIR / "invalid_negative_price.csv")},
    )

    assert response.status_code == 400
    assert response.json()["detail"]["valid"] is False


def test_curves_build_endpoint() -> None:
    response = client.post(
        "/curves/build",
        files={"file": _csv_file(MARKET_DIR / "valid_brent_wti_futures.csv")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["curve_summaries"]) == 2
    assert len(payload["calendar_spreads"]) > 0


def test_futures_analyze_endpoint() -> None:
    response = client.post(
        "/positions/futures/analyze",
        files={"file": _csv_file(POSITIONS_DIR / "valid_futures_positions.csv")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["valid"] is True
    assert payload["row_count"] == 6
    assert payload["summary"]["number_of_buckets"] > 0


def test_physical_analyze_endpoint() -> None:
    response = client.post(
        "/positions/physical/analyze",
        files={"file": _csv_file(POSITIONS_DIR / "valid_physical_cargoes.csv")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["valid"] is True
    assert payload["row_count"] == 5
    assert payload["summary"]["number_of_buckets"] > 0


def test_net_exposure_endpoint() -> None:
    response = client.post(
        "/exposure/net",
        files=_position_files(),
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["net_exposure_buckets"]) > 0
    assert payload["summary"]["number_of_exposure_buckets"] > 0


def test_hedge_simulation_endpoint() -> None:
    response = client.post(
        "/hedging/simulate",
        files=_position_files(),
        data={"target_hedge_ratio": "0.80", "contract_size_bbl": "1000"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["hedge_recommendations"]) > 0
    assert payload["hedge_summary"]["number_of_recommendations"] > 0


def test_stress_endpoint() -> None:
    response = client.post(
        "/risk/stress",
        files=_position_files(),
        data={"scenario_name": "PARALLEL_DOWN_5"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["stress_bucket_results"]) > 0
    assert payload["stress_summary"]["scenario_name"] == "PARALLEL_DOWN_5"


def test_excel_report_endpoint_returns_xlsx() -> None:
    response = client.post(
        "/reports/excel",
        files={
            "market_data_file": _csv_file(MARKET_DIR / "valid_brent_wti_futures.csv"),
            "futures_file": _csv_file(POSITIONS_DIR / "valid_futures_positions.csv"),
            "physical_file": _csv_file(POSITIONS_DIR / "valid_physical_cargoes.csv"),
        },
        data={"target_hedge_ratio": "0.80", "stress_scenario": "PARALLEL_DOWN_5"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert response.content[:2] == b"PK"


def test_non_csv_upload_is_rejected() -> None:
    response = client.post(
        "/market-data/validate",
        files={"file": ("bad.txt", b"not,csv", "text/plain")},
    )

    assert response.status_code == 400
    assert "Only .csv" in response.json()["detail"]["error"]


def test_empty_file_is_rejected() -> None:
    response = client.post(
        "/market-data/validate",
        files={"file": ("empty.csv", b"", "text/csv")},
    )

    assert response.status_code == 400
    assert "empty" in response.json()["detail"]["error"]


def _csv_file(path: Path):
    return (path.name, path.read_bytes(), "text/csv")


def _position_files():
    return {
        "futures_file": _csv_file(POSITIONS_DIR / "valid_futures_positions.csv"),
        "physical_file": _csv_file(POSITIONS_DIR / "valid_physical_cargoes.csv"),
    }
