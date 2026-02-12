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
- **Frontend:** React, Vite, TanStack Router, TanStack Query, Tailwind CSS, Shadcn UI.
- **Backend:** FastAPI, Pydantic, Uvicorn.
- **Supported Platforms:** YouTube, TikTok, Instagram, Twitter/X, Pinterest, Spotify.
- **Type Safety:** End-to-end type safety with generated API clients.

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

Simply run the `run_app.bat` script in the root directory.
This will launch both the backend (port 8000) and frontend (port 5173).

- Frontend: [http://localhost:5173](http://localhost:5173)
- API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## Project Structure

- `api/`: FastAPI backend service.
  - `services/`: Core logic for each platform downloader.
  - `routers/`: API endpoints.
- `web-client/`: Vite + React frontend.
  - `src/routes/`: File-based routing.
  - `src/client/`: Generated API client.
- `downloads/`: Directory where media is saved.

## Usage

### Quick Start (Windows)
Double-click the `run.bat` file in the project root. This will:
1. Navigate to the web directory.
2. Start the Next.js development server.
3. Keep the window open for logs.

Open your browser to `http://localhost:3000`.

### Manual Start
1. Open a terminal in the `web` directory.
2. Run:
   ```bash
   npm run dev
   ```
3. Visit `http://localhost:3000`.

## Documentation
Detailed documentation is available in the `docs` folder:
- [Product Requirements (PRD)](docs/PRD.md)
- [Functional Specs (FSD)](docs/FSD.md)
- [Technical Specs (TSD)](docs/TSD.md)
- [Developer Log (DEVLOG)](docs/DEVLOG.md)

## Troubleshooting
- **Download Fails?** Check the terminal window running the app for detailed Python error logs.
- **"Python not found"?** Ensure Python is installed and added to your system PATH.
- **Cookies Error?** Some platforms (like YouTube premium content) require cookies. Place your `youtube.com_cookies.txt` in the `cookies/` directory.
