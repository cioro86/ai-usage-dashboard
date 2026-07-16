#!/usr/bin/env bash

cd "$(dirname "$0")/.."

cleanup() {
  if [[ -n "${REFRESH_PID:-}" ]] && kill -0 "$REFRESH_PID" 2>/dev/null; then
    kill "$REFRESH_PID" 2>/dev/null || true
    wait "$REFRESH_PID" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

python3 ./scripts/refresh-benchmarks.py

./scripts/refresh.sh &
REFRESH_PID=$!

python3 -m http.server 8080 --bind 127.0.0.1