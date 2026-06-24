#!/usr/bin/env sh
set -eu

REMOTE_DIR="${FITHUB_REMOTE_DIR:-/opt/fithub}"

if [ "$(id -u)" = "0" ]; then
  SUDO=""
else
  if ! command -v sudo >/dev/null 2>&1; then
    echo "sudo is required when bootstrapping as a non-root user." >&2
    exit 1
  fi
  SUDO="sudo"
fi

run_root() {
  echo "+ $*"
  if [ -n "$SUDO" ]; then
    $SUDO sh -c "$*"
  else
    sh -c "$*"
  fi
}

compose_ready() {
  if command -v docker >/dev/null 2>&1; then
    if $SUDO docker compose version >/dev/null 2>&1; then
      return 0
    fi
    if command -v docker-compose >/dev/null 2>&1 && $SUDO docker-compose version >/dev/null 2>&1; then
      return 0
    fi
  fi
  return 1
}

start_service_if_available() {
  service_name="$1"
  if command -v systemctl >/dev/null 2>&1; then
    run_root "systemctl enable --now $service_name"
  else
    run_root "service $service_name start || true"
  fi
}

install_with_apt() {
  run_root "apt-get update"
  run_root "DEBIAN_FRONTEND=noninteractive apt-get install -y ca-certificates curl gnupg tar gzip python3 nginx docker.io"
  if ! compose_ready; then
    run_root "DEBIAN_FRONTEND=noninteractive apt-get install -y docker-compose-plugin || DEBIAN_FRONTEND=noninteractive apt-get install -y docker-compose"
  fi
}

install_with_yum() {
  run_root "yum install -y ca-certificates curl tar gzip python3 nginx docker"
  if ! compose_ready; then
    echo "Docker Compose was not installed by yum. Install docker compose plugin manually, then rerun this script." >&2
    exit 1
  fi
}

if command -v apt-get >/dev/null 2>&1; then
  install_with_apt
elif command -v yum >/dev/null 2>&1; then
  install_with_yum
else
  echo "Unsupported server OS: expected apt-get or yum." >&2
  exit 1
fi

start_service_if_available docker
start_service_if_available nginx
run_root "mkdir -p '$REMOTE_DIR/releases'"
run_root "chmod 755 '$REMOTE_DIR'"

echo "Checking installed runtime ..."
python3 --version
$SUDO docker version >/dev/null
if $SUDO docker compose version >/dev/null 2>&1; then
  $SUDO docker compose version
elif command -v docker-compose >/dev/null 2>&1; then
  $SUDO docker-compose version
else
  echo "docker compose or docker-compose is required." >&2
  exit 1
fi
nginx -v

if [ -n "$SUDO" ]; then
  current_user="$(id -un)"
  run_root "usermod -aG docker '$current_user' || true"
  echo "User '$current_user' was added to the docker group if possible. Reconnect SSH before deploying without sudo."
fi

echo "FitHub Tencent server bootstrap completed. Remote directory: $REMOTE_DIR"
