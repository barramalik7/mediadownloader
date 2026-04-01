# Product Requirements Document (PRD)

## 1. Introduction
**Product Name:** Media Downloader  
**Version:** 2.0  
**Purpose:** A local web application to download videos, images, and audio from popular social media platforms without watermarks and in high quality.

## 2. Problem Statement
Users need to archive or reuse media from social platforms. Existing tools are cluttered with ads, compress quality, or require CLI proficiency. This tool provides a clean UI backed by powerful Python engines.

## 3. Goals & Objectives
- **Simplicity:** One-page interface for media downloads.
- **Quality:** Highest available quality (up to 4K).
- **Versatility:** Support YouTube, TikTok, Instagram, Twitter/X, Pinterest, Spotify.
- **Flexibility:** Extract audio (MP3) from video sources or download images/galleries.
- **Privacy:** Fully local execution — no data leaves the user's machine.
- **Clarity:** Typed frontend boundaries for form state and streamed download events.
- **Operability:** Surface local runtime readiness through health and preflight diagnostics.

## 4. Target Audience
- Content creators, data archivists, and general users saving media for offline use.

## 5. Tech Stack
- **Frontend:** React 18, Vite, TanStack Start, Tailwind CSS.
- **Backend:** FastAPI (Python), Pydantic, Uvicorn.
- **Download Engines:** `yt-dlp`, `gallery-dl`, `spotdl` (with Python-version caveat).
- **API Contract:** FastAPI endpoints with streamed progress events over SSE plus local readiness diagnostics.

## 6. Functional Requirements

### 6.1 Content Downloading
- Paste a URL from any supported platform.
- Auto-detect the platform from the URL.
- Choose video quality (Best, 1080p, 720p, 480p).
- Choose output format (MP4, MP3, or original Image/Gallery).
- **Automation:** One-click application launcher (`run_app.bat`) for Windows users.

### 6.2 System Feedback
- Loading spinner during download.
- Streaming progress updates during download.
- Success message on completion.
- Specific error messages on failure.
- Actionable startup/dependency messaging when the backend or local runtime is degraded.

## 7. Future Enhancements
- [ ] Download History UI.
- [ ] Batch downloading (playlists/profiles).
- [ ] Custom download location via UI settings.
- [ ] Browser-level E2E coverage for the full local download flow.
