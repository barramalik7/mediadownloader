# Technical Specification Document (TSD)

## 1. System Architecture
The application uses a decoupled frontend-backend architecture with a typed API contract, now utilizing **TanStack Start** for Server-Side Rendering (SSR).

### 1.1 Stack
| Layer | Technology |
|---|---|
| **Frontend** | React 18, Vite, TanStack Start (SSR), TanStack Query, Tailwind CSS |
| **Backend** | FastAPI (Python), Pydantic, Uvicorn |
| **API Interaction** | Native `fetch` with Vite proxy to FastAPI backend |
| **Download Engines** | `yt-dlp` (Video/Audio), `gallery-dl` (Images/Galleries), `spotdl` (Spotify) |

## 2. Directory Structure
```
/
├── api/                    # FastAPI Backend
│   ├── main.py             # App entry, CORS config
│   ├── requirements.txt    # Python dependencies
│   ├── routers/
│   │   └── download.py     # POST /api/download/ endpoint
│   ├── services/           # Platform-specific download logic
│   └── utils/
│       └── helpers.py      # Shared logic
├── web-client/             # Vite + React (TanStack Start) Frontend
│   ├── src/
│   │   ├── app.tsx         # Server entry point
│   │   ├── entry-client.tsx # Client hydration entry
│   │   ├── router.tsx      # Router factory
│   │   ├── routes/         # File-based routes (__root.tsx, index.tsx)
│   │   ├── components/     # UI components
│   │   └── lib/            # Utilities
│   ├── package.json
│   └── vite.config.ts      # Vite config with TanStack Start plugin & Proxy
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
| `GET` | `/api/download/` | (SSE) Stream progress updates |

### 3.2 Request Model (`DownloadRequest`)
```python
class DownloadRequest(BaseModel):
    url: str
    quality: Optional[str] = "1"        # "1"=Best, "2"=1080p, "3"=720p, "4"=480p
    format: Optional[Literal["mp4", "mp3", "jpg", "png"]] = "mp4"
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
User → DownloaderForm (React) → native fetch() → Vite Proxy
  → POST /api/download/ (FastAPI)
    → detect_platform(url)
    → service.download_{platform}(url, ...)
      → Stream SSE events (progress)
      → subprocess.run(...)
      → file saved to downloads/{platform}/
    → DownloadResponse → Frontend → UI update
```

## 5. Key Dependencies

### Python (`api/requirements.txt`)
- `fastapi`, `uvicorn`, `pydantic`
- `yt-dlp[curl-cffi]`, `gallery-dl`, `spotdl`, `Pillow`

### Node.js (`web-client/package.json`)
- `@tanstack/react-start`, `@tanstack/react-router`, `@tanstack/react-query`
- `@tanstack/react-router-devtools`, `@tanstack/react-query-devtools`
- `tailwindcss`, `lucide-react`, `class-variance-authority`

## 6. Security & Constraints
- **Local Execution Only:** The app runs entirely on localhost. Do not deploy to serverless platforms.
- **CORS:** Restricted to `http://localhost:5173` (Vite dev server).
- **Cookies:** Stored in `/cookies` for authenticated platform access.
