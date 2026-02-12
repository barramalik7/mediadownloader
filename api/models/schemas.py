from pydantic import BaseModel, HttpUrl
from typing import Optional, Literal

class DownloadRequest(BaseModel):
    url: str
    quality: Optional[str] = "1"
    format: Optional[Literal["mp4", "mp3"]] = "mp4"

class DownloadResponse(BaseModel):
    success: bool
    message: str
    output: Optional[str] = None
    error: Optional[str] = None
    file_path: Optional[str] = None
