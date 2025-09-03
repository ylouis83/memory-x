#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH=$(cd "$(dirname "$0")/.." && pwd)

APP=${APP_PATH:-memory-x/src/api/app.py}

if [ ! -f "$APP" ]; then
  APP="src/api/app.py"
fi

echo "Running API: $APP"
python "$APP"

