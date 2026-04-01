from typing import Annotated, Literal, Optional

from pydantic import BaseModel, Field, HttpUrl

class DownloadRequest(BaseModel):
    url: HttpUrl
    quality: Optional[str] = "1"
    format: Optional[Literal["mp4", "mp3", "jpg", "png"]] = "mp4"


DownloadRuntimeErrorCode = Literal[
    "invalid_platform_input",
    "missing_dependency",
    "subprocess_failure",
    "internal_error",
]
DownloadStartErrorCode = Literal["unsupported_platform"]


class DownloadDownloadingEvent(BaseModel):
    status: Literal["downloading"]
    log: Optional[str] = None
    progress: Optional[float] = None


class DownloadCompletedEvent(BaseModel):
    status: Literal["completed"]
    message: str
    progress: Optional[float] = None


class DownloadErrorEvent(BaseModel):
    status: Literal["error"]
    code: DownloadRuntimeErrorCode
    message: str


DownloadStreamEvent = Annotated[
    DownloadDownloadingEvent | DownloadCompletedEvent | DownloadErrorEvent,
    Field(discriminator="status"),
]


class ErrorDetailResponse(BaseModel):
    code: DownloadStartErrorCode
    detail: str


class HealthResponse(BaseModel):
    status: Literal["ok"]


class PreflightCheck(BaseModel):
    ok: bool
    value: Optional[str] = None
    hint: Optional[str] = None
    required_for: Optional[str] = None


class PreflightResponse(BaseModel):
    status: Literal["ok", "degraded"]
    status_message: str
    checks: dict[str, PreflightCheck]
