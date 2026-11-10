#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
port="${1:-8765}"
url="http://localhost:${port}"

if curl -s -o /dev/null "${url}/api/lessons"; then
  echo "Server already running at ${url}"
else
  echo "Starting server at ${url} (Ctrl+C to stop)"
  python3 server.py "${port}" &
  server_pid=$!
  trap 'kill ${server_pid} 2>/dev/null' INT TERM EXIT
  for _ in $(seq 1 30); do
    curl -s -o /dev/null "${url}/api/lessons" && break
    sleep 0.2
  done
fi

if command -v open >/dev/null; then
  open "${url}"
elif command -v xdg-open >/dev/null; then
  xdg-open "${url}"
fi

if [[ -n "${server_pid:-}" ]]; then
  wait "${server_pid}"
fi
