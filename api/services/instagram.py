import sys
import os
from ..utils.helpers import get_downloads_dir, find_cookie, stream_download_command
import json
from typing import Generator

def download_instagram(url: str = None, format_choice: str = "mp4", cookies_dir: str = None, output_dir: str = None):
    """Download media from Instagram using gallery-dl."""
    try:
        if "instagram.com" not in url:
            error_data = {"status": "error", "message": "Invalid Instagram URL"}
            yield f"data: {json.dumps(error_data)}\n\n"
            return

        # Determine output folder name
        folder_name = "instagram_downloads"
        if "instagram.com/" in url:
            try:
                parts = url.split("instagram.com/")[-1].split("/")
                if parts[0]:
                    folder_name = f"{parts[0]}_instagram"
            except:
                pass

        if output_dir is None:
            output_dir = get_downloads_dir("instagram", subfolder=folder_name)
        else:
            os.makedirs(output_dir, exist_ok=True)

        cmd = [sys.executable, "-m", "gallery_dl", url, "--directory", output_dir]

        cookie_path = find_cookie(cookies_dir, ["instagram.com_cookies.txt", "www.instagram.com_cookies.txt", "cookies.txt"])
        if cookie_path:
            cmd.extend(["--cookies", cookie_path])

        return stream_download_command(cmd)

    except Exception as e:
        error_data = {"status": "error", "message": f"Internal Server Error: {str(e)}"}
        yield f"data: {json.dumps(error_data)}\n\n"
