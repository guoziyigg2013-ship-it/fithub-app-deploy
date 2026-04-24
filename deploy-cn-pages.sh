#!/bin/zsh
set -euo pipefail

PROJECT_NAME="${1:-fithub-cn}"
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
TMP_DIR="$(mktemp -d)"

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

cp "$ROOT_DIR/index.html" "$TMP_DIR/index.html"
cp "$ROOT_DIR/mobile.html" "$TMP_DIR/mobile.html"
cp "$ROOT_DIR/styles.css" "$TMP_DIR/styles.css"
cp "$ROOT_DIR/app.js" "$TMP_DIR/app.js"
cp "$ROOT_DIR/sw.js" "$TMP_DIR/sw.js"
cp "$ROOT_DIR/config.js" "$TMP_DIR/config.js"
if [ -d "$ROOT_DIR/assets" ]; then
  cp -R "$ROOT_DIR/assets" "$TMP_DIR/assets"
fi

echo "Deploying FitHub CN static shell to Cloudflare Pages project: $PROJECT_NAME"
cd "$ROOT_DIR"
npx --yes wrangler pages deploy "$TMP_DIR" --project-name "$PROJECT_NAME" --branch main
