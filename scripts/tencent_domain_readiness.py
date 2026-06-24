#!/usr/bin/env python3
"""Validate DNS, ACME, and TLS readiness for FitHub Tencent Cloud domains."""

from __future__ import annotations

import argparse
import json
import socket
import ssl
import sys
import time
import urllib.parse
from pathlib import Path
from typing import Any, Callable, NamedTuple


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import production_readiness


DEFAULT_TIMEOUT_SECONDS = 5.0
DEFAULT_MIN_CERT_DAYS = 14


class DomainTarget(NamedTuple):
    role: str
    origin: str
    host: str


ProbeResolve = Callable[[str], list[str]]
ProbeTcp = Callable[[str, int, float], tuple[bool, str]]
ProbeTls = Callable[[str, float], dict[str, Any]]


def normalize_origin(value: str) -> str:
    raw = str(value or "").strip().rstrip("/")
    if not raw:
        raise ValueError("origin is missing")
    parsed = urllib.parse.urlparse(raw)
    if not parsed.scheme:
        raw = "https://" + raw
        parsed = urllib.parse.urlparse(raw)
    origin = f"{parsed.scheme}://{parsed.netloc}".rstrip("/")
    failures: list[str] = []
    production_readiness.validate_https_custom_url("Tencent domain", origin, failures)
    if failures:
        raise ValueError("; ".join(failures))
    return origin


def origin_host(origin: str) -> str:
    parsed = urllib.parse.urlparse(normalize_origin(origin))
    host = (parsed.hostname or "").lower()
    if not host:
        raise ValueError(f"Invalid origin: {origin}")
    return host


def build_targets(api_origin: str, web_origin: str = "", media_origin: str = "") -> list[DomainTarget]:
    raw_targets = [
        ("api", api_origin),
        ("web", web_origin),
        ("media", media_origin),
    ]
    targets: list[DomainTarget] = []
    seen: set[str] = set()
    for role, raw_origin in raw_targets:
        if not raw_origin:
            continue
        origin = normalize_origin(raw_origin)
        host = origin_host(origin)
        key = f"{role}:{host}"
        if key in seen:
            continue
        targets.append(DomainTarget(role=role, origin=origin, host=host))
        seen.add(key)
    if not targets:
        raise ValueError("At least --api-origin or --web-origin is required.")
    return targets


def resolve_host(host: str) -> list[str]:
    addresses: set[str] = set()
    infos = socket.getaddrinfo(host, None, proto=socket.IPPROTO_TCP)
    for info in infos:
        sockaddr = info[4]
        if sockaddr:
            addresses.add(str(sockaddr[0]))
    return sorted(addresses)


def tcp_connect(host: str, port: int, timeout: float = DEFAULT_TIMEOUT_SECONDS) -> tuple[bool, str]:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True, ""
    except OSError as exc:
        return False, str(exc)


def tls_probe(host: str, timeout: float = DEFAULT_TIMEOUT_SECONDS) -> dict[str, Any]:
    started = time.time()
    context = ssl.create_default_context()
    with socket.create_connection((host, 443), timeout=timeout) as sock:
        with context.wrap_socket(sock, server_hostname=host) as tls_sock:
            cert = tls_sock.getpeercert()
            cipher = tls_sock.cipher()
            not_after = str(cert.get("notAfter") or "")
            expires_at = ssl.cert_time_to_seconds(not_after) if not_after else 0
            sans = [value for key, value in cert.get("subjectAltName", []) if key == "DNS"]
            subject_parts = []
            for part in cert.get("subject", []):
                subject_parts.extend(f"{key}={value}" for key, value in part)
            return {
                "ok": True,
                "host": host,
                "subject": ", ".join(subject_parts),
                "sans": sans,
                "notAfter": not_after,
                "expiresAt": expires_at,
                "daysRemaining": max(0, int((expires_at - time.time()) / 86400)) if expires_at else 0,
                "cipher": cipher[0] if cipher else "",
                "elapsedMs": int((time.time() - started) * 1000),
            }


