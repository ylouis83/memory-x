# Memory-X Configuration Guide

This document explains how to configure the Memory-X platform for local
experiments and production deployments. All configuration parameters are read
from environment variables (see `configs/settings.py`). You can provide them via
an `.env` file or your process manager.

## 1. Prerequisites

- Python 3.9+
- SQLite (default) or an alternative backend (Cloud Spanner, Mem0)
- Optional: DashScope API key for Qwen models
- Optional: sys schema views installed on your MySQL instance when using the
  medical graph modules

## 2. Essential Environment Variables

Create a `.env` file in the project root (or export variables manually):

```ini
# Core service
MEMORY_DEBUG=true
MEMORY_SERVICE_HOST=0.0.0.0
MEMORY_SERVICE_PORT=5000

# Logging
MEMORY_LOG_LEVEL=INFO
MEMORY_LOG_FILE=./logs/memory.log

# Security (always override in production)
MEMORY_SECRET_KEY=change-me
MEMORY_JWT_SECRET=change-me

# DashScope (optional)
DASHSCOPE_API_KEY=your-dashscope-api-key
```

Source the `.env` file via `source scripts/setup_venv.sh && source .venv/bin/activate && set -a && source .env && set +a` or use a process manager such as
`systemd`/`supervisor`.

## 3. Database Backends

| Variable            | Description | Default |
|---------------------|-------------|---------|
| `MEMORY_DB_TYPE`    | `sqlite`, `spanner`, or `mem0` | `sqlite` |
| `MEMORY_DB_PATH`    | SQLite path when using the default backend | `./memory_db/memory.db` |
| `MEMORY_DB_HOST`    | Host for remote databases | `localhost` |
| `MEMORY_DB_PORT`    | Port for remote databases | `3306` |
| `MEMORY_DB_USER`    | Username for remote databases | _(empty)_ |
| `MEMORY_DB_PASSWORD`| Password for remote databases | _(empty)_ |
| `MEMORY_DB_NAME`    | Database/schema name | `memory_x` |

### SQLite (default)
No additional setup is required. Ensure the `data/` directory is writable.

### Google Cloud Spanner
Set `MEMORY_DB_TYPE=spanner` and provide the connection parameters expected by
`src/storage/spanner_store.py` (service account credentials, etc.).

### Mem0 Backend
Set `MEMORY_DB_TYPE=mem0` and install the dependency:

```bash
pip install git+https://github.com/mem0ai/mem0.git
```

The Mem0 backend is useful for high-quality semantic retrieval.

## 4. Memory Behaviour

| Variable                      | Purpose |
|-------------------------------|---------|
| `MEMORY_MAX_SHORT_TERM`       | Number of short-term messages kept in memory |
| `MEMORY_MAX_WORKING_MEMORY`   | Maximum distinct entity values tracked |
| `MEMORY_IMPORTANCE_THRESHOLD` | Minimum importance required for long-term persistence |
| `MEMORY_TTL_DAYS`             | Retention policy (days) for long-term entries |
| `MEMORY_MAX_CONTEXT_ROUNDS`   | Context rounds passed to AI models |
| `MEMORY_ENTITY_RECOGNITION`   | Enable/disable built-in entity extraction |
| `MEMORY_INTENT_DETECTION`     | Enable/disable rule-based intent detection |

## 5. DashScope Integration

Set `DASHSCOPE_API_KEY` to enable the `/api/dashscope/*` routes and the
DashScope-driven memory manager (`src/core/dashscope_memory_manager.py`). Without
this key, the routes are skipped at startup.

Adjust model parameters in `configs/llm_config.py` for temperature, max tokens,
model ID, etc.

## 6. Medical Graph Module

The medical graph API (`/api/graph/*`) requires:

1. `data/medical_graph.db` to be writable – the initialisation code creates the
   database automatically.
2. MySQL sys schema (`sys` metrics) if you enable features in
   `src/core/graph_update_engine.py` that rely on the sys views.
3. Optional DashScope key if you use the Qwen update engine.

## 7. Frontend Configuration

The front-end (React + Vite) reads its settings from `frontend/.env` (see
`frontend/README.md`). Common variables:

```ini
VITE_API_BASE_URL=http://localhost:5000
VITE_ENABLE_DASHSCOPE=false
```

Run `npm install` followed by `npm run dev` to start the UI.

## 8. Sample .env

```ini
MEMORY_DEBUG=false
MEMORY_SERVICE_HOST=0.0.0.0
MEMORY_SERVICE_PORT=5000
MEMORY_SECRET_KEY=${RANDOM_HEX}
MEMORY_JWT_SECRET=${RANDOM_HEX}
MEMORY_DB_TYPE=sqlite
MEMORY_DB_PATH=./memory_db/memory.db
MEMORY_LOG_LEVEL=INFO
MEMORY_LOG_FILE=./logs/memory.log
MEMORY_MAX_SHORT_TERM=10
MEMORY_MAX_WORKING_MEMORY=100
MEMORY_IMPORTANCE_THRESHOLD=3
DASHSCOPE_API_KEY=
```

Rename the file to `.env` and adjust values for your environment.

## 9. Troubleshooting

- **DashScope routes missing** – Check that `DASHSCOPE_API_KEY` is set before
  starting the app.
- **Medical graph import error** – Ensure the `data/` directory exists or set
  `MYAWR_LOCK_DIR` when running external scripts that integrate with Memory-X.
- **Mem0 backend KeyError** – Upgrade to the latest commit; Mem0 results are now
  normalised to match the standard schema.

For additional issues, consult `docs/issues/`.
