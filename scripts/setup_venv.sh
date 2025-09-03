#!/usr/bin/env bash
set -euo pipefail

PY=${PYTHON:-python3}
VENV_DIR=${VENV_DIR:-.venv}

if [ ! -d "$VENV_DIR" ]; then
  echo "Creating venv at $VENV_DIR"
  $PY -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
pip install --upgrade pip

REQ=${REQ_FILE:-requirements.txt}
if [ -f "$REQ" ]; then
  echo "Installing requirements from $REQ"
  pip install -r "$REQ"
else
  echo "requirements.txt not found; skipping."
fi

echo "Virtualenv ready. To activate: source $VENV_DIR/bin/activate"

