import sys
import os
from ..utils.helpers import get_downloads_dir, find_cookie, stream_download_command
import json
from typing import Generator

def download_pinterest(url: str, format_choice: str = "mp4", cookies_dir: str = None, output_dir: str = None):
    """Download media from Pinterest using gallery-dl."""
    try:
        if not url:
            error_data = {"status": "error", "message": "URL is required", "error": "Missing URL"}
            yield f"data: {json.dumps(error_data)}\n\n"
            return

        if "pinterest.com" not in url and "pin.it" not in url:
            error_data = {"status": "error", "message": "Invalid Pinterest URL"}
            yield f"data: {json.dumps(error_data)}\n\n"
            return

        if output_dir is None:
            output_dir = get_downloads_dir("pinterest")
        else:
            os.makedirs(output_dir, exist_ok=True)

        cmd = [sys.executable, "-m", "gallery_dl", url, "--directory", output_dir]

        cookie_path = find_cookie(cookies_dir, ["pinterest.com_cookies.txt"])
        if cookie_path:
            cmd.extend(["--cookies", cookie_path])

        yield from stream_download_command(cmd)

    except Exception as e:
        error_data = {"status": "error", "message": f"Internal Server Error: {str(e)}"}
        yield f"data: {json.dumps(error_data)}\n\n"