def check_target(
    target: DomainTarget,
    *,
    expected_ip: str = "",
    check_acme: bool = False,
    check_tls: bool = False,
    min_cert_days: int = DEFAULT_MIN_CERT_DAYS,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    resolver: ProbeResolve = resolve_host,
    tcp_probe: ProbeTcp = tcp_connect,
    tls_checker: ProbeTls = tls_probe,
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    target_result: dict[str, Any] = {
        "role": target.role,
        "origin": target.origin,
        "host": target.host,
        "ready": True,
        "addresses": [],
        "checks": checks,
    }

    try:
        addresses = resolver(target.host)
    except Exception as exc:
        addresses = []
        checks.append({"name": "dns", "ok": False, "detail": str(exc)})
    else:
        target_result["addresses"] = addresses
        checks.append(
            {
                "name": "dns",
                "ok": bool(addresses),
                "detail": ", ".join(addresses) if addresses else "no A/AAAA records resolved",
            }
        )

    if expected_ip:
        checks.append(
            {
                "name": "expected-ip",
                "ok": expected_ip in addresses,
                "detail": f"expected {expected_ip}; resolved {', '.join(addresses) or 'none'}",
            }
        )

    if check_acme:
        ok, detail = tcp_probe(target.host, 80, timeout)
        checks.append(
            {
                "name": "acme-http-01",
                "ok": ok,
                "detail": "port 80 reachable" if ok else f"port 80 unreachable: {detail}",
            }
        )

    if check_tls:
        ok, detail = tcp_probe(target.host, 443, timeout)
        checks.append(
            {
                "name": "https-port",
                "ok": ok,
                "detail": "port 443 reachable" if ok else f"port 443 unreachable: {detail}",
            }
        )
        if ok:
            try:
                tls = tls_checker(target.host, timeout)
            except Exception as exc:
                checks.append({"name": "tls-certificate", "ok": False, "detail": str(exc)})
            else:
                days_remaining = int(tls.get("daysRemaining") or 0)
                checks.append(
                    {
                        "name": "tls-certificate",
                        "ok": bool(tls.get("ok")) and days_remaining >= min_cert_days,
                        "detail": (
                            f"valid; expires in {days_remaining} days"
                            if bool(tls.get("ok")) and days_remaining >= min_cert_days
                            else f"certificate expires too soon: {days_remaining} days"
                        ),
                        "tls": tls,
                    }
                )

    target_result["ready"] = all(bool(item.get("ok")) for item in checks)
    return target_result


def build_report(
    *,
    api_origin: str,
    web_origin: str = "",
    media_origin: str = "",
    expected_ip: str = "",
    check_acme: bool = False,
    check_tls: bool = False,
    min_cert_days: int = DEFAULT_MIN_CERT_DAYS,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    resolver: ProbeResolve = resolve_host,
    tcp_probe: ProbeTcp = tcp_connect,
    tls_checker: ProbeTls = tls_probe,
) -> dict[str, Any]:
    targets = build_targets(api_origin, web_origin, media_origin)
    results = [
        check_target(
            target,
            expected_ip=expected_ip,
            check_acme=check_acme,
            check_tls=check_tls,
            min_cert_days=min_cert_days,
            timeout=timeout,
            resolver=resolver,
            tcp_probe=tcp_probe,
            tls_checker=tls_checker,
        )
        for target in targets
    ]
    blocker_count = sum(
        1
        for target in results
        for check in target["checks"]
        if not check.get("ok")
    )
    return {
        "ready": blocker_count == 0,
        "status": "ready" if blocker_count == 0 else "blocked",
        "blockerCount": blocker_count,
        "expectedIp": expected_ip,
        "checks": {
            "acme": check_acme,
            "tls": check_tls,
            "minCertDays": min_cert_days,
        },
        "domains": results,
    }


def print_markdown(report: dict[str, Any]) -> None:
    print(f"FitHub Tencent domain readiness: {report['status']}")
    if report.get("expectedIp"):
        print(f"Expected server IP: {report['expectedIp']}")
    print("")
    for domain in report["domains"]:
        status = "OK" if domain["ready"] else "BLOCKED"
        print(f"- {domain['role']} `{domain['host']}`: {status}")
        for check in domain["checks"]:
            marker = "OK" if check.get("ok") else "FAIL"
            print(f"  - {marker} {check['name']}: {check.get('detail') or ''}")
    if report["ready"]:
        print("\nAll requested domain checks passed.")
    else:
        print(f"\n{report['blockerCount']} domain readiness blocker(s) found.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate FitHub Tencent Cloud domain readiness.")
    parser.add_argument("--api-origin", required=True, help="Production API origin, e.g. https://api.example.cn")
    parser.add_argument("--web-origin", default="", help="Production web origin, e.g. https://app.example.cn")
    parser.add_argument("--media-origin", default="", help="Production media origin, e.g. https://media.example.cn")
    parser.add_argument("--expected-ip", default="", help="Tencent Cloud server public IP expected in DNS answers.")
    parser.add_argument("--check-acme", action="store_true", help="Require port 80 to be reachable for ACME HTTP-01.")
    parser.add_argument("--check-tls", action="store_true", help="Require port 443 and a valid TLS certificate.")
    parser.add_argument("--min-cert-days", type=int, default=DEFAULT_MIN_CERT_DAYS)
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    try:
        report = build_report(
            api_origin=args.api_origin,
            web_origin=args.web_origin,
            media_origin=args.media_origin,
            expected_ip=args.expected_ip,
            check_acme=args.check_acme,
            check_tls=args.check_tls,
            min_cert_days=args.min_cert_days,
            timeout=args.timeout,
        )
    except ValueError as exc:
        print(f"FitHub Tencent domain readiness failed: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print_markdown(report)
    return 0 if report["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
