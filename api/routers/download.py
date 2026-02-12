from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from ..models.schemas import DownloadRequest, DownloadResponse
from ..services import youtube, tiktok, instagram, twitter, spotify, pinterest
from ..utils.helpers import get_cookies_dir

router = APIRouter()

# Platform detection map
PLATFORM_DETECTORS = [
    ("tiktok.com", "tiktok"),
    ("instagram.com", "instagram"),
    ("twitter.com", "twitter"),
    ("x.com", "twitter"),
    ("youtube.com", "youtube"),
    ("youtu.be", "youtube"),
    ("pinterest.com", "pinterest"),
    ("pin.it", "pinterest"),
    ("spotify.com", "spotify"),
]


from urllib.parse import urlparse

def detect_platform(url: str) -> str | None:
    """Detect the platform from a URL using strict hostname validation."""
    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            return None
            
        hostname = parsed.netloc.lower()
        if hostname.startswith("www."):
            hostname = hostname[4:]
            
        for domain, platform in PLATFORM_DETECTORS:
            if hostname == domain or hostname.endswith("." + domain):
                return platform
        return None
    except Exception:
        return None



@router.post("/")
async def download_media(request: DownloadRequest):
    """Download media from supported platforms."""
    platform = detect_platform(request.url)

    if not platform:
        raise HTTPException(status_code=400, detail="Unsupported platform or invalid URL")

    cookies_dir = get_cookies_dir()

    # Dispatch to appropriate service
    service_map = {
        "youtube": lambda: youtube.download_youtube(request.url, request.quality, request.format, cookies_dir),
        "tiktok": lambda: tiktok.download_tiktok(request.url, request.quality, request.format, cookies_dir),
        "instagram": lambda: instagram.download_instagram(request.url, cookies_dir),
        "twitter": lambda: twitter.download_twitter(request.url, cookies_dir),
        "spotify": lambda: spotify.download_spotify(request.url),
        "pinterest": lambda: pinterest.download_pinterest(request.url, cookies_dir),
    }

    return StreamingResponse(service_map[platform](), media_type="text/event-stream")
