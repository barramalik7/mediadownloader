import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api.routers import download
from api.models.schemas import HealthResponse, PreflightResponse
from api.utils.helpers import get_preflight_status

logger = logging.getLogger("mediadownloader.startup")


@asynccontextmanager
async def lifespan(app: FastAPI):
    payload = get_preflight_status()
    if payload["status"] != "ok":
        logger.warning("Backend preflight degraded at startup: %s", payload["status_message"])
    yield


app = FastAPI(
    title="Media Downloader API",
    description="Backend API for downloading media from various platforms",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
origins = [
    "http://localhost:5173",  # Vite dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(download.router, prefix="/api/download", tags=["download"])

@app.get("/")
def read_root():
    return {"message": "Media Downloader API is running"}


@app.get("/api/health", response_model=HealthResponse)
def health_check():
    return {"status": "ok"}


@app.get("/api/health/preflight", response_model=PreflightResponse)
def health_preflight():
    payload = get_preflight_status()
    status_code = 200 if payload["status"] == "ok" else 200
    return JSONResponse(content=payload, status_code=status_code)
