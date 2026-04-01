import logging
import os
import re
import shutil
import subprocess
import sys
from collections import deque
from importlib.util import find_spec
from pathlib import Path
from typing import Generator

from pydantic import TypeAdapter

from ..models.schemas import (
    DownloadCompletedEvent,
    DownloadDownloadingEvent,
    DownloadErrorEvent,
    DownloadRuntimeErrorCode,
    DownloadStreamEvent,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
STREAM_EVENT_ADAPTER = TypeAdapter(DownloadStreamEvent)
logger = logging.getLogger("mediadownloader.download")
PREFLIGHT_CHECK_DETAILS = {
    "python": {
        "required_for": "running backend download tools",
        "hint": "Use a supported Python interpreter and virtual environment for the backend.",
    },
    "ffmpeg": {
        "required_for": "media conversion and merged video outputs",
        "hint": "Install ffmpeg and add it to PATH.",
    },
    "yt_dlp": {
        "required_for": "YouTube, TikTok, and Twitter/X video downloads",
        "hint": "Install yt-dlp in the active backend environment.",
    },
    "gallery_dl": {
        "required_for": "Instagram and Pinterest image or gallery downloads",
        "hint": "Install gallery-dl in the active backend environment.",
    },
    "spotdl": {
        "required_for": "Spotify downloads",
        "hint": "Spotify downloads require spotdl and are unavailable on Python 3.14 right now.",
    },
    "downloads_dir": {
        "required_for": "writing downloaded files",
        "hint": "Create the downloads directory and ensure the backend can write to it.",
    },
    "cookies_dir": {
        "required_for": "authenticated platform access via cookie files",
        "hint": "Create the cookies directory and place supported cookies.txt files there when needed.",
    },
}


def get_downloads_dir(platform: str, subfolder: str | None = None) -> str:
    """Get the downloads directory for a platform, creating it if needed."""
    parts = [PROJECT_ROOT, "downloads", platform]
    if subfolder:
        parts = [PROJECT_ROOT, "downloads", subfolder]
    output_dir = os.path.join(*[str(p) for p in parts])
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def get_cookies_dir() -> str:
    """Get the cookies directory path."""
    return str(PROJECT_ROOT / "cookies")


def find_cookie(cookies_dir: str, candidates: list[str]) -> str | None:
    """Search for the first matching cookie file from a list of candidates."""
    if not cookies_dir:
        return None

    for name in candidates:
        path = os.path.join(cookies_dir, name)
        if os.path.exists(path):
            return path

    return None


def ensure_output_dir(output_dir: str | None, platform: str, subfolder: str | None = None) -> str:
    """Use the provided output directory or fall back to the platform downloads directory."""
    if output_dir is None:
        return get_downloads_dir(platform, subfolder=subfolder)

    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def emit_sse_event(event: DownloadStreamEvent) -> str:
    payload = STREAM_EVENT_ADAPTER.dump_json(event).decode("utf-8")
    return f"data: {payload}\n\n"


def emit_downloading_event(log: str, progress: float | None = None) -> str:
    return emit_sse_event(
        DownloadDownloadingEvent(
            status="downloading",
            log=log,
            progress=progress,
        )
    )


def emit_completed_event(message: str = "Download successful", progress: float | None = 100) -> str:
    return emit_sse_event(
        DownloadCompletedEvent(
            status="completed",
            message=message,
            progress=progress,
        )
    )


def emit_error_event(message: str, code: DownloadRuntimeErrorCode) -> str:
    return emit_sse_event(
        DownloadErrorEvent(
            status="error",
            code=code,
            message=message,
        )
    )


def classify_subprocess_failure(message: str) -> DownloadRuntimeErrorCode:
    normalized = message.lower()
    missing_dependency_hints = (
        "no module named",
        "ffmpeg",
        "not installed",
        "not found",
        "is required",
        "missing",
    )

    if any(hint in normalized for hint in missing_dependency_hints):
        return "missing_dependency"

    return "subprocess_failure"


def stream_download_command(cmd: list[str]) -> Generator[str, None, None]:
    """Execute a subprocess command and yield SSE-formatted progress updates."""
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            encoding="utf-8",
            errors="replace",
        )

        progress_re = re.compile(r"\[download\]\s+(\d+\.\d+)%")
        recent_lines: deque[str] = deque(maxlen=10)

        if process.stdout is None:
            logger.exception("download_process_missing_stdout")
            yield emit_error_event("Download process did not expose stdout", code="internal_error")
            return

        for line in process.stdout:
            line_clean = line.strip()
            if not line_clean:
                continue

            recent_lines.append(line_clean)
            progress = None
            match = progress_re.search(line_clean)
            if match:
                try:
                    progress = float(match.group(1))
                except ValueError:
                    progress = None

            yield emit_downloading_event(line_clean, progress=progress)

        process.wait()

        if process.returncode == 0:
            logger.info("download_subprocess_completed")
            yield emit_completed_event()
        else:
            failure_message = recent_lines[-1] if recent_lines else "Download failed. Check logs."
            failure_code = classify_subprocess_failure(failure_message)
            logger.warning("download_subprocess_failed code=%s message=%s", failure_code, failure_message)
            yield emit_error_event(failure_message, code=failure_code)

    except OSError as exc:
        logger.warning("download_dependency_failure error=%s", exc)
        yield emit_error_event(f"Dependency execution failed: {exc}", code="missing_dependency")
    except Exception as exc:
        logger.exception("download_internal_error")
        yield emit_error_event(f"Internal Server Error: {exc}", code="internal_error")


def get_preflight_status() -> dict[str, object]:
    downloads_dir = PROJECT_ROOT / "downloads"
    cookies_dir = PROJECT_ROOT / "cookies"

    checks = {
        "python": {
            "ok": True,
            "value": sys.executable,
        },
        "ffmpeg": {
            "ok": shutil.which("ffmpeg") is not None,
            "value": shutil.which("ffmpeg"),
        },
        "yt_dlp": {
            "ok": find_spec("yt_dlp") is not None,
        },
        "gallery_dl": {
            "ok": find_spec("gallery_dl") is not None,
        },
        "spotdl": {
            "ok": find_spec("spotdl") is not None,
        },
        "downloads_dir": {
            "ok": downloads_dir.exists() and os.access(downloads_dir, os.W_OK),
            "value": str(downloads_dir),
        },
        "cookies_dir": {
            "ok": cookies_dir.exists() and os.access(cookies_dir, os.R_OK),
            "value": str(cookies_dir),
        },
    }

    for name, check in checks.items():
        details = PREFLIGHT_CHECK_DETAILS.get(name, {})
        check["required_for"] = details.get("required_for")
        check["hint"] = details.get("hint")

    status = "ok" if all(check["ok"] for check in checks.values()) else "degraded"
    status_message = "Backend runtime is ready." if status == "ok" else "Backend runtime is degraded."

    return {
        "status": status,
        "status_message": status_message,
        "checks": checks,
    }
