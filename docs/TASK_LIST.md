# Project Task List

## Completed
- [x] **v1.0: Initial Build**
    - [x] Analyze codebase structure.
    - [x] Create PRD, FSD, TSD, DEVLOG.
    - [x] Build Next.js frontend + Python scripts.
- [x] **v2.0: Architecture Refactoring**
    - [x] Migrate backend to FastAPI.
    - [x] Migrate frontend to Vite + TanStack.
    - [x] Generate typed API client from OpenAPI.
    - [x] DRY refactor (shared `utils/helpers.py`).
    - [x] Cleanup legacy files (`web/`, `scripts/`, etc.).
    - [x] Update all documentation and `.gitignore`.

## Roadmap & Backlog
- [ ] **Feature: Download History**
    - [ ] Create database/log for tracking downloads.
    - [ ] Build History UI page.
- [ ] **Feature: Batch Downloading**
    - [ ] Support playlist URLs and comma-separated URLs.
- [ ] **UI Improvements**
    - [ ] Real-time progress bar (WebSocket or SSE).
    - [ ] Dark/Light mode toggle.
    - [ ] Enhanced responsive design.
- [ ] **Code Quality**
    - [ ] Add comprehensive error handling for missing Python deps.
    - [ ] Add unit tests for backend services.
    - [ ] Add E2E tests for frontend flows.
