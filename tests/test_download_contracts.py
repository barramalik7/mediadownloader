import json

from pydantic import TypeAdapter, ValidationError

from api.contracts.generation import (
    CONTRACT_SCHEMA_PATH,
    FRONTEND_CONTRACT_PATH,
    build_contract_schema,
    render_typescript_contract,
)
from api.models.schemas import (
    DownloadCompletedEvent,
    DownloadDownloadingEvent,
    DownloadErrorEvent,
    DownloadRequest,
    DownloadStreamEvent,
)
from api.services import spotify
from api.utils.helpers import classify_subprocess_failure, emit_sse_event


def collect_events(generator):
    return list(generator)


def test_download_request_rejects_invalid_url():
    try:
        DownloadRequest(url="not-a-url")
    except ValidationError:
        return

    raise AssertionError("DownloadRequest accepted an invalid URL")


def test_spotify_invalid_input_returns_sse_error_event():
    events = collect_events(spotify.download_spotify(""))

    assert len(events) == 1
    assert events[0].startswith("data: ")
    assert json.loads(events[0][6:].strip()) == {
        "status": "error",
        "code": "invalid_platform_input",
        "message": "URL is required",
    }


def test_download_stream_event_union_accepts_all_supported_statuses():
    adapter = TypeAdapter(DownloadStreamEvent)

    downloading = adapter.validate_python({"status": "downloading", "log": "step", "progress": 12.5})
    completed = adapter.validate_python({"status": "completed", "message": "ok", "progress": 100})
    error = adapter.validate_python({"status": "error", "code": "subprocess_failure", "message": "failed"})

    assert isinstance(downloading, DownloadDownloadingEvent)
    assert isinstance(completed, DownloadCompletedEvent)
    assert isinstance(error, DownloadErrorEvent)


def test_emit_sse_event_serializes_typed_event():
    payload = DownloadCompletedEvent(status="completed", message="Download successful", progress=100)

    assert emit_sse_event(payload) == 'data: {"status":"completed","message":"Download successful","progress":100.0}\n\n'


def test_error_event_requires_machine_readable_code():
    payload = DownloadErrorEvent(status="error", code="subprocess_failure", message="Download failed")

    assert emit_sse_event(payload) == 'data: {"status":"error","code":"subprocess_failure","message":"Download failed"}\n\n'


def test_generated_contract_schema_artifact_is_current():
    expected = json.dumps(build_contract_schema(), indent=2) + "\n"

    assert CONTRACT_SCHEMA_PATH.read_text(encoding="utf-8") == expected


def test_generated_typescript_contract_artifact_is_current():
    assert FRONTEND_CONTRACT_PATH.read_text(encoding="utf-8") == render_typescript_contract()


def test_classify_subprocess_failure_detects_missing_dependency():
    assert classify_subprocess_failure("ModuleNotFoundError: No module named 'spotdl'") == "missing_dependency"
    assert classify_subprocess_failure("ffmpeg not found. Please install ffmpeg.") == "missing_dependency"


def test_classify_subprocess_failure_defaults_to_subprocess_failure():
    assert classify_subprocess_failure("Download failed due to extractor error") == "subprocess_failure"
