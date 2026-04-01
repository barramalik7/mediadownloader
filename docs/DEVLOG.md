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
- **Frontend:** Migrated from Next.js to **Vite + TanStack Router**.
  - Created `web-client/` directory.
  - Built `DownloaderForm` around native `fetch` and streamed progress updates.
  - Created reusable UI components (Button, Card, Input, Select, Label).

### QC & Cleanup
- **Deleted:** `web/` (old Next.js), `scripts/` (old Python scripts), `run.bat`, `characterWorkflow.ts`, `system_prompt_personalized.md`, root `requirements.txt`.
- **DRY refactor:** Created `api/utils/helpers.py` with shared functions for download directories, cookie lookup, and subprocess streaming, reducing repeated boilerplate across platform services.
- **Fixed:** Removed unused `import os` from `main.py`, stale `localhost:3000` CORS origin, `as any` type casts in frontend.
- **Router refactor:** Extracted platform detection into `detect_platform()` function and used a dispatch map instead of if/elif chain.
- **Updated:** `.gitignore`, `README.md`, all docs (`PRD`, `FSD`, `TSD`, `DEVLOG`, `TASK_LIST`).

### Tech Debt Resolved
- Removed Node.js → Python process spawning overhead.
- Added missing `__init__.py` files for all Python packages.

## [2026-02-12] Migration to TanStack Start (SSR)
- **Architecture:** Migrated from CSR (TanStack Router) to SSR (TanStack Start).
- **Frontend Runtime:** Updated the TanStack Start server entry to use `createStartHandler` with `defaultStreamHandler`.
- **Frontend:**
  - Replaced `main.tsx` with `entry-client.tsx` (hydration) and `router.tsx` (router factory).
  - Updated `__root.tsx` to handle document streaming (`HeadContent`, `Scripts`).
  - Fixed `localStorage` SSR crash in `ThemeProvider`.
  - Added `notFoundComponent` to root route.
- **Cleanup:**
  - Removed unused generated client and React Query wiring.
  - Wired `DownloaderForm` to use relative `/api` paths (via Vite proxy).
  - Removed `index.html`.
- **Verification:** Verified dev server, browser rendering, and production build.

## [2026-02-12] Bug Fixes: Error Handling & Streaming
- **Backend (Critical):** Fixed generator delegation bug in all services (`tiktok.py`, `youtube.py`, etc.). Changed `return stream_download_command(cmd)` to `yield from ...` to correctly stream output.
- **Frontend:** Fixed logic where backend errors were being swallowed by a stream-parsing path. Errors now bubble up correctly to the UI.
- **Result:** "Connection closed unexpectedly" errors are now replaced by actual error messages (e.g., "Download failed", "ffmpeg not found").

## [2026-03-29] Frontend Cleanup and Boundary Refactor
- **Tooling:** Added ESLint flat config for ESLint v9 and introduced Vitest + Testing Library for frontend smoke tests.
- **Architecture:** Removed unused React Query and OpenAPI client tooling from the frontend stack while keeping TanStack Start for routing and SSR.
- **Feature Refactor:** Split `DownloaderForm` into a UI component, a download service, and a dedicated hook for stream orchestration and UI state.
- **Runtime Entry:** Replaced the stale `src/app.tsx` server entry with `src/server.ts`.
- **Docs:** Updated frontend descriptions so they match the current fetch/SSE-based implementation instead of an unused generated client flow.

## [2026-03-29] Backend Contract Hardening
- **Validation:** Tightened backend request validation by moving download URLs to `HttpUrl`.
- **Service Contract:** Standardized all download services on SSE output, including invalid-input handling for Spotify.
- **Diagnostics:** Added `/api/health` and `/api/health/preflight` for local runtime readiness checks.
- **Runtime:** Restricted the backend launcher/start instructions to `127.0.0.1` to match the local-only posture.
- **Testing:** Added pytest coverage for request validation, router behavior, health endpoints, and SSE streaming.
- **Python 3.14 Compatibility:** Marked `spotdl` as unavailable on Python 3.14 in dependency management so setup can succeed while preflight reports the degraded Spotify capability.

## [2026-03-30] Documentation and Tooling Sync
- **Backend Refactor:** Documented the adapter-registry dispatch model centered on `api/services/adapters.py` and `api/services/registry.py`.
- **Health Diagnostics:** Aligned docs with `HealthResponse` and `PreflightResponse`, including per-check `hint` and `required_for`.
- **Frontend Boundaries:** Updated docs to describe `DownloaderForm`, `useDownloadFlow()`, and `downloadMediaStream()` as separate concerns backed by typed stream events.
- **Verification:** Added repo-accurate instructions for backend pytest, frontend Vitest, production build, and manual smoke testing.
- **Cleanup:** Corrected stale references to removed files, older generated-client language, and outdated cookie filename guidance.
