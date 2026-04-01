import logging
import os
import sys
from dataclasses import dataclass
from typing import Callable, Generator

from ..utils.helpers import emit_error_event, ensure_output_dir, find_cookie, stream_download_command


@dataclass(frozen=True)
class DownloadCommandInput:
    url: str
    quality: str = "1"
    format_choice: str = "mp4"
    cookies_dir: str | None = None
    output_dir: str | None = None


@dataclass(frozen=True)
class DownloadCommandSpec:
    command: list[str]
    output_dir: str


@dataclass(frozen=True)
class PlatformAdapter:
    name: str
    validate: Callable[[str], str | None]
    build_command: Callable[[DownloadCommandInput], DownloadCommandSpec]


logger = logging.getLogger("mediadownloader.download")


def stream_platform_download(
    adapter: PlatformAdapter,
    download_input: DownloadCommandInput,
    command_runner: Callable[[list[str]], Generator[str, None, None]] = stream_download_command,
) -> Generator[str, None, None]:
    error = adapter.validate(download_input.url)
    if error:
        logger.warning("download_invalid_platform_input platform=%s message=%s", adapter.name, error)
        yield emit_error_event(error, code="invalid_platform_input")
        return

    try:
        spec = adapter.build_command(download_input)
        logger.info(
            "download_stream_started platform=%s format=%s quality=%s",
            adapter.name,
            download_input.format_choice,
            download_input.quality,
        )
        yield from command_runner(spec.command)
    except Exception as exc:
        logger.exception("download_stream_preparation_failed platform=%s", adapter.name)
        yield emit_error_event(f"Internal Server Error: {exc}", code="internal_error")


def validate_required_url(platform_name: str, url: str) -> str | None:
    if not url:
        return "URL is required"

    if platform_name not in url:
        return f"Invalid {platform_name.split('.')[0].capitalize()} URL"

    return None


def validate_twitter_url(url: str) -> str | None:
    if not url:
        return "URL is required"

    if "twitter.com" not in url and "x.com" not in url:
        return "Invalid Twitter/X URL"

    return None


def validate_pinterest_url(url: str) -> str | None:
    if not url:
        return "URL is required"

    if "pinterest.com" not in url and "pin.it" not in url:
        return "Invalid Pinterest URL"

    return None


def _build_youtube_command(download_input: DownloadCommandInput) -> DownloadCommandSpec:
    quality_formats = {
        "1": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
        "2": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best[height<=1080]",
        "3": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio/best[height<=720]",
        "4": "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=480]+bestaudio/best[height<=480]",
    }

    is_audio_only = download_input.format_choice.lower() == "mp3"
    format_string = (
        "bestaudio[ext=m4a]/bestaudio/best"
        if is_audio_only
        else quality_formats.get(download_input.quality, quality_formats["1"])
    )

    output_dir = ensure_output_dir(download_input.output_dir, "youtube")
    output_template = os.path.join(output_dir, "%(title)s.%(ext)s")
    command = [
        sys.executable,
        "-m",
        "yt_dlp",
        download_input.url,
        "-f",
        format_string,
        "-o",
        output_template,
        "--no-playlist",
        "--impersonate",
        "chrome-131:macos-14",
    ]

    if is_audio_only:
        command.extend(["--extract-audio", "--audio-format", "mp3", "--audio-quality", "0"])
    else:
        command.extend(["--merge-output-format", "mp4"])

    cookie_path = find_cookie(download_input.cookies_dir, ["youtube.com_cookies.txt"])
    if cookie_path:
        command.extend(["--cookies", cookie_path])

    return DownloadCommandSpec(command=command, output_dir=output_dir)


def _build_tiktok_command(download_input: DownloadCommandInput) -> DownloadCommandSpec:
    quality_formats = {
        "1": "bestvideo+bestaudio/best",
        "2": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
        "3": "bestvideo[height<=720]+bestaudio/best[height<=720]",
        "4": "bestvideo[height<=480]+bestaudio/best[height<=480]",
    }

    is_audio_only = download_input.format_choice.lower() == "mp3"
    format_string = "bestaudio/best" if is_audio_only else quality_formats.get(download_input.quality, quality_formats["1"])

    output_dir = ensure_output_dir(download_input.output_dir, "tiktok")
    output_template = os.path.join(output_dir, "%(uploader)s_%(id)s.%(ext)s")
    command = [
        sys.executable,
        "-m",
        "yt_dlp",
        download_input.url,
        "-f",
        format_string,
        "-o",
        output_template,
        "--no-playlist",
        "--impersonate",
        "chrome-116:windows-10",
    ]

    if is_audio_only:
        command.extend(["--extract-audio", "--audio-format", "mp3", "--audio-quality", "0"])
    else:
        command.extend(["--merge-output-format", "mp4", "--extractor-args", "tiktok:api_hostname=api22-normal-c-useast2a.tiktokv.com"])

    cookie_path = find_cookie(download_input.cookies_dir, ["www.tiktok.com_cookies.txt"])
    if cookie_path:
        command.extend(["--cookies", cookie_path])

    return DownloadCommandSpec(command=command, output_dir=output_dir)


