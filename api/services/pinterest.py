from .adapters import DownloadCommandInput, stream_platform_download
from .registry import PLATFORM_ADAPTERS

def download_pinterest(url: str, format_choice: str = "mp4", cookies_dir: str = None, output_dir: str = None):
    """Download media from Pinterest using gallery-dl."""
    yield from stream_platform_download(
        PLATFORM_ADAPTERS["pinterest"],
        DownloadCommandInput(
            url=url,
            format_choice=format_choice,
            cookies_dir=cookies_dir,
            output_dir=output_dir,
        ),
    )
