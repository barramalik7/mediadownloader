# Project Task List

## Completed
- [x] **v1.0: Initial Build**
    - [x] Analyze codebase structure.
    - [x] Create PRD, FSD, TSD, DEVLOG.
    - [x] Build Next.js frontend + Python scripts.
- [x] **v2.0: Architecture Refactoring**
    - [x] Migrate backend to FastAPI.
    - [x] Migrate frontend to Vite + TanStack.
    - [x] Replace generated-client assumptions with typed fetch/SSE boundaries.
    - [x] DRY refactor (shared `utils/helpers.py`).
    - [x] Cleanup legacy files (`web/`, `scripts/`, etc.).
    - [x] Update all documentation and `.gitignore`.
    - [x] Document one-click launcher (`run_app.bat`) and image download features.
    - [x] Add health and preflight diagnostics for local runtime readiness.
    - [x] Add automated backend and frontend test coverage for current contracts.

## Roadmap & Backlog
- [ ] **Feature: Download History**
    - [ ] Create database/log for tracking downloads.
    - [ ] Build History UI page.
- [ ] **Feature: Batch Downloading**
    - [ ] Support playlist URLs and comma-separated URLs.
- [ ] **UI Improvements**
    - [ ] Enhanced responsive design.
- [ ] **Code Quality**
    - [ ] Add comprehensive error handling for missing Python deps.
    - [ ] Add browser-level E2E tests for frontend flows.
    - [ ] Extend adapter coverage to more platform-specific command variants.
