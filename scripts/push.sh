#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "Not a git repository here: $(pwd)" >&2
  exit 1
fi

if ! git remote get-url origin >/dev/null 2>&1; then
  echo "No remote 'origin' configured for memory-x." >&2
  echo "Run: git remote add origin <git@github.com:USER/REPO.git>" >&2
  exit 2
fi

echo "Pushing '$branch' to origin..."
git push -u origin "$branch"
echo "Done."

