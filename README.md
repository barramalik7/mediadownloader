# Media Downloader

A premium, local-first web interface for downloading videos, audio, images, and galleries from supported social platforms without routing your media through a third-party service.

![Media Downloader UI](https://placehold.co/600x400?text=Media+Downloader+UI)

## Features
- **Zero Watermarks:** Clean downloads from TikTok and Instagram.
- **High Quality:** Support for up to 1080p+ video resolution.
- **Image & Gallery Downloads:** High-quality image support for Pinterest and Instagram.
- **Audio Extraction:** Convert any video to high-quality MP3.
- **Streamed Progress:** The UI consumes SSE progress events during a live download.
- **Multi-Platform:** Support for:
  - TikTok
  - Instagram (Reels & Posts)
  - YouTube (Video & Audio)
  - Twitter / X
  - Pinterest
  - Spotify
- **Frontend:** React, Vite, TanStack Start (SSR), Tailwind CSS, Shadcn UI.
- **Backend:** FastAPI, Pydantic, Uvicorn.
- **Supported Platforms:** YouTube, TikTok, Instagram, Twitter/X, Pinterest, Spotify.
- **Typed Frontend Boundaries:** Explicit TypeScript types for form state and streamed download events.
- **Diagnostics:** Health and preflight endpoints expose backend readiness for local development.

## Getting Started

### Prerequisites
- Node.js (v18+)
- Python (v3.10+)
- FFmpeg (for media processing)

### Installation

1.  **Backend Setup**
    ```bash
    pip install -r api/requirements.txt
    pip install -r api/requirements-dev.txt
    ```

2.  **Frontend Setup**
    ```bash
    cd web-client
    npm install
    copy .env.example .env
    cd ..
    ```

### Running the App

#### Option 1: Quick Start (Recommended for Windows)
Simply double-click **`run_app.bat`** in the project root. This will automatically:
1.  Start the Backend Server (Port 8000)
2.  Start the Frontend Server (Port 5173)

#### Option 2: Manual Start

1.  **Start the Backend**
    ```bash
    # From project root
    python -m uvicorn api.main:app --host 127.0.0.1 --reload --port 8000
    ```

2.  **Start the Frontend**
    ```bash
    # From web-client directory
    cd web-client
    # Optional: set VITE_BACKEND_TARGET in .env when your backend runs on a non-default local port
    npm run dev
    ```

- Frontend: [http://localhost:5173](http://localhost:5173)
- API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health: [http://localhost:8000/api/health](http://localhost:8000/api/health)
- Preflight: [http://localhost:8000/api/health/preflight](http://localhost:8000/api/health/preflight)

### API Behavior
- `POST /api/download/` streams `text/event-stream` events instead of returning a single JSON payload.
- Valid event flow is `downloading* -> completed` or `downloading* -> error`.
- Invalid request bodies return FastAPI validation errors (`422`) before streaming starts.
- Supported URL validation that passes schema checks but fails platform detection returns `400`.

### Integration Readiness
- The Vite dev proxy target is configurable via `web-client/.env` using `VITE_BACKEND_TARGET`. Default: `http://127.0.0.1:8000`.
- `GET /api/health/preflight` returns runtime readiness diagnostics with a top-level `status_message` plus per-check `hint` and `required_for`.
- A `degraded` preflight means the backend is reachable, but one or more local dependencies or directories are not ready.
- Dependency notes:
  - `ffmpeg`: required for merged video outputs and MP3 conversion
  - `yt-dlp`: required for YouTube, TikTok, and Twitter/X video downloads
  - `gallery-dl`: required for Instagram and Pinterest image/gallery downloads
  - `spotdl`: required for Spotify downloads and currently unsupported on Python 3.14
  - `cookies/`: required for authenticated content on supported platforms

### Verification
Run these commands from the repo root or the `web-client` directory as noted:
```bash
python -m pytest -q
cd web-client
npm test
npm run build
```

### Manual Smoke Checks
1. Copy `scripts/smoke-urls.example.json` to `scripts/smoke-urls.json`.
2. Fill only the sample URLs you want to verify locally.
3. Start backend and frontend normally.
4. Run:
   ```bash
   python scripts/manual_smoke.py
   ```
5. Review the preflight summary and terminal event result per platform.

## Project Structure

- `api/`: FastAPI backend service.
  - `main.py`: App setup, CORS, startup preflight logging, health routes.
  - `models/schemas.py`: Request, SSE event, and preflight response models.
  - `routers/`: API endpoints.
  - `services/adapters.py`: Platform adapter definitions and command builders.
  - `services/registry.py`: Platform adapter registry used by the router.
  - `requirements-dev.txt`: Backend test dependencies.
- `web-client/`: TanStack Start (SSR) frontend.
  - `src/routes/`: File-based routing (`__root.tsx`, `index.tsx`).
  - `src/server.ts`: Server entry point.
  - `src/entry-client.tsx`: Client hydration.
  - `src/features/download/`: Download stream parsing, state machine, and typed events.
  - `src/test/`: Frontend test setup.
  - `eslint.config.js`: ESLint v9 flat config.
  - `vitest.config.ts`: Frontend test runner config.
- `downloads/`: Directory where media is saved.
- `scripts/manual_smoke.py`: Manual end-to-end smoke runner for live platform URLs.
- `tests/`: Backend route, contract, and adapter coverage.
- `pytest.ini`: Backend pytest discovery config.

## Documentation
Detailed documentation is available in the `docs` folder:
- [Product Requirements (PRD)](docs/PRD.md)
- [Functional Specs (FSD)](docs/FSD.md)
- [Technical Specs (TSD)](docs/TSD.md)
- [Developer Log (DEVLOG)](docs/DEVLOG.md)
- [Task List](docs/TASK_LIST.md)

## Authentication (Cookies)
Some platforms (YouTube Premium, Age-gated content, Instagram, Twitter) require cookies to verify your identity and avoid rate limits.

### How to get cookies:
1.  Install the **"Get cookies.txt LOCALLY"** extension for [Chrome](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflccgomhhjfcah) or [Firefox](https://addons.mozilla.org/en-US/firefox/addon/get-cookies-txt-locally/).
2.  **Login** to the platform (e.g., `www.youtube.com`) in your browser.
3.  Click the extension icon and select **"Export"** (ensure "Netscape HTTP Cookie File" format is selected/default).
4.  Save the file to the `cookies/` folder in this project root.
5.  **Rename the file** exactly as follows:
    - YouTube: `youtube.com_cookies.txt`
    - Instagram: `instagram.com_cookies.txt` or `www.instagram.com_cookies.txt`
    - Twitter/X: `twitter.com_cookies.txt` or `x.com_cookies.txt`
    - TikTok: `www.tiktok.com_cookies.txt`
    - Pinterest: `pinterest.com_cookies.txt`

Spotify downloads do not currently read cookie files in the backend, and `spotdl` support is degraded on Python 3.14.

## Troubleshooting
- **Download Fails?** Check the terminal window running the app for detailed Python error logs.
- **"Python not found"?** Ensure Python is installed and added to your system PATH.
- **"ffmpeg not found"?** Install FFmpeg and add it to your system PATH. This is required for MP3 conversion and some video formats.
- **Want to verify runtime readiness?** Open `/api/health/preflight` to see dependency and directory checks.
- **Cookies Error?** Some platforms (like YouTube premium content) require cookies. Place your `youtube.com_cookies.txt` in the `cookies/` directory.
- **"Connection closed unexpectedly"?** This usually means the backend crashed or exited early. Check the backend terminal for error details.
