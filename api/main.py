from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import download

app = FastAPI(
    title="Media Downloader API",
    description="Backend API for downloading media from various platforms",
    version="1.0.0"
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
