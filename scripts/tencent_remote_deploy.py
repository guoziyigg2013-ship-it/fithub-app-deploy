#!/usr/bin/env python3
"""Upload and run a FitHub release on a Tencent Cloud server.

The script defaults to dry-run so we can review the exact SSH/SCP steps before
touching a production server.
"""

from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import build_tencent_release


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REMOTE_DIR = "/opt/fithub"
DEFAULT_ENV_FILE = ROOT / "deploy" / "tencent-cloud" / ".env.production"
DEFAULT_NGINX_FILE = ROOT / "deploy" / "tencent-cloud" / "nginx-fithub.conf"


class CommandStep(NamedTuple):
    label: str
    command: list[str]
    redacted_command: list[str] | None = None

    def display(self) -> str:
        return " ".join(shlex.quote(part) for part in (self.redacted_command or self.command))


def latest_release_archive(dist_dir: Path) -> Path:
    candidates = sorted(
        dist_dir.glob("fithub-tencent-release-*.tar.gz"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        raise FileNotFoundError(f"No Tencent release archive found in {dist_dir}. Run npm run release:tencent first.")
    return candidates[0]


def ssh_base_args(*, port: int = 22, identity_file: Path | None = None) -> list[str]:
    args = ["ssh", "-p", str(port)]
    if identity_file:
        args.extend(["-i", str(identity_file)])
    return args


def scp_base_args(*, port: int = 22, identity_file: Path | None = None) -> list[str]:
    args = ["scp", "-P", str(port)]
    if identity_file:
        args.extend(["-i", str(identity_file)])
    return args


def ssh_target(user: str, host: str) -> str:
    user = str(user or "").strip()
    host = str(host or "").strip()
    if not host:
        raise ValueError("--host is required.")
    return f"{user}@{host}" if user else host


def remote_shell(command: str, *, target: str, port: int, identity_file: Path | None) -> list[str]:
    return [*ssh_base_args(port=port, identity_file=identity_file), target, "sh", "-lc", command]


def remote_path(*parts: str) -> str:
    return "/".join(str(part).strip("/") for part in parts if str(part).strip("/"))


def validate_local_inputs(archive: Path, env_file: Path, nginx_file: Path | None) -> None:
    for path, label in ((archive, "release archive"), (env_file, "production env")):
        if not path.exists():
            raise FileNotFoundError(f"Missing {label}: {path}")
        if not path.is_file():
            raise ValueError(f"{label} is not a file: {path}")
    if nginx_file and not nginx_file.exists():
        raise FileNotFoundError(f"Missing Nginx config: {nginx_file}")
    if archive.suffixes[-2:] != [".tar", ".gz"] and archive.suffix != ".gz":
        raise ValueError(f"Release archive should be a .tar.gz file: {archive}")


def build_steps(
    *,
    host: str,
    user: str = "root",
    port: int = 22,
    identity_file: Path | None = None,
    archive: Path,
    env_file: Path,
    nginx_file: Path | None,
    remote_dir: str = DEFAULT_REMOTE_DIR,
    check_public: bool = False,
    restart_nginx: bool = False,
) -> list[CommandStep]:
    target = ssh_target(user, host)
    remote_dir = "/" + str(remote_dir or DEFAULT_REMOTE_DIR).strip("/")
    release_name = archive.name
    release_remote = "/" + remote_path(remote_dir, "releases", release_name)
    app_remote = "/" + remote_path(remote_dir, "fithub-app-deploy")
    deploy_remote = "/" + remote_path(app_remote, "deploy", "tencent-cloud")

    steps = [
        CommandStep(
            "Create remote release directory",
            remote_shell(
                f"mkdir -p {shlex.quote(remote_dir + '/releases')}",
                target=target,
                port=port,
                identity_file=identity_file,
            ),
        ),
        CommandStep(
            "Upload release archive",
            [*scp_base_args(port=port, identity_file=identity_file), str(archive), f"{target}:{release_remote}"],
        ),
        CommandStep(
            "Extract release archive",
            remote_shell(
                "set -e; "
                f"cd {shlex.quote(remote_dir)}; "
                "rm -rf fithub-app-deploy; "
                f"tar -xzf {shlex.quote(release_remote)}",
                target=target,
                port=port,
                identity_file=identity_file,
            ),
        ),
        CommandStep(
            "Upload production env",
            [*scp_base_args(port=port, identity_file=identity_file), str(env_file), f"{target}:{deploy_remote}/.env.production"],
            redacted_command=[
                *scp_base_args(port=port, identity_file=identity_file),
                "<local .env.production>",
                f"{target}:{deploy_remote}/.env.production",
            ],
        ),
    ]

    if nginx_file:
        steps.append(
            CommandStep(
                "Upload Nginx config",
                [*scp_base_args(port=port, identity_file=identity_file), str(nginx_file), f"{target}:{deploy_remote}/nginx-fithub.conf"],
            )
        )
        if restart_nginx:
            steps.append(
                CommandStep(
                    "Install and reload Nginx config",
                    remote_shell(
                        "set -e; "
                        f"cp {shlex.quote(deploy_remote + '/nginx-fithub.conf')} /etc/nginx/conf.d/fithub.conf; "
                        "nginx -t; "
                        "systemctl reload nginx",
                        target=target,
                        port=port,
                        identity_file=identity_file,
                    ),
                )
            )

    deploy_command = (
        "set -e; "
        f"cd {shlex.quote(deploy_remote)}; "
        "chmod +x deploy.sh; "
    )
    if check_public:
        deploy_command += "FITHUB_DEPLOY_CHECK_PUBLIC=1 ./deploy.sh"
    else:
        deploy_command += "./deploy.sh"
    steps.append(
        CommandStep(
            "Run Tencent Cloud deployment",
            remote_shell(deploy_command, target=target, port=port, identity_file=identity_file),
        )
    )
    return steps


def run_steps(steps: list[CommandStep]) -> None:
    for step in steps:
        print(f"\n==> {step.label}")
        print("$", step.display())
        subprocess.run(step.command, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Upload and deploy a FitHub Tencent release to a server.")
    parser.add_argument("--host", required=True, help="Tencent Cloud server public IP or hostname.")
    parser.add_argument("--user", default="root", help="SSH username. Defaults to root.")
    parser.add_argument("--port", type=int, default=22, help="SSH port.")
    parser.add_argument("--identity-file", default="", help="Optional SSH private key.")
    parser.add_argument("--archive", default="", help="Release archive. Defaults to the latest dist/fithub-tencent-release-*.tar.gz.")
    parser.add_argument("--env-file", default=str(DEFAULT_ENV_FILE), help="Real .env.production to upload. This file is not committed.")
    parser.add_argument("--nginx-file", default=str(DEFAULT_NGINX_FILE), help="Generated nginx-fithub.conf to upload.")
    parser.add_argument("--skip-nginx", action="store_true", help="Do not upload nginx-fithub.conf.")
    parser.add_argument("--restart-nginx", action="store_true", help="Install nginx config to /etc/nginx/conf.d/fithub.conf and reload nginx.")
    parser.add_argument("--remote-dir", default=DEFAULT_REMOTE_DIR, help="Remote base directory. Defaults to /opt/fithub.")
    parser.add_argument("--check-public", action="store_true", help="Run public backend check after deploy.sh.")
    parser.add_argument("--apply", action="store_true", help="Actually run SSH/SCP commands. Omit for dry-run.")
    args = parser.parse_args()

    identity_file = Path(args.identity_file).expanduser() if args.identity_file else None
    archive = Path(args.archive).expanduser() if args.archive else latest_release_archive(ROOT / "dist")
    env_file = Path(args.env_file).expanduser()
    nginx_file = None if args.skip_nginx else Path(args.nginx_file).expanduser()

    try:
        validate_local_inputs(archive, env_file, nginx_file)
        steps = build_steps(
            host=args.host,
            user=args.user,
            port=args.port,
            identity_file=identity_file,
            archive=archive,
            env_file=env_file,
            nginx_file=nginx_file,
            remote_dir=args.remote_dir,
            check_public=args.check_public,
            restart_nginx=args.restart_nginx,
        )
    except (OSError, ValueError) as exc:
        print(f"Tencent remote deploy failed: {exc}", file=sys.stderr)
        return 1

    print("FitHub Tencent remote deployment " + ("apply" if args.apply else "dry run"))
    print(f"Archive: {archive}")
    print(f"SHA256: {build_tencent_release.file_sha256(archive)}")
    print(f"Remote: {ssh_target(args.user, args.host)}:{args.remote_dir}")
    for index, step in enumerate(steps, start=1):
        print(f"{index}. {step.label}: {step.display()}")

    if not args.apply:
        print("\nDry-run only. Re-run with --apply when the commands look right.")
        return 0

    try:
        run_steps(steps)
    except subprocess.CalledProcessError as exc:
        print(f"Tencent remote deploy command failed with exit code {exc.returncode}.", file=sys.stderr)
        return exc.returncode or 1
    print("\nFitHub Tencent remote deployment completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