def _extract_instagram_folder_name(url: str) -> str:
    folder_name = "instagram_downloads"
    if "instagram.com/" in url:
        try:
            parts = url.split("instagram.com/")[-1].split("/")
            if parts[0]:
                folder_name = f"{parts[0]}_instagram"
        except Exception:
            return folder_name
    return folder_name


def _build_instagram_command(download_input: DownloadCommandInput) -> DownloadCommandSpec:
    folder_name = _extract_instagram_folder_name(download_input.url)
    output_dir = ensure_output_dir(download_input.output_dir, "instagram", subfolder=folder_name)
    command = [sys.executable, "-m", "gallery_dl", download_input.url, "--directory", output_dir]

    cookie_path = find_cookie(
        download_input.cookies_dir,
        ["instagram.com_cookies.txt", "www.instagram.com_cookies.txt", "cookies.txt"],
    )
    if cookie_path:
        command.extend(["--cookies", cookie_path])

    return DownloadCommandSpec(command=command, output_dir=output_dir)


def _extract_twitter_folder_name(url: str) -> str:
    username = "twitter_media"
    try:
        parts = url.split("/")
        for index, part in enumerate(parts):
            if "twitter.com" in part or "x.com" in part:
                if index + 1 < len(parts) and parts[index + 1]:
                    username = parts[index + 1]
                break
    except Exception:
        return username
    return username


def _build_twitter_command(download_input: DownloadCommandInput) -> DownloadCommandSpec:
    username = _extract_twitter_folder_name(download_input.url)
    output_dir = ensure_output_dir(download_input.output_dir, "twitter", subfolder=f"{username}_twitter")
    command = [sys.executable, "-m", "gallery_dl", download_input.url, "--directory", output_dir]

    cookie_path = find_cookie(
        download_input.cookies_dir,
        ["twitter.com_cookies.txt", "x.com_cookies.txt", "cookies.txt"],
    )
    if cookie_path:
        command.extend(["--cookies", cookie_path])

    return DownloadCommandSpec(command=command, output_dir=output_dir)


def _build_pinterest_command(download_input: DownloadCommandInput) -> DownloadCommandSpec:
    output_dir = ensure_output_dir(download_input.output_dir, "pinterest")
    command = [sys.executable, "-m", "gallery_dl", download_input.url, "--directory", output_dir]

    cookie_path = find_cookie(download_input.cookies_dir, ["pinterest.com_cookies.txt"])
    if cookie_path:
        command.extend(["--cookies", cookie_path])

    return DownloadCommandSpec(command=command, output_dir=output_dir)


def _build_spotify_command(download_input: DownloadCommandInput) -> DownloadCommandSpec:
    output_dir = ensure_output_dir(download_input.output_dir, "spotify")
    command = [sys.executable, "-m", "spotdl", download_input.url, "--output", output_dir]
    return DownloadCommandSpec(command=command, output_dir=output_dir)


YOUTUBE_ADAPTER = PlatformAdapter(
    name="youtube",
    validate=lambda url: None if ("youtube.com" in url or "youtu.be" in url) else "Invalid YouTube URL",
    build_command=_build_youtube_command,
)
TIKTOK_ADAPTER = PlatformAdapter(
    name="tiktok",
    validate=lambda url: None if "tiktok.com" in url else "Invalid TikTok URL",
    build_command=_build_tiktok_command,
)
INSTAGRAM_ADAPTER = PlatformAdapter(
    name="instagram",
    validate=lambda url: None if "instagram.com" in url else "Invalid Instagram URL",
    build_command=_build_instagram_command,
)
TWITTER_ADAPTER = PlatformAdapter(
    name="twitter",
    validate=validate_twitter_url,
    build_command=_build_twitter_command,
)
PINTEREST_ADAPTER = PlatformAdapter(
    name="pinterest",
    validate=validate_pinterest_url,
    build_command=_build_pinterest_command,
)
SPOTIFY_ADAPTER = PlatformAdapter(
    name="spotify",
    validate=lambda url: None if url and "spotify.com" in url else ("URL is required" if not url else "Invalid Spotify URL"),
    build_command=_build_spotify_command,
)
