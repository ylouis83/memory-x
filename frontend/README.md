# Memory-X Frontend

This folder contains the Vite + React (TypeScript) application that visualises
conversation history, memory statistics, and graph insights exposed by the
Memory-X backend.

## Prerequisites

- Node.js 18+
- npm 9+ (or pnpm/yarn if preferred)
- Running backend (default `http://localhost:5000`)

## Installation

```bash
cd frontend
npm install
```

This installs all dependencies listed in `package.json` (Material-UI, Zustand,
Axios, etc.).

## Environment Variables

Create a `frontend/.env.local` (or `.env`) file to override defaults:

```ini
VITE_API_BASE_URL=http://localhost:5000
VITE_ENABLE_DASHSCOPE=false
```

- `VITE_API_BASE_URL` – Base URL for API requests.
- `VITE_ENABLE_DASHSCOPE` – Toggle DashScope-specific UI elements.

## Development

Start the dev server (Vite) with hot module reloading:

```bash
npm run dev
```

Open the suggested URL (typically `http://localhost:5173`). The dev server
proxies API requests based on `VITE_API_BASE_URL`.

## Linting & Formatting

```bash
npm run lint   # ESLint
npm run typecheck
```

## Build & Preview

```bash
npm run build     # Produces static assets in dist/
npm run preview   # Serves the production build locally
```

The build output can be hosted on any static server (Netlify, Vercel, nginx).

## Project Structure

```
frontend/
├── public/           # Static assets
├── src/
│   ├── components/   # UI building blocks
│   ├── pages/        # Route-level pages
│   ├── services/     # API clients
│   ├── store/        # Zustand stores
│   └── utils/        # Shared helpers
├── vite.config.ts
└── package.json
```

## Connecting to the Backend

Ensure the backend is running (`bash scripts/start_all.sh` or `python -m
src.api.app`). The UI uses the following endpoints:

- `/api/memory/*` for conversation data
- `/api/memory/<user_id>/stats` for dashboard summaries
- `/api/graph/*` for medical graph visualisations (optional)

If you enable DashScope features, confirm that the backend has
`DASHSCOPE_API_KEY` configured.
