# Memory-X API Reference

This document summarises the HTTP endpoints exposed by the Memory-X service
(the default base URL is `http://HOST:PORT/`).  Unless otherwise noted the
endpoints return JSON responses and require no authentication.

## Health Check

- **GET `/health`** – Returns service status and version metadata.

## Memory Management

All memory endpoints leverage the `SimpleMemoryIntegratedAI` pipeline.

- **POST `/api/memory`**
  - Body: `{ "user_id": "string", "message": "string", "response": "string?", "entities": {}, "intent": "", "importance": 2 }`
  - Processes a chat message, stores relevant details in short/long-term
    memory, and returns the generated reply plus storage metadata.

- **GET `/api/memory/<user_id>`**
  - Query params: `query` (optional), `limit` (default 10)
  - Retrieves recent short-term messages (when `query` is empty) or performs a
    semantic search against long-term memory using `retrieve_memories`.

- **POST `/api/memory/delete`**
  - SQLite backend only.  Body: `{ "user_id": "string", "pattern": "%keyword%" }`
  - Deletes long-term rows matching the SQL `LIKE` pattern.

- **GET `/api/memory/<user_id>/stats`** – Returns counters for short-term, working,
  and persisted memories.

- **POST `/api/memory/<user_id>/clear`** – Clears the in-memory session state for
  the user (short-term + working memory).

- **POST `/api/memory/chat`**
  - Body: `{ "user_id": "string", "message": "string" }`
  - Convenience wrapper that returns the generated response together with
    memory operation logs and statistics.

- **POST `/api/memory/query`**
  - Body: `{ "user_id": "string", "type": "basic|temporal|entity", "params": {} }`
  - Currently `basic` executes a semantic retrieval; `temporal` and `entity`
    are placeholders for future filtering strategies.

## Medical Decision Support

- **POST `/api/medical/decide`**
  - Body: `{ "current": {...}, "new": {...}, "approximate_time": bool, "high_risk": bool }`
  - Evaluates whether a medication entry should be appended, updated, or merged
    using `compute_merge_confidence` from `src/core/merge_confidence.py`.

## Demo Routes

- **GET `/demo/mem0`** – Serves the bundled Mem0 front-end demo HTML.
- **GET `/`** – Redirects to `/demo/mem0`.

## DashScope Integration (optional)

Available only when DashScope dependencies are installed and
`DASHSCOPE_API_KEY` is configured.

Base path: `/api/dashscope`

- **POST `/chat`** – Similar to `/api/memory/chat` but powered by DashScope
  models.
- **POST `/search`** – Vector search via DashScope embeddings.
- **GET `/stats/<user_id>`** – Summarises stored DashScope memories.
- **GET `/working-memory/<user_id>`** – Returns short-term and working memory
  snapshots.
- **POST `/clear-session/<user_id>`** – Clears session caches.
- **GET `/health`** – Verifies API key configuration.
- **POST `/test-connection`** – Performs a live chat completion request to
  validate connectivity.

## Medical Graph API (optional)

Exposed when the graph modules are installed.  Base path: `/api/graph`

- **GET `/health`** – Health probe for the graph service.
- **POST `/extract`** – Body: `{ "text": "...", "user_id": "string", "session_id": "string" }`.
  Runs entity extraction and stores results in the medical graph database.
- **GET `/entities/<type>`** – Lists diseases/symptoms/medicines by name.
- **GET `/relations/disease-symptom`** – Returns disease–symptom edges for a user.
- **GET `/relations/disease-medicine`** – Returns disease–medicine edges.
- **GET `/user/<user_id>/summary`** – Aggregated graph metrics for the user.
- **GET `/user/<user_id>/graph`** – Full node/edge listing for the user graph.

These APIs require the SQLite medical graph store (see
`src/core/medical_graph_manager.py`); ensure the `data/` directory is writable
and `sys_schema` views are installed for advanced metrics.

## Error Handling

Most endpoints return errors in the format `{ "error": "message" }` with an
appropriate HTTP status code.  For debugging, check the Loguru output path
configured via `configs/settings.py`.
