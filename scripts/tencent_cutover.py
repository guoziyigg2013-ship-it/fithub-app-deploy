#!/usr/bin/env python3
"""Orchestrate the final Tencent Cloud cutover for FitHub.

This script intentionally defaults to a dry run. Use --apply only after the
Tencent Cloud backend domain, Supabase project, and Mini Program AppID are all
confirmed.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import NamedTuple


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import build_tencent_release
import configure_production
import init_tencent_env
import tencent_cloud_preflight


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ENV_OUTPUT = ROOT / "deploy" / "tencent-cloud" / ".env.production"
DEFAULT_NGINX_OUTPUT = ROOT / "deploy" / "tencent-cloud" / "nginx-fithub.conf"
DEFAULT_RELEASE_OUTPUT = ROOT / "dist"


class CutoverResult(NamedTuple):
    api_origin: str
    miniapp_appid: str
    env_output: Path
    nginx_output: Path
    changed_files: list[str]
    archive_path: Path | None = None
    manifest_path: Path | None = None


def redact_env(values: dict[str, str]) -> list[str]:
    lines: list[str] = []
    for key in (
        "FITHUB_PUBLIC_API_ORIGIN",
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
        "FITHUB_MEDIA_STORAGE_PROVIDER",
        "FITHUB_MEDIA_BUCKET",
        "FITHUB_TENCENT_COS_SECRET_ID",
        "FITHUB_TENCENT_COS_SECRET_KEY",
        "FITHUB_TENCENT_COS_REGION",
        "FITHUB_TENCENT_COS_BUCKET",
        "FITHUB_TENCENT_COS_PUBLIC_BASE_URL",
        "FITHUB_ADMIN_TOKEN",
        "FITHUB_MEDIA_MAINTENANCE_TOKEN",
    ):
        value = values.get(key, "")
        lines.append(f"{key}={init_tencent_env.redact_value(key, value)}")
    return lines


def validate_backend_if_requested(backend_url: str) -> None:
    if not backend_url:
        return
    failures: list[str] = []
    tencent_cloud_preflight.validate_live_backend(backend_url, failures)
    if failures:
        raise ValueError("; ".join(failures))


def run_cutover(
    *,
    root: Path,
    api_origin: str,
    miniapp_appid: str,
    supabase_url: str,
    supabase_service_role_key: str,
    web_origin: str = "",
    admin_token: str = "",
    media_maintenance_token: str = "",
    media_bucket: str = "fithub-media",
    media_storage_provider: str = "supabase",
    cos_secret_id: str = "",
    cos_secret_key: str = "",
    cos_region: str = "",
    cos_bucket: str = "",
    cos_public_base_url: str = "",
    apply: bool = False,
    write_env: bool = False,
    force: bool = False,
    skip_nginx: bool = False,
    skip_release: bool = False,
    release_version: str = "",
    release_output_dir: Path | None = None,
    env_output: Path | None = None,
    nginx_output: Path | None = None,
    backend_url: str = "",
) -> CutoverResult:
    root = Path(root)
    api_origin = configure_production.normalize_api_origin(api_origin)
    miniapp_appid = configure_production.normalize_appid(miniapp_appid)
    env_output = Path(env_output or DEFAULT_ENV_OUTPUT)
    nginx_output = Path(nginx_output or DEFAULT_NGINX_OUTPUT)
    release_output_dir = Path(release_output_dir or DEFAULT_RELEASE_OUTPUT)

    env_values = init_tencent_env.build_env_values(
        api_origin=api_origin,
        supabase_url=supabase_url,
        supabase_service_role_key=supabase_service_role_key,
        admin_token=admin_token,
        media_maintenance_token=media_maintenance_token,
        media_bucket=media_bucket,
        media_storage_provider=media_storage_provider,
        cos_secret_id=cos_secret_id,
        cos_secret_key=cos_secret_key,
        cos_region=cos_region,
        cos_bucket=cos_bucket,
        cos_public_base_url=cos_public_base_url,
    )
    validate_backend_if_requested(backend_url)

    previews = configure_production.configure(
        root,
        api_origin,
        miniapp_appid,
        dry_run=not apply,
    )
    changed_files = [
        line[4:].split(" (after)", 1)[0]
        for preview in previews
        for line in preview.splitlines()
        if line.startswith("+++") and "(after)" in line
    ]

    if apply and write_env:
        init_tencent_env.write_text_securely(env_output, init_tencent_env.render_env(env_values), force=force)
        if not skip_nginx:
            init_tencent_env.write_text_securely(
                nginx_output,
                init_tencent_env.render_nginx_config(api_origin, web_origin),
                force=force,
            )

    archive_path = None
    manifest_path = None
    if apply and not skip_release:
        archive_path, manifest_path = build_tencent_release.build_archive(
            root,
            release_output_dir,
            version=release_version,
        )

    print("FitHub Tencent Cloud cutover " + ("applied" if apply else "dry run"))
    print(f"API Origin: {api_origin}")
    print(f"Mini Program AppID: {miniapp_appid}")
    print("Environment preview:")
    for line in redact_env(env_values):
        print(f"  {line}")
    print("")
    print("Config diff:")
    for preview in previews:
        print(preview, end="" if preview.endswith("\n") else "\n")
    if write_env:
        verb = "Wrote" if apply else "Would write"
        print(f"{verb} env file: {env_output}")
        if not skip_nginx:
            print(f"{verb} Nginx config: {nginx_output}")
    if not skip_release:
        if apply:
            print(f"Release archive: {archive_path}")
            print(f"Release manifest: {manifest_path}")
        else:
            print(f"Would build Tencent release archive in: {release_output_dir}")
    print("")
    print("Next:")
    print("1. Upload the release archive to the Tencent Cloud server.")
    print("2. Copy .env.production and nginx-fithub.conf to deploy/tencent-cloud/ on the server.")
    print("3. Run deploy/tencent-cloud/deploy.sh on the server.")
    print("4. Run npm run check:production after the API domain is live.")

    return CutoverResult(
        api_origin=api_origin,
        miniapp_appid=miniapp_appid,
        env_output=env_output,
        nginx_output=nginx_output,
        changed_files=changed_files,
        archive_path=archive_path,
        manifest_path=manifest_path,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Dry-run or apply FitHub Tencent Cloud production cutover.")
    parser.add_argument("--api-origin", required=True, help="Production API origin, for example https://api.example.cn")
    parser.add_argument("--web-origin", default="", help="Optional public Web origin, for example https://app.example.cn.")
    parser.add_argument("--miniapp-appid", required=True, help="Real WeChat Mini Program AppID.")
    parser.add_argument("--supabase-url", required=True, help="Real Supabase Project URL.")
    parser.add_argument("--supabase-service-role-key", required=True, help="Real Supabase service_role key.")
    parser.add_argument("--admin-token", default="", help="Optional fixed admin token. Defaults to generated.")
    parser.add_argument("--media-maintenance-token", default="", help="Optional fixed media maintenance token.")
    parser.add_argument("--media-bucket", default="fithub-media")
    parser.add_argument("--media-storage-provider", default="supabase", choices=["supabase", "cos", "inline"])
    parser.add_argument("--cos-secret-id", default="")
    parser.add_argument("--cos-secret-key", default="")
    parser.add_argument("--cos-region", default="")
    parser.add_argument("--cos-bucket", default="")
    parser.add_argument("--cos-public-base-url", default="")
    parser.add_argument("--apply", action="store_true", help="Actually update files. Omit for dry-run.")
    parser.add_argument("--write-env", action="store_true", help="Write .env.production and nginx config when --apply is set.")
    parser.add_argument("--force", action="store_true", help="Overwrite generated env/nginx files.")
    parser.add_argument("--skip-nginx", action="store_true")
    parser.add_argument("--skip-release", action="store_true")
    parser.add_argument("--release-version", default="")
    parser.add_argument("--release-output-dir", default=str(DEFAULT_RELEASE_OUTPUT))
    parser.add_argument("--env-output", default=str(DEFAULT_ENV_OUTPUT))
    parser.add_argument("--nginx-output", default=str(DEFAULT_NGINX_OUTPUT))
    parser.add_argument("--backend-url", default="", help="Optional live backend URL to validate after deployment.")
    args = parser.parse_args()

    try:
        run_cutover(
            root=ROOT,
            api_origin=args.api_origin,
            web_origin=args.web_origin,
            miniapp_appid=args.miniapp_appid,
            supabase_url=args.supabase_url,
            supabase_service_role_key=args.supabase_service_role_key,
            admin_token=args.admin_token,
            media_maintenance_token=args.media_maintenance_token,
            media_bucket=args.media_bucket,
            media_storage_provider=args.media_storage_provider,
            cos_secret_id=args.cos_secret_id,
            cos_secret_key=args.cos_secret_key,
            cos_region=args.cos_region,
            cos_bucket=args.cos_bucket,
            cos_public_base_url=args.cos_public_base_url,
            apply=args.apply,
            write_env=args.write_env,
            force=args.force,
            skip_nginx=args.skip_nginx,
            skip_release=args.skip_release,
            release_version=args.release_version,
            release_output_dir=Path(args.release_output_dir),
            env_output=Path(args.env_output),
            nginx_output=Path(args.nginx_output),
            backend_url=args.backend_url,
        )
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"Tencent cutover failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
