import sys
import os
from ..utils.helpers import get_downloads_dir, stream_download_command
import json
from typing import Generator

def download_spotify(url: str, output_dir: str = None):
    """Download music from Spotify using spotdl."""
    try:
        if not url:
            from ..models.schemas import DownloadResponse
            return DownloadResponse(success=False, message="URL is required", error="Missing URL")

        if "spotify.com" not in url:
            error_data = {"status": "error", "message": "Invalid Spotify URL"}
            yield f"data: {json.dumps(error_data)}\n\n"
            return

        if output_dir is None:
            output_dir = get_downloads_dir("spotify")
        else:
            os.makedirs(output_dir, exist_ok=True)

        cmd = [sys.executable, "-m", "spotdl", url, "--output", output_dir]

        return stream_download_command(cmd)

    except Exception as e:
        error_data = {"status": "error", "message": f"Internal Server Error: {str(e)}"}
        yield f"data: {json.dumps(error_data)}\n\n"
