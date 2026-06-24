#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ENV_FILE="$SCRIPT_DIR/.env.production"
DATA_VOLUME="${FITHUB_DATA_VOLUME:-fithub-data}"
BACKUP_DIR="${FITHUB_DEPLOY_BACKUP_DIR:-$SCRIPT_DIR/backups}"
BACKUP_RETENTION="${FITHUB_DEPLOY_BACKUP_RETENTION:-20}"

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

volume_exists() {
  docker volume inspect "$1" >/dev/null 2>&1
}

legacy_data_volumes() {
  docker volume ls --format '{{.Name}}' | awk -v canonical="$DATA_VOLUME" '$0 != canonical && $0 ~ /(^|_)fithub-data$/ { print }'
}

ensure_canonical_data_volume() {
  if [ "${FITHUB_SKIP_VOLUME_BACKUP:-0}" = "1" ]; then
    echo "Skipping FitHub data volume migration because FITHUB_SKIP_VOLUME_BACKUP=1."
    return
  fi

  if volume_exists "$DATA_VOLUME"; then
    return
  fi

  local legacy_volumes legacy_count legacy_volume
  legacy_volumes="$(legacy_data_volumes || true)"
  legacy_count="$(printf "%s\n" "$legacy_volumes" | sed '/^$/d' | wc -l | tr -d ' ')"
  if [ "$legacy_count" = "0" ]; then
    echo "No existing FitHub data volume found. This looks like the first Tencent Cloud deployment."
    return
  fi

  if [ "$legacy_count" != "1" ]; then
    echo "Multiple legacy FitHub data volumes found:"
    printf "%s\n" "$legacy_volumes"
    echo "Refusing to deploy until the correct volume is chosen and migrated manually."
    exit 1
  fi

  legacy_volume="$(printf "%s\n" "$legacy_volumes" | sed '/^$/d' | sed -n '1p')"
  echo "Migrating legacy FitHub data volume '$legacy_volume' to canonical volume '$DATA_VOLUME' ..."
  docker volume create "$DATA_VOLUME" >/dev/null
  docker run --rm \
    -v "$legacy_volume:/from:ro" \
    -v "$DATA_VOLUME:/to" \
    busybox sh -c 'cd /from && tar cf - . | (cd /to && tar xpf -)'
  echo "Legacy data volume migrated. Keeping '$legacy_volume' untouched as an extra safety copy."
}

prune_old_volume_backups() {
  local retention
  retention="$BACKUP_RETENTION"
  if ! printf "%s" "$retention" | grep -Eq '^[0-9]+$'; then
    retention=20
  fi
  if [ "$retention" -le 0 ]; then
    return
  fi
  find "$BACKUP_DIR" -maxdepth 1 -type f -name 'fithub-data-predeploy-*.tar.gz' -print \
    | sort -r \
    | awk -v keep="$retention" 'NR > keep { print }' \
    | xargs -r rm -f
}

backup_data_volume() {
  if [ "${FITHUB_SKIP_VOLUME_BACKUP:-0}" = "1" ]; then
    echo "Skipping FitHub data volume backup because FITHUB_SKIP_VOLUME_BACKUP=1."
    return
  fi

  ensure_canonical_data_volume
  if ! volume_exists "$DATA_VOLUME"; then
    return
  fi

  mkdir -p "$BACKUP_DIR"
  local stamp backup_name
  stamp="$(date -u +%Y%m%d-%H%M%SZ)"
  backup_name="fithub-data-predeploy-$stamp.tar.gz"
  echo "Creating pre-deploy FitHub data backup: $BACKUP_DIR/$backup_name"
  docker run --rm \
    -v "$DATA_VOLUME:/data/fithub:ro" \
    -v "$BACKUP_DIR:/backup" \
    busybox sh -c "cd /data/fithub && tar -czf /backup/$backup_name ."
  prune_old_volume_backups
}

write_postdeploy_storage_snapshot() {
  if [ "${FITHUB_SKIP_VOLUME_BACKUP:-0}" = "1" ]; then
    return
  fi
  mkdir -p "$BACKUP_DIR"
  local stamp target token
  stamp="$(date -u +%Y%m%d-%H%M%SZ)"
  target="$BACKUP_DIR/fithub-storage-status-postdeploy-$stamp.json"
  token="$(grep -E '^FITHUB_ADMIN_TOKEN=' "$ENV_FILE" | tail -1 | cut -d= -f2- || true)"
  if [ -n "$token" ]; then
    if curl -fsS --max-time 10 -H "Authorization: Bearer $token" http://127.0.0.1:10000/api/admin/export > "$target"; then
      echo "Post-deploy admin snapshot written: $target"
      return
    fi
  fi
  curl -fsS --max-time 10 http://127.0.0.1:10000/api/storage/status?remote=1 > "$target" \
    && echo "Post-deploy storage status written: $target" \
    || echo "Warning: could not write post-deploy storage snapshot."
}

cd "$SCRIPT_DIR"
python3 "$REPO_ROOT/scripts/tencent_server_doctor.py" \
  --env-file "$ENV_FILE" \
  --compose-file "$SCRIPT_DIR/docker-compose.yml" \
  --allow-running-service
python3 "$REPO_ROOT/scripts/tencent_cloud_preflight.py" --env-file "$ENV_FILE" --compose-file "$SCRIPT_DIR/docker-compose.yml"
backup_data_volume
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

write_postdeploy_storage_snapshot

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
