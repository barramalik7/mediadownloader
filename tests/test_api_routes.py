from fastapi.testclient import TestClient

from api.main import app
client = TestClient(app)


def test_download_route_rejects_unsupported_platform():
    response = client.post(
        "/api/download/",
        json={"url": "https://example.com/video", "quality": "1", "format": "mp4"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "code": "unsupported_platform",
        "detail": "Unsupported platform or invalid URL",
    }


def test_download_route_rejects_invalid_url_with_422():
    response = client.post(
        "/api/download/",
        json={"url": "not-a-url", "quality": "1", "format": "mp4"},
    )

    assert response.status_code == 422


def test_download_route_streams_sse_events(monkeypatch):
    def fake_stream(*args, **kwargs):
        yield 'data: {"status": "completed", "message": "Download successful"}\n\n'

    monkeypatch.setattr("api.routers.download.stream_platform_download", fake_stream)

    response = client.post(
        "/api/download/",
        json={"url": "https://www.youtube.com/watch?v=demo", "quality": "1", "format": "mp4"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert '"status": "completed"' in response.text


def test_download_route_openapi_documents_text_event_stream():
    schema = app.openapi()
    responses = schema["paths"]["/api/download/"]["post"]["responses"]
    error_ref = responses["400"]["content"]["application/json"]["schema"]["$ref"]
    component_name = error_ref.split("/")[-1]
    error_schema = schema["components"]["schemas"][component_name]

    assert "text/event-stream" in responses["200"]["content"]
    assert "application/json" in responses["400"]["content"]
    assert "code" in error_schema["properties"]


def test_health_endpoint_exists():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_preflight_endpoint_reports_runtime_status():
    response = client.get("/api/health/preflight")

    assert response.status_code == 200
    payload = response.json()

    assert payload["status"] in {"ok", "degraded"}
    assert isinstance(payload["status_message"], str)
    assert "checks" in payload
    assert payload["checks"]["ffmpeg"]["required_for"] == "media conversion and merged video outputs"
    assert "hint" in payload["checks"]["spotdl"]
