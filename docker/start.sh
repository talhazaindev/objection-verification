#!/bin/sh
set -e

export PORT="${PORT:-8080}"
export INTERNAL_API_URL="${INTERNAL_API_URL:-http://127.0.0.1:8000}"
export PYTHONPATH="/app/backend"
export NODE_ENV="production"

NODE_BIN="$(command -v node || command -v nodejs)"
if [ -z "$NODE_BIN" ]; then
  echo "ERROR: Node.js not found in container"
  exit 1
fi

echo "Starting Objection prototype (port=${PORT})"
echo "Node: $($NODE_BIN --version)"

envsubst '${PORT}' < /etc/nginx/nginx.conf.template > /etc/nginx/conf.d/default.conf
rm -f /etc/nginx/sites-enabled/default

cd /app/backend
echo "Starting FastAPI on 127.0.0.1:8000"
uvicorn app.main:app --host 127.0.0.1 --port 8000 &
UVICORN_PID=$!

cd /app/frontend
echo "Starting Next.js on 127.0.0.1:3000"
HOSTNAME=127.0.0.1 PORT=3000 "$NODE_BIN" server.js &
NEXT_PID=$!

# Give app servers a moment to bind before nginx accepts traffic
sleep 2

if ! kill -0 "$UVICORN_PID" 2>/dev/null; then
  echo "ERROR: FastAPI failed to start"
  exit 1
fi

if ! kill -0 "$NEXT_PID" 2>/dev/null; then
  echo "ERROR: Next.js failed to start"
  exit 1
fi

echo "Starting nginx on port ${PORT}"
exec nginx -g 'daemon off;'
