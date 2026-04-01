# Technical Specification Document (TSD)

## 1. System Architecture
The application uses a decoupled frontend-backend architecture and utilizes **TanStack Start** for Server-Side Rendering (SSR).

### 1.1 Stack
| Layer | Technology |
|---|---|
| **Frontend** | React 18, Vite, TanStack Start (SSR), Tailwind CSS |
| **Backend** | FastAPI (Python), Pydantic, Uvicorn |
| **API Interaction** | Native `fetch` with Vite proxy to FastAPI backend, plus preflight diagnostics fallback |
| **Download Engines** | `yt-dlp` (Video/Audio), `gallery-dl` (Images/Galleries), `spotdl` (Spotify, Python < 3.14) |
| **Frontend Tooling** | ESLint v9 flat config, Vitest, Testing Library |
| **Backend Tooling** | pytest, httpx, `api/requirements-dev.txt` |

## 2. Directory Structure
```
/
├── api/                    # FastAPI Backend
│   ├── main.py             # App entry, CORS config
│   ├── requirements.txt    # Runtime Python dependencies
│   ├── requirements-dev.txt # Backend test dependencies
│   ├── models/
│   │   └── schemas.py      # Request, stream event, and health schemas
│   ├── routers/
│   │   └── download.py     # POST /api/download/ endpoint
│   ├── services/
│   │   ├── adapters.py     # Platform adapters + command builders
│   │   └── registry.py     # Shared adapter registry
│   └── utils/
│       └── helpers.py      # SSE helpers, subprocess streaming, preflight checks
├── web-client/             # Vite + React (TanStack Start) Frontend
│   ├── src/
│   │   ├── server.ts       # Server entry point
│   │   ├── entry-client.tsx # Client hydration entry
│   │   ├── router.tsx      # Router factory
│   │   ├── routes/         # File-based routes (__root.tsx, index.tsx)
│   │   ├── components/     # UI components
│   │   ├── features/
│   │   │   └── download/   # Stream client, reducer, tests, typed events
│   │   ├── test/           # Vitest setup
│   │   └── lib/            # Utilities
│   ├── package.json        # Frontend deps and scripts
│   ├── eslint.config.js    # ESLint v9 flat config
│   ├── vitest.config.ts    # Frontend test runner config
│   └── vite.config.ts      # Vite config with TanStack Start plugin & Proxy
├── scripts/
│   ├── manual_smoke.py     # Manual smoke runner against live URLs
│   └── smoke-urls.example.json
├── tests/                  # Backend route, contract, and adapter tests
├── cookies/                # Platform cookie files
├── downloads/              # Downloaded media output
├── docs/                   # Project documentation
├── pytest.ini              # Backend pytest discovery config
├── run_app.bat             # Launch script (both servers)
└── README.md
```

## 3. API Specification

### 3.1 Endpoints
| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Basic API banner |
| `GET` | `/api/health` | Lightweight health check |
| `GET` | `/api/health/preflight` | Runtime readiness checks with integration hints for local dependencies |
| `POST` | `/api/download/` | Returns a `text/event-stream` response with download progress events |

### 3.2 Request Model (`DownloadRequest`)
```python
class DownloadRequest(BaseModel):
    url: HttpUrl
    quality: Optional[str] = "1"        # "1"=Best, "2"=1080p, "3"=720p, "4"=480p
    format: Optional[Literal["mp4", "mp3", "jpg", "png"]] = "mp4"
```

### 3.3 Stream Event Contract
```json
{ "status": "downloading", "progress": 42, "log": "Downloading..." }
{ "status": "completed", "progress": 100, "message": "Download successful" }
{ "status": "error", "message": "Download failed" }
```

### 3.4 Error Boundary
- `422`: request body/schema invalid, stream never starts
- `400`: URL valid but platform unsupported, stream never starts
- `200 text/event-stream`: request accepted and stream starts; any runtime failure after that is emitted as a terminal `error` event
- Valid stream lifecycle: zero or more `downloading` events followed by exactly one `completed` or `error` event

### 3.5 Integration Diagnostics
- Frontend uses relative `/api` requests and relies on Vite dev proxy for local backend routing.
- Vite proxy target is configurable through `VITE_BACKEND_TARGET`; default remains `http://127.0.0.1:8000`.
- When the initial download request cannot start, frontend falls back to `/api/health/preflight` to distinguish:
  - backend/proxy unreachable
  - backend reachable but runtime dependencies degraded
- `PreflightResponse` includes:
  - `status`
  - `status_message`
  - `checks.<name>.ok`
  - `checks.<name>.value`
  - `checks.<name>.hint`
  - `checks.<name>.required_for`

## 4. Data Flow
```
User → DownloaderForm (React UI) → useDownloadFlow() → downloadMediaStream()
  → native fetch() → Vite Proxy
  → POST /api/download/ (FastAPI)
    → if startup request fails: GET /api/health/preflight for actionable diagnostics
    → detect_platform(url)
    → PLATFORM_ADAPTERS[platform]
    → stream_platform_download(...)
      → Stream SSE events via helper serializers
      → subprocess.Popen(...)
      → file saved to downloads/{platform}/
    → stream events → frontend state update
```

## 5. Key Dependencies

### Python (`api/requirements.txt`)
- `fastapi`, `uvicorn`, `pydantic`
- `yt-dlp[curl-cffi]`, `gallery-dl`, `spotdl` (Python < 3.14), `Pillow`
- Dev/test tooling lives in `api/requirements-dev.txt`

### Node.js (`web-client/package.json`)
- `@tanstack/react-start`, `@tanstack/react-router`
- `@tanstack/react-router-devtools`
- `tailwindcss`, `lucide-react`, `class-variance-authority`
- `vitest`, `@testing-library/react`, `@testing-library/jest-dom`
- `eslint`, `typescript-eslint`, `eslint-plugin-react-hooks`, `eslint-plugin-react-refresh`

## 6. Security & Constraints
- **Local Execution Only:** The app runs entirely on localhost. Do not deploy to serverless platforms.
- **CORS:** Restricted to `http://localhost:5173` (Vite dev server).
- **Backend Bind Address:** Use `127.0.0.1` for local startup.
- **Cookies:** Stored in `/cookies` for authenticated platform access.
- **Manual Smoke Checks:** Live third-party integration checks are run manually via `scripts/manual_smoke.py`, not in the automated suite.

## 7. Verification
- Backend automated verification: `python -m pytest -q`
- Frontend automated verification:
  - `npm test`
  - `npm run build`
- Manual live-platform verification: `python scripts/manual_smoke.py`
