# Developer Log (DEVLOG)

## 2026-02-12 - Initial Codebase Analysis & Documentation

### Findings
- Architecture: Next.js frontend + Python scripts spawned via `child_process`.
- `yt-dlp` with `curl_cffi` used for browser impersonation.
- Simple `useState` state management in `DownloaderForm.tsx`.
- CSS variables with Tailwind for "glassmorphism" dark theme.

### Decisions
- Created `docs/` folder with PRD, FSD, TSD, DEVLOG, TASK_LIST.

---

## 2026-02-12 - Architecture Refactoring (v2.0)

### Changes
- **Backend:** Migrated from Next.js Route Handlers (Node.js spawning Python) to **FastAPI** (direct Python execution).
  - Created `api/` directory with `services/`, `routers/`, `models/`, `utils/`.
  - Each platform downloader refactored into a service module.
  - Unified `POST /api/download/` endpoint with auto platform detection.
- **Frontend:** Migrated from Next.js to **Vite + TanStack Router + TanStack Query**.
  - Created `web-client/` directory.
  - Generated type-safe API client from OpenAPI spec via `@hey-api/openapi-ts`.
  - Built `DownloaderForm` with `useMutation` for download requests.
  - Created reusable UI components (Button, Card, Input, Select, Label).

### QC & Cleanup
- **Deleted:** `web/` (old Next.js), `scripts/` (old Python scripts), `run.bat`, `characterWorkflow.ts`, `system_prompt_personalized.md`, root `requirements.txt`.
- **DRY refactor:** Created `api/utils/helpers.py` with shared functions (`get_downloads_dir()`, `find_cookie()`, `run_download_command()`), reducing ~50% duplicated code across 6 services.
- **Fixed:** Removed unused `import os` from `main.py`, stale `localhost:3000` CORS origin, `as any` type casts in frontend.
- **Router refactor:** Extracted platform detection into `detect_platform()` function and used a dispatch map instead of if/elif chain.
- **Updated:** `.gitignore`, `README.md`, all docs (`PRD`, `FSD`, `TSD`, `DEVLOG`, `TASK_LIST`).

### Tech Debt Resolved
- Removed Node.js → Python process spawning overhead.
- End-to-end type safety established via OpenAPI contract.
- Added missing `__init__.py` files for all Python packages.

## [2026-02-12] Migration to TanStack Start (SSR)
- **Architecture:** Migrated from CSR (TanStack Router) to SSR (TanStack Start).
- **Backend:** Updated `app.tsx` to use `createStartHandler` with `defaultStreamHandler`.
- **Frontend:**
  - Replaced `main.tsx` with `entry-client.tsx` (hydration) and `router.tsx` (router factory).
  - Updated `__root.tsx` to handle document streaming (`HeadContent`, `Scripts`).
  - Fixed `localStorage` SSR crash in `ThemeProvider`.
  - Wrapped root in `QueryClientProvider` for SSR.
  - Added `notFoundComponent` to root route.
- **Cleanup:**
  - Removed `src/client` (unused generated code).
  - Wired `DownloaderForm` to use relative `/api` paths (via Vite proxy).
  - Removed `index.html`.
- **Verification:** Verified dev server, browser rendering, and production build.

## [2026-02-12] Bug Fixes: Error Handling & Streaming
- **Backend (Critical):** Fixed generator delegation bug in all services (`tiktok.py`, `youtube.py`, etc.). Changed `return stream_download_command(cmd)` to `yield from ...` to correctly stream output.
- **Frontend:** Fixed logic in `DownloaderForm.tsx` where backend errors were being swallowed by a `catch` block intended for JSON parsing. Now backend errors bubble up correctly to the UI.
- **Result:** "Connection closed unexpectedly" errors are now replaced by actual error messages (e.g., "Download failed", "ffmpeg not found").
