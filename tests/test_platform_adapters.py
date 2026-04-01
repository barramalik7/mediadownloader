import sys
import shutil
from pathlib import Path

import pytest

from api.services import adapters
from api.services.adapters import DownloadCommandInput
from api.services.registry import PLATFORM_ADAPTERS


@pytest.mark.parametrize(
    ("platform", "url", "expected"),
    [
        ("youtube", "https://www.youtube.com/watch?v=demo", None),
        ("youtube", "https://example.com/video", "Invalid YouTube URL"),
        ("tiktok", "https://www.tiktok.com/@demo/video/123", None),
        ("tiktok", "https://example.com/video", "Invalid TikTok URL"),
        ("instagram", "https://www.instagram.com/openai/p/demo/", None),
        ("instagram", "https://example.com/video", "Invalid Instagram URL"),
        ("twitter", "https://x.com/openai/status/123", None),
        ("twitter", "https://example.com/video", "Invalid Twitter/X URL"),
        ("pinterest", "https://www.pinterest.com/pin/123", None),
        ("pinterest", "https://example.com/video", "Invalid Pinterest URL"),
        ("spotify", "https://open.spotify.com/track/123", None),
        ("spotify", "", "URL is required"),
    ],
)
def test_platform_adapter_validation(platform: str, url: str, expected: str | None):
    adapter = PLATFORM_ADAPTERS[platform]

    assert adapter.validate(url) == expected


def test_youtube_adapter_builds_audio_command_with_cookie():
    cookies_dir = Path.cwd() / "cookies" / "adapter-test-youtube"
    cookies_dir.mkdir(parents=True, exist_ok=True)
    cookie_file = cookies_dir / "youtube.com_cookies.txt"
    cookie_file.write_text("cookie-data", encoding="utf-8")

    try:
        output_dir = str(Path.cwd() / "downloads" / "youtube-adapter-test")
        adapter = PLATFORM_ADAPTERS["youtube"]

        spec = adapter.build_command(
            DownloadCommandInput(
                url="https://www.youtube.com/watch?v=demo",
                quality="1",
                format_choice="mp3",
                cookies_dir=str(cookies_dir),
                output_dir=output_dir,
            )
        )

        assert spec.command[:3] == [sys.executable, "-m", "yt_dlp"]
        assert "--extract-audio" in spec.command
        assert "--audio-format" in spec.command
        assert "--cookies" in spec.command
        assert str(cookie_file) in spec.command
        assert spec.output_dir == output_dir
    finally:
        cookie_file.unlink(missing_ok=True)
        shutil.rmtree(cookies_dir, ignore_errors=True)


@pytest.mark.parametrize(
    ("platform", "url", "format_choice", "expected_module", "output_fragment"),
    [
        ("instagram", "https://www.instagram.com/openai/p/demo/", "mp4", "gallery_dl", "openai_instagram"),
        ("twitter", "https://x.com/openai/status/123", "mp4", "gallery_dl", "openai_twitter"),
        ("pinterest", "https://www.pinterest.com/pin/123", "png", "gallery_dl", "pinterest"),
        ("spotify", "https://open.spotify.com/track/123", "mp3", "spotdl", "spotify"),
    ],
)
def test_platform_adapter_builds_expected_command(platform: str, url: str, format_choice: str, expected_module: str, output_fragment: str):
    adapter = PLATFORM_ADAPTERS[platform]

    spec = adapter.build_command(
        DownloadCommandInput(
            url=url,
            quality="1",
            format_choice=format_choice,
            cookies_dir=None,
            output_dir=None,
        )
    )

    assert spec.command[:3] == [sys.executable, "-m", expected_module]
    assert output_fragment in spec.output_dir


def test_tiktok_adapter_builds_video_command_with_extractor_args():
    adapter = PLATFORM_ADAPTERS["tiktok"]
    output_dir = str(Path.cwd() / "downloads" / "tiktok-adapter-test")

    spec = adapter.build_command(
        DownloadCommandInput(
            url="https://www.tiktok.com/@demo/video/123",
            quality="2",
            format_choice="mp4",
            cookies_dir=None,
            output_dir=output_dir,
        )
    )

    assert spec.command[:3] == [sys.executable, "-m", "yt_dlp"]
    assert "--extractor-args" in spec.command
    assert "tiktok:api_hostname=api22-normal-c-useast2a.tiktokv.com" in spec.command
    assert spec.output_dir == output_dir


@pytest.mark.parametrize(
    ("platform", "url"),
    [
        ("youtube", "https://example.com/video"),
        ("tiktok", "https://example.com/video"),
        ("instagram", "https://example.com/video"),
        ("twitter", "https://example.com/video"),
        ("pinterest", "https://example.com/video"),
        ("spotify", ""),
    ],
)
def test_stream_platform_download_emits_invalid_platform_input(platform: str, url: str):
    adapter = PLATFORM_ADAPTERS[platform]

    events = list(
        adapters.stream_platform_download(
            adapter,
            DownloadCommandInput(url=url),
        )
    )

    assert len(events) == 1
    assert '"status":"error"' in events[0]
    assert '"code":"invalid_platform_input"' in events[0]
