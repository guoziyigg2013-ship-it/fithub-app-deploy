#!/usr/bin/env python3
"""Issue Let's Encrypt certificates on a Tencent Cloud host for FitHub."""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
import tempfile
import urllib.parse
from pathlib import Path
from typing import NamedTuple


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import production_readiness


ROOT = Path(__file__).resolve().parent.parent
ACME_TEMPLATE = ROOT / "deploy" / "tencent-cloud" / "nginx-acme-bootstrap.conf.example"


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


def origin_host(value: str) -> str:
    raw = str(value or "").strip().rstrip("/")
    parsed = urllib.parse.urlparse(raw)
    if not parsed.scheme:
        parsed = urllib.parse.urlparse("https://" + raw)
    host = (parsed.hostname or "").lower()
    if not host:
        raise ValueError(f"Invalid domain or origin: {value}")
    origin = "https://" + host
    failures: list[str] = []
    production_readiness.validate_https_custom_url("TLS domain", origin, failures)
    if failures:
        raise ValueError("; ".join(failures))
    return host


def parse_domains(api_origin: str, web_origin: str = "", extra_domains: list[str] | None = None) -> list[str]:
    domains = [origin_host(api_origin)]
    if web_origin:
        domains.append(origin_host(web_origin))
    for domain in extra_domains or []:
        domains.append(origin_host(domain))
    unique: list[str] = []
    for domain in domains:
        if domain not in unique:
            unique.append(domain)
    return unique


def render_acme_config(domains: list[str]) -> str:
    if not domains:
        raise ValueError("At least one domain is required.")
    template = ACME_TEMPLATE.read_text(encoding="utf-8")
    return template.replace("api.yourdomain.com app.yourdomain.com", " ".join(domains))


def write_temp_acme_config(domains: list[str]) -> Path:
    temp_dir = Path(tempfile.mkdtemp(prefix="fithub-acme-"))
    path = temp_dir / "fithub-acme-bootstrap.conf"
    path.write_text(render_acme_config(domains), encoding="utf-8")
    return path


def build_certbot_command(domains: list[str], *, email: str, staging: bool = False) -> str:
    if not email or "@" not in email:
        raise ValueError("--email must be a valid contact email for Let's Encrypt.")
    domain_args = " ".join(f"-d {shlex.quote(domain)}" for domain in domains)
    staging_arg = " --staging" if staging else ""
    return (
        "set -e; "
        "mkdir -p /var/www/certbot /etc/nginx/conf.d; "
        "cp /tmp/fithub-acme-bootstrap.conf /etc/nginx/conf.d/fithub-acme-bootstrap.conf; "
        "nginx -t; "
        "systemctl reload nginx || service nginx reload; "
        "certbot certonly --webroot -w /var/www/certbot "
        f"{domain_args} "
        f"--email {shlex.quote(email)} --agree-tos --non-interactive --keep-until-expiring{staging_arg}; "
        "systemctl reload nginx || service nginx reload"
    )


def build_steps(
    *,
    host: str,
    user: str = "root",
    port: int = 22,
    identity_file: Path | None = None,
    api_origin: str,
    web_origin: str = "",
    extra_domains: list[str] | None = None,
    email: str,
    staging: bool = False,
    acme_config: Path | None = None,
) -> tuple[list[CommandStep], list[str]]:
    domains = parse_domains(api_origin, web_origin, extra_domains)
    target = ssh_target(user, host)
    acme_config = acme_config or write_temp_acme_config(domains)
    steps = [
        CommandStep(
            "Upload ACME bootstrap Nginx config",
            [*scp_base_args(port=port, identity_file=identity_file), str(acme_config), f"{target}:/tmp/fithub-acme-bootstrap.conf"],
        ),
        CommandStep(
            "Issue Let's Encrypt certificate",
            remote_shell(
                build_certbot_command(domains, email=email, staging=staging),
                target=target,
                port=port,
                identity_file=identity_file,
            ),
        ),
    ]
    return steps, domains


def run_steps(steps: list[CommandStep]) -> None:
    for step in steps:
        print(f"\n==> {step.label}")
        print("$", step.display())
        subprocess.run(step.command, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Issue FitHub HTTPS certificates on a Tencent Cloud server.")
    parser.add_argument("--host", required=True, help="Tencent Cloud server public IP or hostname.")
    parser.add_argument("--user", default="root", help="SSH username. Defaults to root.")
    parser.add_argument("--port", type=int, default=22, help="SSH port.")
    parser.add_argument("--identity-file", default="", help="Optional SSH private key.")
    parser.add_argument("--api-origin", required=True, help="Production API origin, e.g. https://api.example.cn")
    parser.add_argument("--web-origin", default="", help="Optional Web origin, e.g. https://app.example.cn")
    parser.add_argument("--domain", action="append", default=[], help="Additional domain to include in the certificate.")
    parser.add_argument("--email", required=True, help="Let's Encrypt contact email.")
    parser.add_argument("--staging", action="store_true", help="Use Let's Encrypt staging environment for a dry certificate trial.")
    parser.add_argument("--apply", action="store_true", help="Actually run SSH/SCP commands. Omit for dry-run.")
    args = parser.parse_args()

    identity_file = Path(args.identity_file).expanduser() if args.identity_file else None
    try:
        steps, domains = build_steps(
            host=args.host,
            user=args.user,
            port=args.port,
            identity_file=identity_file,
            api_origin=args.api_origin,
            web_origin=args.web_origin,
            extra_domains=args.domain,
            email=args.email,
            staging=args.staging,
        )
    except (OSError, ValueError) as exc:
        print(f"Tencent remote certbot failed: {exc}", file=sys.stderr)
        return 1

    print("FitHub Tencent remote certificate " + ("apply" if args.apply else "dry run"))
    print(f"Remote: {ssh_target(args.user, args.host)}")
    print("Domains: " + ", ".join(domains))
    for index, step in enumerate(steps, start=1):
        print(f"{index}. {step.label}: {step.display()}")

    if not args.apply:
        print("\nDry-run only. Re-run with --apply when DNS points to this server and commands look right.")
        return 0

    try:
        run_steps(steps)
    except subprocess.CalledProcessError as exc:
        print(f"Tencent remote certbot command failed with exit code {exc.returncode}.", file=sys.stderr)
        return exc.returncode or 1
    print("\nFitHub Tencent remote certificate completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
