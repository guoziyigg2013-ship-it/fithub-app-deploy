#!/usr/bin/env python3
"""Create a secret-safe Tencent Cloud launch command plan for FitHub."""

from __future__ import annotations

import argparse
import json
import shlex
import sys
from pathlib import Path
from typing import Any, NamedTuple


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = ROOT / "deploy" / "tencent-cloud" / "launch-plan.example.json"
SENSITIVE_KEYS = {
    "supabaseServiceRoleKey",
    "cosSecretKey",
    "adminToken",
    "mediaMaintenanceToken",
}


class PlanStep(NamedTuple):
    label: str
    command: list[str]
    missing: list[str] = []

    def display(self) -> str:
        return " ".join(shlex.quote(part) for part in self.command)

    @property
    def ready(self) -> bool:
        return not self.missing


def load_config(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("launch plan config must be a JSON object")
    return {str(key): str(value) for key, value in raw.items() if value is not None}


def value(config: dict[str, str], key: str, placeholder: str) -> str:
    raw = str(config.get(key) or "").strip()
    return raw or placeholder


def is_missing(config: dict[str, str], key: str) -> bool:
    raw = str(config.get(key) or "").strip()
    if not raw:
        return True
    lowered = raw.lower()
    return any(token in lowered for token in ("your", "example", "你的", "占位", "<", ">"))


def redact_config(config: dict[str, str]) -> dict[str, str]:
    redacted: dict[str, str] = {}
    for key, val in config.items():
        if key in SENSITIVE_KEYS and val:
            redacted[key] = val[:6] + "..." + val[-4:] if len(val) > 12 else "***"
        else:
            redacted[key] = val
    return redacted


def step(label: str, command: list[str], config: dict[str, str], required: list[str]) -> PlanStep:
    return PlanStep(label=label, command=command, missing=[key for key in required if is_missing(config, key)])


def build_plan(config: dict[str, str]) -> dict[str, Any]:
    api_origin = value(config, "apiOrigin", "https://api.yourdomain.com")
    web_origin = value(config, "webOrigin", "https://app.yourdomain.com")
    media_origin = value(config, "mediaOrigin", "https://media.yourdomain.com")
    miniapp_appid = value(config, "miniappAppId", "wx你的真实小程序AppID")
    supabase_url = value(config, "supabaseUrl", "https://你的项目ref.supabase.co")
    supabase_key = value(config, "supabaseServiceRoleKey", "你的service_role")
    server_ip = value(config, "serverIp", "你的服务器公网IP")
    ssh_user = value(config, "sshUser", "root")
    ssh_key = value(config, "sshKey", "~/.ssh/你的腾讯云密钥")
    cert_email = value(config, "certEmail", "你的证书通知邮箱")
    release_version = value(config, "releaseVersion", "production-cutover")
    release_archive = value(config, "releaseArchive", f"dist/fithub-tencent-release-{release_version}.tar.gz")
    cos_secret_id = value(config, "cosSecretId", "你的腾讯云COSSecretId")
    cos_secret_key = value(config, "cosSecretKey", "你的腾讯云COSSecretKey")
    cos_region = value(config, "cosRegion", "ap-guangzhou")
    cos_bucket = value(config, "cosBucket", "fithub-media-1250000000")

    steps = [
        step(
            "生成腾讯云发布包",
            ["npm", "run", "release:tencent", "--", "--version", release_version],
            config,
            [],
        ),
        step(
            "切换 Web/小程序配置并生成生产 env",
            [
                "npm",
                "run",
                "cutover:tencent",
                "--",
                "--api-origin",
                api_origin,
                "--web-origin",
                web_origin,
                "--miniapp-appid",
                miniapp_appid,
                "--supabase-url",
                supabase_url,
                "--supabase-service-role-key",
                "<SUPABASE_SERVICE_ROLE_KEY>",
                "--media-storage-provider",
                "cos",
                "--cos-secret-id",
                cos_secret_id,
                "--cos-secret-key",
                "<COS_SECRET_KEY>",
                "--cos-region",
                cos_region,
                "--cos-bucket",
                cos_bucket,
                "--cos-public-base-url",
                media_origin,
                "--apply",
                "--write-env",
                "--force",
            ],
            config,
            ["apiOrigin", "webOrigin", "miniappAppId", "supabaseUrl", "supabaseServiceRoleKey", "cosSecretId", "cosSecretKey", "cosBucket", "mediaOrigin"],
        ),
        step(
            "初始化腾讯云服务器",
            [
                "npm",
                "run",
                "bootstrap:tencent-remote",
                "--",
                "--host",
                server_ip,
                "--user",
                ssh_user,
                "--identity-file",
                ssh_key,
                "--remote-dir",
                "/opt/fithub",
                "--apply",
            ],
            config,
            ["serverIp", "sshKey"],
        ),
        step(
            "检查 DNS 与 ACME 端口",
            [
                "npm",
                "run",
                "check:tencent-domains",
                "--",
                "--api-origin",
                api_origin,
                "--web-origin",
                web_origin,
                "--media-origin",
                media_origin,
                "--expected-ip",
                server_ip,
                "--check-acme",
            ],
            config,
            ["apiOrigin", "webOrigin", "mediaOrigin", "serverIp"],
        ),
        step(
            "签发 HTTPS 证书",
            [
                "npm",
                "run",
                "cert:tencent-remote",
                "--",
                "--host",
                server_ip,
                "--user",
                ssh_user,
                "--identity-file",
                ssh_key,
                "--api-origin",
                api_origin,
                "--web-origin",
                web_origin,
                "--email",
                cert_email,
                "--apply",
            ],
            config,
            ["serverIp", "sshKey", "apiOrigin", "webOrigin", "certEmail"],
        ),
        step(
            "检查 HTTPS/TLS",
            [
                "npm",
                "run",
                "check:tencent-domains",
                "--",
                "--api-origin",
                api_origin,
                "--web-origin",
                web_origin,
                "--media-origin",
                media_origin,
                "--expected-ip",
                server_ip,
                "--check-acme",
                "--check-tls",
            ],
            config,
            ["apiOrigin", "webOrigin", "mediaOrigin", "serverIp"],
        ),
        step(
            "上传并部署腾讯云发布包",
            [
                "npm",
                "run",
                "deploy:tencent-remote",
                "--",
                "--host",
                server_ip,
                "--user",
                ssh_user,
                "--identity-file",
                ssh_key,
                "--archive",
                release_archive,
                "--env-file",
                "deploy/tencent-cloud/.env.production",
                "--nginx-file",
                "deploy/tencent-cloud/nginx-fithub.conf",
                "--remote-dir",
                "/opt/fithub",
                "--check-public",
                "--restart-nginx",
                "--apply",
            ],
            config,
            ["serverIp", "sshKey"],
        ),
        step(
            "运行腾讯云上线总控门禁",
            [
                "npm",
                "run",
                "check:tencent-launch",
                "--",
                "--api-origin",
                api_origin,
                "--web-origin",
                web_origin,
                "--media-origin",
                media_origin,
                "--expected-ip",
                server_ip,
                "--check-domain-network",
                "--check-acme",
                "--check-tls",
                "--check-live",
            ],
            config,
            ["apiOrigin", "webOrigin", "mediaOrigin", "serverIp"],
        ),
        step(
            "运行最终验收",
            [
                "npm",
                "run",
                "check:final",
                "--",
                "--production-frontend-url",
                web_origin + "/",
                "--production-backend-url",
                api_origin,
                "--verify-frontend-api-origin",
                "--require-cos-media",
            ],
            config,
            ["apiOrigin", "webOrigin"],
        ),
    ]

    missing = sorted({key for item in steps for key in item.missing})
    return {
        "ready": not missing,
        "missing": missing,
        "config": redact_config(config),
        "steps": [
            {
                "label": item.label,
                "command": item.command,
                "display": item.display(),
                "ready": item.ready,
                "missing": item.missing,
            }
            for item in steps
        ],
    }


def print_markdown(plan: dict[str, Any], config_path: Path) -> None:
    print("# FitHub 腾讯云上线执行计划")
    print("")
    print(f"- 配置文件：{config_path}")
    print(f"- 状态：{'ready' if plan['ready'] else 'missing-inputs'}")
    if plan["missing"]:
        print("- 缺少输入：" + ", ".join(plan["missing"]))
    print("")
    for index, item in enumerate(plan["steps"], start=1):
        mark = "OK" if item["ready"] else "WAIT"
        print(f"## {index}. {item['label']} [{mark}]")
        if item["missing"]:
            print("缺少：" + ", ".join(item["missing"]))
        print("")
        print("```bash")
        print(item["display"])
        print("```")
        print("")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a FitHub Tencent Cloud launch command plan.")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="JSON file with Tencent launch inputs.")
    parser.add_argument("--write-example", action="store_true", help="Write an example config file if it does not exist.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    config_path = Path(args.config)
    if args.write_example:
        example = {
            "apiOrigin": "https://api.yourdomain.com",
            "webOrigin": "https://app.yourdomain.com",
            "mediaOrigin": "https://media.yourdomain.com",
            "miniappAppId": "wx你的真实小程序AppID",
            "serverIp": "你的服务器公网IP",
            "sshUser": "root",
            "sshKey": "~/.ssh/你的腾讯云密钥",
            "certEmail": "ops@example.com",
            "releaseVersion": "production-cutover",
            "releaseArchive": "dist/fithub-tencent-release-production-cutover.tar.gz",
            "supabaseUrl": "https://你的项目ref.supabase.co",
            "supabaseServiceRoleKey": "你的service_role",
            "cosSecretId": "你的腾讯云COSSecretId",
            "cosSecretKey": "你的腾讯云COSSecretKey",
            "cosRegion": "ap-guangzhou",
            "cosBucket": "fithub-media-1250000000",
        }
        config_path.parent.mkdir(parents=True, exist_ok=True)
        if not config_path.exists():
            config_path.write_text(json.dumps(example, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    try:
        config = load_config(config_path)
        plan = build_plan(config)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"FitHub Tencent launch plan failed: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
    else:
        print_markdown(plan, config_path)
    return 0 if plan["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
