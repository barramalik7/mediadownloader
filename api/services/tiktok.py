import sys
import os
from ..utils.helpers import get_downloads_dir, find_cookie, stream_download_command
import json
from typing import Generator

def download_tiktok(url: str, quality: str = "1", format_choice: str = "mp4", cookies_dir: str = None, output_dir: str = None):
    """Download media from TikTok using yt-dlp."""
    try:
        if "tiktok.com" not in url:
            error_data = {"status": "error", "message": "Invalid TikTok URL"}
            yield f"data: {json.dumps(error_data)}\n\n"
            return

        quality_formats = {
            "1": "bestvideo+bestaudio/best",
            "2": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
            "3": "bestvideo[height<=720]+bestaudio/best[height<=720]",
            "4": "bestvideo[height<=480]+bestaudio/best[height<=480]"
        }

        is_audio_only = format_choice.lower() == "mp3"
        format_string = "bestaudio/best" if is_audio_only else quality_formats.get(quality, quality_formats["1"])

        if output_dir is None:
            output_dir = get_downloads_dir("tiktok")
        else:
            os.makedirs(output_dir, exist_ok=True)

        output_template = os.path.join(output_dir, "%(uploader)s_%(id)s.%(ext)s")

        cmd = [sys.executable, "-m", "yt_dlp", url, "-f", format_string, "-o", output_template, "--no-playlist", "--impersonate", "chrome-116:windows-10"]

        if is_audio_only:
            cmd.extend(["--extract-audio", "--audio-format", "mp3", "--audio-quality", "0"])
        else:
            cmd.extend(["--merge-output-format", "mp4", "--extractor-args", "tiktok:api_hostname=api22-normal-c-useast2a.tiktokv.com"])

        cookie_path = find_cookie(cookies_dir, ["www.tiktok.com_cookies.txt"])
        if cookie_path:
            cmd.extend(["--cookies", cookie_path])

        yield from stream_download_command(cmd)

    except Exception as e:
        error_data = {"status": "error", "message": f"Internal Server Error: {str(e)}"}
        yield f"data: {json.dumps(error_data)}\n\n"
