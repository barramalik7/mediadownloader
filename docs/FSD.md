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
  - **Format Selector:** Dropdown (MP4 / MP3).
  - **Download Button:** Shows spinner while loading.
- **Status Area:** Success (green) or Error (red) messages below the form.

## 3. System Components & Logic

### 3.1 Frontend (React + Vite + TanStack Start)
- **Framework:** TanStack Start (SSR) with file-based routing.
- **Component:** `DownloaderForm.tsx` manages form state via `useState` and handles SSE streams.
- **Submission:** Uses native `fetch` to call `/api/download/` (proxy to backend).
- **Payload:**
  ```json
  { "url": "https://...", "quality": "1", "format": "mp4" }
  ```
- **Platform detection** is handled automatically by the backend.

### 3.2 Backend API (FastAPI)
- **Endpoint:** `POST /api/download/`
- **Platform Detection:** The router auto-detects the platform from the URL domain (e.g., `youtube.com` → YouTube service).
- **Service Dispatch:** Routes to one of 6 service modules in `api/services/`.
- **Streaming:** Progress updates are streamed back to the client via Server-Sent Events (SSE).
- **Each service:**
  1. Resolves the output directory via `get_downloads_dir()`.
  2. Finds cookies via `find_cookie()`.
  3. Builds the CLI command (`yt-dlp`, `gallery-dl`, or `spotdl`).
  4. Executes via `run_download_command()` and returns a `DownloadResponse`.

## 4. Workflows

### 4.1 Successful Download
1. User pastes URL → Clicks "Start Download".
2. Frontend sends POST to `/api/download/`.
3. Backend detects platform → Dispatches to service.
4. Service downloads file to `downloads/{platform}/`.
5. Progress updates are streamed via SSE to the frontend.
6. Returns `{ success: true, message: "Download successful" }`.
7. Frontend shows green success message and 100% progress.

### 4.2 Invalid URL
1. Backend cannot match domain to any platform.
2. Returns `400 Bad Request: "Unsupported platform or invalid URL"`.
3. Frontend shows red error message.

### 4.3 Download Error
1. Platform matched, but download fails (private/deleted content).
2. Service returns `{ success: false, error: "..." }`.
3. Backend raises `500 Internal Server Error` with detail.
4. Frontend shows error detail.
