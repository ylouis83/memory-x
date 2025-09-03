#!/usr/bin/env bash
set -euo pipefail

root_dir=$(cd "$(dirname "$0")/.." && pwd)
cd "$root_dir"

echo "Cleaning caches, logs, test reports..."
rm -rf .pytest_cache .mypy_cache __pycache__
find . -name "__pycache__" -type d -prune -exec rm -rf {} + || true
rm -f .coverage *.log
rm -rf logs/* 2>/dev/null || true
rm -f tests/test_report_*.json tests/memory_test_report_*.json tests/reports/*.json 2>/dev/null || true

echo "Done."

