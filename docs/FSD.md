# Functional Specification Document (FSD)

## 1. Overview
This document details the functional behavior of the Media Downloader, covering UI interactions and backend processing logic.

## 2. User Interface
### 2.1 Main Page (`/`)
- **Header:** Sticky header with app branding and download icon.
- **Hero Section:** Title and description.
- **Download Form (Card):**
  - **URL Input:** Text field for pasting the media link.
  - **Quality Selector:** Dropdown (Best, 1080p, 720p, 480p).
  - **Format Selector:** Dropdown (MP4 / MP3 / JPG / PNG).
  - **Launcher:** Windows users can use `run_app.bat` for automatic setup and launch.
  - **Download Button:** Shows spinner while loading.
- **Status Area:** Progress bar during active download, plus success (green) or error (red) messages below the form.

## 3. System Components & Logic

### 3.1 Frontend (React + Vite + TanStack Start)
- **Framework:** TanStack Start (SSR) with file-based routing.
- **Component:** `DownloaderForm.tsx` focuses on rendering the form and status UI.
- **Hook:** `useDownloadFlow()` manages form state, progress, success, and error transitions.
- **Service:** `downloadMediaStream()` handles `fetch` and SSE decoding before emitting typed events to the hook.
- **Submission:** Uses native `fetch` to call `/api/download/` (proxy to backend).
- **Payload:**
  ```json
  { "url": "https://...", "quality": "1", "format": "mp4" }
  ```
- **Platform detection** is handled automatically by the backend.

### 3.2 Backend API (FastAPI)
- **Endpoint:** `POST /api/download/`
- **Health Endpoints:** `GET /api/health` and `GET /api/health/preflight`
- **Platform Detection:** The router auto-detects the platform from the URL domain (e.g., `youtube.com` → YouTube service).
- **Service Dispatch:** Routes through a platform adapter registry in `api/services/registry.py`.
- **Streaming:** Progress updates are streamed back to the client via Server-Sent Events (SSE).
- **Validation:** Request URLs are validated as real URLs before platform dispatch.
- **Each adapter flow:**
  1. Resolves the output directory via shared helper logic.
  2. Finds cookies via `find_cookie()`.
  3. Builds the CLI command (`yt-dlp` for video/audio, `gallery-dl` for images/galleries, or `spotdl` for music).
  4. Executes via streamed subprocess output and emits a consistent SSE event contract.

### 3.3 Runtime Diagnostics
- `/api/health` confirms that the API process is alive.
- `/api/health/preflight` reports whether local runtime prerequisites are available, including Python path, downloader modules, `ffmpeg`, and access to `cookies/` and `downloads/`.
- A degraded preflight status is expected when an optional dependency is unavailable for the current interpreter, such as `spotdl` on Python 3.14.

## 4. Workflows

### 4.1 Successful Download
1. User pastes URL → Clicks "Start Download".
2. Frontend sends POST to `/api/download/`.
3. Backend detects platform → Dispatches to service.
4. Service downloads file to `downloads/{platform}/`.
5. Progress updates are streamed via SSE to the frontend.
6. Backend emits a final `{ "status": "completed", "message": "Download successful" }` event.
7. Frontend shows green success message and 100% progress.

### 4.2 Invalid URL
1. A malformed or non-URL payload fails request validation.
2. FastAPI returns `422` before the stream starts.
3. Frontend shows the validation failure message.

### 4.3 Unsupported Platform
1. Request URL passes schema validation but backend cannot match the host to a supported platform.
2. Backend returns `400 Bad Request: "Unsupported platform or invalid URL"`.
3. Frontend shows red error message.

### 4.4 Download Error
1. Platform matched, but download fails (private/deleted content).
2. Service emits an SSE error event or the endpoint returns an immediate HTTP error.
3. Frontend maps the failure into the error state.
4. Frontend shows the error detail.

### 4.5 Startup or Runtime Degradation
1. Frontend cannot start the download request, or the backend stream cannot be established.
2. Frontend requests `/api/health/preflight`.
3. If backend is degraded, frontend surfaces the first failing check hint in the error message.
4. If backend is unreachable, frontend falls back to a generic proxy/backend-unreachable message.
