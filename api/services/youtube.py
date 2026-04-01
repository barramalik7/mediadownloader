from .adapters import DownloadCommandInput, stream_platform_download
from .registry import PLATFORM_ADAPTERS

def download_youtube(url: str, quality: str = "1", format_choice: str = "mp4", cookies_dir: str = None, output_dir: str = None):
    """Download media from YouTube using yt-dlp."""
    yield from stream_platform_download(
        PLATFORM_ADAPTERS["youtube"],
        DownloadCommandInput(
            url=url,
            quality=quality,
            format_choice=format_choice,
            cookies_dir=cookies_dir,
            output_dir=output_dir,
        ),
    )
