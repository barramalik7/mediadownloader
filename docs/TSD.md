# Technical Specification Document (TSD)

## 1. System Architecture
The application uses a decoupled frontend-backend architecture with a typed API contract.

### 1.1 Stack
| Layer | Technology |
|---|---|
| **Frontend** | React 18, Vite, TanStack Router, TanStack Query, Tailwind CSS |
| **Backend** | FastAPI (Python), Pydantic, Uvicorn |
| **API Contract** | OpenAPI 3.0 (auto-generated), `@hey-api/openapi-ts` (client generation) |
| **Download Engines** | `yt-dlp` (YouTube, TikTok), `gallery-dl` (Instagram, Twitter, Pinterest), `spotdl` (Spotify) |

## 2. Directory Structure
```
/
├── api/                    # FastAPI Backend
│   ├── main.py             # App entry, CORS config
│   ├── requirements.txt    # Python dependencies
│   ├── routers/
│   │   └── download.py     # POST /api/download/ endpoint
│   ├── services/           # Platform-specific download logic
│   │   ├── youtube.py
│   │   ├── tiktok.py
│   │   ├── instagram.py
│   │   ├── twitter.py
│   │   ├── spotify.py
│   │   └── pinterest.py
│   ├── models/
│   │   └── schemas.py      # Pydantic models (DownloadRequest, DownloadResponse)
│   └── utils/
│       └── helpers.py      # Shared logic (paths, cookies, subprocess)
├── web-client/             # Vite + React Frontend
│   ├── src/
│   │   ├── main.tsx        # App entry
│   │   ├── routes/         # TanStack Router file-based routes
│   │   ├── client/         # Auto-generated API client
│   │   ├── components/     # UI components (Button, Card, Input, Select, Label)
│   │   └── lib/            # Utilities (cn)
│   ├── package.json
│   └── vite.config.ts
├── cookies/                # Platform cookie files
├── downloads/              # Downloaded media output
├── docs/                   # Project documentation
├── run_app.bat             # Launch script (both servers)
└── README.md
```

## 3. API Specification

### 3.1 Endpoints
| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `POST` | `/api/download/` | Download media from URL |

### 3.2 Request Model (`DownloadRequest`)
```python
class DownloadRequest(BaseModel):
    url: str
    quality: Optional[str] = "1"        # "1"=Best, "2"=1080p, "3"=720p, "4"=480p
    format: Optional[Literal["mp4", "mp3"]] = "mp4"
```

### 3.3 Response Model (`DownloadResponse`)
```python
class DownloadResponse(BaseModel):
    success: bool
    message: str
    output: Optional[str] = None
    error: Optional[str] = None
    file_path: Optional[str] = None
```

## 4. Data Flow
```
User → DownloaderForm (React) → useMutation → downloadMediaApiDownloadPost()
  → POST /api/download/ (FastAPI)
    → detect_platform(url)
    → service.download_{platform}(url, ...)
      → subprocess.run([yt-dlp|gallery-dl|spotdl, ...])
      → file saved to downloads/{platform}/
    → DownloadResponse → Frontend → UI update
```

## 5. Key Dependencies

### Python (`api/requirements.txt`)
- `fastapi`, `uvicorn`, `pydantic`
- `yt-dlp[curl-cffi]`, `gallery-dl`, `spotdl`, `Pillow`

### Node.js (`web-client/package.json`)
- `react`, `react-dom`, `@tanstack/react-router`, `@tanstack/react-query`
- `@hey-api/openapi-ts`, `@hey-api/client-fetch`
- `tailwindcss`, `lucide-react`, `class-variance-authority`

## 6. Security & Constraints
- **Local Execution Only:** The app runs entirely on localhost. Do not deploy to serverless platforms.
- **CORS:** Restricted to `http://localhost:5173` (Vite dev server).
- **Cookies:** Stored in `/cookies` for authenticated platform access.
