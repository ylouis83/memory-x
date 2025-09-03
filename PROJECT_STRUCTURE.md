Memory‑X Project Structure

- root
  - README.md: Quick overview and usage
  - requirements.txt, requirements-dev.txt
  - docker-compose.yml, Dockerfile
  - configs/: Runtime settings
  - docs/: Architecture and integration notes
  - examples/: Small runnable demos
  - src/
    - api/: Minimal API app and routes
    - core/: Core memory logic (rules, confidence, FHIR policy)
    - models/: Data models (if any shared)
    - modules/: Utilities like medical validator, time parsing
    - storage/: Store backends (SQLite, Spanner, Mem0)
    - utils/: Query helpers and migration scripts
  - tests/: Unit/integration tests and reports
  - scripts/: Local dev helpers

Scripts
- scripts/setup_venv.sh: Create venv and install deps
- scripts/test.sh: Run pytest for this project
- scripts/run_api.sh: Start the minimal API app
- scripts/clean.sh: Remove caches/logs/test reports
- scripts/push.sh: Push current branch to origin

Common Tasks
- Setup: `bash scripts/setup_venv.sh && source .venv/bin/activate`
- Test: `bash scripts/test.sh -q`
- Run API: `bash scripts/run_api.sh`
- Clean: `bash scripts/clean.sh`
- Push: `git remote add origin <url>; bash scripts/push.sh`

