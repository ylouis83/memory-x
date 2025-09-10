Memory‑X Project Structure

- root
  - README.md: Quick overview and usage
  - requirements.txt: Python dependencies
  - docker-compose.yml, Dockerfile: Container deployment
  - configs/: Runtime settings
  - docs/: Architecture and integration notes
  - examples/: Small runnable demos
  - frontend/: React + TypeScript Web UI
    - src/: Source code
      - components/: UI components (ChatInterface, MemoryBrowser, etc.)
      - contexts/: React context for state management
      - services/: API client and service layer
      - types/: TypeScript type definitions
    - public/: Static assets
    - package.json: Frontend dependencies
  - src/: Backend Python code
    - api/: Minimal API app and routes
    - core/: Core memory logic (rules, confidence, FHIR policy)
    - modules/: Medical validator and time parsing utilities
    - storage/: Store backends (SQLite, Spanner, Mem0)
  - tests/: Unit/integration tests and reports
  - scripts/: Local dev helpers

Scripts
- scripts/setup_venv.sh: Create venv and install deps
- scripts/test.sh: Run pytest for this project
- scripts/run_api.sh: Start the backend API service
- scripts/run_frontend.sh: Start the frontend dev server
- scripts/start_all.sh: Start both frontend and backend
- scripts/clean.sh: Remove caches/logs/test reports

Common Tasks
- Full Setup: `bash scripts/start_all.sh`
- Backend Only: `bash scripts/setup_venv.sh && source .venv/bin/activate && bash scripts/run_api.sh`
- Frontend Only: `bash scripts/run_frontend.sh` 
- Test: `bash scripts/test.sh`
- Clean: `bash scripts/clean.sh`

