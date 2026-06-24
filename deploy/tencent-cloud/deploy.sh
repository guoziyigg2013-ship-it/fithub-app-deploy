#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ENV_FILE="$SCRIPT_DIR/.env.production"

if [ ! -f "$ENV_FILE" ]; then
  echo "Missing $ENV_FILE"
  echo "Create it from .env.production.example and fill real production values first."
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is required on the server."
  exit 1
fi

if docker compose version >/dev/null 2>&1; then
  COMPOSE=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE=(docker-compose)
else
  echo "docker compose or docker-compose is required on the server."
  exit 1
fi

cd "$SCRIPT_DIR"
python3 "$REPO_ROOT/scripts/tencent_server_doctor.py" \
  --env-file "$ENV_FILE" \
  --compose-file "$SCRIPT_DIR/docker-compose.yml" \
  --allow-running-service
python3 "$REPO_ROOT/scripts/tencent_cloud_preflight.py" --env-file "$ENV_FILE" --compose-file "$SCRIPT_DIR/docker-compose.yml"
"${COMPOSE[@]}" up -d --build

echo "Waiting for FitHub API health ..."
HEALTHY=0
for attempt in $(seq 1 30); do
  if curl -fsS --max-time 3 http://127.0.0.1:10000/healthz >/dev/null; then
    echo "FitHub API is healthy on localhost:10000"
    HEALTHY=1
    break
  fi
  sleep 2
done

if [ "$HEALTHY" != "1" ]; then
  echo "FitHub API did not become healthy in time. Recent logs:"
  "${COMPOSE[@]}" logs --tail=80 fithub-api || true
  exit 1
fi

if [ "${FITHUB_DEPLOY_CHECK_PUBLIC:-0}" = "1" ]; then
  PUBLIC_ORIGIN="$(grep -E '^FITHUB_PUBLIC_API_ORIGIN=' "$ENV_FILE" | tail -1 | cut -d= -f2-)"
  python3 "$REPO_ROOT/scripts/tencent_server_doctor.py" \
    --env-file "$ENV_FILE" \
    --compose-file "$SCRIPT_DIR/docker-compose.yml" \
    --skip-docker \
    --skip-compose \
    --skip-port \
    --check-public \
    --backend-url "$PUBLIC_ORIGIN"
fi

echo "FitHub Tencent Cloud deployment completed."
