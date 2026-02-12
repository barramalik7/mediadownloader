@echo off
TITLE Media Downloader Launcher

echo Starting Backend Server...
start "Media Downloader Backend" cmd /k "call .venv\Scripts\activate.bat 2>nul & python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload"

echo Starting Frontend Server...
start "Media Downloader Frontend" cmd /k "cd web-client & npm run dev"

echo.
echo Application is starting...
echo Frontend will be available at: http://localhost:5173
echo Backend API is available at: http://localhost:8000/docs
echo.
echo Press any key to exit this launcher (servers will keep running)...
pause >nul
