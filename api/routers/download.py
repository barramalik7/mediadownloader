import logging
from urllib.parse import urlparse

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from fastapi.responses import JSONResponse
from ..models.schemas import DownloadRequest, ErrorDetailResponse
from ..services.adapters import DownloadCommandInput, stream_platform_download
from ..services.registry import PLATFORM_ADAPTERS
from ..utils.helpers import get_cookies_dir

router = APIRouter()
logger = logging.getLogger("mediadownloader.download")

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



STREAM_EXAMPLE = (
    'data: {"status":"downloading","log":"[download] 45.2%","progress":45.2}\n\n'
    'data: {"status":"completed","message":"Download successful","progress":100.0}\n\n'
)


@router.post(
    "/",
    response_class=StreamingResponse,
    responses={
        200: {
            "description": (
                "Server-Sent Events stream. Valid event sequence is zero or more "
                "`downloading` events followed by exactly one terminal `completed` or `error` event."
            ),
            "content": {
                "text/event-stream": {
                    "example": STREAM_EXAMPLE,
                }
            },
        },
        400: {
            "model": ErrorDetailResponse,
            "description": "Request URL is valid but the platform is not supported.",
        },
        422: {
            "description": "Request validation failed.",
        },
    },
)
async def download_media(request: DownloadRequest):
    """Download media from supported platforms."""
    url = str(request.url)
    platform = detect_platform(url)

    if not platform:
        payload = ErrorDetailResponse(code="unsupported_platform", detail="Unsupported platform or invalid URL")
        return JSONResponse(status_code=400, content=payload.model_dump())

    cookies_dir = get_cookies_dir()
    adapter = PLATFORM_ADAPTERS[platform]
    logger.info("download_request_received platform=%s format=%s quality=%s", platform, request.format, request.quality)
    stream = stream_platform_download(
        adapter,
        DownloadCommandInput(
            url=url,
            quality=request.quality,
            format_choice=request.format,
            cookies_dir=cookies_dir,
        ),
    )

    return StreamingResponse(stream, media_type="text/event-stream")
