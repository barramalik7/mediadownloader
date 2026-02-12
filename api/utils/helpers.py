import os
import sys
import subprocess
from ..models.schemas import DownloadResponse
from pathlib import Path
from typing import Generator
import re
import json

# Project root is 2 levels up from this file (api/utils/helpers.py -> api -> project_root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def get_downloads_dir(platform: str, subfolder: str = None) -> str:
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


def run_download_command(cmd: list[str]) -> DownloadResponse:
    """Execute a subprocess command and return a standardized DownloadResponse."""
    try:
        process = subprocess.run(cmd, capture_output=True, text=True)
        if process.returncode == 0:
            return DownloadResponse(success=True, message="Download successful", output=process.stdout)
        else:
            return DownloadResponse(success=False, message="Download failed", error=process.stderr, output=process.stdout)
    except Exception as e:
        return DownloadResponse(success=False, message="Internal Server Error", error=str(e))


def stream_download_command(cmd: list[str]) -> Generator[str, None, None]:
    """Execute a subprocess command and yield SSE-formatted progress updates."""
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Merge stderr into stdout
            text=True,
            bufsize=1,
            universal_newlines=True,
            encoding='utf-8',
            errors='replace' # Prevent decoding errors
        )
        
        # Regex for yt-dlp progress: [download]  45.2% ...
        progress_re = re.compile(r"\[download\]\s+(\d+\.\d+)%")

        for line in process.stdout:
            line_clean = line.strip()
            if not line_clean:
                continue

            progress = None
            match = progress_re.search(line_clean)
            if match:
                try:
                    progress = float(match.group(1))
                except ValueError:
                    pass
            
            # Construct event data
            data = {
                "status": "downloading",
                "log": line_clean
            }
            if progress is not None:
                data["progress"] = progress
            
            yield f"data: {json.dumps(data)}\n\n"

        process.wait()

        if process.returncode == 0:
            final_data = {
                "status": "completed", 
                "progress": 100, 
                "message": "Download successful"
            }
            yield f"data: {json.dumps(final_data)}\n\n"
        else:
            error_data = {
                "status": "error", 
                "message": "Download failed. Check logs."
            }
            yield f"data: {json.dumps(error_data)}\n\n"

    except Exception as e:
        error_data = {
            "status": "error", 
            "message": f"Internal Server Error: {str(e)}"
        }
        yield f"data: {json.dumps(error_data)}\n\n"

