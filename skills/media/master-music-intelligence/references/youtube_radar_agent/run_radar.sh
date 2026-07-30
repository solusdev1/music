#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
MAX_RESULTS="${1:-5}"
LIMIT_QUERIES="${2:-0}"
shift || true
shift || true
EXTRA_ARGS=("$@")
if [ "$LIMIT_QUERIES" = "0" ]; then
  uv run --with yt-dlp python scripts/radar_gospel_blues_viral.py --max-results "$MAX_RESULTS" "${EXTRA_ARGS[@]}"
else
  uv run --with yt-dlp python scripts/radar_gospel_blues_viral.py --max-results "$MAX_RESULTS" --limit-queries "$LIMIT_QUERIES" "${EXTRA_ARGS[@]}"
fi
