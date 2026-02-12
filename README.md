# Media Downloader

A premium, local-first web interface for downloading high-quality videos and audio from TikTok, YouTube, Instagram, Twitter, and Spotify without watermarks.

![Media Downloader UI](https://placehold.co/600x400?text=Media+Downloader+UI)

## Features
- **Zero Watermarks:** Clean downloads from TikTok and Instagram.
- **High Quality:** Support for up to 1080p+ video resolution.
- **Audio Extraction:** Convert any video to high-quality MP3.
- **Multi-Platform:** Support for:
  - TikTok
  - Instagram (Reels & Posts)
  - YouTube (Video & Audio)
  - Twitter / X
  - Pinterest
  - Spotify
- **Frontend:** React, Vite, TanStack Start (SSR), TanStack Query, Tailwind CSS, Shadcn UI.
- **Backend:** FastAPI, Pydantic, Uvicorn.
- **Supported Platforms:** YouTube, TikTok, Instagram, Twitter/X, Pinterest, Spotify.
- **Type Safety:** End-to-end type safety.

## Getting Started

### Prerequisites
- Node.js (v18+)
- Python (v3.10+)
- FFmpeg (for media processing)

### Installation

1.  **Backend Setup**
    ```bash
    pip install -r api/requirements.txt
    ```

2.  **Frontend Setup**
    ```bash
    cd web-client
    npm install
    cd ..
    ```

### Running the App

1.  **Start the Backend**
    ```bash
    # From project root
    python -m uvicorn api.main:app --reload --port 8000
    ```

2.  **Start the Frontend**
    ```bash
    # From web-client directory
    cd web-client
    npm run dev
    ```

- Frontend: [http://localhost:5173](http://localhost:5173)
- API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## Project Structure

- `api/`: FastAPI backend service.
  - `routers/`: API endpoints.
- `web-client/`: TanStack Start (SSR) frontend.
  - `src/routes/`: File-based routing (`__root.tsx`, `index.tsx`).
  - `src/app.tsx`: Server entry point.
  - `src/entry-client.tsx`: Client hydration.
- `downloads/`: Directory where media is saved.

## Documentation
Detailed documentation is available in the `docs` folder:
- [Product Requirements (PRD)](docs/PRD.md)
- [Functional Specs (FSD)](docs/FSD.md)
- [Technical Specs (TSD)](docs/TSD.md)
- [Developer Log (DEVLOG)](docs/DEVLOG.md)

## Authentication (Cookies)
Some platforms (YouTube Premium, Age-gated content, Instagram, Twitter) require cookies to verify your identity and avoid rate limits.

### How to get cookies:
1.  Install the **"Get cookies.txt LOCALLY"** extension for [Chrome](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflccgomhhjfcah) or [Firefox](https://addons.mozilla.org/en-US/firefox/addon/get-cookies-txt-locally/).
2.  **Login** to the platform (e.g., `www.youtube.com`) in your browser.
3.  Click the extension icon and select **"Export"** (ensure "Netscape HTTP Cookie File" format is selected/default).
4.  Save the file to the `cookies/` folder in this project root.
5.  **Rename the file** exactly as follows:
    - YouTube: `youtube.com_cookies.txt`
    - Instagram: `instagram.com_cookies.txt`
    - Twitter/X: `twitter.com_cookies.txt`
    - TikTok: `tiktok.com_cookies.txt`
    - Spotify: `spotify.com_cookies.txt`

## Troubleshooting
- **Download Fails?** Check the terminal window running the app for detailed Python error logs.
- **"Python not found"?** Ensure Python is installed and added to your system PATH.
- **"ffmpeg not found"?** Install FFmpeg and add it to your system PATH. This is required for MP3 conversion and some video formats.
- **Cookies Error?** Some platforms (like YouTube premium content) require cookies. Place your `youtube.com_cookies.txt` in the `cookies/` directory.
- **"Connection closed unexpectedly"?** This usually means the backend crashed or exited early. Check the backend terminal for error details.
