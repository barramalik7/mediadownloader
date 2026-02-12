import sys
import os
from ..utils.helpers import get_downloads_dir, find_cookie, stream_download_command
import json
from typing import Generator

def download_twitter(url: str, cookies_dir: str = None, output_dir: str = None):
    """Download media from Twitter/X using gallery-dl."""
    try:
        if not url:
            error_data = {"status": "error", "message": "URL is required", "error": "Missing URL"}
            yield f"data: {json.dumps(error_data)}\n\n"
            return

        if "twitter.com" not in url and "x.com" not in url:
            error_data = {"status": "error", "message": "Invalid Twitter/X URL"}
            yield f"data: {json.dumps(error_data)}\n\n"
            return

        # Extract username for folder naming
        username = "twitter_media"
        if "twitter.com" in url or "x.com" in url:
            try:
                parts = url.split('/')
                for i, part in enumerate(parts):
                    if "twitter.com" in part or "x.com" in part:
                        if i + 1 < len(parts):
                            username = parts[i + 1]
                        break
            except:
                pass

        if output_dir is None:
            output_dir = get_downloads_dir("twitter", subfolder=f"{username}_twitter")
        else:
            os.makedirs(output_dir, exist_ok=True)

        cmd = [sys.executable, "-m", "gallery_dl", url, "--directory", output_dir]

        cookie_path = find_cookie(cookies_dir, ["twitter.com_cookies.txt", "x.com_cookies.txt", "cookies.txt"])
        if cookie_path:
            cmd.extend(["--cookies", cookie_path])

        return stream_download_command(cmd)

    except Exception as e:
        error_data = {"status": "error", "message": f"Internal Server Error: {str(e)}"}
        yield f"data: {json.dumps(error_data)}\n\n"
