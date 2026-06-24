#!/usr/bin/env python3
"""Bootstrap a Tencent Cloud host for FitHub deployments.

The script defaults to dry-run so the exact SSH/SCP steps can be reviewed
before installing Docker, Nginx, or other runtime packages on a server.
"""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REMOTE_DIR = "/opt/fithub"
DEFAULT_BOOTSTRAP_FILE = ROOT / "deploy" / "tencent-cloud" / "bootstrap-server.sh"


class CommandStep(NamedTuple):
    label: str
    command: list[str]

    def display(self) -> str:
        return " ".join(shlex.quote(part) for part in self.command)


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


def validate_local_inputs(bootstrap_file: Path) -> None:
    if not bootstrap_file.exists():
        raise FileNotFoundError(f"Missing bootstrap script: {bootstrap_file}")
    if not bootstrap_file.is_file():
        raise ValueError(f"Bootstrap path is not a file: {bootstrap_file}")


def build_steps(
    *,
    host: str,
    user: str = "root",
    port: int = 22,
    identity_file: Path | None = None,
    remote_dir: str = DEFAULT_REMOTE_DIR,
    bootstrap_file: Path = DEFAULT_BOOTSTRAP_FILE,
) -> list[CommandStep]:
    target = ssh_target(user, host)
    remote_script = "/tmp/fithub-bootstrap-server.sh"
    remote_dir = "/" + str(remote_dir or DEFAULT_REMOTE_DIR).strip("/")
    return [
        CommandStep(
            "Upload server bootstrap script",
            [*scp_base_args(port=port, identity_file=identity_file), str(bootstrap_file), f"{target}:{remote_script}"],
        ),
        CommandStep(
            "Run server bootstrap script",
            remote_shell(
                f"chmod +x {shlex.quote(remote_script)}; FITHUB_REMOTE_DIR={shlex.quote(remote_dir)} {shlex.quote(remote_script)}",
                target=target,
                port=port,
                identity_file=identity_file,
            ),
        ),
    ]


def run_steps(steps: list[CommandStep]) -> None:
    for step in steps:
        print(f"\n==> {step.label}")
        print("$", step.display())
        subprocess.run(step.command, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap a Tencent Cloud server for FitHub.")
    parser.add_argument("--host", required=True, help="Tencent Cloud server public IP or hostname.")
    parser.add_argument("--user", default="root", help="SSH username. Defaults to root.")
    parser.add_argument("--port", type=int, default=22, help="SSH port.")
    parser.add_argument("--identity-file", default="", help="Optional SSH private key.")
    parser.add_argument("--remote-dir", default=DEFAULT_REMOTE_DIR, help="Remote base directory. Defaults to /opt/fithub.")
    parser.add_argument("--bootstrap-file", default=str(DEFAULT_BOOTSTRAP_FILE), help="Local bootstrap-server.sh path.")
    parser.add_argument("--apply", action="store_true", help="Actually run SSH/SCP commands. Omit for dry-run.")
    args = parser.parse_args()

    identity_file = Path(args.identity_file).expanduser() if args.identity_file else None
    bootstrap_file = Path(args.bootstrap_file).expanduser()
    try:
        validate_local_inputs(bootstrap_file)
        steps = build_steps(
            host=args.host,
            user=args.user,
            port=args.port,
            identity_file=identity_file,
            remote_dir=args.remote_dir,
            bootstrap_file=bootstrap_file,
        )
    except (OSError, ValueError) as exc:
        print(f"Tencent remote bootstrap failed: {exc}", file=sys.stderr)
        return 1

    print("FitHub Tencent remote bootstrap " + ("apply" if args.apply else "dry run"))
    print(f"Remote: {ssh_target(args.user, args.host)}:{args.remote_dir}")
    for index, step in enumerate(steps, start=1):
        print(f"{index}. {step.label}: {step.display()}")

    if not args.apply:
        print("\nDry-run only. Re-run with --apply when the commands look right.")
        return 0

    try:
        run_steps(steps)
    except subprocess.CalledProcessError as exc:
        print(f"Tencent remote bootstrap command failed with exit code {exc.returncode}.", file=sys.stderr)
        return exc.returncode or 1
    print("\nFitHub Tencent remote bootstrap completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
