from .adapters import DownloadCommandInput, stream_platform_download
from .registry import PLATFORM_ADAPTERS

def download_spotify(url: str, output_dir: str = None):
    """Download music from Spotify using spotdl."""
    yield from stream_platform_download(
        PLATFORM_ADAPTERS["spotify"],
        DownloadCommandInput(
            url=url,
            output_dir=output_dir,
        ),
    )
