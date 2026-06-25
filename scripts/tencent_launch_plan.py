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


def manual_item(label: str, value: str, config: dict[str, str], required: list[str], detail: str = "") -> dict[str, Any]:
    missing = [key for key in required if is_missing(config, key)]
    return {
        "label": label,
        "value": value,
        "detail": detail,
        "ready": not missing,
        "missing": missing,
    }


def build_wechat_domain_tasks(config: dict[str, str], api_origin: str, media_origin: str) -> list[dict[str, Any]]:
    download_origin = media_origin or api_origin
    return [
        manual_item(
            "request 合法域名",
            api_origin,
            config,
            ["apiOrigin"],
            "微信公众平台 -> 开发管理 -> 开发设置 -> 服务器域名。",
        ),
        manual_item(
            "uploadFile 合法域名",
            api_origin,
            config,
            ["apiOrigin"],
            "头像、动态图片和视频上传会走 API 域名。",
        ),
        manual_item(
            "downloadFile 合法域名",
            download_origin,
            config,
            ["mediaOrigin"],
            "正式环境应使用腾讯 COS/CDN 媒体域名，避免图片/视频走 API 服务。",
        ),
        {
            "label": "socket 合法域名",
            "value": "暂无",
            "detail": "当前版本没有 WebSocket；以后做实时聊天再配置。",
            "ready": True,
            "missing": [],
        },
    ]


def build_manual_checks(config: dict[str, str], api_origin: str, web_origin: str, media_origin: str) -> list[dict[str, Any]]:
    return [
        manual_item(
            "微信小程序真实 AppID",
            value(config, "miniappAppId", "wx你的真实小程序AppID"),
            config,
            ["miniappAppId"],
            "必须来自企业主体小程序，不能继续使用 touristappid。",
        ),
        manual_item(
            "备案后的 Web 用户访问域名",
            web_origin,
            config,
            ["webOrigin"],
            "正式用户入口，例如 https://app.yourdomain.com。",
        ),
        manual_item(
            "备案后的 API 服务域名",
            api_origin,
            config,
            ["apiOrigin"],
            "小程序 request/uploadFile 合法域名都依赖它。",
        ),
        manual_item(
            "腾讯 COS/CDN 媒体域名",
            media_origin,
            config,
            ["mediaOrigin", "cosSecretId", "cosSecretKey", "cosBucket"],
            "正式媒体下载域名，用于头像、动态图片、视频和缩略图。",
        ),
        manual_item(
            "发布前生产数据快照权限",
            "FITHUB_ADMIN_TOKEN",
            config,
            ["adminToken"],
            "用于上线前后快照对比，防止用户、关注、消息、预约数据丢失。",
        ),
        {
            "label": "隐私协议与权限说明",
            "value": "定位、相册/摄像头、运动健康数据、私信与社区内容",
            "detail": "小程序提审材料需要与实际功能一致；未接入的能力不要写成已接入。",
            "ready": True,
            "missing": [],
        },
    ]


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
    before_snapshot = value(config, "beforeSnapshot", "<BEFORE_SNAPSHOT_JSON>")
    after_snapshot = value(config, "afterSnapshot", "<AFTER_SNAPSHOT_JSON>")
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
            "发布前生产数据快照",
            [
                "env",
                "FITHUB_ADMIN_TOKEN=<FITHUB_ADMIN_TOKEN>",
                "npm",
                "run",
                "snapshot:prod",
                "--",
                "--backend-url",
                api_origin,
                "--output-dir",
                "backups/tencent-cutover-before",
            ],
            config,
            ["apiOrigin", "adminToken"],
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
            "发布后生产数据快照并对比",
            [
                "env",
                "FITHUB_ADMIN_TOKEN=<FITHUB_ADMIN_TOKEN>",
                "npm",
                "run",
                "snapshot:prod",
                "--",
                "--backend-url",
                api_origin,
                "--compare",
                before_snapshot,
                "--output-dir",
                "backups/tencent-cutover-after",
            ],
            config,
            ["apiOrigin", "adminToken"],
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
        step(
            "生成上线证据报告",
            [
                "npm",
                "run",
                "evidence:tencent-launch",
                "--",
                "--frontend-url",
                web_origin + "/",
                "--backend-url",
                api_origin,
                "--release-archive",
                release_archive,
                "--snapshot",
                after_snapshot,
                "--check-live",
            ],
            config,
            ["apiOrigin", "webOrigin"],
        ),
    ]

    missing = sorted({key for item in steps for key in item.missing})
    wechat_domains = build_wechat_domain_tasks(config, api_origin, media_origin)
    manual_checks = build_manual_checks(config, api_origin, web_origin, media_origin)
    missing = sorted(
        {
            *missing,
            *(key for item in wechat_domains for key in item["missing"]),
            *(key for item in manual_checks for key in item["missing"]),
        }
    )
    return {
        "ready": not missing,
        "missing": missing,
        "config": redact_config(config),
        "wechatDomains": wechat_domains,
        "manualChecks": manual_checks,
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
    print("## 微信公众平台后台配置")
    print("")
    print("在“开发管理 -> 开发设置 -> 服务器域名”中配置以下域名：")
    print("")
    for item in plan["wechatDomains"]:
        mark = "OK" if item["ready"] else "WAIT"
        print(f"- [{mark}] {item['label']}: {item['value']}")
        if item["detail"]:
            print(f"  - {item['detail']}")
        if item["missing"]:
            print(f"  - 缺少：{', '.join(item['missing'])}")
    print("")
    print("## 发布前人工核对")
    print("")
    for item in plan["manualChecks"]:
        mark = "OK" if item["ready"] else "WAIT"
        print(f"- [{mark}] {item['label']}: {item['value']}")
        if item["detail"]:
            print(f"  - {item['detail']}")
        if item["missing"]:
            print(f"  - 缺少：{', '.join(item['missing'])}")
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
            "adminToken": "你的FITHUB_ADMIN_TOKEN",
            "cosSecretId": "你的腾讯云COSSecretId",
            "cosSecretKey": "你的腾讯云COSSecretKey",
            "cosRegion": "ap-guangzhou",
            "cosBucket": "fithub-media-1250000000",
            "mediaMaintenanceToken": "你的FITHUB_MEDIA_MAINTENANCE_TOKEN",
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
