from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


KEY_ENDPOINTS = {
    ("get", "/health"): "Health",
    ("get", "/capabilities"): "Capabilities",
    ("get", "/api/info"): "Capabilities",
    ("get", "/demo/sample-files"): "Demo",
    ("post", "/demo/run"): "Demo",
    ("post", "/market-data/validate"): "Market Data",
    ("post", "/curves/build"): "Curves",
    ("post", "/positions/futures/analyze"): "Positions",
    ("post", "/positions/physical/analyze"): "Positions",
    ("post", "/exposure/net"): "Exposure",
    ("post", "/hedging/simulate"): "Hedging",
    ("post", "/risk/stress"): "Risk",
    ("post", "/reports/excel"): "Reports",
    ("get", "/runs"): "Runs",
    ("get", "/runs/{run_id}"): "Runs",
    ("get", "/runs/{run_id}/report"): "Runs",
}


def test_openapi_json_is_available() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["openapi"]


def test_openapi_title_is_flowdeck_api() -> None:
    response = client.get("/openapi.json")

    assert response.json()["info"]["title"] == "FlowDeck API"
    assert response.json()["info"]["version"] == "0.1.0"


def test_key_paths_exist_in_openapi() -> None:
    schema = client.get("/openapi.json").json()

    for method, path in KEY_ENDPOINTS:
        assert path in schema["paths"]
        assert method in schema["paths"][path]


def test_each_endpoint_has_product_tags() -> None:
    schema = client.get("/openapi.json").json()

    for method, path in KEY_ENDPOINTS:
        operation = schema["paths"][path][method]
        assert operation["tags"] == [KEY_ENDPOINTS[(method, path)]]


def test_health_has_response_schema() -> None:
    operation = client.get("/openapi.json").json()["paths"]["/health"]["get"]

    schema_ref = operation["responses"]["200"]["content"]["application/json"][
        "schema"
    ]["$ref"]
    assert schema_ref.endswith("/HealthResponse")


def test_capabilities_has_response_schema() -> None:
    operation = client.get("/openapi.json").json()["paths"]["/capabilities"]["get"]

    schema_ref = operation["responses"]["200"]["content"]["application/json"][
        "schema"
    ]["$ref"]
    assert schema_ref.endswith("/CapabilitiesResponse")


def test_error_schema_is_present() -> None:
    components = client.get("/openapi.json").json()["components"]["schemas"]

    assert "ErrorResponse" in components
    assert "ErrorEnvelope" in components
    error_schema = components["ErrorResponse"]
    assert set(error_schema["properties"]) >= {"error_code", "message", "details"}


def test_excel_endpoint_documents_file_response() -> None:
    operation = client.get("/openapi.json").json()["paths"]["/reports/excel"]["post"]

    assert (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        in operation["responses"]["200"]["content"]
    )
    file_schema = operation["responses"]["200"]["content"][
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ]["schema"]
    assert file_schema == {"type": "string", "format": "binary"}
