import argparse
import base64
import hashlib
import hmac
import json
import mimetypes
import os
import re
import secrets
import sys
import threading
import time
import uuid
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlencode, urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent


def read_int_env(name, default, minimum=None):
    raw_value = os.getenv(name)
    try:
        value = int(str(raw_value if raw_value is not None else default).strip())
    except (TypeError, ValueError):
        value = int(default)
    if minimum is not None:
        value = max(int(minimum), value)
    return value


def normalize_url_prefix(raw_value):
    value = (raw_value or "").strip()
    if not value or value == "/":
        return ""
    return "/" + value.strip("/")


def default_data_dir():
    render_disk_root = Path("/var/data")
    if render_disk_root.exists():
        return (render_disk_root / "fithub").resolve()
    return (ROOT / "data").resolve()


URL_PREFIX = normalize_url_prefix(os.getenv("FITHUB_URL_PREFIX", "/"))
DATA_DIR = Path(os.getenv("FITHUB_DATA_DIR", str(default_data_dir()))).expanduser().resolve()
STATE_FILE = DATA_DIR / "shared_state.json"
SUPABASE_URL = (os.getenv("SUPABASE_URL") or "").strip().rstrip("/")
SUPABASE_SERVICE_ROLE_KEY = (os.getenv("SUPABASE_SERVICE_ROLE_KEY") or "").strip()
SUPABASE_STATE_TABLE = (os.getenv("FITHUB_SUPABASE_TABLE") or "fithub_app_state").strip()
SUPABASE_STATE_ROW_ID = (os.getenv("FITHUB_SUPABASE_ROW_ID") or "primary").strip()
SUPABASE_TIMEOUT_SECONDS = float(os.getenv("FITHUB_SUPABASE_TIMEOUT") or "12")
SUPABASE_BACKUP_RETENTION = read_int_env("FITHUB_SUPABASE_BACKUP_RETENTION", 96, minimum=4)
SUPABASE_BACKUP_PRUNE_INTERVAL_SECONDS = read_int_env("FITHUB_SUPABASE_PRUNE_INTERVAL_SECONDS", 3600, minimum=60)
SUPABASE_BACKUP_PREFIX = f"{SUPABASE_STATE_ROW_ID}-backup"
SUPABASE_PHONE_RECOVERY_PREFIX = f"{SUPABASE_STATE_ROW_ID}-phone"
MAP_PROVIDER = (os.getenv("FITHUB_MAP_PROVIDER") or "").strip().lower()
AMAP_WEB_KEY = (os.getenv("FITHUB_AMAP_WEB_KEY") or "").strip()
AMAP_SECURITY_CODE = (os.getenv("FITHUB_AMAP_SECURITY_CODE") or "").strip()
BAIDU_MAP_AK = (os.getenv("FITHUB_BAIDU_MAP_AK") or "").strip()
SUPABASE_MEDIA_BUCKET = (os.getenv("FITHUB_MEDIA_BUCKET") or "fithub-media").strip()
MEDIA_IMAGE_LIMIT_BYTES = int(os.getenv("FITHUB_IMAGE_UPLOAD_LIMIT_BYTES") or str(10 * 1024 * 1024))
MEDIA_VIDEO_LIMIT_BYTES = int(os.getenv("FITHUB_VIDEO_UPLOAD_LIMIT_BYTES") or str(8 * 1024 * 1024))
MEDIA_THUMB_LIMIT_BYTES = int(os.getenv("FITHUB_THUMB_UPLOAD_LIMIT_BYTES") or str(2 * 1024 * 1024))
MEDIA_MAINTENANCE_TOKEN = (os.getenv("FITHUB_MEDIA_MAINTENANCE_TOKEN") or "").strip()
ADMIN_TOKEN = (os.getenv("FITHUB_ADMIN_TOKEN") or MEDIA_MAINTENANCE_TOKEN).strip()
PUBLIC_API_ORIGIN = (os.getenv("FITHUB_PUBLIC_API_ORIGIN") or "").strip().rstrip("/")
SMS_PROVIDER = (os.getenv("FITHUB_SMS_PROVIDER") or "").strip().lower()
SMS_CODE_LENGTH = int(os.getenv("FITHUB_SMS_CODE_LENGTH") or "6")
SMS_CODE_TTL_SECONDS = int(os.getenv("FITHUB_SMS_CODE_TTL_SECONDS") or "300")
SMS_RESEND_SECONDS = int(os.getenv("FITHUB_SMS_RESEND_SECONDS") or "60")
SMS_HASH_SALT = (os.getenv("FITHUB_SMS_CODE_SALT") or SUPABASE_SERVICE_ROLE_KEY or "fithub-sms").strip()
SMS_DEV_MODE = str(os.getenv("FITHUB_SMS_DEV_MODE") or "").strip().lower() in {"1", "true", "yes", "on"}
TENCENT_SMS_SECRET_ID = (os.getenv("FITHUB_TENCENT_SMS_SECRET_ID") or "").strip()
TENCENT_SMS_SECRET_KEY = (os.getenv("FITHUB_TENCENT_SMS_SECRET_KEY") or "").strip()
TENCENT_SMS_APP_ID = (os.getenv("FITHUB_TENCENT_SMS_APP_ID") or "").strip()
TENCENT_SMS_SIGN_NAME = (os.getenv("FITHUB_TENCENT_SMS_SIGN_NAME") or "").strip()
TENCENT_SMS_TEMPLATE_ID = (os.getenv("FITHUB_TENCENT_SMS_TEMPLATE_ID") or "").strip()
TENCENT_SMS_REGION = (os.getenv("FITHUB_TENCENT_SMS_REGION") or "ap-guangzhou").strip()
WECHAT_MINIAPP_APP_ID = (os.getenv("FITHUB_WECHAT_MINIAPP_APP_ID") or "").strip()
WECHAT_MINIAPP_APP_SECRET = (os.getenv("FITHUB_WECHAT_MINIAPP_APP_SECRET") or "").strip()
WECHAT_MINIAPP_DEV_MODE = str(os.getenv("FITHUB_WECHAT_MINIAPP_DEV_MODE") or "").strip().lower() in {"1", "true", "yes", "on"}


def url_with_prefix(path="/"):
    clean_path = "/" + str(path or "/").lstrip("/")
    if clean_path == "//":
        clean_path = "/"
    return f"{URL_PREFIX}{clean_path}" if URL_PREFIX else clean_path


API_PREFIX = url_with_prefix("/api")


def strip_url_prefix(path):
    if URL_PREFIX:
        if path == URL_PREFIX:
            return ""
        if path.startswith(f"{URL_PREFIX}/"):
            return path[len(URL_PREFIX):]
        return None
    return path


def runtime_config():
    provider = MAP_PROVIDER if MAP_PROVIDER in {"amap", "baidu"} else ""
    if not provider:
        if AMAP_WEB_KEY:
            provider = "amap"
        elif BAIDU_MAP_AK:
            provider = "baidu"

    return {
        "mapProvider": provider,
        "amapKey": AMAP_WEB_KEY,
        "amapSecurityCode": AMAP_SECURITY_CODE,
        "baiduAk": BAIDU_MAP_AK,
        "mediaStorageProvider": "supabase" if supabase_media_storage_enabled() else "",
        "mediaBucket": SUPABASE_MEDIA_BUCKET if supabase_media_storage_enabled() else "",
        "mediaLimits": {
            "imageBytes": MEDIA_IMAGE_LIMIT_BYTES,
            "videoBytes": MEDIA_VIDEO_LIMIT_BYTES,
            "thumbnailBytes": MEDIA_THUMB_LIMIT_BYTES,
        },
        "smsEnabled": sms_verification_enabled(),
        "smsProvider": SMS_PROVIDER if sms_provider_configured() else ("debug" if SMS_DEV_MODE else ""),
        "wechatMiniappEnabled": bool(WECHAT_MINIAPP_APP_ID and WECHAT_MINIAPP_APP_SECRET) or WECHAT_MINIAPP_DEV_MODE,
    }


def client_runtime_config():
    config = {"apiOrigin": PUBLIC_API_ORIGIN}
    config.update(runtime_config())
    return config

DEFAULT_POSITION = {
    "key": "xiamen",
    "city": "厦门",
    "district": "思明区",
    "label": "厦门 · 思明区",
    "lat": 24.4798,
    "lng": 118.0894,
    "source": "default",
}

DEFAULT_LOCATION_STATUS = "默认城市为厦门，你可以点击顶部城市切换成自己的城市或使用实时定位。"

STORE_LOCK = threading.Lock()
STATE_CACHE = None
SUPABASE_MEDIA_BUCKET_READY = False
SUPABASE_LAST_BACKUP_PRUNE_TS = 0.0
STATE_RUNTIME_META = {
    "loaded_from": "uninitialized",
    "supabase_writable": True,
    "last_known_remote_real_profiles": 0,
    "last_known_remote_signal_score": 0,
    "remote_repair_required": False,
    "supabase_config_valid": True,
}
MAX_INLINE_AVATAR_CHARS = 120_000
MAX_INLINE_MEDIA_CHARS = 12_000_000
LEGACY_DEMO_ENTHUSIAST_IDS = {"enthusiast-demo-a", "enthusiast-demo-b"}
NATIVE_DEVICE_LABELS = {
    "apple-health": "Apple Health",
    "apple-healthkit": "Apple Health",
    "apple-watch": "Apple Watch",
    "healthkit": "Apple Health",
    "health-connect": "Health Connect",
    "xiaomi-watch": "小米手表",
    "xiaomi-scale": "小米智能秤",
}
NATIVE_WORKOUT_SPORT_MAP = {
    "running": ("run", "户外跑步"),
    "walking": ("outdoor-walk", "户外行走"),
    "hiking": ("hiking", "徒步"),
    "cycling": ("outdoor-cycling", "户外骑行"),
    "indoorcycling": ("cycling", "室内骑行"),
    "swimming": ("swim", "泳池游泳"),
    "yoga": ("yoga", "瑜伽"),
    "pilates": ("pilates", "普拉提"),
    "traditionalstrengthtraining": ("strength", "传统力量训练"),
    "functionalstrengthtraining": ("strength", "传统力量训练"),
    "strengthtraining": ("strength", "传统力量训练"),
    "highintensityintervaltraining": ("hiit", "HIIT"),
    "rowing": ("rowing", "划船机"),
    "elliptical": ("elliptical", "椭圆机"),
    "stairclimbing": ("stairs", "爬楼梯"),
    "mixedcardio": ("cardio-mix", "混合有氧"),
}


def now_utc():
    return datetime.now(timezone.utc)


def iso_at(minutes_ago=0):
    return (now_utc() - timedelta(minutes=minutes_ago)).isoformat()


def local_time_label(value=None):
    current = value or now_utc()
    return current.astimezone(timezone(timedelta(hours=8))).strftime("%m-%d %H:%M")


def data_uri_svg(svg):
    return f"data:image/svg+xml;charset=UTF-8,{quote(svg)}"


def demo_asset(name):
    return f"assets/demo/{name}"


def demo_image(title, accent_a, accent_b):
    is_coach_scene = any(token in str(title or "") for token in ["教练", "私教", "普拉提", "塑形", "动作", "训练"])
    scene_markup = (
        f"""
            <rect x="86" y="292" width="256" height="24" rx="12" fill="#30343b"/>
            <rect x="134" y="238" width="28" height="96" rx="14" fill="#2b3038"/>
            <rect x="236" y="232" width="28" height="102" rx="14" fill="#2b3038"/>
            <circle cx="476" cy="202" r="48" fill="#e9b996"/>
            <path d="M429 196c8-44 36-68 70-57 24 8 36 29 36 55-34-20-65-20-106 2z" fill="#34261f"/>
            <path d="M398 360c10-74 42-114 82-114 50 0 88 44 98 114z" fill="{accent_a}"/>
            <rect x="586" y="268" width="96" height="82" rx="18" fill="#30343b"/>
            <circle cx="606" cy="360" r="22" fill="#30343b"/>
            <circle cx="664" cy="360" r="22" fill="#30343b"/>
        """
        if is_coach_scene
        else f"""
            <rect x="90" y="244" width="120" height="126" rx="18" fill="#2d343d"/>
            <rect x="114" y="260" width="72" height="16" rx="8" fill="{accent_a}"/>
            <rect x="128" y="296" width="16" height="62" rx="8" fill="#c8d1d8"/>
            <rect x="158" y="286" width="16" height="72" rx="8" fill="#c8d1d8"/>
            <rect x="264" y="306" width="176" height="22" rx="11" fill="#30343b"/>
            <circle cx="280" cy="342" r="28" fill="#30343b"/>
            <circle cx="424" cy="342" r="28" fill="#30343b"/>
            <rect x="508" y="238" width="142" height="164" rx="26" fill="#353c45"/>
            <rect x="534" y="268" width="90" height="96" rx="20" fill="#99a9b4"/>
            <rect x="626" y="282" width="42" height="16" rx="8" fill="{accent_b}"/>
        """
    )
    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="800" height="520" viewBox="0 0 800 520">
      <defs>
        <linearGradient id="wall" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stop-color="#f7f3ed"/>
          <stop offset="100%" stop-color="#dfe8ea"/>
        </linearGradient>
        <linearGradient id="floor" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stop-color="#efe4d5"/>
          <stop offset="100%" stop-color="#b9956a"/>
        </linearGradient>
        <linearGradient id="glass" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stop-color="#d8ebf4"/>
          <stop offset="100%" stop-color="#9fb7c4"/>
        </linearGradient>
        <filter id="soft" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="12"/>
        </filter>
      </defs>
      <rect width="800" height="520" rx="36" fill="url(#wall)"/>
      <rect y="338" width="800" height="182" fill="url(#floor)"/>
      <path d="M0 338h800" stroke="rgba(80,70,58,0.18)" stroke-width="4"/>
      <rect x="54" y="58" width="238" height="220" rx="20" fill="url(#glass)"/>
      <rect x="316" y="58" width="238" height="220" rx="20" fill="url(#glass)"/>
      <rect x="578" y="58" width="168" height="220" rx="20" fill="url(#glass)"/>
      <path d="M174 58v220M436 58v220M662 58v220M54 168h692" stroke="rgba(255,255,255,0.48)" stroke-width="8"/>
      <circle cx="94" cy="94" r="78" fill="{accent_a}" opacity="0.16" filter="url(#soft)"/>
      <circle cx="694" cy="102" r="92" fill="{accent_b}" opacity="0.16" filter="url(#soft)"/>
      {scene_markup}
      <rect x="40" y="402" width="330" height="70" rx="24" fill="rgba(24,29,35,0.58)"/>
      <text x="70" y="447" fill="#fff" font-size="30" font-family="Arial, PingFang SC, sans-serif" font-weight="700">{title}</text>
    </svg>
    """
    return data_uri_svg(svg)


def portrait_avatar(skin="#f5c9a8", hair="#41291c", shirt="#1f2125", bg_a="#f4d6bf", bg_b="#c89266"):
    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="320" height="320" viewBox="0 0 320 320">
      <defs>
        <linearGradient id="bg" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stop-color="{bg_a}"/>
          <stop offset="100%" stop-color="{bg_b}"/>
        </linearGradient>
        <linearGradient id="shirt" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stop-color="{shirt}"/>
          <stop offset="100%" stop-color="#111319"/>
        </linearGradient>
      </defs>
      <rect width="320" height="320" rx="52" fill="url(#bg)"/>
      <circle cx="258" cy="70" r="58" fill="rgba(255,255,255,0.22)"/>
      <circle cx="76" cy="262" r="104" fill="rgba(255,255,255,0.12)"/>
      <rect x="64" y="204" width="192" height="116" rx="58" fill="url(#shirt)"/>
      <rect x="113" y="160" width="94" height="58" rx="24" fill="{skin}"/>
      <circle cx="160" cy="119" r="62" fill="{skin}"/>
      <path d="M97 122c4-48 32-76 68-76 37 0 64 25 67 74-26-20-53-29-79-26-22 2-39 10-56 28z" fill="{hair}"/>
      <path d="M104 120c18-30 42-43 72-39 20 3 38 12 55 29-8-37-35-61-68-61-35 0-61 27-59 71z" fill="rgba(255,255,255,0.08)"/>
      <circle cx="139" cy="122" r="4" fill="#38251c"/>
      <circle cx="181" cy="122" r="4" fill="#38251c"/>
      <path d="M142 148c9 8 27 8 36 0" fill="none" stroke="#a66b58" stroke-width="5" stroke-linecap="round"/>
      <path d="M76 304h168" stroke="rgba(255,255,255,0.22)" stroke-width="10" stroke-linecap="round"/>
    </svg>
    """
    return data_uri_svg(svg)


def gym_avatar(bg_a="#26323e", bg_b="#7b91a8", accent="#f28c28"):
    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="320" height="320" viewBox="0 0 320 320">
      <defs>
        <linearGradient id="bg" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stop-color="{bg_a}"/>
          <stop offset="100%" stop-color="{bg_b}"/>
        </linearGradient>
        <linearGradient id="floor" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stop-color="#e7ded0"/>
          <stop offset="100%" stop-color="#a98860"/>
        </linearGradient>
      </defs>
      <rect width="320" height="320" rx="52" fill="url(#bg)"/>
      <rect x="0" y="202" width="320" height="118" fill="url(#floor)" opacity="0.92"/>
      <rect x="28" y="42" width="264" height="126" rx="24" fill="rgba(225,239,246,0.78)"/>
      <path d="M116 42v126M204 42v126M28 104h264" stroke="rgba(255,255,255,0.72)" stroke-width="7"/>
      <rect x="54" y="154" width="72" height="94" rx="15" fill="#2d343d"/>
      <rect x="70" y="170" width="40" height="10" rx="5" fill="{accent}"/>
      <rect x="76" y="192" width="10" height="42" rx="5" fill="#cfd6dc"/>
      <rect x="96" y="184" width="10" height="50" rx="5" fill="#cfd6dc"/>
      <rect x="150" y="206" width="108" height="16" rx="8" fill="#30343b"/>
      <circle cx="162" cy="236" r="18" fill="#30343b"/>
      <circle cx="246" cy="236" r="18" fill="#30343b"/>
      <rect x="218" y="126" width="54" height="96" rx="18" fill="rgba(37,44,52,0.86)"/>
      <rect x="230" y="144" width="30" height="54" rx="10" fill="#aab6bf"/>
    </svg>
    """
    return data_uri_svg(svg)


def relative_time_label(iso_text):
    if not iso_text:
        return "刚刚"
    try:
        created = datetime.fromisoformat(iso_text)
    except ValueError:
        return "刚刚"
    delta = now_utc() - created
    minutes = max(0, int(delta.total_seconds() // 60))
    if minutes < 1:
        return "刚刚"
    if minutes < 60:
        return f"{minutes} 分钟前"
    hours = minutes // 60
    if hours < 24:
        return f"{hours} 小时前"
    days = hours // 24
    if days < 7:
        return f"{days} 天前"
    return created.astimezone(timezone(timedelta(hours=8))).strftime("%m-%d")


def default_avatar_for_role(role):
    is_gym = role == "gym"
    badge = (
        '<path d="M105 170h110v74H105z" fill="#eef4f8"/>'
        '<path d="M126 170v74M160 170v74M194 170v74M105 204h110" stroke="#c7d3dc" stroke-width="8"/>'
        if is_gym
        else '<circle cx="160" cy="126" r="48" fill="#f4f7f9"/><path d="M78 286c13-64 46-97 82-97s69 33 82 97" fill="#f4f7f9"/>'
    )
    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="320" height="320" viewBox="0 0 320 320">
      <defs>
        <linearGradient id="bg" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stop-color="#eef3f7"/>
          <stop offset="100%" stop-color="#cbd8e3"/>
        </linearGradient>
        <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="0" dy="12" stdDeviation="14" flood-color="#7d8b98" flood-opacity="0.18"/>
        </filter>
      </defs>
      <rect width="320" height="320" rx="62" fill="url(#bg)"/>
      <circle cx="244" cy="74" r="58" fill="rgba(255,255,255,0.46)"/>
      <circle cx="88" cy="256" r="110" fill="rgba(255,255,255,0.24)"/>
      <g filter="url(#shadow)">{badge}</g>
      <path d="M96 286h128" stroke="rgba(117,132,146,0.32)" stroke-width="10" stroke-linecap="round"/>
    </svg>
    """
    return data_uri_svg(svg)


def compact_avatar_image(url, role):
    if not url:
        return default_avatar_for_role(role)
    if isinstance(url, str) and url.startswith("data:") and len(url) > MAX_INLINE_AVATAR_CHARS:
        return default_avatar_for_role(role)
    return url


def compact_media_item(item):
    trimmed = dict(item)
    url = trimmed.get("url", "")
    if isinstance(url, str) and url.startswith("data:") and len(url) > MAX_INLINE_MEDIA_CHARS:
        trimmed["tooLarge"] = True
        trimmed["name"] = item.get("name") or ("视频文件" if item.get("type") == "video" else "图片文件")
    for key in ("thumbnailUrl", "posterUrl"):
        asset_url = trimmed.get(key, "")
        if isinstance(asset_url, str) and asset_url.startswith("data:") and len(asset_url) > MAX_INLINE_AVATAR_CHARS:
            trimmed[key] = ""
            trimmed[f"{key}TooLarge"] = True
    return trimmed


def sanitize_state(state):
    state.setdefault("reports", [])
    state.setdefault("moderationQueue", [])
    state.setdefault("adminActions", [])
    state.setdefault("blocks", [])
    for profile in state.get("profiles", {}).values():
        profile["avatarImage"] = compact_avatar_image(profile.get("avatarImage"), profile.get("role", "enthusiast"))
    for post in state.get("posts", {}).values():
        post["media"] = [compact_media_item(item) for item in post.get("media", [])]
    normalize_blocks(state)
    return state


def parse_optional_float(value):
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_optional_int(value):
    if value in (None, ""):
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def parse_optional_iso_datetime(value):
    text = str(value or "").strip()
    if not text:
        return None
    normalized = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def normalize_phone(value):
    raw = "".join(ch for ch in str(value or "") if ch.isdigit())
    return raw


def calculate_bmi(height_cm, weight_kg):
    if not height_cm or not weight_kg:
        return None
    height_meter = height_cm / 100
    if height_meter <= 0:
        return None
    return round(weight_kg / (height_meter * height_meter), 1)


def estimate_body_fat(gender, bmi):
    if not bmi:
        return None
    if gender == "女":
        estimate = bmi * 1.18 - 6.2
    elif gender == "男":
        estimate = bmi * 1.06 - 10.8
    else:
        estimate = bmi * 1.12 - 8.8
    return round(max(8.0, min(42.0, estimate)), 1)


def storage_log(message):
    print(f"[FitHub storage] {message}", file=sys.stderr)


def sms_provider_configured():
    if SMS_PROVIDER == "tencent":
        return all([
            TENCENT_SMS_SECRET_ID,
            TENCENT_SMS_SECRET_KEY,
            TENCENT_SMS_APP_ID,
            TENCENT_SMS_SIGN_NAME,
            TENCENT_SMS_TEMPLATE_ID,
        ])
    return False


def sms_verification_enabled():
    return SMS_DEV_MODE or sms_provider_configured()


def wechat_miniapp_login_enabled():
    return WECHAT_MINIAPP_DEV_MODE or bool(WECHAT_MINIAPP_APP_ID and WECHAT_MINIAPP_APP_SECRET)


def ensure_verification_registry(state):
    return state.setdefault("otpCodes", {})


def cleanup_verification_registry(state):
    registry = ensure_verification_registry(state)
    current = now_utc()
    expired = []
    for phone, item in registry.items():
        expires_at = parse_optional_iso_datetime(item.get("expiresAt"))
        if expires_at and expires_at < current:
            expired.append(phone)
    for phone in expired:
        registry.pop(phone, None)


def hash_sms_code(phone, code):
    return hashlib.sha256(f"{normalize_phone(phone)}:{code}:{SMS_HASH_SALT}".encode("utf-8")).hexdigest()


def generate_sms_code():
    digits = "0123456789"
    return "".join(secrets.choice(digits) for _ in range(max(4, SMS_CODE_LENGTH)))


def mark_session_phone_verified(session, phone):
    verified = session.setdefault("verifiedPhones", {})
    verified[normalize_phone(phone)] = iso_at()


def is_session_phone_verified(session, phone):
    phone_key = normalize_phone(phone)
    if not phone_key:
        return False
    verified = session.get("verifiedPhones", {})
    return bool(verified.get(phone_key))


def hmac_sha256(key, msg):
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def sha256_hex(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def exchange_wechat_miniapp_code(js_code, dev_openid=""):
    code = str(js_code or "").strip()
    if not code:
        raise ValueError("缺少微信登录凭证。")
    if WECHAT_MINIAPP_DEV_MODE and not (WECHAT_MINIAPP_APP_ID and WECHAT_MINIAPP_APP_SECRET):
        seed = str(dev_openid or code).strip()
        openid = f"dev-openid-{sha256_hex(seed)[:24]}"
        return {
            "openid": openid,
            "unionid": "",
            "session_key": f"dev-session-{sha256_hex(seed + ':session')[:24]}",
            "source": "dev",
        }
    if not (WECHAT_MINIAPP_APP_ID and WECHAT_MINIAPP_APP_SECRET):
        raise ValueError("微信小程序登录还没有配置 AppID 和 AppSecret。")

    query = urlencode(
        {
            "appid": WECHAT_MINIAPP_APP_ID,
            "secret": WECHAT_MINIAPP_APP_SECRET,
            "js_code": code,
            "grant_type": "authorization_code",
        }
    )
    request = Request(f"https://api.weixin.qq.com/sns/jscode2session?{query}", method="GET")
    with urlopen(request, timeout=12) as response:
        payload = json.loads(response.read().decode("utf-8") or "{}")
    if payload.get("errcode"):
        raise ValueError(f"微信登录失败：{payload.get('errmsg') or payload.get('errcode')}")
    if not payload.get("openid"):
        raise ValueError("微信登录没有返回 openid。")
    payload["source"] = "wechat"
    return payload


def send_sms_via_tencent(phone, code):
    host = "sms.tencentcloudapi.com"
    endpoint = f"https://{host}/"
    service = "sms"
    action = "SendSms"
    version = "2021-01-11"
    timestamp = int(now_utc().timestamp())
    date = now_utc().strftime("%Y-%m-%d")
    payload = {
        "SmsSdkAppId": TENCENT_SMS_APP_ID,
        "SignName": TENCENT_SMS_SIGN_NAME,
        "TemplateId": TENCENT_SMS_TEMPLATE_ID,
        "TemplateParamSet": [code, str(max(1, SMS_CODE_TTL_SECONDS // 60))],
        "PhoneNumberSet": [f"+86{normalize_phone(phone)}"],
        "SessionContext": "FitHubLogin",
    }
    payload_json = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    canonical_headers = (
        "content-type:application/json; charset=utf-8\n"
        f"host:{host}\n"
        f"x-tc-action:{action.lower()}\n"
    )
    signed_headers = "content-type;host;x-tc-action"
    canonical_request = "\n".join([
        "POST",
        "/",
        "",
        canonical_headers,
        signed_headers,
        sha256_hex(payload_json),
    ])
    credential_scope = f"{date}/{service}/tc3_request"
    string_to_sign = "\n".join([
        "TC3-HMAC-SHA256",
        str(timestamp),
        credential_scope,
        sha256_hex(canonical_request),
    ])
    secret_date = hmac_sha256(("TC3" + TENCENT_SMS_SECRET_KEY).encode("utf-8"), date)
    secret_service = hmac.new(secret_date, service.encode("utf-8"), hashlib.sha256).digest()
    secret_signing = hmac.new(secret_service, b"tc3_request", hashlib.sha256).digest()
    signature = hmac.new(secret_signing, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()
    authorization = (
        f"TC3-HMAC-SHA256 Credential={TENCENT_SMS_SECRET_ID}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, Signature={signature}"
    )
    request = Request(
        endpoint,
        data=payload_json.encode("utf-8"),
        headers={
            "Authorization": authorization,
            "Content-Type": "application/json; charset=utf-8",
            "Host": host,
            "X-TC-Action": action,
            "X-TC-Version": version,
            "X-TC-Timestamp": str(timestamp),
            "X-TC-Region": TENCENT_SMS_REGION,
        },
        method="POST",
    )
    with urlopen(request, timeout=12) as response:
        body = json.loads(response.read().decode("utf-8"))
    error = (body.get("Response") or {}).get("Error")
    if error:
        raise ValueError(error.get("Message") or "短信发送失败，请稍后再试。")
    status_item = ((body.get("Response") or {}).get("SendStatusSet") or [{}])[0]
    if status_item.get("Code") != "Ok":
        raise ValueError(status_item.get("Message") or "短信发送失败，请稍后再试。")


def send_sms_code(state, session, phone, purpose="login"):
    cleanup_verification_registry(state)
    phone_key = validate_phone_or_raise(phone)
    registry = ensure_verification_registry(state)
    current = now_utc()
    current_item = registry.get(phone_key) or {}
    last_sent = parse_optional_iso_datetime(current_item.get("lastSentAt"))
    if last_sent:
        wait_seconds = SMS_RESEND_SECONDS - int((current - last_sent).total_seconds())
        if wait_seconds > 0:
            if SMS_DEV_MODE and not sms_provider_configured() and current_item.get("debugCode"):
                return {
                    "phone": phone_key,
                    "cooldownSeconds": wait_seconds,
                    "expiresInSeconds": max(
                        0,
                        int(
                            (
                                parse_optional_iso_datetime(current_item.get("expiresAt")) - current
                            ).total_seconds()
                        )
                        if parse_optional_iso_datetime(current_item.get("expiresAt"))
                        else SMS_CODE_TTL_SECONDS
                    ),
                    "debugCode": str(current_item.get("debugCode") or ""),
                }
            raise ValueError(f"验证码已发送，请 {wait_seconds} 秒后再试。")

    code = generate_sms_code()
    if sms_provider_configured():
        if SMS_PROVIDER == "tencent":
            send_sms_via_tencent(phone_key, code)
    elif not SMS_DEV_MODE:
        raise ValueError("短信验证码服务尚未配置，请先联系管理员开通。")

    registry[phone_key] = {
        "codeHash": hash_sms_code(phone_key, code),
        "expiresAt": (current + timedelta(seconds=SMS_CODE_TTL_SECONDS)).isoformat(),
        "lastSentAt": current.isoformat(),
        "purpose": purpose,
        "attempts": 0,
        "sessionId": session.get("id"),
        "debugCode": code if SMS_DEV_MODE and not sms_provider_configured() else "",
    }
    response = {
        "phone": phone_key,
        "cooldownSeconds": SMS_RESEND_SECONDS,
        "expiresInSeconds": SMS_CODE_TTL_SECONDS,
    }
    if SMS_DEV_MODE and not sms_provider_configured():
        response["debugCode"] = code
    return response


def verify_sms_code(state, session, phone, code):
    cleanup_verification_registry(state)
    phone_key = validate_phone_or_raise(phone)
    raw_code = str(code or "").strip()
    if len(raw_code) < 4:
        raise ValueError("请输入短信验证码。")

    registry = ensure_verification_registry(state)
    item = registry.get(phone_key)
    if not item:
        raise ValueError("请先获取短信验证码。")

    expires_at = parse_optional_iso_datetime(item.get("expiresAt"))
    if not expires_at or expires_at < now_utc():
        registry.pop(phone_key, None)
        raise ValueError("验证码已过期，请重新获取。")

    if item.get("codeHash") != hash_sms_code(phone_key, raw_code):
        item["attempts"] = int(item.get("attempts") or 0) + 1
        if item["attempts"] >= 8:
            registry.pop(phone_key, None)
            raise ValueError("验证码错误次数过多，请重新获取。")
        raise ValueError("验证码不正确，请重新输入。")

    registry.pop(phone_key, None)
    mark_session_phone_verified(session, phone_key)
    session["lastVerifiedPhone"] = phone_key
    return phone_key


def set_runtime_storage_state(loaded_from, supabase_writable, state=None):
    STATE_RUNTIME_META["loaded_from"] = loaded_from
    STATE_RUNTIME_META["supabase_writable"] = bool(supabase_writable)
    if isinstance(state, dict):
        metrics = state_integrity_metrics(state)
        STATE_RUNTIME_META["last_known_remote_real_profiles"] = metrics["real_profiles"]
        STATE_RUNTIME_META["last_known_remote_signal_score"] = metrics["score"]


def supabase_storage_enabled():
    return bool(supabase_config_valid() and SUPABASE_SERVICE_ROLE_KEY)


def supabase_config_valid():
    parsed = urlparse(SUPABASE_URL or "")
    valid = bool(parsed.scheme in {"http", "https"} and parsed.netloc)
    STATE_RUNTIME_META["supabase_config_valid"] = valid
    return valid


def supabase_media_storage_enabled():
    return bool(supabase_storage_enabled() and SUPABASE_MEDIA_BUCKET)


def build_supabase_public_media_url(object_path):
    quoted_path = quote(str(object_path or "").lstrip("/"), safe="/")
    return f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_MEDIA_BUCKET}/{quoted_path}"


def supabase_public_media_prefix():
    return build_supabase_public_media_url("").rstrip("/")


def extract_storage_path_from_public_url(url):
    text = str(url or "").strip()
    if not text:
        return ""
    prefix = supabase_public_media_prefix()
    if not text.startswith(prefix):
        return ""
    suffix = text[len(prefix):].lstrip("/")
    return unquote(suffix)


def ensure_supabase_media_bucket():
    global SUPABASE_MEDIA_BUCKET_READY
    if SUPABASE_MEDIA_BUCKET_READY or not supabase_media_storage_enabled():
        return

    buckets = supabase_storage_request("GET", "bucket", expect_json=True) or []
    if any(str(item.get("id") or "") == SUPABASE_MEDIA_BUCKET for item in buckets if isinstance(item, dict)):
        SUPABASE_MEDIA_BUCKET_READY = True
        return

    try:
        supabase_storage_request(
            "POST",
            "bucket",
            payload={
                "id": SUPABASE_MEDIA_BUCKET,
                "name": SUPABASE_MEDIA_BUCKET,
                "public": True,
                "allowedMimeTypes": ["image/*", "video/*"],
            },
            expect_json=True,
        )
    except Exception as exc:
        body = ""
        if hasattr(exc, "read"):
            try:
                body = exc.read().decode("utf-8", errors="ignore")
            except Exception:  # noqa: BLE001
                body = ""
        if getattr(exc, "code", None) not in {400, 409} or ("exists" not in body.lower() and "duplicate" not in body.lower()):
            raise
    SUPABASE_MEDIA_BUCKET_READY = True


def decode_data_url(data_url):
    text = str(data_url or "").strip()
    match = re.match(r"^data:([^;,]+)?(?:;charset=[^;,]+)?;base64,(.+)$", text, re.DOTALL)
    if not match:
        raise ValueError("媒体内容格式不正确，请重新选择文件。")
    content_type = (match.group(1) or "application/octet-stream").strip()
    try:
        binary = base64.b64decode(match.group(2), validate=True)
    except Exception as exc:  # noqa: BLE001
        raise ValueError("媒体内容无法解析，请重新上传。") from exc
    return content_type, binary


def sanitize_file_name(file_name, content_type):
    raw = str(file_name or "").strip()
    base, ext = os.path.splitext(raw)
    safe_base = re.sub(r"[^a-zA-Z0-9._-]+", "-", base).strip("-._") or "asset"
    safe_ext = re.sub(r"[^a-zA-Z0-9.]+", "", ext).lower()
    if not safe_ext:
        guessed = mimetypes.guess_extension(content_type or "")
        safe_ext = guessed or ""
    return f"{safe_base}{safe_ext}"


def upload_media_asset(data_url, *, file_name, category, asset_type, force_inline=False, max_bytes_override=None):
    asset_type = str(asset_type or "image").strip().lower()
    if asset_type not in {"image", "video"}:
        raise ValueError("暂不支持这个媒体类型，请重新选择图片或视频。")

    content_type, binary = decode_data_url(data_url)
    if asset_type == "video" and not content_type.startswith("video/"):
        raise ValueError("当前文件不是有效视频，请重新选择。")
    if asset_type == "image" and not content_type.startswith("image/"):
        raise ValueError("当前文件不是有效图片，请重新选择。")

    max_bytes = max_bytes_override or (MEDIA_VIDEO_LIMIT_BYTES if asset_type == "video" else MEDIA_IMAGE_LIMIT_BYTES)
    if len(binary) > max_bytes:
        raise ValueError("媒体文件过大，请选择更短的视频或更小的图片。")

    if force_inline or not supabase_media_storage_enabled():
        return {
            "type": asset_type,
            "url": data_url,
            "name": sanitize_file_name(file_name, content_type),
            "contentType": content_type,
            "storageProvider": "inline",
            "sizeBytes": len(binary),
        }

    ensure_supabase_media_bucket()

    timestamp = now_utc().strftime("%Y/%m/%d")
    sanitized_name = sanitize_file_name(file_name, content_type)
    object_path = f"{category}/{timestamp}/{uuid.uuid4().hex[:12]}-{sanitized_name}"
    quoted_path = quote(object_path, safe="/")
    supabase_storage_request(
        "POST",
        f"object/{SUPABASE_MEDIA_BUCKET}/{quoted_path}",
        payload=binary,
        headers={
            "Content-Type": content_type,
            "x-upsert": "false",
            "Cache-Control": "3600",
        },
        expect_json=True,
    )
    return {
        "type": asset_type,
        "url": build_supabase_public_media_url(object_path),
        "name": sanitized_name,
        "contentType": content_type,
        "storageProvider": "supabase",
        "storagePath": object_path,
        "sizeBytes": len(binary),
    }


def iter_media_storage_paths(media_item):
    if not isinstance(media_item, dict):
        return []
    paths = []
    for key in ("storagePath", "thumbnailStoragePath"):
        path = str(media_item.get(key) or "").strip().lstrip("/")
        if path and path not in paths:
            paths.append(path)
    return paths


def remember_session_draft_media(session, media_item):
    if not isinstance(session, dict):
        return
    registry = session.setdefault("draftMediaPaths", [])
    known_paths = {
        str(entry.get("path") or "").strip().lstrip("/")
        for entry in registry
        if isinstance(entry, dict)
    }
    created_at = iso_at()
    for path in iter_media_storage_paths(media_item):
        if path in known_paths:
            continue
        registry.append({"path": path, "createdAt": created_at})
        known_paths.add(path)


def release_session_draft_media(session, media_items):
    if not isinstance(session, dict):
        return
    paths_to_drop = set()
    for item in media_items or []:
        paths_to_drop.update(iter_media_storage_paths(item))
    if not paths_to_drop:
        return
    registry = session.setdefault("draftMediaPaths", [])
    session["draftMediaPaths"] = [
        entry
        for entry in registry
        if str((entry or {}).get("path") or "").strip().lstrip("/") not in paths_to_drop
    ]


def session_allows_media_delete(session, media_item):
    if not isinstance(session, dict):
        return False
    paths = iter_media_storage_paths(media_item)
    if not paths:
        return True
    registry = {
        str(entry.get("path") or "").strip().lstrip("/")
        for entry in session.get("draftMediaPaths", [])
        if isinstance(entry, dict)
    }
    return all(path in registry for path in paths)


def delete_media_asset(media_item):
    deleted_paths = []
    if not supabase_media_storage_enabled():
        return deleted_paths
    for path in iter_media_storage_paths(media_item):
        quoted_path = quote(path, safe="/")
        try:
            supabase_storage_request(
                "DELETE",
                f"object/{SUPABASE_MEDIA_BUCKET}/{quoted_path}",
                expect_json=False,
                allow_statuses={404},
            )
        except Exception as exc:  # noqa: BLE001
            storage_log(f"Media delete skipped for {path}: {exc}")
            continue
        deleted_paths.append(path)
    return deleted_paths


def list_media_bucket_entries(prefix="", limit=1000, offset=0):
    if not supabase_media_storage_enabled():
        return []
    normalized_prefix = str(prefix or "").strip().strip("/")
    return (
        supabase_storage_request(
            "POST",
            f"object/list/{SUPABASE_MEDIA_BUCKET}",
            payload={
                "prefix": normalized_prefix,
                "limit": max(1, int(limit)),
                "offset": max(0, int(offset)),
                "sortBy": {"column": "name", "order": "asc"},
            },
            expect_json=True,
        )
        or []
    )


def is_media_bucket_folder_entry(entry):
    if not isinstance(entry, dict):
        return False
    name = str(entry.get("name") or "").strip()
    if not name:
        return False
    if str(entry.get("id") or "").strip():
        return False
    if entry.get("metadata") not in (None, {}):
        return False
    if entry.get("updated_at") or entry.get("created_at") or entry.get("last_accessed_at"):
        return False
    return True


def iter_media_bucket_objects(prefix="", limit=1000):
    pending_prefixes = [str(prefix or "").strip().strip("/")]
    while pending_prefixes:
        current_prefix = pending_prefixes.pop(0)
        offset = 0
        while True:
            entries = list_media_bucket_entries(current_prefix, limit=limit, offset=offset)
            if not entries:
                break
            for entry in entries:
                if is_media_bucket_folder_entry(entry):
                    folder_name = str(entry.get("name") or "").strip().strip("/")
                    next_prefix = "/".join(filter(None, [current_prefix, folder_name]))
                    if next_prefix:
                        pending_prefixes.append(next_prefix)
                    continue
                path = "/".join(filter(None, [current_prefix, str(entry.get("name") or "").strip().strip("/")]))
                item = dict(entry)
                item["path"] = path
                yield item
            if len(entries) < limit:
                break
            offset += len(entries)


def _collect_storage_paths_from_state(value, collected):
    if isinstance(value, dict):
        for key, item in value.items():
            if key in {"storagePath", "thumbnailStoragePath"}:
                path = str(item or "").strip().lstrip("/")
                if path:
                    collected.add(path)
                continue
            if key in {"url", "thumbnailUrl", "posterUrl", "avatarImage"}:
                derived = extract_storage_path_from_public_url(item)
                if derived:
                    collected.add(derived)
            _collect_storage_paths_from_state(item, collected)
        return
    if isinstance(value, list):
        for item in value:
            _collect_storage_paths_from_state(item, collected)


def collect_referenced_media_paths(state):
    collected = set()
    if not isinstance(state, dict):
        return collected
    _collect_storage_paths_from_state(state, collected)
    return collected


def collect_session_draft_media_paths(state):
    paths = set()
    if not isinstance(state, dict):
        return paths
    for session in (state.get("sessions") or {}).values():
        if not isinstance(session, dict):
            continue
        for entry in session.get("draftMediaPaths", []) or []:
            path = str((entry or {}).get("path") or "").strip().lstrip("/")
            if path:
                paths.add(path)
    return paths


def derive_media_object_timestamp(path, entry):
    for key in ("updated_at", "created_at", "last_accessed_at"):
        parsed = parse_optional_iso_datetime(entry.get(key))
        if parsed:
            return parsed

    parts = [segment for segment in str(path or "").split("/") if segment]
    if len(parts) >= 4 and all(part.isdigit() for part in parts[1:4]):
        try:
            year, month, day = (int(parts[1]), int(parts[2]), int(parts[3]))
            return now_utc().replace(year=year, month=month, day=day, hour=0, minute=0, second=0, microsecond=0)
        except ValueError:
            return None
    return None


def collect_media_bucket_inventory():
    inventory = []
    for entry in iter_media_bucket_objects():
        path = str(entry.get("path") or "").strip().lstrip("/")
        if not path:
            continue
        inventory.append(
            {
                "path": path,
                "createdAt": derive_media_object_timestamp(path, entry),
                "sizeBytes": int((entry.get("metadata") or {}).get("size") or entry.get("size") or 0),
            }
        )
    return inventory


def classify_media_bucket_objects(state, stale_after_hours=24):
    referenced = collect_referenced_media_paths(state)
    draft_paths = collect_session_draft_media_paths(state)
    cutoff = now_utc() - timedelta(hours=max(1, int(stale_after_hours or 24)))
    report = {
        "referenced": [],
        "activeDrafts": [],
        "recentUnreferenced": [],
        "orphanCandidates": [],
    }

    for item in collect_media_bucket_inventory():
        path = item["path"]
        created_at = item["createdAt"]
        serialized = {
            **item,
            "createdAt": created_at.isoformat() if created_at else "",
        }
        if path in referenced:
            report["referenced"].append(serialized)
        elif path in draft_paths:
            report["activeDrafts"].append(serialized)
        elif created_at and created_at >= cutoff:
            report["recentUnreferenced"].append(serialized)
        else:
            report["orphanCandidates"].append(serialized)
    return report


def summarize_media_report(report):
    summary = {}
    for key, items in report.items():
        total_bytes = sum(int(item.get("sizeBytes") or 0) for item in items)
        by_category = {}
        for item in items:
            category = str(item.get("path") or "unknown").split("/", 1)[0] or "unknown"
            by_category[category] = by_category.get(category, 0) + 1
        summary[key] = {
            "count": len(items),
            "sizeBytes": total_bytes,
            "byCategory": by_category,
        }
    return summary


def build_media_maintenance_report(state, *, stale_after_hours=24, delete=False):
    if not supabase_media_storage_enabled():
        return {
            "enabled": False,
            "deletedPaths": [],
            "summary": {},
            "report": {
                "referenced": [],
                "activeDrafts": [],
                "recentUnreferenced": [],
                "orphanCandidates": [],
            },
        }

    report = classify_media_bucket_objects(state, stale_after_hours)
    deleted_paths = []
    if delete:
        for item in report["orphanCandidates"]:
            deleted_paths.extend(delete_media_asset({"storagePath": item["path"]}))

    return {
        "enabled": True,
        "deletedPaths": deleted_paths,
        "summary": summarize_media_report(report),
        "report": report,
    }


def is_demo_profile_id(profile_id):
    return (
        profile_id in LEGACY_DEMO_ENTHUSIAST_IDS
        or str(profile_id or "").startswith("gym-demo-")
        or str(profile_id or "").startswith("coach-demo-")
    )


def count_real_profiles(state):
    profiles = state.get("profiles", {}) if isinstance(state, dict) else {}
    return sum(1 for profile_id in profiles if not is_demo_profile_id(profile_id))


def state_integrity_metrics(state):
    if not isinstance(state, dict):
        return {
            "real_profiles": 0,
            "phone_profiles": 0,
            "accounts": 0,
            "real_follows": 0,
            "real_posts": 0,
            "real_bookings": 0,
            "real_threads": 0,
            "real_checkins": 0,
            "score": 0,
        }

    profiles = state.get("profiles", {}) or {}
    real_profile_ids = {
        profile_id
        for profile_id in profiles.keys()
        if not is_demo_profile_id(profile_id)
    }
    phone_profiles = sum(
        1
        for profile_id, profile in profiles.items()
        if profile_id in real_profile_ids and normalize_phone(profile.get("phone"))
    )
    accounts = sum(
        1
        for account in (state.get("accounts", {}) or {}).values()
        if normalize_phone(account.get("phone"))
        or any(str(profile_id or "").strip() for profile_id in (account.get("profilesByRole") or {}).values())
    )
    real_follows = sum(
        1
        for item in state.get("follows", []) or []
        if item.get("sourceProfileId") in real_profile_ids
        or item.get("targetProfileId") in real_profile_ids
    )
    real_posts = sum(
        1
        for post in (state.get("posts", {}) or {}).values()
        if post.get("authorProfileId") in real_profile_ids
    )
    real_bookings = sum(
        1
        for booking in state.get("bookings", []) or []
        if booking.get("createdByProfileId") in real_profile_ids
        or booking.get("targetProfileId") in real_profile_ids
    )
    real_threads = sum(
        1
        for thread in state.get("threads", []) or []
        if any(participant in real_profile_ids for participant in thread.get("participants", []) or [])
    )
    real_checkins = sum(
        len((profile.get("checkins") or []))
        for profile_id, profile in profiles.items()
        if profile_id in real_profile_ids
    )
    score = (
        len(real_profile_ids) * 1000
        + phone_profiles * 500
        + accounts * 400
        + real_follows * 40
        + real_posts * 25
        + real_bookings * 25
        + real_threads * 15
        + real_checkins * 8
    )
    return {
        "real_profiles": len(real_profile_ids),
        "phone_profiles": phone_profiles,
        "accounts": accounts,
        "real_follows": real_follows,
        "real_posts": real_posts,
        "real_bookings": real_bookings,
        "real_threads": real_threads,
        "real_checkins": real_checkins,
        "score": score,
    }


def is_materially_richer_state(candidate_metrics, baseline_metrics):
    candidate_score = int((candidate_metrics or {}).get("score") or 0)
    baseline_score = int((baseline_metrics or {}).get("score") or 0)
    if candidate_score <= baseline_score:
        return False

    candidate_real_profiles = int((candidate_metrics or {}).get("real_profiles") or 0)
    baseline_real_profiles = int((baseline_metrics or {}).get("real_profiles") or 0)
    candidate_phone_profiles = int((candidate_metrics or {}).get("phone_profiles") or 0)
    baseline_phone_profiles = int((baseline_metrics or {}).get("phone_profiles") or 0)
    candidate_accounts = int((candidate_metrics or {}).get("accounts") or 0)
    baseline_accounts = int((baseline_metrics or {}).get("accounts") or 0)
    candidate_follows = int((candidate_metrics or {}).get("real_follows") or 0)
    baseline_follows = int((baseline_metrics or {}).get("real_follows") or 0)

    if baseline_score == 0 and candidate_score > 0:
        return True
    if candidate_real_profiles > baseline_real_profiles:
        return True
    if candidate_phone_profiles > baseline_phone_profiles:
        return True
    if candidate_accounts > baseline_accounts + 1:
        return True
    if candidate_follows > baseline_follows + 2:
        return True
    return candidate_score >= max(baseline_score + 120, int(max(1, baseline_score) * 1.35))


def storage_runtime_status(state=None):
    loaded_from = str(STATE_RUNTIME_META.get("loaded_from") or "uninitialized")
    supabase_configured = supabase_storage_enabled()
    supabase_writable = bool(STATE_RUNTIME_META.get("supabase_writable", True))
    metrics = state_integrity_metrics(state)
    warnings = []

    if not supabase_configured:
        warnings.append("Supabase 未启用，当前只能使用本地 JSON；生产环境不建议这样运行。")
    if loaded_from == "local-fallback":
        warnings.append("最近一次远端读取失败，服务正在使用本地 fallback，写入不会覆盖远端数据。")
    if supabase_configured and not supabase_writable:
        warnings.append("Supabase 当前不可写，用户新数据可能暂存在本地 fallback。")
    if metrics["real_profiles"] > 0 and loaded_from in {"local-file", "supabase-empty"} and supabase_configured:
        warnings.append("检测到真实用户数据，但当前加载源不是常规 Supabase 主状态，请关注部署环境。")

    status = "ok"
    if warnings:
        status = "degraded" if supabase_configured else "local-only"

    return {
        "ok": status == "ok",
        "status": status,
        "checkedAt": iso_at(),
        "storage": {
            "loadedFrom": loaded_from,
            "supabaseConfigured": bool(supabase_configured),
            "supabaseConfigValid": bool(STATE_RUNTIME_META.get("supabase_config_valid", True)),
            "supabaseWritable": supabase_writable,
            "remoteWriteProtected": loaded_from == "local-fallback" or not supabase_writable,
            "dataDir": str(DATA_DIR),
        },
        "supabase": {
            "table": SUPABASE_STATE_TABLE if supabase_configured else "",
            "rowId": SUPABASE_STATE_ROW_ID if supabase_configured else "",
            "timeoutSeconds": SUPABASE_TIMEOUT_SECONDS,
            "backupRetention": SUPABASE_BACKUP_RETENTION,
            "backupPruneIntervalSeconds": SUPABASE_BACKUP_PRUNE_INTERVAL_SECONDS,
        },
        "media": {
            "storageProvider": "supabase" if supabase_media_storage_enabled() else "inline",
            "bucket": SUPABASE_MEDIA_BUCKET if supabase_media_storage_enabled() else "",
            "imageLimitBytes": MEDIA_IMAGE_LIMIT_BYTES,
            "videoLimitBytes": MEDIA_VIDEO_LIMIT_BYTES,
            "thumbnailLimitBytes": MEDIA_THUMB_LIMIT_BYTES,
        },
        "metrics": metrics,
        "warnings": warnings,
    }


def supabase_state_rows_report(limit=160):
    if not supabase_storage_enabled():
        return {
            "reachable": False,
            "primaryRowPresent": False,
            "backupRows": 0,
            "phoneRecoveryRows": 0,
            "latestUpdatedAt": "",
        }

    rows = supabase_request(
        "GET",
        f"{SUPABASE_STATE_TABLE}?select=id,updated_at&order=updated_at.desc&limit={max(1, int(limit))}",
    ) or []
    backup_prefix = f"{SUPABASE_BACKUP_PREFIX}-20"
    phone_prefix = f"{SUPABASE_PHONE_RECOVERY_PREFIX}-"
    return {
        "reachable": True,
        "primaryRowPresent": any(str(row.get("id") or "") == SUPABASE_STATE_ROW_ID for row in rows),
        "backupRows": sum(1 for row in rows if str(row.get("id") or "").startswith(backup_prefix)),
        "latestBackupPresent": any(str(row.get("id") or "") == f"{SUPABASE_BACKUP_PREFIX}-latest" for row in rows),
        "phoneRecoveryRows": sum(1 for row in rows if str(row.get("id") or "").startswith(phone_prefix)),
        "latestUpdatedAt": str((rows[0] or {}).get("updated_at") or "") if rows else "",
    }


def prune_supabase_backup_rows(force=False):
    global SUPABASE_LAST_BACKUP_PRUNE_TS
    if not supabase_storage_enabled() or SUPABASE_BACKUP_RETENTION <= 0:
        return {"deleted": 0, "skipped": True}

    current_ts = time.monotonic()
    if not force and SUPABASE_LAST_BACKUP_PRUNE_TS and current_ts - SUPABASE_LAST_BACKUP_PRUNE_TS < SUPABASE_BACKUP_PRUNE_INTERVAL_SECONDS:
        return {"deleted": 0, "skipped": True}

    rows = supabase_request(
        "GET",
        f"{SUPABASE_STATE_TABLE}?select=id,updated_at&order=updated_at.desc&limit={max(120, SUPABASE_BACKUP_RETENTION + 80)}",
    ) or []
    backup_prefix = f"{SUPABASE_BACKUP_PREFIX}-20"
    hourly_backups = [
        row
        for row in rows
        if str(row.get("id") or "").startswith(backup_prefix)
    ]
    expired = hourly_backups[SUPABASE_BACKUP_RETENTION:]
    deleted = 0
    for row in expired:
        row_id = str(row.get("id") or "")
        if not row_id:
            continue
        supabase_request(
            "DELETE",
            f"{SUPABASE_STATE_TABLE}?id=eq.{quote(row_id, safe='')}",
            prefer="return=minimal",
        )
        deleted += 1

    SUPABASE_LAST_BACKUP_PRUNE_TS = current_ts
    return {"deleted": deleted, "skipped": False}


def supabase_rest_url(path):
    return f"{SUPABASE_URL}/rest/v1/{path.lstrip('/')}"


def supabase_storage_url(path):
    return f"{SUPABASE_URL}/storage/v1/{path.lstrip('/')}"


def supabase_request(method, path, payload=None, prefer=None):
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Accept": "application/json",
    }
    if payload is not None:
        headers["Content-Type"] = "application/json"
    if prefer:
        headers["Prefer"] = prefer

    data = None
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    request = Request(
        supabase_rest_url(path),
        data=data,
        headers=headers,
        method=method.upper(),
    )

    with urlopen(request, timeout=SUPABASE_TIMEOUT_SECONDS) as response:
        raw = response.read()
        if not raw:
            return None
        return json.loads(raw.decode("utf-8"))


def supabase_storage_request(method, path, payload=None, headers=None, expect_json=True, allow_statuses=None):
    request_headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Accept": "application/json" if expect_json else "*/*",
    }
    if headers:
        request_headers.update(headers)

    data = payload
    if isinstance(payload, (dict, list)):
        request_headers.setdefault("Content-Type", "application/json")
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    request = Request(
        supabase_storage_url(path),
        data=data,
        headers=request_headers,
        method=method.upper(),
    )

    try:
        with urlopen(request, timeout=SUPABASE_TIMEOUT_SECONDS) as response:
            raw = response.read()
            if not raw:
                return None
            if expect_json:
                return json.loads(raw.decode("utf-8"))
            return raw
    except Exception as exc:
        status = getattr(exc, "code", None)
        if allow_statuses and status in allow_statuses:
            raw = exc.read() if hasattr(exc, "read") else b""
            if not raw:
                return None
            if expect_json:
                return json.loads(raw.decode("utf-8"))
            return raw
        raise


def load_state_from_supabase():
    STATE_RUNTIME_META["remote_repair_required"] = False
    rows = supabase_request(
        "GET",
        f"{SUPABASE_STATE_TABLE}?id=eq.{quote(SUPABASE_STATE_ROW_ID, safe='')}&select=payload",
    )
    primary_state = None
    primary_metrics = state_integrity_metrics(None)
    if rows:
        payload = rows[0].get("payload")
        if isinstance(payload, dict):
            primary_state = sanitize_state(payload)
            primary_metrics = state_integrity_metrics(primary_state)

    backup_rows = supabase_request(
        "GET",
        f"{SUPABASE_STATE_TABLE}?select=id,payload,updated_at&order=updated_at.desc&limit=20",
    ) or []
    best_backup_state = None
    best_backup_metrics = state_integrity_metrics(None)
    best_backup_row_id = ""
    for row in backup_rows:
        row_id = str(row.get("id") or "")
        payload = row.get("payload")
        if not row_id.startswith(SUPABASE_BACKUP_PREFIX) or not isinstance(payload, dict):
            continue
        candidate_state = sanitize_state(payload)
        candidate_metrics = state_integrity_metrics(candidate_state)
        if is_materially_richer_state(candidate_metrics, best_backup_metrics):
            best_backup_state = candidate_state
            best_backup_metrics = candidate_metrics
            best_backup_row_id = row_id

    if primary_state is None and best_backup_state is not None:
        storage_log(f"Supabase primary row missing, restored from backup row: {best_backup_row_id}")
        STATE_RUNTIME_META["remote_repair_required"] = True
        return best_backup_state

    if primary_state is not None and best_backup_state is not None and is_materially_richer_state(best_backup_metrics, primary_metrics):
        storage_log(
            "Supabase primary row looked less complete than backup; "
            f"using backup row {best_backup_row_id} instead."
        )
        STATE_RUNTIME_META["remote_repair_required"] = True
        return best_backup_state

    return primary_state


def load_state_from_local(create_if_missing=True):
    if create_if_missing:
        ensure_data_file()
    elif not STATE_FILE.exists():
        return None
    with STATE_FILE.open("r", encoding="utf-8") as handle:
        return sanitize_state(json.load(handle))


def save_state_to_supabase(state):
    payload = sanitize_state(deepcopy(state))
    saved_at = now_utc()
    rows_to_save = [
        {
            "id": SUPABASE_STATE_ROW_ID,
            "payload": payload,
            "updated_at": saved_at.isoformat(),
        },
        {
            "id": f"{SUPABASE_BACKUP_PREFIX}-latest",
            "payload": payload,
            "updated_at": saved_at.isoformat(),
        },
        {
            "id": f"{SUPABASE_BACKUP_PREFIX}-{saved_at.strftime('%Y%m%d%H')}",
            "payload": payload,
            "updated_at": saved_at.isoformat(),
        },
    ]
    rows_to_save.extend(build_phone_recovery_rows(payload, saved_at))
    supabase_request(
        "POST",
        f"{SUPABASE_STATE_TABLE}?on_conflict=id",
        rows_to_save,
        prefer="resolution=merge-duplicates,return=minimal",
    )
    try:
        prune_result = prune_supabase_backup_rows()
        if prune_result.get("deleted"):
            storage_log(f"Pruned {prune_result['deleted']} old Supabase backup row(s).")
    except Exception as exc:
        storage_log(f"Supabase backup prune skipped: {exc}")
    set_runtime_storage_state("supabase", True, payload)


def find_profile_by_role_phone(state, role, phone):
    phone_key = normalize_phone(phone)
    if not phone_key:
        return None
    matches = [
        profile
        for profile in state.get("profiles", {}).values()
        if profile.get("role") == role and normalize_phone(profile.get("phone")) == phone_key
    ]
    return pick_preferred_profile(state, matches)


def find_profiles_by_phone(state, phone):
    phone_key = normalize_phone(phone)
    if not phone_key:
        return []
    profiles = [
        profile
        for profile in state.get("profiles", {}).values()
        if normalize_phone(profile.get("phone")) == phone_key
    ]
    profiles.sort(key=lambda item: profile_signal_score(state, item), reverse=True)
    return profiles


def find_profiles_by_account_role(state, account_id, role):
    account_key = str(account_id or "").strip()
    if not account_key or role not in {"enthusiast", "gym", "coach"}:
        return []
    profiles = [
        profile
        for profile in state.get("profiles", {}).values()
        if profile.get("accountId") == account_key and profile.get("role") == role
    ]
    profiles.sort(key=lambda item: profile_signal_score(state, item), reverse=True)
    return profiles


def collect_profile_alias_ids(state, profile_id):
    profiles = state.get("profiles", {})
    alias_registry = ensure_profile_alias_registry(state)
    start_id = str(profile_id or "").strip()
    visited = set()
    while start_id in alias_registry and start_id not in visited:
        visited.add(start_id)
        start_id = alias_registry[start_id]
    start = profiles.get(start_id)
    if not start:
        return {profile_id} if profile_id else set()

    role = str(start.get("role") or "").strip()
    if role not in {"enthusiast", "gym", "coach"}:
        return {profile_id}

    discovered_ids = set()
    queue = [start]
    known_account_ids = set()
    known_phones = set()

    while queue:
        current = queue.pop()
        current_id = current.get("id")
        if not current_id or current_id in discovered_ids:
            continue
        discovered_ids.add(current_id)

        account_id = str(current.get("accountId") or "").strip()
        phone = normalize_phone(current.get("phone"))
        if account_id:
            known_account_ids.add(account_id)
        if phone:
            known_phones.add(phone)

        for candidate in profiles.values():
            if candidate.get("id") in discovered_ids:
                continue
            if str(candidate.get("role") or "").strip() != role:
                continue
            candidate_account_id = str(candidate.get("accountId") or "").strip()
            candidate_phone = normalize_phone(candidate.get("phone"))
            if (
                candidate_account_id
                and candidate_account_id in known_account_ids
            ) or (
                candidate_phone
                and candidate_phone in known_phones
            ):
                queue.append(candidate)

    return discovered_ids or {profile_id}


def phone_recovery_row_id(phone):
    phone_key = normalize_phone(phone)
    return f"{SUPABASE_PHONE_RECOVERY_PREFIX}-{phone_key}" if phone_key else ""


def recovery_slice_metrics(payload):
    if not isinstance(payload, dict):
        return {"profiles": 0, "follows": 0, "posts": 0, "bookings": 0, "threads": 0, "score": 0}
    profiles = len(payload.get("profiles") or {})
    follows = len(payload.get("follows") or [])
    posts = len(payload.get("posts") or {})
    bookings = len(payload.get("bookings") or [])
    threads = len(payload.get("threads") or [])
    score = profiles * 1000 + follows * 120 + posts * 90 + bookings * 70 + threads * 60
    return {
        "profiles": profiles,
        "follows": follows,
        "posts": posts,
        "bookings": bookings,
        "threads": threads,
        "score": score,
    }


def build_phone_recovery_slice(state, phone):
    phone_key = normalize_phone(phone)
    if len(phone_key) != 11:
        return None

    account = resolve_account_by_phone(state, phone_key)
    matched_profiles = find_profiles_by_phone(state, phone_key)
    if not account and not matched_profiles:
        return None

    canonical_profile_ids = []
    alias_profile_ids = set()

    if account:
        for profile_id in (account.get("profilesByRole") or {}).values():
            canonical_profile_id = resolve_canonical_profile_id(state, profile_id)
            if canonical_profile_id and canonical_profile_id not in canonical_profile_ids:
                canonical_profile_ids.append(canonical_profile_id)
    for profile in matched_profiles:
        canonical_profile_id = resolve_canonical_profile_id(state, profile.get("id"))
        if canonical_profile_id and canonical_profile_id not in canonical_profile_ids:
            canonical_profile_ids.append(canonical_profile_id)

    for profile_id in canonical_profile_ids:
        alias_profile_ids.update(collect_profile_alias_ids(state, profile_id))

    if not alias_profile_ids:
        alias_profile_ids = {profile.get("id") for profile in matched_profiles if profile.get("id")}

    alias_profile_ids = {
        profile_id
        for profile_id in alias_profile_ids
        if profile_id in (state.get("profiles") or {})
    }
    if not alias_profile_ids:
        return None

    account_ids = set()
    if account and account.get("id"):
        account_ids.add(account["id"])
    for profile_id in alias_profile_ids:
        profile = (state.get("profiles") or {}).get(profile_id)
        account_id = str((profile or {}).get("accountId") or "").strip()
        if account_id:
            account_ids.add(account_id)

    related_profiles = {
        profile_id: deepcopy((state.get("profiles") or {}).get(profile_id))
        for profile_id in alias_profile_ids
        if (state.get("profiles") or {}).get(profile_id)
    }
    related_accounts = {
        account_id: deepcopy((state.get("accounts") or {}).get(account_id))
        for account_id in account_ids
        if (state.get("accounts") or {}).get(account_id)
    }
    related_follows = [
        deepcopy(item)
        for item in (state.get("follows") or [])
        if item.get("sourceProfileId") in alias_profile_ids or item.get("targetProfileId") in alias_profile_ids
    ]
    related_blocks = [
        deepcopy(item)
        for item in (state.get("blocks") or [])
        if item.get("sourceProfileId") in alias_profile_ids or item.get("targetProfileId") in alias_profile_ids
    ]
    favorite_post_ids = {
        item.get("postId")
        for item in (state.get("postFavorites") or [])
        if item.get("sourceProfileId") in alias_profile_ids and item.get("postId")
    }
    related_posts = {
        post_id: deepcopy(post)
        for post_id, post in (state.get("posts") or {}).items()
        if (
            post.get("authorProfileId") in alias_profile_ids
            or post_id in favorite_post_ids
            or any(profile_id in alias_profile_ids for profile_id in post.get("likes", []) or [])
            or any((comment or {}).get("authorProfileId") in alias_profile_ids for comment in post.get("comments", []) or [])
        )
    }
    related_bookings = [
        deepcopy(item)
        for item in (state.get("bookings") or [])
        if item.get("createdByProfileId") in alias_profile_ids or item.get("targetProfileId") in alias_profile_ids
    ]
    related_threads = [
        deepcopy(item)
        for item in (state.get("threads") or [])
        if any(participant in alias_profile_ids for participant in (item.get("participants") or []))
    ]
    related_favorites = [
        deepcopy(item)
        for item in (state.get("postFavorites") or [])
        if item.get("sourceProfileId") in alias_profile_ids
    ]
    related_aliases = {
        source: target
        for source, target in (state.get("profileAliases") or {}).items()
        if source in alias_profile_ids or target in alias_profile_ids
    }

    return {
        "phone": phone_key,
        "accountId": account.get("id") if account else "",
        "profiles": related_profiles,
        "accounts": related_accounts,
        "follows": related_follows,
        "blocks": related_blocks,
        "posts": related_posts,
        "bookings": related_bookings,
        "threads": related_threads,
        "postFavorites": related_favorites,
        "profileAliases": related_aliases,
        "updatedAt": iso_at(),
    }


def build_phone_recovery_rows(state, saved_at):
    profiles = state.get("profiles", {}) if isinstance(state, dict) else {}
    phones = sorted(
        {
            normalize_phone(profile.get("phone"))
            for profile_id, profile in profiles.items()
            if not is_demo_profile_id(profile_id) and normalize_phone(profile.get("phone"))
        }
    )
    rows = []
    for phone in phones:
        payload = build_phone_recovery_slice(state, phone)
        if not payload:
            continue
        rows.append(
            {
                "id": phone_recovery_row_id(phone),
                "payload": payload,
                "updated_at": saved_at.isoformat(),
            }
        )
    return rows


def merge_phone_recovery_slice(state, payload):
    if not isinstance(payload, dict):
        return False

    changed = False
    accounts = state.setdefault("accounts", {})
    profiles = state.setdefault("profiles", {})

    for account_id, account in (payload.get("accounts") or {}).items():
        if not account_id or not isinstance(account, dict):
            continue
        existing = accounts.get(account_id)
        if not existing:
            accounts[account_id] = deepcopy(account)
            changed = True
            continue
        merged_roles = {**(existing.get("profilesByRole") or {}), **(account.get("profilesByRole") or {})}
        if existing.get("phone") != account.get("phone") and account.get("phone"):
            existing["phone"] = account.get("phone")
            changed = True
        if existing.get("restoreToken") != account.get("restoreToken") and account.get("restoreToken"):
            existing["restoreToken"] = account.get("restoreToken")
            changed = True
        if existing.get("profilesByRole") != merged_roles:
            existing["profilesByRole"] = merged_roles
            changed = True
        merged_providers = {**(existing.get("identityProviders") or {}), **(account.get("identityProviders") or {})}
        if existing.get("identityProviders") != merged_providers:
            existing["identityProviders"] = merged_providers
            changed = True
        before_identity = json.dumps(existing.get("identityProviders", {}), ensure_ascii=False, sort_keys=True)
        ensure_account_identity_bindings(existing)
        after_identity = json.dumps(existing.get("identityProviders", {}), ensure_ascii=False, sort_keys=True)
        if before_identity != after_identity:
            changed = True

    for profile_id, profile in (payload.get("profiles") or {}).items():
        if not profile_id or not isinstance(profile, dict):
            continue
        existing = profiles.get(profile_id)
        if not existing:
            profiles[profile_id] = deepcopy(profile)
            changed = True
            continue
        before = json.dumps(existing, ensure_ascii=False, sort_keys=True)
        merge_duplicate_profile_data(existing, profile)
        if existing.get("accountId") in (None, "") and profile.get("accountId"):
            existing["accountId"] = profile.get("accountId")
        after = json.dumps(existing, ensure_ascii=False, sort_keys=True)
        if before != after:
            changed = True

    alias_registry = state.setdefault("profileAliases", {})
    for source, target in (payload.get("profileAliases") or {}).items():
        if not source or not target:
            continue
        if alias_registry.get(source) != target:
            alias_registry[source] = target
            changed = True

    existing_follows = {
        (item.get("sourceProfileId"), item.get("targetProfileId"))
        for item in (state.get("follows") or [])
    }
    for item in payload.get("follows") or []:
        key = (item.get("sourceProfileId"), item.get("targetProfileId"))
        if not all(key) or key in existing_follows:
            continue
        state.setdefault("follows", []).append(deepcopy(item))
        existing_follows.add(key)
        changed = True

    existing_blocks = {
        (item.get("sourceProfileId"), item.get("targetProfileId"))
        for item in (state.get("blocks") or [])
    }
    for item in payload.get("blocks") or []:
        key = (item.get("sourceProfileId"), item.get("targetProfileId"))
        if not all(key) or key in existing_blocks:
            continue
        state.setdefault("blocks", []).append(deepcopy(item))
        existing_blocks.add(key)
        changed = True

    existing_posts = state.setdefault("posts", {})
    for post_id, post in (payload.get("posts") or {}).items():
        if not post_id or not isinstance(post, dict):
            continue
        existing_post = existing_posts.get(post_id)
        if not existing_post:
            existing_posts[post_id] = deepcopy(post)
            changed = True
            continue
        before = json.dumps(existing_post, ensure_ascii=False, sort_keys=True)
        merge_recovered_post_data(existing_post, post)
        after = json.dumps(existing_post, ensure_ascii=False, sort_keys=True)
        if before != after:
            changed = True

    existing_booking_ids = {
        item.get("id")
        for item in (state.get("bookings") or [])
        if item.get("id")
    }
    for item in payload.get("bookings") or []:
        item_id = item.get("id")
        if not item_id or item_id in existing_booking_ids:
            continue
        state.setdefault("bookings", []).append(deepcopy(item))
        existing_booking_ids.add(item_id)
        changed = True

    existing_thread_ids = {
        item.get("id")
        for item in (state.get("threads") or [])
        if item.get("id")
    }
    for item in payload.get("threads") or []:
        item_id = item.get("id")
        if not item_id:
            continue
        existing_thread = next((thread for thread in state.get("threads", []) if thread.get("id") == item_id), None)
        if existing_thread:
            before = json.dumps(existing_thread, ensure_ascii=False, sort_keys=True)
            merge_recovered_thread_data(existing_thread, item)
            after = json.dumps(existing_thread, ensure_ascii=False, sort_keys=True)
            if before != after:
                changed = True
            continue
        state.setdefault("threads", []).append(deepcopy(item))
        existing_thread_ids.add(item_id)
        changed = True

    favorite_pairs = {
        (item.get("sourceProfileId"), item.get("postId"))
        for item in (state.get("postFavorites") or [])
    }
    for item in payload.get("postFavorites") or []:
        key = (item.get("sourceProfileId"), item.get("postId"))
        if not all(key) or key in favorite_pairs:
            continue
        state.setdefault("postFavorites", []).append(deepcopy(item))
        favorite_pairs.add(key)
        changed = True

    if changed:
        normalize_follows(state)
        normalize_blocks(state)
        normalize_threads(state)
        reconcile_account_registry(state)
    return changed


def merge_recovered_post_data(existing_post, recovered_post):
    for field in ["authorProfileId", "createdAt", "content", "meta"]:
        if existing_post.get(field) in (None, "") and recovered_post.get(field) not in (None, ""):
            existing_post[field] = recovered_post.get(field)

    if not existing_post.get("media") and recovered_post.get("media"):
        existing_post["media"] = deepcopy(recovered_post.get("media") or [])
    if not existing_post.get("checkin") and recovered_post.get("checkin"):
        existing_post["checkin"] = deepcopy(recovered_post.get("checkin"))

    likes = []
    for profile_id in (existing_post.get("likes") or []) + (recovered_post.get("likes") or []):
        if profile_id and profile_id not in likes:
            likes.append(profile_id)
    existing_post["likes"] = likes

    existing_post["comments"] = merge_records_by_id(
        recovered_post.get("comments", []),
        existing_post.get("comments", []),
    )


def merge_recovered_thread_data(existing_thread, recovered_thread):
    participants = []
    for profile_id in (existing_thread.get("participants") or []) + (recovered_thread.get("participants") or []):
        if profile_id and profile_id not in participants:
            participants.append(profile_id)
    existing_thread["participants"] = participants

    messages = {}
    for message in recovered_thread.get("messages", []) or []:
        message_id = (message or {}).get("id")
        if message_id:
            messages[message_id] = deepcopy(message)
    for message in existing_thread.get("messages", []) or []:
        message_id = (message or {}).get("id")
        if message_id:
            messages[message_id] = deepcopy(message)
    existing_thread["messages"] = sorted(messages.values(), key=lambda item: item.get("createdAt", ""))


def load_phone_recovery_from_supabase(phone):
    if not supabase_storage_enabled():
        return None
    phone_key = normalize_phone(phone)
    if len(phone_key) != 11:
        return None

    best_payload = None
    best_metrics = recovery_slice_metrics(None)

    direct_row_id = phone_recovery_row_id(phone_key)
    if direct_row_id:
        rows = supabase_request(
            "GET",
            f"{SUPABASE_STATE_TABLE}?id=eq.{quote(direct_row_id, safe='')}&select=payload",
        ) or []
        if rows and isinstance(rows[0].get("payload"), dict):
            candidate_payload = rows[0].get("payload")
            candidate_metrics = recovery_slice_metrics(candidate_payload)
            if is_materially_richer_state(candidate_metrics, best_metrics):
                best_payload = candidate_payload
                best_metrics = candidate_metrics

    backup_rows = supabase_request(
        "GET",
        f"{SUPABASE_STATE_TABLE}?select=id,payload,updated_at&order=updated_at.desc&limit=20",
    ) or []
    for row in backup_rows:
        row_id = str(row.get("id") or "")
        payload = row.get("payload")
        if not row_id.startswith(SUPABASE_BACKUP_PREFIX) or not isinstance(payload, dict):
            continue
        candidate_payload = build_phone_recovery_slice(payload, phone_key)
        candidate_metrics = recovery_slice_metrics(candidate_payload)
        if is_materially_richer_state(candidate_metrics, best_metrics):
            best_payload = candidate_payload
            best_metrics = candidate_metrics

    return best_payload


def load_phone_recovery_rows_from_supabase(limit=500):
    if not supabase_storage_enabled():
        return []
    rows = supabase_request(
        "GET",
        f"{SUPABASE_STATE_TABLE}?select=id,payload,updated_at&order=updated_at.desc&limit={max(1, int(limit))}",
    ) or []
    latest_by_phone = {}
    prefix = f"{SUPABASE_PHONE_RECOVERY_PREFIX}-"
    for row in rows:
        row_id = str(row.get("id") or "")
        payload = row.get("payload")
        if not row_id.startswith(prefix) or not isinstance(payload, dict):
            continue
        phone_key = normalize_phone(payload.get("phone") or row_id[len(prefix):])
        if len(phone_key) != 11 or phone_key in latest_by_phone:
            continue
        latest_by_phone[phone_key] = payload
    return list(latest_by_phone.values())


def merge_phone_recovery_rows_from_supabase(state):
    if not supabase_storage_enabled():
        return False
    try:
        payloads = load_phone_recovery_rows_from_supabase()
    except Exception as exc:
        storage_log(f"Phone recovery row scan skipped: {exc}")
        return False

    changed = False
    merged_count = 0
    for payload in payloads:
        if merge_phone_recovery_slice(state, payload):
            changed = True
            merged_count += 1
    if changed:
        storage_log(f"Merged {merged_count} phone recovery row(s) into primary state.")
    return changed


def restore_phone_identity_from_supabase(state, phone):
    payload = load_phone_recovery_from_supabase(phone)
    if not payload:
        return False
    changed = merge_phone_recovery_slice(state, payload)
    return bool(resolve_account_by_phone(state, phone)) or changed


def session_phone_candidates(state, session):
    candidates = []

    def add(phone):
        phone_key = normalize_phone(phone)
        if len(phone_key) == 11 and phone_key not in candidates:
            candidates.append(phone_key)

    add(session.get("lastVerifiedPhone"))
    for phone in (session.get("verifiedPhones") or {}).keys():
        add(phone)
    for account_id in session.get("managedAccountIds", []):
        account = ensure_account_registry(state).get(str(account_id or "").strip())
        add((account or {}).get("phone"))
    for profile_id in session.get("managedProfileIds", []):
        profile = (state.get("profiles") or {}).get(resolve_canonical_profile_id(state, profile_id))
        add((profile or {}).get("phone"))
    current_profile = (state.get("profiles") or {}).get(resolve_canonical_profile_id(state, session.get("currentActorProfileId")))
    add((current_profile or {}).get("phone"))
    return candidates


def ensure_session_identity(state, session, preferred_role="", requested_profile_id=""):
    requested_profile_id = resolve_canonical_profile_id(state, requested_profile_id)
    if requested_profile_id:
        allowed, canonical_profile_id = session_manages_profile(state, session, requested_profile_id)
        if allowed:
            return True, canonical_profile_id
        requested_profile = (state.get("profiles") or {}).get(requested_profile_id)
        if requested_profile:
            account = ensure_profile_account(state, requested_profile, requested_profile.get("phone"))
            attach_account_to_session(state, session, account, preferred_role or requested_profile.get("role") or session.get("selectedRole"))
            allowed, canonical_profile_id = session_manages_profile(state, session, requested_profile_id)
            if allowed:
                return True, canonical_profile_id

    current_actor_profile_id = resolve_canonical_profile_id(state, session.get("currentActorProfileId"))
    if current_actor_profile_id:
        allowed, canonical_profile_id = session_manages_profile(state, session, current_actor_profile_id)
        if allowed:
            return True, canonical_profile_id

    fallback_role = preferred_role if preferred_role in {"enthusiast", "gym", "coach"} else str(session.get("selectedRole") or "").strip()
    for phone in session_phone_candidates(state, session):
        account = resolve_account_by_phone(state, phone)
        if not account:
            restore_phone_identity_from_supabase(state, phone)
            account = resolve_account_by_phone(state, phone)
        if not account:
            continue
        attach_account_to_session(state, session, account, fallback_role)
        if requested_profile_id:
            allowed, canonical_profile_id = session_manages_profile(state, session, requested_profile_id)
            if allowed:
                return True, canonical_profile_id
        current_actor_profile_id = resolve_canonical_profile_id(state, session.get("currentActorProfileId"))
        if current_actor_profile_id:
            return True, current_actor_profile_id

    return False, requested_profile_id or ""


def resolve_canonical_profile_id(state, profile_id):
    if not profile_id:
        return ""
    alias_registry = ensure_profile_alias_registry(state)
    resolved_id = str(profile_id or "").strip()
    visited = set()
    while resolved_id in alias_registry and resolved_id not in visited:
        visited.add(resolved_id)
        resolved_id = alias_registry[resolved_id]
    alias_ids = collect_profile_alias_ids(state, resolved_id)
    profiles = [state.get("profiles", {}).get(item_id) for item_id in alias_ids]
    preferred = pick_preferred_profile(state, profiles)
    return preferred.get("id") if preferred else resolved_id


def canonicalize_profile_ids(state, profile_ids):
    canonical_ids = []
    seen = set()
    for profile_id in profile_ids or []:
        canonical_id = resolve_canonical_profile_id(state, profile_id)
        if canonical_id and canonical_id not in seen and canonical_id in state.get("profiles", {}):
            seen.add(canonical_id)
            canonical_ids.append(canonical_id)
    return canonical_ids


def profile_signal_score(state, profile):
    if not profile:
        return (-1, "", "")

    profile_id = profile.get("id")
    posts = sum(1 for item in state.get("posts", {}).values() if item.get("authorProfileId") == profile_id)
    incoming_follows = sum(1 for item in state.get("follows", []) if item.get("targetProfileId") == profile_id)
    outgoing_follows = sum(1 for item in state.get("follows", []) if item.get("sourceProfileId") == profile_id)
    incoming_bookings = sum(1 for item in state.get("bookings", []) if item.get("targetProfileId") == profile_id)
    outgoing_bookings = sum(1 for item in state.get("bookings", []) if item.get("createdByProfileId") == profile_id)
    reviews = len(profile.get("reviews", []))
    checkins = len(profile.get("checkins", []))
    listed_bonus = 6 if profile.get("listed", True) else 0
    avatar_bonus = 2 if profile.get("avatarImage") else 0
    bio_bonus = 2 if profile.get("bio") else 0

    total = (
        posts * 18
        + incoming_follows * 12
        + outgoing_follows * 8
        + incoming_bookings * 16
        + outgoing_bookings * 10
        + reviews * 14
        + checkins * 10
        + listed_bonus
        + avatar_bonus
        + bio_bonus
    )
    return (total, profile.get("createdAt") or "", profile_id or "")


def pick_preferred_profile(state, profiles):
    candidates = [profile for profile in profiles if profile]
    if not candidates:
        return None
    return max(candidates, key=lambda item: profile_signal_score(state, item))


def make_profile(**kwargs):
    profile = {
        "id": kwargs["id"],
        "accountId": kwargs.get("accountId", ""),
        "owner_session_id": kwargs.get("owner_session_id"),
        "role": kwargs["role"],
        "name": kwargs["name"],
        "handle": kwargs["handle"],
        "avatar": kwargs.get("avatar", kwargs["name"][:1]),
        "avatarImage": kwargs.get("avatarImage", default_avatar_for_role(kwargs["role"])),
        "coverImage": kwargs.get("coverImage", ""),
        "city": kwargs.get("city", "厦门"),
        "locationLabel": kwargs.get("locationLabel", "厦门 · 思明区"),
        "lat": kwargs.get("lat", 24.4798),
        "lng": kwargs.get("lng", 118.0894),
        "bio": kwargs.get("bio", ""),
        "shortDesc": kwargs.get("shortDesc", ""),
        "price": kwargs.get("price", ""),
        "tags": kwargs.get("tags", []),
        "level": kwargs.get("level", ""),
        "goal": kwargs.get("goal", ""),
        "hours": kwargs.get("hours", ""),
        "contactName": kwargs.get("contactName", ""),
        "phone": kwargs.get("phone", ""),
        "gender": kwargs.get("gender", ""),
        "heightCm": kwargs.get("heightCm", None),
        "weightKg": kwargs.get("weightKg", None),
        "favoriteSports": kwargs.get("favoriteSports", []),
        "connectedDevices": kwargs.get("connectedDevices", []),
        "healthSource": kwargs.get("healthSource", ""),
        "deviceSyncedAt": kwargs.get("deviceSyncedAt", ""),
        "healthSnapshot": kwargs.get("healthSnapshot", {}),
        "healthHistory": kwargs.get("healthHistory", []),
        "restingHeartRate": kwargs.get("restingHeartRate", None),
        "bodyFat": kwargs.get("bodyFat", None),
        "externalWorkoutIds": kwargs.get("externalWorkoutIds", []),
        "pricingPlans": kwargs.get("pricingPlans", []),
        "years": kwargs.get("years", ""),
        "certifications": kwargs.get("certifications", []),
        "checkins": kwargs.get("checkins", []),
        "listed": kwargs.get("listed", True),
        "reviews": kwargs.get("reviews", []),
        "createdAt": kwargs.get("createdAt", iso_at()),
    }
    return profile


def merge_records_by_id(seed_items, existing_items):
    merged = {}
    for item in seed_items or []:
        item_id = item.get("id")
        if item_id:
            merged[item_id] = deepcopy(item)
    for item in existing_items or []:
        item_id = item.get("id")
        if item_id and item_id in merged:
            merged[item_id] = {**merged[item_id], **deepcopy(item)}
        elif item_id:
            merged[item_id] = deepcopy(item)
    return list(merged.values())


def ensure_account_registry(state):
    return state.setdefault("accounts", {})


def ensure_profile_alias_registry(state):
    aliases = state.setdefault("profileAliases", {})
    normalized = {}
    for source_id, target_id in aliases.items():
        source_key = str(source_id or "").strip()
        target_key = str(target_id or "").strip()
        if source_key and target_key and source_key != target_key:
            normalized[source_key] = target_key
    if normalized != aliases:
        state["profileAliases"] = normalized
    return state["profileAliases"]


def register_profile_alias(state, source_profile_id, target_profile_id):
    source_id = str(source_profile_id or "").strip()
    target_id = str(target_profile_id or "").strip()
    if not source_id or not target_id or source_id == target_id:
        return
    aliases = ensure_profile_alias_registry(state)
    visited = {source_id}
    while target_id in aliases and target_id not in visited:
        visited.add(target_id)
        target_id = aliases[target_id]
    aliases[source_id] = target_id


def create_account_record(phone=""):
    phone_key = normalize_phone(phone)
    created_at = iso_at()
    account = {
        "id": f"acct-{uuid.uuid4().hex[:10]}",
        "restoreToken": f"restore-{uuid.uuid4().hex}",
        "phone": phone_key,
        "profilesByRole": {},
        "primaryProvider": "phone" if phone_key else "",
        "identityProviders": {},
        "authVersion": 1,
        "createdAt": created_at,
    }
    ensure_account_identity_bindings(account)
    return {
        **account,
    }


def find_account_by_token(state, account_id, restore_token):
    if not account_id or not restore_token:
        return None
    account = ensure_account_registry(state).get(account_id)
    if account and account.get("restoreToken") == restore_token:
        return account
    return None


def ensure_profile_account(state, profile, phone=""):
    accounts = ensure_account_registry(state)
    account_id = profile.get("accountId")
    account = accounts.get(account_id) if account_id else None
    if not account:
        account = create_account_record(phone or profile.get("phone"))
        accounts[account["id"]] = account
        profile["accountId"] = account["id"]

    normalized_phone = normalize_phone(phone or account.get("phone") or profile.get("phone"))
    if normalized_phone:
        account["phone"] = normalized_phone

    ensure_account_identity_bindings(account)
    account.setdefault("profilesByRole", {})[profile["role"]] = profile["id"]
    profile["accountId"] = account["id"]
    return account


def find_account_by_phone(state, phone, preferred_role=""):
    phone_key = normalize_phone(phone)
    if not phone_key:
        return None

    fallback = None
    for account in ensure_account_registry(state).values():
        if normalize_phone(account.get("phone")) != phone_key:
            continue
        if preferred_role and preferred_role in (account.get("profilesByRole") or {}):
            return account
        if fallback is None:
            fallback = account
    return fallback


def validate_phone_or_raise(phone):
    phone_key = normalize_phone(phone)
    if len(phone_key) != 11:
        raise ValueError("请输入正确的 11 位手机号。")
    return phone_key


def mask_phone(phone):
    phone_key = normalize_phone(phone)
    if len(phone_key) != 11:
        return phone_key
    return f"{phone_key[:3]}****{phone_key[-4:]}"


def ensure_account_identity_bindings(account):
    if not isinstance(account, dict):
        return {}
    providers = account.setdefault("identityProviders", {})
    if not isinstance(providers, dict):
        providers = {}
        account["identityProviders"] = providers

    phone_key = normalize_phone(account.get("phone"))
    if phone_key:
        phone_provider = providers.setdefault("phone", {})
        phone_provider["type"] = "phone"
        phone_provider["identifier"] = phone_key
        phone_provider["maskedIdentifier"] = mask_phone(phone_key)
        phone_provider["verified"] = True
        phone_provider.setdefault("verifiedAt", account.get("createdAt") or iso_at())
        phone_provider.setdefault("boundAt", account.get("createdAt") or iso_at())

    for provider_type in ["wechat", "apple"]:
        provider = providers.get(provider_type)
        if not isinstance(provider, dict):
            continue
        provider["type"] = provider_type
        provider.setdefault("verified", bool(provider.get("identifier")))
        provider.setdefault("maskedIdentifier", "已绑定" if provider.get("identifier") else "")

    if not account.get("primaryProvider"):
        account["primaryProvider"] = "phone" if phone_key else next(iter(providers.keys()), "")
    account["authVersion"] = max(1, int(account.get("authVersion") or 1))
    return providers


def bind_account_identity_provider(account, provider_type, identifier, **extra):
    provider_type = str(provider_type or "").strip()
    identifier = str(identifier or "").strip()
    if not provider_type or not identifier:
        return None
    providers = account.setdefault("identityProviders", {})
    provider = providers.setdefault(provider_type, {})
    provider.update(
        {
            "type": provider_type,
            "identifier": identifier,
            "maskedIdentifier": "已绑定",
            "verified": True,
            "verifiedAt": iso_at(),
            "boundAt": provider.get("boundAt") or iso_at(),
        }
    )
    for key, value in extra.items():
        if value not in (None, ""):
            provider[key] = value
    if not account.get("primaryProvider"):
        account["primaryProvider"] = provider_type
    ensure_account_identity_bindings(account)
    return provider


def find_account_by_identity_provider(state, provider_type, identifier):
    provider_type = str(provider_type or "").strip()
    identifier = str(identifier or "").strip()
    if not provider_type or not identifier:
        return None
    for account in ensure_account_registry(state).values():
        provider = (account.get("identityProviders") or {}).get(provider_type)
        if isinstance(provider, dict) and str(provider.get("identifier") or "").strip() == identifier:
            return account
    return None


def resolve_account_by_phone(state, phone):
    phone_key = normalize_phone(phone)
    if not phone_key:
        return None

    account = find_account_by_phone(state, phone)
    matched_profiles = find_profiles_by_phone(state, phone)

    if not account and not matched_profiles:
        return None

    if not account and matched_profiles:
        account = ensure_profile_account(state, matched_profiles[0], phone)

    if not account:
        return None

    account["phone"] = phone_key
    role_map = account.setdefault("profilesByRole", {})
    ensure_account_identity_bindings(account)

    roles_to_reconcile = set(role_map.keys())
    roles_to_reconcile.update(
        str(profile.get("role") or "").strip()
        for profile in matched_profiles
        if str(profile.get("role") or "").strip() in {"enthusiast", "gym", "coach"}
    )

    for role in sorted(roles_to_reconcile):
        candidates = []
        existing_profile = state["profiles"].get(role_map.get(role, ""))
        if existing_profile:
            candidates.append(existing_profile)
        for profile in find_profiles_by_account_role(state, account["id"], role):
            if profile not in candidates:
                candidates.append(profile)
        for profile in matched_profiles:
            if str(profile.get("role") or "").strip() != role:
                continue
            if profile.get("accountId") != account["id"]:
                profile["accountId"] = account["id"]
            if profile not in candidates:
                candidates.append(profile)
        preferred = pick_preferred_profile(state, candidates)
        if preferred:
            role_map[role] = preferred["id"]

    return account


def serialize_phone_matches(state, phone):
    account = resolve_account_by_phone(state, phone)
    if not account:
        return []

    items = []
    seen_profiles = set()
    for role, profile_id in sorted(account.get("profilesByRole", {}).items()):
        canonical_profile_id = resolve_canonical_profile_id(state, profile_id)
        if canonical_profile_id in seen_profiles:
            continue
        seen_profiles.add(canonical_profile_id)
        profile = state.get("profiles", {}).get(canonical_profile_id)
        if not profile:
            continue
        items.append(
            {
                "role": role,
                "profileId": canonical_profile_id,
                "name": profile.get("name") or "平台用户",
                "phone": account.get("phone", ""),
                "avatarImage": compact_avatar_image(profile.get("avatarImage"), role),
            }
        )
    return items


def reconcile_account_registry(state):
    changed = deduplicate_profiles_by_phone_role(state)
    if deduplicate_profiles_by_account_role(state):
        changed = True
    before_favorites = json.dumps(state.get("postFavorites", []), ensure_ascii=False, sort_keys=True)
    normalize_post_favorites(state)
    after_favorites = json.dumps(state.get("postFavorites", []), ensure_ascii=False, sort_keys=True)
    if before_favorites != after_favorites:
        changed = True
    old_accounts = ensure_account_registry(state)
    rebuilt_accounts = {}
    phone_index = {}

    def build_account_seed(existing_account, phone=""):
        normalized_phone = normalize_phone(phone or (existing_account or {}).get("phone"))
        seed = {
            "id": (existing_account or {}).get("id") or f"acct-{uuid.uuid4().hex[:10]}",
            "restoreToken": (existing_account or {}).get("restoreToken") or f"restore-{uuid.uuid4().hex}",
            "phone": normalized_phone,
            "profilesByRole": {},
            "primaryProvider": (existing_account or {}).get("primaryProvider") or ("phone" if normalized_phone else ""),
            "identityProviders": deepcopy((existing_account or {}).get("identityProviders") or {}),
            "authVersion": max(1, int((existing_account or {}).get("authVersion") or 1)),
            "createdAt": (existing_account or {}).get("createdAt") or iso_at(),
        }
        ensure_account_identity_bindings(seed)
        return seed

    for profile in state.get("profiles", {}).values():
        role = str(profile.get("role") or "").strip()
        if role not in {"enthusiast", "gym", "coach"}:
            continue

        existing_account = old_accounts.get(profile.get("accountId") or "")
        phone_key = normalize_phone(profile.get("phone") or (existing_account or {}).get("phone"))
        target = None

        if phone_key and phone_key in phone_index:
            target = rebuilt_accounts[phone_index[phone_key]]
        elif existing_account and existing_account.get("id") in rebuilt_accounts:
            target = rebuilt_accounts[existing_account["id"]]
        elif existing_account:
            target = build_account_seed(existing_account, phone_key)
            rebuilt_accounts[target["id"]] = target
        else:
            target = build_account_seed(None, phone_key)
            rebuilt_accounts[target["id"]] = target
            changed = True

        if phone_key:
            if target.get("phone") != phone_key:
                target["phone"] = phone_key
                changed = True
            phone_index[phone_key] = target["id"]
        before_identity = json.dumps(target.get("identityProviders", {}), ensure_ascii=False, sort_keys=True)
        ensure_account_identity_bindings(target)
        after_identity = json.dumps(target.get("identityProviders", {}), ensure_ascii=False, sort_keys=True)
        if before_identity != after_identity:
            changed = True

        if profile.get("accountId") != target["id"]:
            profile["accountId"] = target["id"]
            changed = True

        current_role_profile = state["profiles"].get(target["profilesByRole"].get(role, ""))
        preferred_profile = pick_preferred_profile(state, [current_role_profile, profile])
        preferred_profile_id = preferred_profile["id"] if preferred_profile else profile["id"]
        if target["profilesByRole"].get(role) != preferred_profile_id:
            target["profilesByRole"][role] = preferred_profile_id
            changed = True

    for account_id, account in old_accounts.items():
        if account_id in rebuilt_accounts:
            continue
        providers = account.get("identityProviders") or {}
        has_provider_identity = any(
            isinstance(provider, dict) and str(provider.get("identifier") or "").strip()
            for provider in providers.values()
        )
        if not has_provider_identity and not normalize_phone(account.get("phone")):
            continue
        preserved = build_account_seed(account, account.get("phone", ""))
        rebuilt_accounts[preserved["id"]] = preserved
        if preserved.get("phone"):
            phone_index[preserved["phone"]] = preserved["id"]

    if rebuilt_accounts != old_accounts:
        state["accounts"] = rebuilt_accounts
        changed = True

    for session in state.get("sessions", {}).values():
        session.setdefault("managedProfileIds", [])
        session.setdefault("managedAccountIds", [])
        session.setdefault("verifiedPhones", {})
        if normalize_session_profiles(state, session):
            changed = True

    return changed


def merge_string_lists(*values):
    merged = []
    for value in values:
        for item in value or []:
            text = str(item or "").strip()
            if text and text not in merged:
                merged.append(text)
    return merged


def merge_plan_lists(primary, secondary):
    merged = {}
    for item in secondary or []:
        if not isinstance(item, dict):
            continue
        key = f"{item.get('title','')}|{item.get('price','')}|{item.get('detail','')}"
        merged[key] = deepcopy(item)
    for item in primary or []:
        if not isinstance(item, dict):
            continue
        key = f"{item.get('title','')}|{item.get('price','')}|{item.get('detail','')}"
        merged[key] = deepcopy(item)
    return list(merged.values())


def merge_profile_records(primary_items, secondary_items):
    merged = {}
    for item in secondary_items or []:
        if isinstance(item, dict) and item.get("id"):
            merged[item["id"]] = deepcopy(item)
    for item in primary_items or []:
        if isinstance(item, dict) and item.get("id"):
            merged[item["id"]] = deepcopy(item)
    values = list(merged.values())
    values.sort(key=lambda item: item.get("createdAt", ""), reverse=True)
    return values


def merge_duplicate_profile_data(canonical, duplicate):
    for field in [
        "phone",
        "gender",
        "heightCm",
        "weightKg",
        "bodyFat",
        "restingHeartRate",
        "healthSource",
        "deviceSyncedAt",
        "city",
        "locationLabel",
        "bio",
        "shortDesc",
        "price",
        "hours",
        "contactName",
        "years",
        "coverImage",
        "avatarImage",
        "goal",
        "level",
        "lat",
        "lng",
    ]:
        if canonical.get(field) in (None, "", 0) and duplicate.get(field) not in (None, "", 0):
            canonical[field] = duplicate.get(field)

    canonical["listed"] = bool(canonical.get("listed", True) or duplicate.get("listed", True))
    canonical["createdAt"] = min(
        [item for item in [canonical.get("createdAt"), duplicate.get("createdAt")] if item],
        default=canonical.get("createdAt") or duplicate.get("createdAt") or iso_at(),
    )
    canonical["tags"] = merge_string_lists(canonical.get("tags"), duplicate.get("tags"))
    canonical["favoriteSports"] = merge_string_lists(canonical.get("favoriteSports"), duplicate.get("favoriteSports"))
    canonical["connectedDevices"] = merge_string_lists(canonical.get("connectedDevices"), duplicate.get("connectedDevices"))
    canonical["certifications"] = merge_string_lists(canonical.get("certifications"), duplicate.get("certifications"))
    canonical["externalWorkoutIds"] = merge_string_lists(canonical.get("externalWorkoutIds"), duplicate.get("externalWorkoutIds"))
    canonical["pricingPlans"] = merge_plan_lists(canonical.get("pricingPlans"), duplicate.get("pricingPlans"))
    canonical["reviews"] = merge_profile_records(canonical.get("reviews"), duplicate.get("reviews"))
    canonical["checkins"] = merge_profile_records(canonical.get("checkins"), duplicate.get("checkins"))
    canonical["healthHistory"] = merge_profile_records(canonical.get("healthHistory"), duplicate.get("healthHistory"))
    canonical["healthSnapshot"] = {
        **(duplicate.get("healthSnapshot") or {}),
        **(canonical.get("healthSnapshot") or {}),
    }


def replace_profile_references(state, source_profile_id, target_profile_id):
    if source_profile_id == target_profile_id:
        return
    register_profile_alias(state, source_profile_id, target_profile_id)

    for follow in state.get("follows", []):
        if follow.get("sourceProfileId") == source_profile_id:
            follow["sourceProfileId"] = target_profile_id
        if follow.get("targetProfileId") == source_profile_id:
            follow["targetProfileId"] = target_profile_id

    for booking in state.get("bookings", []):
        if booking.get("createdByProfileId") == source_profile_id:
            booking["createdByProfileId"] = target_profile_id
        if booking.get("targetProfileId") == source_profile_id:
            booking["targetProfileId"] = target_profile_id

    for favorite in state.get("postFavorites", []):
        if favorite.get("sourceProfileId") == source_profile_id:
            favorite["sourceProfileId"] = target_profile_id

    for post in state.get("posts", {}).values():
        if post.get("authorProfileId") == source_profile_id:
            post["authorProfileId"] = target_profile_id
        post["likes"] = [target_profile_id if item == source_profile_id else item for item in post.get("likes", [])]
        for comment in post.get("comments", []):
            if comment.get("authorProfileId") == source_profile_id:
                comment["authorProfileId"] = target_profile_id

    for profile in state.get("profiles", {}).values():
        for review in profile.get("reviews", []):
            if review.get("authorProfileId") == source_profile_id:
                review["authorProfileId"] = target_profile_id

    for thread in state.get("threads", []):
        thread["participants"] = [
            target_profile_id if item == source_profile_id else item
            for item in thread.get("participants", [])
        ]
        for message in thread.get("messages", []):
            if message.get("senderProfileId") == source_profile_id:
                message["senderProfileId"] = target_profile_id

    for session in state.get("sessions", {}).values():
        managed_ids = []
        for profile_id in session.get("managedProfileIds", []):
            remapped = target_profile_id if profile_id == source_profile_id else profile_id
            if remapped not in managed_ids:
                managed_ids.append(remapped)
        session["managedProfileIds"] = managed_ids
        if session.get("currentActorProfileId") == source_profile_id:
            session["currentActorProfileId"] = target_profile_id

    for account in ensure_account_registry(state).values():
        profiles_by_role = account.get("profilesByRole") or {}
        for role, profile_id in list(profiles_by_role.items()):
            if profile_id == source_profile_id:
                profiles_by_role[role] = target_profile_id


def normalize_follows(state):
    unique = []
    seen = set()
    for item in state.get("follows", []):
        source = item.get("sourceProfileId")
        target = item.get("targetProfileId")
        if not source or not target or source == target:
            continue
        pair = (source, target)
        if pair in seen:
            continue
        seen.add(pair)
        unique.append(item)
    state["follows"] = unique


def normalize_threads(state):
    merged_threads = {}
    for thread in state.get("threads", []):
        participants = []
        for item in thread.get("participants", []):
            if item and item not in participants:
                participants.append(item)
        if len(participants) < 2:
            continue
        participants = sorted(participants[:2])
        thread_id = get_thread_id(participants[0], participants[1])
        target = merged_threads.setdefault(
            thread_id,
            {"id": thread_id, "participants": participants, "messages": []},
        )
        existing_message_ids = {message.get("id") for message in target["messages"]}
        for message in thread.get("messages", []):
            if message.get("id") in existing_message_ids:
                continue
            target["messages"].append(message)
            existing_message_ids.add(message.get("id"))
        target["messages"].sort(key=lambda item: item.get("createdAt", ""))
    state["threads"] = list(merged_threads.values())


def normalize_post_favorites(state):
    unique = []
    seen = set()
    valid_profile_ids = set(state.get("profiles", {}).keys())
    valid_posts = state.get("posts", {})
    for item in state.get("postFavorites", []):
        source = item.get("sourceProfileId")
        post_id = item.get("postId")
        post = valid_posts.get(post_id)
        if source not in valid_profile_ids or not post:
            continue
        pair = (source, post_id)
        if pair in seen:
            continue
        seen.add(pair)
        unique.append(
            {
                "sourceProfileId": source,
                "postId": post_id,
                "createdAt": item.get("createdAt") or iso_at(),
            }
        )
    state["postFavorites"] = unique


def deduplicate_profiles_by_phone_role(state):
    profiles_by_key = {}
    changed = False

    for profile in list(state.get("profiles", {}).values()):
        role = str(profile.get("role") or "").strip()
        phone = normalize_phone(profile.get("phone"))
        if role not in {"enthusiast", "gym", "coach"} or not phone:
            continue
        profiles_by_key.setdefault((phone, role), []).append(profile)

    for (_phone, _role), profiles in profiles_by_key.items():
        if len(profiles) < 2:
            continue
        canonical = pick_preferred_profile(state, profiles)
        duplicates = [profile for profile in profiles if profile.get("id") != canonical.get("id")]
        if not duplicates:
            continue

        for duplicate in duplicates:
            merge_duplicate_profile_data(canonical, duplicate)
            replace_profile_references(state, duplicate["id"], canonical["id"])
            state["profiles"].pop(duplicate["id"], None)
            changed = True

    if changed:
        normalize_follows(state)
        normalize_threads(state)

    return changed


def deduplicate_profiles_by_account_role(state):
    profiles_by_key = {}
    changed = False

    for profile in list(state.get("profiles", {}).values()):
        role = str(profile.get("role") or "").strip()
        account_id = str(profile.get("accountId") or "").strip()
        if role not in {"enthusiast", "gym", "coach"} or not account_id:
            continue
        profiles_by_key.setdefault((account_id, role), []).append(profile)

    for (_account_id, _role), profiles in profiles_by_key.items():
        if len(profiles) < 2:
            continue
        canonical = pick_preferred_profile(state, profiles)
        duplicates = [profile for profile in profiles if profile.get("id") != canonical.get("id")]
        if not duplicates:
            continue

        for duplicate in duplicates:
            merge_duplicate_profile_data(canonical, duplicate)
            replace_profile_references(state, duplicate["id"], canonical["id"])
            state["profiles"].pop(duplicate["id"], None)
            changed = True

    if changed:
        normalize_follows(state)
        normalize_threads(state)

    return changed


def attach_account_to_session(state, session, account, preferred_role=""):
    account_id = str(account.get("id") or "").strip()
    if account_id and account_id not in session["managedAccountIds"]:
        session["managedAccountIds"].append(account_id)
    phone_key = normalize_phone(account.get("phone"))
    if phone_key:
        session["lastVerifiedPhone"] = phone_key
    role_profiles = account.setdefault("profilesByRole", {})
    for role in {"enthusiast", "gym", "coach"}:
        canonical = pick_preferred_profile(
            state,
            [
                state.get("profiles", {}).get(resolve_canonical_profile_id(state, role_profiles.get(role, ""))),
                *find_profiles_by_account_role(state, account.get("id"), role),
            ],
        )
        if canonical:
            role_profiles[role] = canonical["id"]
        else:
            role_profiles.pop(role, None)

    for profile_id in role_profiles.values():
        if profile_id in state.get("profiles", {}) and profile_id not in session["managedProfileIds"]:
            session["managedProfileIds"].append(profile_id)

    desired_role = preferred_role if preferred_role in role_profiles else next(iter(role_profiles.keys()), "")
    desired_profile_id = role_profiles.get(desired_role)
    if not desired_profile_id:
        desired_profile_id = next(iter(role_profiles.values()), None)
        if desired_profile_id:
            desired_profile = state["profiles"].get(desired_profile_id)
            desired_role = desired_profile["role"] if desired_profile else desired_role

    if desired_role:
        session["selectedRole"] = desired_role
    if desired_profile_id:
        session["currentActorProfileId"] = desired_profile_id
    normalize_session_profiles(state, session)


def serialize_managed_accounts(state, session):
    items = []
    seen = set()

    account_ids = []
    for account_id in session.get("managedAccountIds", []):
        account_key = str(account_id or "").strip()
        if account_key and account_key not in account_ids:
            account_ids.append(account_key)
    for profile_id in session.get("managedProfileIds", []):
        profile = state.get("profiles", {}).get(profile_id)
        account_id = str((profile or {}).get("accountId") or "").strip()
        if account_id and account_id not in account_ids:
            account_ids.append(account_id)

    for account_id in account_ids:
        account = ensure_account_registry(state).get(account_id)
        if not account:
            continue
        if account["id"] in seen:
            continue
        seen.add(account["id"])
        providers = ensure_account_identity_bindings(account)
        serialized_providers = []
        for provider_type, provider in sorted(providers.items()):
            if not isinstance(provider, dict):
                continue
            serialized_providers.append(
                {
                    "type": provider_type,
                    "maskedIdentifier": provider.get("maskedIdentifier", ""),
                    "verified": bool(provider.get("verified")),
                    "boundAt": provider.get("boundAt", ""),
                    "verifiedAt": provider.get("verifiedAt", ""),
                }
            )
        items.append(
            {
                "id": account["id"],
                "restoreToken": account["restoreToken"],
                "phone": account.get("phone", ""),
                "phoneMasked": mask_phone(account.get("phone", "")),
                "roles": sorted(account.get("profilesByRole", {}).keys()),
                "primaryProvider": account.get("primaryProvider", ""),
                "identityProviders": serialized_providers,
                "pendingProviderBindings": [
                    provider_type
                    for provider_type in ["wechat", "apple"]
                    if provider_type not in providers
                ],
                "authVersion": max(1, int(account.get("authVersion") or 1)),
            }
        )

    return items


def cleanup_formal_test_state(state):
    changed = False

    for profile_id in LEGACY_DEMO_ENTHUSIAST_IDS:
        profile = state.get("profiles", {}).get(profile_id)
        if profile and profile.get("listed", True):
            profile["listed"] = False
            changed = True

    stale_post_ids = [
        post_id
        for post_id, post in state.get("posts", {}).items()
        if post.get("authorProfileId") in LEGACY_DEMO_ENTHUSIAST_IDS
    ]
    for post_id in stale_post_ids:
        del state["posts"][post_id]
        changed = True

    filtered_follows = [
        item
        for item in state.get("follows", [])
        if item.get("sourceProfileId") not in LEGACY_DEMO_ENTHUSIAST_IDS
        and item.get("targetProfileId") not in LEGACY_DEMO_ENTHUSIAST_IDS
    ]
    if len(filtered_follows) != len(state.get("follows", [])):
        state["follows"] = filtered_follows
        changed = True

    filtered_bookings = [
        item for item in state.get("bookings", []) if item.get("createdByProfileId") not in LEGACY_DEMO_ENTHUSIAST_IDS
    ]
    if len(filtered_bookings) != len(state.get("bookings", [])):
        state["bookings"] = filtered_bookings
        changed = True

    filtered_threads = [
        item
        for item in state.get("threads", [])
        if not any(participant in LEGACY_DEMO_ENTHUSIAST_IDS for participant in item.get("participants", []))
    ]
    if len(filtered_threads) != len(state.get("threads", [])):
        state["threads"] = filtered_threads
        changed = True

    for post in state.get("posts", {}).values():
        likes = [item for item in post.get("likes", []) if item not in LEGACY_DEMO_ENTHUSIAST_IDS]
        comments = [item for item in post.get("comments", []) if item.get("authorProfileId") not in LEGACY_DEMO_ENTHUSIAST_IDS]
        if likes != post.get("likes", []):
            post["likes"] = likes
            changed = True
        if comments != post.get("comments", []):
            post["comments"] = comments
            changed = True

    for profile in state.get("profiles", {}).values():
        reviews = [item for item in profile.get("reviews", []) if item.get("authorProfileId") not in LEGACY_DEMO_ENTHUSIAST_IDS]
        if reviews != profile.get("reviews", []):
            profile["reviews"] = reviews
            changed = True

    for session in state.get("sessions", {}).values():
        managed_ids = [item for item in session.get("managedProfileIds", []) if item not in LEGACY_DEMO_ENTHUSIAST_IDS]
        if managed_ids != session.get("managedProfileIds", []):
            session["managedProfileIds"] = managed_ids
            changed = True
        if session.get("currentActorProfileId") in LEGACY_DEMO_ENTHUSIAST_IDS:
            session["currentActorProfileId"] = managed_ids[0] if managed_ids else None
            changed = True

    return changed


def merge_demo_state(state):
    seed = initial_state()
    demo_profile_ids = set(seed["profiles"].keys())
    changed = cleanup_formal_test_state(state)

    for profile_id, seed_profile in seed["profiles"].items():
        existing = state["profiles"].get(profile_id)
        if not existing:
            state["profiles"][profile_id] = deepcopy(seed_profile)
            changed = True
            continue

        merged_profile = {**existing, **deepcopy(seed_profile)}
        merged_profile["owner_session_id"] = existing.get("owner_session_id")
        merged_profile["createdAt"] = existing.get("createdAt", seed_profile.get("createdAt"))
        merged_profile["reviews"] = merge_records_by_id(seed_profile.get("reviews", []), existing.get("reviews", []))

        if merged_profile != existing:
            state["profiles"][profile_id] = merged_profile
            changed = True

    for post_id, seed_post in seed["posts"].items():
        existing = state["posts"].get(post_id)
        if not existing:
            state["posts"][post_id] = deepcopy(seed_post)
            changed = True
            continue

        merged_post = {**existing, **deepcopy(seed_post)}
        merged_post["likes"] = sorted(set((existing.get("likes") or []) + (seed_post.get("likes") or [])))
        merged_post["comments"] = merge_records_by_id(seed_post.get("comments", []), existing.get("comments", []))

        if merged_post != existing:
            state["posts"][post_id] = merged_post
            changed = True

    existing_follow_pairs = {
        (item["sourceProfileId"], item["targetProfileId"])
        for item in state.get("follows", [])
    }
    for follow in seed.get("follows", []):
        pair = (follow["sourceProfileId"], follow["targetProfileId"])
        if pair not in existing_follow_pairs:
            state.setdefault("follows", []).append(deepcopy(follow))
            existing_follow_pairs.add(pair)
            changed = True

    existing_booking_ids = {item["id"] for item in state.get("bookings", [])}
    for booking in seed.get("bookings", []):
        if booking["id"] not in existing_booking_ids:
            state.setdefault("bookings", []).append(deepcopy(booking))
            existing_booking_ids.add(booking["id"])
            changed = True

    existing_thread_ids = {item["id"] for item in state.get("threads", [])}
    for thread in seed.get("threads", []):
        if thread["id"] not in existing_thread_ids:
            state.setdefault("threads", []).append(deepcopy(thread))
            existing_thread_ids.add(thread["id"])
            changed = True

    stale_demo_posts = [
        post_id
        for post_id, post in state.get("posts", {}).items()
        if post.get("authorProfileId") in demo_profile_ids and post_id not in seed["posts"]
    ]
    for post_id in stale_demo_posts:
        del state["posts"][post_id]
        changed = True

    if cleanup_formal_test_state(state):
        changed = True

    return changed


def make_post(post_id, author_profile_id, minutes_ago, content, meta, media=None, likes=None, comments=None, checkin=None):
    return {
        "id": post_id,
        "authorProfileId": author_profile_id,
        "createdAt": iso_at(minutes_ago),
        "content": content,
        "meta": meta,
        "media": media or [],
        "likes": likes or [],
        "comments": comments or [],
        "checkin": checkin,
    }


def initial_state():
    profiles = {
        "enthusiast-demo-a": make_profile(
            id="enthusiast-demo-a",
            role="enthusiast",
            name="模拟用户 A",
            handle="@demo.user.a",
            avatar="A",
            avatarImage=portrait_avatar(skin="#f6d1b5", hair="#6b4736", shirt="#f28c28", bg_a="#f6dfc7", bg_b="#d6a174"),
            city="厦门",
            locationLabel="厦门 · 思明区",
            lat=24.4812,
            lng=118.0911,
            bio="模拟测试用户，主要用于测试关注、预约、评分、点赞、评论和动态发布。",
            shortDesc="规律训练 10 个月，方便测试健身圈互动。",
            tags=["模拟用户", "减脂", "打卡"],
            level="规律训练",
            goal="减脂 5kg，维持一周四练",
        ),
        "enthusiast-demo-b": make_profile(
            id="enthusiast-demo-b",
            role="enthusiast",
            name="模拟用户 B",
            handle="@demo.user.b",
            avatar="B",
            avatarImage=portrait_avatar(skin="#f1c7ad", hair="#50372b", shirt="#4f7ea1", bg_a="#f0d8c5", bg_b="#d2a183"),
            city="厦门",
            locationLabel="厦门 · 湖里区",
            lat=24.5008,
            lng=118.1172,
            bio="模拟测试用户，主要用来测试课程预约、评价、关注和评论功能。",
            shortDesc="训练新手，主要测试预约、评分和定位模块。",
            tags=["模拟用户", "新手入门", "塑形"],
            level="新手入门",
            goal="每周三练，改善体态",
        ),
        "gym-demo-a": make_profile(
            id="gym-demo-a",
            role="gym",
            name="模拟健身房 A",
            handle="@demo.gym.a",
            avatar="馆",
            avatarImage=gym_avatar(bg_a="#1f2a34", bg_b="#748ca2", accent="#f28c28"),
            city="厦门",
            locationLabel="厦门 · 思明区",
            lat=24.4828,
            lng=118.0958,
            bio="模拟健身房 A 用于测试场馆主页、定价、定位、预约、私信和评分链路。",
            shortDesc="24h 营业，团课丰富，适合测试预约功能。",
            price="¥119/月起",
            tags=["模拟场馆", "24h", "团课"],
            hours="24h 营业",
            contactName="测试店长 A",
            phone="13800000001",
            pricingPlans=[
                {"title": "月卡", "detail": "不限次进店", "price": "¥119/月"},
                {"title": "次卡", "detail": "10 次内 60 天有效", "price": "¥199/10次"},
                {"title": "团课包", "detail": "燃脂 / 力量 / 单车", "price": "¥299/12节"},
            ],
            reviews=[
                {"id": "review-gym-a-1", "authorProfileId": "enthusiast-demo-a", "score": 5, "text": "器械很新，晚间也不拥挤，适合测试预约。", "createdAt": iso_at(2 * 24 * 60)},
                {"id": "review-gym-a-2", "authorProfileId": "coach-demo-a", "score": 4, "text": "团课教室空间不错，动线清晰。", "createdAt": iso_at(5 * 24 * 60)},
            ],
        ),
        "gym-demo-b": make_profile(
            id="gym-demo-b",
            role="gym",
            name="模拟健身房 B",
            handle="@demo.gym.b",
            avatar="泳",
            avatarImage=gym_avatar(bg_a="#214d64", bg_b="#76aeca", accent="#59d4ff"),
            city="厦门",
            locationLabel="厦门 · 湖里区",
            lat=24.5064,
            lng=118.1268,
            bio="模拟健身房 B 用于测试泳池馆场景、价格展示和恢复课程预约。",
            shortDesc="恒温泳池，适合测试恢复训练和课程包。",
            price="¥138/月起",
            tags=["模拟场馆", "泳池", "康复"],
            hours="06:00 - 23:00",
            contactName="测试店长 B",
            phone="13800000002",
            pricingPlans=[
                {"title": "游泳月卡", "detail": "泳池 + 更衣淋浴", "price": "¥138/月"},
                {"title": "家庭卡", "detail": "2 大 1 小共享", "price": "¥368/月"},
                {"title": "康复课程包", "detail": "恢复训练 8 节", "price": "¥699/8节"},
            ],
            reviews=[
                {"id": "review-gym-b-1", "authorProfileId": "enthusiast-demo-b", "score": 5, "text": "泳池环境很干净，适合测试家庭卡展示。", "createdAt": iso_at(24 * 60)},
            ],
        ),
        "coach-demo-a": make_profile(
            id="coach-demo-a",
            role="coach",
            name="模拟教练 A",
            handle="@demo.coach.a",
            avatar="林",
            avatarImage=portrait_avatar(skin="#efc3a4", hair="#281d17", shirt="#17181d", bg_a="#d9e0ea", bg_b="#8b98ad"),
            city="厦门",
            locationLabel="厦门 · 思明区",
            lat=24.4805,
            lng=118.0874,
            bio="模拟教练 A 主要用于测试私教定价、档期、评价、评论和主页动态。",
            shortDesc="塑形增肌、燃脂减脂，适合测试私教预约。",
            price="¥260/小时",
            tags=["模拟教练", "减脂塑形", "力量提升"],
            years="6",
            certifications=["NASM", "ACE", "CBBA"],
            pricingPlans=[
                {"title": "私教 1v1", "detail": "动作纠正 + 饮食建议", "price": "¥260/小时"},
                {"title": "12 节课包", "detail": "适合减脂塑形周期", "price": "¥2880/12节"},
                {"title": "双人训练", "detail": "两人拼课", "price": "¥380/小时"},
            ],
            reviews=[
                {"id": "review-coach-a-1", "authorProfileId": "enthusiast-demo-a", "score": 5, "text": "动作纠正特别细，方便测试评分模块。", "createdAt": iso_at(3 * 24 * 60)},
                {"id": "review-coach-a-2", "authorProfileId": "enthusiast-demo-b", "score": 5, "text": "沟通清楚，课表安排很灵活。", "createdAt": iso_at(4 * 24 * 60)},
            ],
        ),
        "coach-demo-b": make_profile(
            id="coach-demo-b",
            role="coach",
            name="模拟教练 B",
            handle="@demo.coach.b",
            avatar="M",
            avatarImage=portrait_avatar(skin="#eab99b", hair="#2a1f19", shirt="#26394e", bg_a="#cfe3ea", bg_b="#7da6bb"),
            city="厦门",
            locationLabel="厦门 · 湖里区",
            lat=24.5042,
            lng=118.1217,
            bio="模拟教练 B 主要用于测试康复训练、双人训练和消息沟通。",
            shortDesc="康复训练、体态调整，适合测试一对一咨询。",
            price="¥220/小时",
            tags=["模拟教练", "康复训练", "体态"],
            years="4",
            certifications=["ACE", "FMS"],
            pricingPlans=[
                {"title": "康复 1v1", "detail": "评估 + 动作重建", "price": "¥220/小时"},
                {"title": "体态调整包", "detail": "8 节调整课程", "price": "¥1680/8节"},
                {"title": "双人恢复课", "detail": "两人共同训练", "price": "¥320/小时"},
            ],
            reviews=[
                {"id": "review-coach-b-1", "authorProfileId": "enthusiast-demo-b", "score": 4, "text": "对体态问题讲得很细。", "createdAt": iso_at(2 * 24 * 60)},
            ],
        ),
    }

    profiles["gym-demo-a"].update(
        {
            "name": "模拟健身房 A · 万象燃炼馆",
            "avatar": "万",
            "avatarImage": demo_asset("gym-a-avatar.jpg"),
            "coverImage": demo_asset("gym-a.jpg"),
            "bio": "模拟门店，位于厦门万象城商圈，用于测试真实场馆照片、定价、预约、评分和主页展示。",
            "shortDesc": "万象城商圈器械馆，支持月卡、次卡和团课测试。",
            "price": "¥169/月起",
            "tags": ["模拟场馆", "力量区", "团课"],
            "hours": "06:00 - 24:00",
            "contactName": "测试店长 林楠",
            "pricingPlans": [
                {"title": "月卡", "detail": "器械区 + 更衣淋浴", "price": "¥169/月"},
                {"title": "次卡", "detail": "12 次 90 天有效", "price": "¥299/12次"},
                {"title": "团课卡", "detail": "搏击 / 单车 / HIIT", "price": "¥399/16节"},
            ],
        }
    )
    profiles["gym-demo-b"].update(
        {
            "name": "模拟健身房 B · 轻氧塑能馆",
            "avatar": "氧",
            "avatarImage": demo_asset("gym-b-avatar.jpg"),
            "coverImage": demo_asset("gym-b.jpg"),
            "bio": "模拟精品训练馆，主打轻氧有氧和恢复类课程，适合测试价格展示和课程预约。",
            "shortDesc": "精品有氧空间，适合恢复训练和轻团课测试。",
            "tags": ["模拟场馆", "精品馆", "恢复"],
            "contactName": "测试店长 苏越",
            "pricingPlans": [
                {"title": "轻氧月卡", "detail": "跑步机 + 骑行区", "price": "¥138/月"},
                {"title": "午间卡", "detail": "工作日 11:00-16:00", "price": "¥99/月"},
                {"title": "恢复课包", "detail": "拉伸恢复 8 节", "price": "¥699/8节"},
            ],
        }
    )
    profiles["coach-demo-a"].update(
        {
            "name": "模拟教练 A · 林燃",
            "avatarImage": demo_asset("coach-a-avatar.jpg"),
            "coverImage": demo_asset("coach-a.jpg"),
            "bio": "模拟私教，擅长力量提升和减脂塑形，用于测试真实头像、课时定价、预约和私信。",
            "shortDesc": "力量提升、减脂塑形，适合测试私教预约。",
            "price": "¥299/小时",
            "tags": ["模拟教练", "力量提升", "减脂塑形"],
            "years": "8",
            "pricingPlans": [
                {"title": "私教 1v1", "detail": "动作纠正 + 饮食建议", "price": "¥299/小时"},
                {"title": "12 节进阶包", "detail": "适合 6 周增肌减脂周期", "price": "¥3180/12节"},
                {"title": "双人训练", "detail": "两人拼课", "price": "¥420/小时"},
            ],
        }
    )
    profiles["coach-demo-b"].update(
        {
            "name": "模拟教练 B · 周芮",
            "avatarImage": demo_asset("coach-b-avatar.jpg"),
            "coverImage": demo_asset("coach-b.jpg"),
            "bio": "模拟女教练，主打体态改善和普拉提恢复，方便测试女性教练主页、评分和动态流。",
            "shortDesc": "体态改善、核心激活，适合恢复和普拉提测试。",
            "price": "¥268/小时",
            "tags": ["模拟教练", "普拉提", "体态改善"],
            "years": "5",
            "pricingPlans": [
                {"title": "普拉提 1v1", "detail": "核心激活 + 体态改善", "price": "¥268/小时"},
                {"title": "恢复课包", "detail": "8 节核心恢复课程", "price": "¥1880/8节"},
                {"title": "双人塑形课", "detail": "适合闺蜜或情侣", "price": "¥360/小时"},
            ],
        }
    )
    profiles["gym-demo-c"] = make_profile(
        id="gym-demo-c",
        role="gym",
        name="模拟健身房 C · Skyline Strength",
        handle="@demo.gym.c",
        avatar="天",
        avatarImage=demo_asset("gym-c-avatar.jpg"),
        coverImage=demo_asset("gym-c.jpg"),
        city="厦门",
        locationLabel="厦门 · 思明区 · 环岛路",
        lat=24.4576,
        lng=118.1103,
        bio="模拟高景观力量馆，方便测试真实场馆图、主页头图、预约链路和价格展示。",
        shortDesc="海景力量训练馆，适合展示精品月卡和私教区。",
        price="¥199/月起",
        tags=["模拟场馆", "景观馆", "力量"],
        hours="06:30 - 23:30",
        contactName="测试店长 韩玥",
        phone="13800000003",
        pricingPlans=[
            {"title": "精品月卡", "detail": "含自由训练区", "price": "¥199/月"},
            {"title": "季卡", "detail": "90 天畅练", "price": "¥499/季"},
            {"title": "私教区使用包", "detail": "适合预约私教", "price": "¥159/次"},
        ],
        reviews=[
            {"id": "review-gym-c-1", "authorProfileId": "enthusiast-demo-a", "score": 5, "text": "视野很好，适合拿来展示精品馆体验。", "createdAt": iso_at(24 * 60)},
        ],
    )
    profiles["gym-demo-d"] = make_profile(
        id="gym-demo-d",
        role="gym",
        name="模拟健身房 D · 城市力量馆",
        handle="@demo.gym.d",
        avatar="城",
        avatarImage=demo_asset("gym-d-avatar.jpg"),
        coverImage=demo_asset("gym-d.jpg"),
        city="厦门",
        locationLabel="厦门 · 湖里区 · SM 商圈",
        lat=24.5088,
        lng=118.1295,
        bio="模拟综合器械馆，器械和自由重量区完整，适合测试主页定价、预约和评分模块。",
        shortDesc="器械区完整，适合测试多种会员卡方案。",
        price="¥149/月起",
        tags=["模拟场馆", "器械区", "自由重量"],
        hours="24h 营业",
        contactName="测试店长 程序",
        phone="13800000004",
        pricingPlans=[
            {"title": "月卡", "detail": "24h 进店训练", "price": "¥149/月"},
            {"title": "力量卡", "detail": "自由重量区优先", "price": "¥239/月"},
            {"title": "新人体验卡", "detail": "7 天不限次", "price": "¥59/周"},
        ],
        reviews=[
            {"id": "review-gym-d-1", "authorProfileId": "enthusiast-demo-b", "score": 4, "text": "器械全，适合演示会员定价和主页。", "createdAt": iso_at(2 * 24 * 60)},
        ],
    )
    profiles["coach-demo-c"] = make_profile(
        id="coach-demo-c",
        role="coach",
        name="模拟教练 C · 陈拓",
        handle="@demo.coach.c",
        avatar="陈",
        avatarImage=demo_asset("coach-c-avatar.jpg"),
        coverImage=demo_asset("coach-c.jpg"),
        city="厦门",
        locationLabel="厦门 · 湖里区 · 五缘湾",
        lat=24.5223,
        lng=118.1563,
        bio="模拟男教练，用于测试增肌、力量和大课包的价格展示与预约互动。",
        shortDesc="增肌力量、训练计划制定，适合进阶课包测试。",
        price="¥328/小时",
        tags=["模拟教练", "增肌", "力量训练"],
        years="7",
        certifications=["NSCA", "CBBA"],
        pricingPlans=[
            {"title": "进阶私教", "detail": "增肌 + 力量计划", "price": "¥328/小时"},
            {"title": "16 节课包", "detail": "适合系统周期训练", "price": "¥4380/16节"},
            {"title": "训练营小班", "detail": "4 人内小班训练", "price": "¥129/人/节"},
        ],
        reviews=[
            {"id": "review-coach-c-1", "authorProfileId": "enthusiast-demo-a", "score": 5, "text": "训练计划很清晰，适合演示教练主页。", "createdAt": iso_at(3 * 24 * 60)},
        ],
    )
    profiles["coach-demo-d"] = make_profile(
        id="coach-demo-d",
        role="coach",
        name="模拟教练 D · Mia 沈",
        handle="@demo.coach.d",
        avatar="M",
        avatarImage=demo_asset("coach-d-avatar.jpg"),
        coverImage=demo_asset("coach-d.jpg"),
        city="厦门",
        locationLabel="厦门 · 思明区 · 明发商业广场",
        lat=24.4714,
        lng=118.1041,
        bio="模拟女教练，主打女性塑形和功能性训练，方便测试头像、价格和私信功能。",
        shortDesc="女性塑形、功能训练，适合晚间档期预约测试。",
        price="¥248/小时",
        tags=["模拟教练", "女性塑形", "功能训练"],
        years="4",
        certifications=["ACE", "FMS"],
        pricingPlans=[
            {"title": "塑形 1v1", "detail": "女性塑形 + 体态调整", "price": "¥248/小时"},
            {"title": "夜间课包", "detail": "下班后专属时段", "price": "¥2580/12节"},
            {"title": "双人塑形课", "detail": "适合好友一起练", "price": "¥340/小时"},
        ],
        reviews=[
            {"id": "review-coach-d-1", "authorProfileId": "enthusiast-demo-b", "score": 5, "text": "沟通很舒服，适合测试女教练主页体验。", "createdAt": iso_at(24 * 60)},
        ],
    )

    posts = {
        "post-user-a-1": make_post(
            "post-user-a-1",
            "enthusiast-demo-a",
            120,
            "模拟用户 A 今天完成胸背训练，方便测试动态流、点赞、评论和时间排序。",
            "模拟动态 · 完成 720 kcal",
            media=[{"type": "image", "url": demo_image("胸背训练", "#f4a24a", "#df6d22"), "name": "demo-workout-a.jpg"}],
            likes=["enthusiast-demo-b", "coach-demo-a"],
            comments=[
                {"id": "comment-a-1", "authorProfileId": "coach-demo-a", "text": "动作做得很稳，明天可以加一点背部收缩练习。", "createdAt": iso_at(90)},
                {"id": "comment-a-2", "authorProfileId": "enthusiast-demo-b", "text": "被你带动了，今晚我也去练。", "createdAt": iso_at(70)},
            ],
        ),
        "post-user-a-2": make_post("post-user-a-2", "enthusiast-demo-a", 24 * 60, "训练后加了 20 分钟有氧和肩颈拉伸。", "模拟动态 · 恢复训练"),
        "post-user-b-1": make_post("post-user-b-1", "enthusiast-demo-b", 180, "模拟用户 B 刚预约了晚间团课，主要测试预约和订单展示流程。", "模拟动态 · 预约记录", likes=["coach-demo-b"]),
        "post-user-b-2": make_post("post-user-b-2", "enthusiast-demo-b", 2 * 24 * 60, "第一次打卡力量区，准备长期记录训练变化。", "模拟动态 · 训练日记"),
        "post-gym-a-1": make_post("post-gym-a-1", "gym-demo-a", 60, "今晚 19:30 燃脂单车还剩 8 个名额。", "课程提醒", likes=["enthusiast-demo-a"]),
        "post-gym-a-2": make_post(
            "post-gym-a-2",
            "gym-demo-a",
            30,
            "模拟健身房 A 新到一批力量器械，方便测试场馆动态展示。",
            "模拟动态 · 设备更新",
            media=[
                {"type": "image", "url": demo_asset("gym-a.jpg"), "name": "demo-gym-a-1.jpg"},
                {"type": "image", "url": demo_asset("gym-d.jpg"), "name": "demo-gym-a-2.jpg"},
            ],
            likes=["enthusiast-demo-a", "enthusiast-demo-b"],
        ),
        "post-gym-b-1": make_post(
            "post-gym-b-1",
            "gym-demo-b",
            185,
            "模拟健身房 B 的周末亲子游泳课已开放预约。",
            "模拟动态 · 课程更新",
            media=[{"type": "image", "url": demo_asset("gym-b.jpg"), "name": "demo-gym-b.jpg"}],
        ),
        "post-gym-c-1": make_post(
            "post-gym-c-1",
            "gym-demo-c",
            75,
            "海景跑步区今晚延长到 23:30，适合测试夜间训练场景。",
            "模拟动态 · 夜场开放",
            media=[{"type": "image", "url": demo_asset("gym-c.jpg"), "name": "demo-gym-c.jpg"}],
            likes=["enthusiast-demo-a"],
        ),
        "post-gym-d-1": make_post(
            "post-gym-d-1",
            "gym-demo-d",
            160,
            "自由重量区新调了灯光和动线，方便测试真实门店展示效果。",
            "模拟动态 · 场馆升级",
            media=[{"type": "image", "url": demo_asset("gym-d.jpg"), "name": "demo-gym-d.jpg"}],
        ),
        "post-coach-a-1": make_post("post-coach-a-1", "coach-demo-a", 30, "模拟教练 A 今晚开放两个私教档期，方便测试即时预约。", "模拟动态 · 即时空闲", likes=["enthusiast-demo-a"]),
        "post-coach-a-2": make_post(
            "post-coach-a-2",
            "coach-demo-a",
            24 * 60,
            "整理了一份模拟学员常见动作错误清单。",
            "模拟动态 · 训练干货",
            media=[{"type": "image", "url": demo_asset("coach-a.jpg"), "name": "demo-coach-a.jpg"}],
            comments=[{"id": "comment-coach-a-1", "authorProfileId": "enthusiast-demo-a", "text": "这个清单很实用，已收藏。", "createdAt": iso_at(20 * 60)}],
        ),
        "post-coach-b-1": make_post(
            "post-coach-b-1",
            "coach-demo-b",
            6 * 60,
            "今天新增了两个康复评估时段，可以直接预约。",
            "模拟动态 · 档期开放",
            media=[{"type": "image", "url": demo_asset("coach-b.jpg"), "name": "demo-coach-b.jpg"}],
        ),
        "post-coach-c-1": make_post(
            "post-coach-c-1",
            "coach-demo-c",
            45,
            "本周新开了一组 4 人力量训练营，方便测试多种定价模式。",
            "模拟动态 · 训练营上新",
            media=[{"type": "image", "url": demo_asset("coach-c.jpg"), "name": "demo-coach-c.jpg"}],
            likes=["enthusiast-demo-a"],
        ),
        "post-coach-d-1": make_post(
            "post-coach-d-1",
            "coach-demo-d",
            120,
            "新增了 20:30 的晚间塑形档期，方便测试即时预约和私信咨询。",
            "模拟动态 · 晚间时段",
            media=[{"type": "image", "url": demo_asset("coach-d.jpg"), "name": "demo-coach-d.jpg"}],
        ),
    }

    follows = [
        {"sourceProfileId": "enthusiast-demo-a", "targetProfileId": "coach-demo-a", "createdAt": iso_at(3 * 24 * 60)},
        {"sourceProfileId": "enthusiast-demo-a", "targetProfileId": "gym-demo-a", "createdAt": iso_at(3 * 24 * 60)},
        {"sourceProfileId": "enthusiast-demo-b", "targetProfileId": "coach-demo-b", "createdAt": iso_at(2 * 24 * 60)},
        {"sourceProfileId": "enthusiast-demo-b", "targetProfileId": "gym-demo-b", "createdAt": iso_at(2 * 24 * 60)},
    ]

    bookings = [
        {
            "id": "booking-1",
            "createdAt": iso_at(60),
            "createdByProfileId": "enthusiast-demo-a",
            "targetProfileId": "coach-demo-a",
            "title": "模拟教练 A · 私教 1v1 体验课",
            "place": "厦门 · 思明区 · FitHub 私教区",
            "time": "今天 19:30",
            "status": "已预约",
            "action": "查看主页",
            "price": "¥260/小时",
        },
        {
            "id": "booking-2",
            "createdAt": iso_at(24 * 60),
            "createdByProfileId": "enthusiast-demo-b",
            "targetProfileId": "gym-demo-b",
            "title": "模拟健身房 B · 康复课程包",
            "place": "厦门 · 湖里区 · 泳池馆",
            "time": "周六 10:00",
            "status": "待确认",
            "action": "查看主页",
            "price": "¥699/8节",
        },
    ]

    threads = [
        {
            "id": "thread-demo-1",
            "participants": ["enthusiast-demo-a", "coach-demo-a"],
            "messages": [
                {"id": "msg-demo-1", "senderProfileId": "enthusiast-demo-a", "text": "教练你好，我想约明晚的私教 1v1。", "createdAt": iso_at(90)},
                {"id": "msg-demo-2", "senderProfileId": "coach-demo-a", "text": "可以，明晚 19:30 还有档期。", "createdAt": iso_at(75)},
            ],
        }
    ]

    return {
        "profiles": profiles,
        "posts": posts,
        "follows": follows,
        "blocks": [],
        "profileAliases": {},
        "postFavorites": [],
        "bookings": bookings,
        "threads": threads,
        "otpCodes": {},
        "accounts": {},
        "sessions": {},
        "reports": [],
        "moderationQueue": [],
        "adminActions": [],
    }


def ensure_data_file():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not STATE_FILE.exists():
        STATE_FILE.write_text(json.dumps(initial_state(), ensure_ascii=False, indent=2), encoding="utf-8")


def load_state():
    if supabase_storage_enabled():
        try:
            state = load_state_from_supabase()
            if state is None:
                storage_log("Supabase state row missing, initializing a fresh remote state.")
                state = load_state_from_local(create_if_missing=False) or initial_state()
                set_runtime_storage_state("supabase-empty", True, state)
                save_state_to_supabase(state)
            else:
                set_runtime_storage_state("supabase", True, state)
            changed = bool(STATE_RUNTIME_META.pop("remote_repair_required", False))
            changed = merge_phone_recovery_rows_from_supabase(state) or changed
            changed = merge_demo_state(state) or changed
            if reconcile_account_registry(state):
                changed = True
            if changed:
                save_state_to_supabase(state)
            return sanitize_state(state)
        except Exception as exc:
            storage_log(f"Supabase load failed, fallback to local file: {exc}")
            state = load_state_from_local(create_if_missing=False) or initial_state()
            set_runtime_storage_state("local-fallback", False)
            changed = merge_demo_state(state)
            if reconcile_account_registry(state):
                changed = True
            return sanitize_state(state)

    state = load_state_from_local(create_if_missing=True)
    set_runtime_storage_state("local-file", True, state)
    changed = merge_demo_state(state)
    if reconcile_account_registry(state):
        changed = True
    if changed:
        save_state(state)
    return sanitize_state(state)


def save_state(state):
    if supabase_storage_enabled():
        if not STATE_RUNTIME_META.get("supabase_writable", True):
            storage_log("Supabase writes skipped because the current state was loaded from local fallback after a remote read failure.")
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            with STATE_FILE.open("w", encoding="utf-8") as handle:
                json.dump(state, handle, ensure_ascii=False, indent=2)
            return

        current_metrics = state_integrity_metrics(state)

        if STATE_RUNTIME_META.get("last_known_remote_real_profiles", 0) > 0 and current_metrics["real_profiles"] == 0:
            storage_log("Refusing to overwrite Supabase with demo-only state because the last known remote state contained registered users.")
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            with STATE_FILE.open("w", encoding="utf-8") as handle:
                json.dump(state, handle, ensure_ascii=False, indent=2)
            return

        previous_metrics = {
            "real_profiles": STATE_RUNTIME_META.get("last_known_remote_real_profiles", 0),
            "score": STATE_RUNTIME_META.get("last_known_remote_signal_score", 0),
        }
        if is_materially_richer_state(previous_metrics, current_metrics):
            storage_log(
                "Refusing to overwrite Supabase with a materially less complete state; "
                "keeping the current payload in local fallback storage only."
            )
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            with STATE_FILE.open("w", encoding="utf-8") as handle:
                json.dump(state, handle, ensure_ascii=False, indent=2)
            return

        try:
            save_state_to_supabase(state)
            return
        except Exception as exc:
            storage_log(f"Supabase save failed, fallback to local file: {exc}")
            STATE_RUNTIME_META["supabase_writable"] = False

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with STATE_FILE.open("w", encoding="utf-8") as handle:
        json.dump(state, handle, ensure_ascii=False, indent=2)


def refresh_state_cache_from_supabase():
    global STATE_CACHE
    if not supabase_storage_enabled():
        return False
    if STATE_RUNTIME_META.get("loaded_from") != "local-fallback":
        return False

    try:
        state = load_state_from_supabase()
        if not state:
            return False
        changed = bool(STATE_RUNTIME_META.pop("remote_repair_required", False))
        changed = merge_phone_recovery_rows_from_supabase(state) or changed
        changed = merge_demo_state(state) or changed
        if reconcile_account_registry(state):
            changed = True
        if changed:
            save_state_to_supabase(state)
        STATE_CACHE = sanitize_state(state)
        set_runtime_storage_state("supabase", True, STATE_CACHE)
        storage_log("Recovered state cache from Supabase after earlier local fallback.")
        return True
    except Exception as exc:
        storage_log(f"Supabase refresh retry failed: {exc}")
        return False


def create_session_record():
    return {
        "id": f"session-{uuid.uuid4().hex[:12]}",
        "selectedRole": "enthusiast",
        "managedProfileIds": [],
        "managedAccountIds": [],
        "draftMediaPaths": [],
        "verifiedPhones": {},
        "lastVerifiedPhone": "",
        "currentActorProfileId": None,
        "userPosition": deepcopy(DEFAULT_POSITION),
        "locationStatus": DEFAULT_LOCATION_STATUS,
        "createdAt": iso_at(),
    }


def attach_profile_to_session(session, profile):
    profile_id = profile["id"]
    if profile_id not in session["managedProfileIds"]:
        session["managedProfileIds"].append(profile_id)
    account_id = str(profile.get("accountId") or "").strip()
    if account_id and account_id not in session["managedAccountIds"]:
        session["managedAccountIds"].append(account_id)
    session["selectedRole"] = profile["role"]
    session["currentActorProfileId"] = profile_id


def normalize_session_profiles(state, session):
    profiles = state.get("profiles", {})
    accounts = ensure_account_registry(state)
    changed = False

    managed_profile_ids = canonicalize_profile_ids(state, session.get("managedProfileIds", []))
    current_actor_profile_id = resolve_canonical_profile_id(state, session.get("currentActorProfileId"))

    managed_account_ids = []
    for account_id in session.get("managedAccountIds", []):
        account_key = str(account_id or "").strip()
        if account_key and account_key in accounts and account_key not in managed_account_ids:
            managed_account_ids.append(account_key)

    for profile_id in list(managed_profile_ids) + ([current_actor_profile_id] if current_actor_profile_id else []):
        profile = profiles.get(profile_id)
        account_id = str((profile or {}).get("accountId") or "").strip()
        if account_id and account_id in accounts and account_id not in managed_account_ids:
            managed_account_ids.append(account_id)

    for account_id in managed_account_ids:
        account = accounts.get(account_id)
        if not account:
            continue
        role_map = account.setdefault("profilesByRole", {})
        for role, profile_id in list(role_map.items()):
            canonical_profile_id = resolve_canonical_profile_id(state, profile_id)
            if canonical_profile_id and canonical_profile_id in profiles:
                if role_map.get(role) != canonical_profile_id:
                    role_map[role] = canonical_profile_id
                    changed = True
                if canonical_profile_id not in managed_profile_ids:
                    managed_profile_ids.append(canonical_profile_id)
            else:
                role_map.pop(role, None)
                changed = True

    if current_actor_profile_id and current_actor_profile_id not in managed_profile_ids:
        managed_profile_ids.append(current_actor_profile_id)

    selected_role = str(session.get("selectedRole") or "enthusiast").strip()
    if selected_role not in {"enthusiast", "gym", "coach"}:
        selected_role = "enthusiast"
        changed = True

    if current_actor_profile_id not in profiles or current_actor_profile_id not in managed_profile_ids:
        current_actor_profile_id = ""

    if not current_actor_profile_id:
        for profile_id in managed_profile_ids:
            profile = profiles.get(profile_id)
            if profile and profile.get("role") == selected_role:
                current_actor_profile_id = profile_id
                break

    if not current_actor_profile_id and managed_profile_ids:
        current_actor_profile_id = managed_profile_ids[0]

    if current_actor_profile_id:
        current_profile = profiles.get(current_actor_profile_id)
        if current_profile and selected_role != current_profile.get("role"):
            selected_role = current_profile.get("role") or selected_role
            changed = True

    deduped_managed_profiles = []
    for profile_id in managed_profile_ids:
        if profile_id in profiles and profile_id not in deduped_managed_profiles:
            deduped_managed_profiles.append(profile_id)

    deduped_managed_accounts = []
    for account_id in managed_account_ids:
        if account_id in accounts and account_id not in deduped_managed_accounts:
            deduped_managed_accounts.append(account_id)

    if session.get("managedProfileIds") != deduped_managed_profiles:
        session["managedProfileIds"] = deduped_managed_profiles
        changed = True
    if session.get("managedAccountIds") != deduped_managed_accounts:
        session["managedAccountIds"] = deduped_managed_accounts
        changed = True
    if session.get("currentActorProfileId") != (current_actor_profile_id or None):
        session["currentActorProfileId"] = current_actor_profile_id or None
        changed = True
    if session.get("selectedRole") != selected_role:
        session["selectedRole"] = selected_role
        changed = True

    return changed


def session_manages_profile(state, session, profile_id):
    canonical_profile_id = resolve_canonical_profile_id(state, profile_id)
    if not canonical_profile_id:
        return False, ""
    managed_ids = canonicalize_profile_ids(state, session.get("managedProfileIds", []))
    return canonical_profile_id in managed_ids, canonical_profile_id


def ensure_session(state, session_id=None):
    sessions = state.setdefault("sessions", {})
    if session_id and session_id in sessions:
        session = sessions[session_id]
        session.setdefault("managedProfileIds", [])
        session.setdefault("managedAccountIds", [])
        session.setdefault("draftMediaPaths", [])
        session.setdefault("verifiedPhones", {})
        session.setdefault("lastVerifiedPhone", "")
        normalize_session_profiles(state, session)
        return session
    session = create_session_record()
    sessions[session["id"]] = session
    return session


def author_name(state, profile_id):
    profile = state["profiles"].get(resolve_canonical_profile_id(state, profile_id))
    return profile["name"] if profile else "平台用户"


def profile_posts(state, profile_id):
    alias_ids = collect_profile_alias_ids(state, profile_id)
    posts = [post for post in state["posts"].values() if post["authorProfileId"] in alias_ids]
    return sorted(posts, key=lambda item: item["createdAt"], reverse=True)


def get_follow_set(state, current_actor_profile_id):
    if not current_actor_profile_id:
        return set()
    source_alias_ids = collect_profile_alias_ids(state, current_actor_profile_id)
    return {
        resolve_canonical_profile_id(state, item["targetProfileId"])
        for item in state["follows"]
        if item["sourceProfileId"] in source_alias_ids and resolve_canonical_profile_id(state, item["targetProfileId"])
    }


def get_follower_set(state, current_actor_profile_id):
    if not current_actor_profile_id:
        return set()
    target_alias_ids = collect_profile_alias_ids(state, current_actor_profile_id)
    return {
        resolve_canonical_profile_id(state, item["sourceProfileId"])
        for item in state["follows"]
        if item["targetProfileId"] in target_alias_ids and resolve_canonical_profile_id(state, item["sourceProfileId"])
    }


def follower_count(state, profile_id):
    return len(get_follower_set(state, profile_id))


def following_count(state, profile_id):
    return len(get_follow_set(state, profile_id))


def normalize_blocks(state):
    unique = []
    seen = set()
    for item in state.get("blocks", []) or []:
        source_id = resolve_canonical_profile_id(state, item.get("sourceProfileId"))
        target_id = resolve_canonical_profile_id(state, item.get("targetProfileId"))
        if not source_id or not target_id or source_id == target_id:
            continue
        key = (source_id, target_id)
        if key in seen:
            continue
        seen.add(key)
        unique.append({
            "sourceProfileId": source_id,
            "targetProfileId": target_id,
            "createdAt": item.get("createdAt") or iso_at(),
        })
    state["blocks"] = unique


def get_block_set(state, current_actor_profile_id):
    if not current_actor_profile_id:
        return set()
    source_alias_ids = collect_profile_alias_ids(state, current_actor_profile_id)
    return {
        resolve_canonical_profile_id(state, item.get("targetProfileId"))
        for item in state.get("blocks", [])
        if item.get("sourceProfileId") in source_alias_ids and resolve_canonical_profile_id(state, item.get("targetProfileId"))
    }


def get_blocked_by_set(state, current_actor_profile_id):
    if not current_actor_profile_id:
        return set()
    target_alias_ids = collect_profile_alias_ids(state, current_actor_profile_id)
    return {
        resolve_canonical_profile_id(state, item.get("sourceProfileId"))
        for item in state.get("blocks", [])
        if item.get("targetProfileId") in target_alias_ids and resolve_canonical_profile_id(state, item.get("sourceProfileId"))
    }


def is_blocking_profile(state, source_profile_id, target_profile_id):
    source_alias_ids = collect_profile_alias_ids(state, source_profile_id)
    target_alias_ids = collect_profile_alias_ids(state, target_profile_id)
    return any(
        item.get("sourceProfileId") in source_alias_ids and item.get("targetProfileId") in target_alias_ids
        for item in state.get("blocks", []) or []
    )


def remove_relationship_between_profiles(state, source_profile_id, target_profile_id):
    source_alias_ids = collect_profile_alias_ids(state, source_profile_id)
    target_alias_ids = collect_profile_alias_ids(state, target_profile_id)
    state["follows"] = [
        item for item in state.get("follows", [])
        if not (
            item.get("sourceProfileId") in source_alias_ids and item.get("targetProfileId") in target_alias_ids
        )
        and not (
            item.get("sourceProfileId") in target_alias_ids and item.get("targetProfileId") in source_alias_ids
        )
    ]


def serialize_review(state, review):
    return {
        "id": review["id"],
        "author": author_name(state, review.get("authorProfileId")),
        "authorProfileId": review.get("authorProfileId"),
        "score": review["score"],
        "text": review["text"],
        "time": relative_time_label(review.get("createdAt")),
        "createdAt": review.get("createdAt"),
    }


def serialize_comment(state, comment):
    profile = state["profiles"].get(comment["authorProfileId"])
    return {
        "id": comment["id"],
        "authorProfileId": comment["authorProfileId"],
        "authorName": profile["name"] if profile else "平台用户",
        "authorAvatarImage": compact_avatar_image(profile["avatarImage"], profile["role"]) if profile else "",
        "text": comment["text"],
        "time": relative_time_label(comment["createdAt"]),
        "createdAt": comment["createdAt"],
    }


def serialize_profile_brief(state, profile_id):
    profile_id = resolve_canonical_profile_id(state, profile_id)
    profile = state.get("profiles", {}).get(profile_id)
    if not profile:
        return {
            "id": profile_id,
            "name": "平台用户",
            "handle": f"@{profile_id}",
            "role": "",
            "city": "",
            "locationLabel": "",
            "shortDesc": "",
            "bio": "",
            "followers": 0,
            "ratingAvg": 0,
            "ratingCount": 0,
            "avatarImage": "",
        }

    reviews = profile.get("reviews", [])
    rating_count = len(reviews)
    rating_avg = round(sum(item["score"] for item in reviews) / rating_count, 1) if rating_count else 0
    return {
        "id": profile["id"],
        "name": profile.get("name", "平台用户"),
        "handle": profile.get("handle") or f"@{profile['id']}",
        "role": profile.get("role", ""),
        "city": profile.get("city", ""),
        "locationLabel": profile.get("locationLabel", ""),
        "shortDesc": profile.get("shortDesc", ""),
        "bio": profile.get("bio", ""),
        "followers": follower_count(state, profile["id"]),
        "ratingAvg": rating_avg,
        "ratingCount": rating_count,
        "avatarImage": compact_avatar_image(profile.get("avatarImage"), profile.get("role", "")),
    }


def serialize_checkin(checkin):
    return {
        "id": checkin["id"],
        "source": checkin.get("source", ""),
        "sportId": checkin.get("sportId", ""),
        "sportLabel": checkin.get("sportLabel", "训练打卡"),
        "duration": checkin.get("duration", 0),
        "distance": checkin.get("distance", 0),
        "calories": checkin.get("calories", 0),
        "paceLabel": checkin.get("paceLabel", ""),
        "bestPaceLabel": checkin.get("bestPaceLabel", ""),
        "heartRateAvg": checkin.get("heartRateAvg", 0),
        "elevationGain": checkin.get("elevationGain", 0),
        "route": deepcopy(checkin.get("route")) if isinstance(checkin.get("route"), dict) else None,
        "note": checkin.get("note", ""),
        "createdAt": checkin["createdAt"],
        "time": relative_time_label(checkin["createdAt"]),
    }


def serialize_post(state, post, current_actor_profile_id):
    current_actor_alias_ids = collect_profile_alias_ids(state, current_actor_profile_id)
    canonical_author_id = resolve_canonical_profile_id(state, post["authorProfileId"])
    return {
        "id": post["id"],
        "authorProfileId": canonical_author_id or post["authorProfileId"],
        "createdAt": post["createdAt"],
        "time": relative_time_label(post["createdAt"]),
        "content": post["content"],
        "meta": post["meta"],
        "media": [compact_media_item(item) for item in post.get("media", [])],
        "likeCount": len(post.get("likes", [])),
        "favoriteCount": len(
            [
                item
                for item in state.get("postFavorites", [])
                if item.get("postId") == post["id"]
            ]
        ),
        "likedByCurrentActor": any(item in current_actor_alias_ids for item in post.get("likes", [])),
        "comments": [serialize_comment(state, item) for item in sorted(post.get("comments", []), key=lambda value: value["createdAt"])],
        "checkin": serialize_checkin(post["checkin"]) if post.get("checkin") else None,
    }


def build_mention_tokens(profile):
    if not profile:
        return []
    tokens = []
    handle = str(profile.get("handle") or "").strip().lower()
    if handle:
        tokens.append(handle)
    name = str(profile.get("name") or "").strip().lower()
    if name:
        tokens.append(f"@{name}")
    return [token for token in tokens if token]


def text_mentions_profile(text, profile):
    content = str(text or "").strip().lower()
    if not content or not profile:
        return False
    return any(token in content for token in build_mention_tokens(profile))


def serialize_notifications(state, current_actor_profile_id):
    if not current_actor_profile_id:
        return []

    current_profile = state.get("profiles", {}).get(current_actor_profile_id)
    notifications = []

    def add_notification(notification_id, actor_profile_id, type_label, text, created_at, post_id):
        if not actor_profile_id or actor_profile_id == current_actor_profile_id:
            return
        actor = serialize_profile_brief(state, actor_profile_id)
        notifications.append(
            {
                "id": notification_id,
                "type": type_label,
                "actorProfileId": actor_profile_id,
                "actorName": actor["name"],
                "actorHandle": actor["handle"],
                "actorAvatarImage": actor["avatarImage"],
                "actorRole": actor["role"],
                "text": text,
                "postId": post_id,
                "time": relative_time_label(created_at),
                "createdAt": created_at,
            }
        )

    for post in state.get("posts", {}).values():
        post_id = post.get("id")
        author_profile_id = post.get("authorProfileId")
        excerpt = str(post.get("content") or "").strip()[:48]

        if author_profile_id == current_actor_profile_id:
            for liker_id in post.get("likes", []):
                add_notification(
                    f"like-{post_id}-{liker_id}",
                    liker_id,
                    "like",
                    f"赞了你的动态：{excerpt or '你的健身圈内容'}",
                    post.get("createdAt"),
                    post_id,
                )
            for comment in post.get("comments", []):
                add_notification(
                    comment.get("id") or f"comment-{post_id}-{comment.get('authorProfileId')}",
                    comment.get("authorProfileId"),
                    "comment",
                    f"评论了你的动态：{str(comment.get('text') or '').strip()}",
                    comment.get("createdAt"),
                    post_id,
                )

        if author_profile_id != current_actor_profile_id and text_mentions_profile(post.get("content"), current_profile):
            add_notification(
                f"mention-post-{post_id}-{author_profile_id}",
                author_profile_id,
                "mention",
                f"在动态里 @ 了你：{excerpt or '点开查看内容'}",
                post.get("createdAt"),
                post_id,
            )

        for comment in post.get("comments", []):
            if comment.get("authorProfileId") == current_actor_profile_id:
                continue
            if text_mentions_profile(comment.get("text"), current_profile):
                add_notification(
                    f"mention-comment-{comment.get('id') or post_id}",
                    comment.get("authorProfileId"),
                    "mention",
                    f"在评论里 @ 了你：{str(comment.get('text') or '').strip()}",
                    comment.get("createdAt"),
                    post_id,
                )

    notifications.sort(key=lambda item: item.get("createdAt") or "", reverse=True)
    return notifications[:60]


def serialize_managed_profile_badges(state, session):
    badges = []
    for profile_id in session.get("managedProfileIds", []) or []:
        canonical_profile_id = resolve_canonical_profile_id(state, profile_id)
        if not canonical_profile_id:
            continue
        notification_items = serialize_notifications(state, canonical_profile_id)
        notification_count = len(notification_items)
        thread_count = 0
        latest_at_values = [item.get("createdAt") for item in notification_items if item.get("createdAt")]
        for thread in serialize_threads(state, canonical_profile_id):
            last_message = thread.get("lastMessage") or {}
            if last_message.get("senderProfileId") and last_message.get("senderProfileId") != canonical_profile_id:
                thread_count += 1
                if last_message.get("createdAt"):
                    latest_at_values.append(last_message.get("createdAt"))
        count = min(99, notification_count + thread_count)
        if count:
            badges.append({
                "profileId": canonical_profile_id,
                "count": count,
                "latestAt": max(latest_at_values) if latest_at_values else "",
            })
    return badges


def serialize_favorite_posts(state, current_actor_profile_id):
    if not current_actor_profile_id:
        return []
    source_alias_ids = collect_profile_alias_ids(state, current_actor_profile_id)
    favorites = [
        item
        for item in state.get("postFavorites", [])
        if item.get("sourceProfileId") in source_alias_ids
    ]
    favorites.sort(key=lambda item: item.get("createdAt") or "", reverse=True)
    serialized = []
    for item in favorites:
        post = state.get("posts", {}).get(item.get("postId"))
        if not post:
            continue
        serialized.append(
            {
                "profile": serialize_profile_brief(state, post.get("authorProfileId")),
                "post": serialize_post(state, post, current_actor_profile_id),
                "favoritedAt": item.get("createdAt") or "",
            }
        )
    return serialized


def serialize_profile(state, profile_id, current_actor_profile_id):
    profile_id = resolve_canonical_profile_id(state, profile_id)
    current_actor_profile_id = resolve_canonical_profile_id(state, current_actor_profile_id)
    profile = deepcopy(state["profiles"][profile_id])
    reviews = [serialize_review(state, item) for item in sorted(profile.get("reviews", []), key=lambda value: value["createdAt"], reverse=True)]
    rating_count = len(reviews)
    rating_avg = round(sum(item["score"] for item in reviews) / rating_count, 1) if rating_count else 0
    profile["followers"] = follower_count(state, profile_id)
    profile["following"] = following_count(state, profile_id)
    profile["ratingAvg"] = rating_avg
    profile["ratingCount"] = rating_count
    profile["reviews"] = reviews
    profile["avatarImage"] = compact_avatar_image(profile.get("avatarImage"), profile["role"])
    profile["posts"] = [serialize_post(state, post, current_actor_profile_id) for post in profile_posts(state, profile_id)[:4]]
    checkin_limit = 120 if profile_id == current_actor_profile_id else 12
    profile["checkins"] = [serialize_checkin(item) for item in sorted(profile.get("checkins", []), key=lambda value: value["createdAt"], reverse=True)[:checkin_limit]]
    profile["healthHistory"] = [
        deepcopy(item)
        for item in sorted(profile.get("healthHistory", []), key=lambda value: value.get("createdAt", ""), reverse=True)[:60]
    ]
    profile["availabilitySlots"] = serialize_availability_slots(profile)
    profile.pop("externalWorkoutIds", None)
    return profile


def serialize_availability_slots(profile):
    slots = []
    for item in profile.get("availabilitySlots", []) or []:
        date_value = str(item.get("date") or item.get("scheduledDate") or "").strip()
        time_value = str(item.get("time") or item.get("scheduledTime") or "").strip()
        if not date_value or not time_value:
            continue
        slots.append(
            {
                "id": str(item.get("id") or f"slot-{uuid.uuid4().hex[:10]}"),
                "date": date_value[:10],
                "time": time_value[:5],
                "durationMinutes": parse_optional_int(item.get("durationMinutes")) or 60,
                "note": str(item.get("note") or "").strip()[:80],
                "status": str(item.get("status") or "open").strip() or "open",
                "createdAt": item.get("createdAt") or "",
                "bookedByProfileId": item.get("bookedByProfileId") or "",
                "bookedAt": item.get("bookedAt") or "",
            }
        )
    slots.sort(key=lambda value: (value.get("date", ""), value.get("time", ""), value.get("createdAt", "")))
    return slots


def serialize_bookings(state, session):
    managed = set(session["managedProfileIds"])
    managed_alias_ids = set()
    for profile_id in managed:
        managed_alias_ids.update(collect_profile_alias_ids(state, profile_id))
    bookings = [
        item for item in state["bookings"]
        if item["createdByProfileId"] in managed_alias_ids or item["targetProfileId"] in managed_alias_ids
    ]
    bookings.sort(key=lambda item: item["createdAt"], reverse=True)
    serialized = []
    for item in bookings:
        source_id = resolve_canonical_profile_id(state, item.get("createdByProfileId"))
        target_id = resolve_canonical_profile_id(state, item.get("targetProfileId"))
        source_profile = state["profiles"].get(source_id)
        target_profile = state["profiles"].get(target_id)
        if item.get("createdByProfileId") in managed_alias_ids and item.get("targetProfileId") in managed_alias_ids:
            direction = "internal"
        elif item.get("targetProfileId") in managed_alias_ids:
            direction = "incoming"
        else:
            direction = "outgoing"

        counterpart = target_profile if direction == "outgoing" else source_profile
        serialized.append(
            {
                **item,
                "direction": direction,
                "createdByProfileName": source_profile.get("name") if source_profile else "平台用户",
                "createdByProfileRole": source_profile.get("role") if source_profile else "",
                "targetProfileName": target_profile.get("name") if target_profile else "平台用户",
                "targetProfileRole": target_profile.get("role") if target_profile else "",
                "counterpartProfileId": resolve_canonical_profile_id(state, counterpart.get("id")) if counterpart else "",
                "counterpartProfileName": counterpart.get("name") if counterpart else "平台用户",
                "counterpartProfileRole": counterpart.get("role") if counterpart else "",
                "counterpartLocationLabel": counterpart.get("locationLabel") if counterpart else "",
            }
        )
    return serialized


def get_thread_id(profile_a, profile_b):
    left, right = sorted([profile_a, profile_b])
    return f"thread-{left}-{right}"


def find_or_create_thread(state, profile_a, profile_b):
    thread_id = get_thread_id(profile_a, profile_b)
    for thread in state["threads"]:
        if thread["id"] == thread_id:
            return thread
    thread = {"id": thread_id, "participants": sorted([profile_a, profile_b]), "messages": []}
    state["threads"].append(thread)
    return thread


def serialize_threads(state, current_actor_profile_id):
    if not current_actor_profile_id:
        return []
    current_actor_alias_ids = collect_profile_alias_ids(state, current_actor_profile_id)
    threads = []
    for thread in state["threads"]:
        if not any(item in current_actor_alias_ids for item in thread["participants"]):
            continue
        other_profile_id = next((item for item in thread["participants"] if item not in current_actor_alias_ids), None)
        other_profile_id = resolve_canonical_profile_id(state, other_profile_id)
        other_profile = state["profiles"].get(other_profile_id)
        messages = [
            {
                "id": message["id"],
                "senderProfileId": resolve_canonical_profile_id(state, message["senderProfileId"]) or message["senderProfileId"],
                "senderName": author_name(state, message["senderProfileId"]),
                "text": message["text"],
                "time": relative_time_label(message["createdAt"]),
                "createdAt": message["createdAt"],
            }
            for message in sorted(thread["messages"], key=lambda item: item["createdAt"])
        ]
        last_message = messages[-1] if messages else None
        threads.append(
            {
                "id": thread["id"],
                "withProfileId": other_profile_id,
                "withProfileName": other_profile["name"] if other_profile else "未知用户",
                "withProfileAvatarImage": compact_avatar_image(other_profile["avatarImage"], other_profile["role"]) if other_profile else "",
                "messages": messages,
                "lastMessage": last_message,
            }
        )
    threads.sort(key=lambda item: item["lastMessage"]["createdAt"] if item["lastMessage"] else "", reverse=True)
    return threads


CONTENT_REVIEW_KEYWORDS = {
    "诈骗": "疑似诈骗",
    "赌博": "违规交易",
    "博彩": "违规交易",
    "毒品": "违法内容",
    "枪支": "违法内容",
    "裸聊": "低俗骚扰",
    "约炮": "低俗骚扰",
    "自杀": "高风险表达",
    "杀人": "暴力威胁",
    "转账": "站外交易风险",
    "私下付款": "站外交易风险",
    "加微信": "站外导流风险",
}


def normalize_moderation_text(text):
    return re.sub(r"\s+", "", str(text or "").strip().lower())


def review_text_content(text, source=""):
    normalized = normalize_moderation_text(text)
    flags = []
    for keyword, label in CONTENT_REVIEW_KEYWORDS.items():
        if keyword.lower() in normalized and label not in flags:
            flags.append(label)
    if len(str(text or "")) > 1200:
        flags.append("内容过长")
    return {
        "status": "pending_review" if flags else "approved",
        "flags": flags,
        "source": source,
        "checkedAt": iso_at(),
    }


def queue_moderation_item(state, item):
    state.setdefault("moderationQueue", [])
    item_type = item.get("type")
    item_id = item.get("targetId")
    source = item.get("source") or "content-review"
    existing = next(
        (
            queued
            for queued in state["moderationQueue"]
            if queued.get("type") == item_type
            and queued.get("targetId") == item_id
            and queued.get("source") == source
            and queued.get("status") == "pending"
        ),
        None,
    )
    if existing:
        existing["updatedAt"] = iso_at()
        existing["flags"] = sorted(set(existing.get("flags", []) + item.get("flags", [])))
        return existing
    queued_item = {
        "id": item.get("id") or f"moderation-{uuid.uuid4().hex[:10]}",
        "type": item_type,
        "targetId": item_id,
        "targetOwnerProfileId": resolve_canonical_profile_id(state, item.get("targetOwnerProfileId") or "") or item.get("targetOwnerProfileId") or "",
        "reporterProfileId": resolve_canonical_profile_id(state, item.get("reporterProfileId") or "") or item.get("reporterProfileId") or "",
        "source": source,
        "flags": item.get("flags") or [],
        "excerpt": str(item.get("excerpt") or "")[:160],
        "status": "pending",
        "createdAt": iso_at(),
        "updatedAt": iso_at(),
    }
    state["moderationQueue"].insert(0, queued_item)
    del state["moderationQueue"][200:]
    return queued_item


def attach_text_moderation(state, record, text, item_type, owner_profile_id, source):
    review = review_text_content(text, source=source)
    record["moderation"] = review
    if review["status"] == "pending_review":
        queue_moderation_item(
            state,
            {
                "type": item_type,
                "targetId": record.get("id"),
                "targetOwnerProfileId": owner_profile_id,
                "source": "content-review",
                "flags": review.get("flags", []),
                "excerpt": text,
            },
        )
    return review


def find_report_target(state, target_type, target_id):
    target_type = str(target_type or "").strip()
    target_id = str(target_id or "").strip()
    if target_type == "profile":
        profile_id = resolve_canonical_profile_id(state, target_id)
        profile = state.get("profiles", {}).get(profile_id)
        if profile:
            return {"type": target_type, "id": profile_id, "ownerProfileId": profile_id, "record": profile}
    if target_type == "post":
        post = state.get("posts", {}).get(target_id)
        if post:
            owner = resolve_canonical_profile_id(state, post.get("authorProfileId")) or post.get("authorProfileId")
            return {"type": target_type, "id": target_id, "ownerProfileId": owner, "record": post}
    if target_type == "comment":
        for post in state.get("posts", {}).values():
            for comment in post.get("comments", []):
                if comment.get("id") == target_id:
                    owner = resolve_canonical_profile_id(state, comment.get("authorProfileId")) or comment.get("authorProfileId")
                    return {"type": target_type, "id": target_id, "ownerProfileId": owner, "record": comment, "postId": post.get("id")}
    if target_type == "message":
        for thread in state.get("threads", []):
            for message in thread.get("messages", []):
                if message.get("id") == target_id:
                    owner = resolve_canonical_profile_id(state, message.get("senderProfileId")) or message.get("senderProfileId")
                    return {"type": target_type, "id": target_id, "ownerProfileId": owner, "record": message, "threadId": thread.get("id")}
    return None


def serialize_moderation_item(state, item):
    owner_id = resolve_canonical_profile_id(state, item.get("targetOwnerProfileId") or "")
    reporter_id = resolve_canonical_profile_id(state, item.get("reporterProfileId") or "")
    return {
        **item,
        "targetOwnerProfile": serialize_profile_brief(state, owner_id) if owner_id else None,
        "reporterProfile": serialize_profile_brief(state, reporter_id) if reporter_id else None,
    }


def build_moderation_dashboard(state):
    reports = state.setdefault("reports", [])
    queue = state.setdefault("moderationQueue", [])
    open_reports = [item for item in reports if item.get("status", "open") == "open"]
    pending_queue = [item for item in queue if item.get("status", "pending") == "pending"]
    return {
        "ok": True,
        "summary": {
            "openReports": len(open_reports),
            "pendingReview": len(pending_queue),
            "totalReports": len(reports),
            "totalQueued": len(queue),
        },
        "reports": [serialize_moderation_item(state, item) for item in reports[:100]],
        "moderationQueue": [serialize_moderation_item(state, item) for item in queue[:100]],
        "adminActions": state.setdefault("adminActions", [])[:50],
    }


def moderation_admin_authorized(headers, query=None, payload=None):
    expected_token = ADMIN_TOKEN
    if not expected_token:
        return False
    provided_token = ""
    auth_header = str(headers.get("Authorization") or "").strip()
    if auth_header.lower().startswith("bearer "):
        provided_token = auth_header[7:].strip()
    if not provided_token and query:
        provided_token = str(query.get("token", [""])[0]).strip()
    if not provided_token and payload:
        provided_token = str(payload.get("token") or "").strip()
    return hmac.compare_digest(provided_token, expected_token)


def bootstrap_response(state, session):
    normalize_session_profiles(state, session)
    current_actor_profile_id = session.get("currentActorProfileId")
    canonical_profile_ids = canonicalize_profile_ids(state, state.get("profiles", {}).keys())
    profiles = [serialize_profile(state, profile_id, current_actor_profile_id) for profile_id in canonical_profile_ids]
    current_actor_alias_ids = collect_profile_alias_ids(state, current_actor_profile_id)
    return {
        "config": runtime_config(),
        "session": {
            "id": session["id"],
            "selectedRole": session["selectedRole"],
            "managedProfileIds": session["managedProfileIds"],
            "managedAccountIds": session["managedAccountIds"],
            "managedAccounts": serialize_managed_accounts(state, session),
            "managedProfileBadges": serialize_managed_profile_badges(state, session),
            "currentActorProfileId": current_actor_profile_id,
            "userPosition": session["userPosition"],
            "locationStatus": session["locationStatus"],
        },
        "profiles": profiles,
        "followSet": sorted(get_follow_set(state, current_actor_profile_id)),
        "followerSet": sorted(get_follower_set(state, current_actor_profile_id)),
        "blockSet": sorted(get_block_set(state, current_actor_profile_id)),
        "blockedBySet": sorted(get_blocked_by_set(state, current_actor_profile_id)),
        "favoritePostIds": sorted(
            str(item.get("postId") or "")
            for item in state.get("postFavorites", [])
            if item.get("sourceProfileId") in current_actor_alias_ids and item.get("postId")
        ),
        "favoritePosts": serialize_favorite_posts(state, current_actor_profile_id),
        "notifications": serialize_notifications(state, current_actor_profile_id),
        "bookings": serialize_bookings(state, session),
        "threads": serialize_threads(state, current_actor_profile_id),
    }


def compact_post_interaction_response(state, session, post):
    current_actor_profile_id = session.get("currentActorProfileId")
    current_actor_alias_ids = collect_profile_alias_ids(state, current_actor_profile_id)
    return {
        "ok": True,
        "sessionId": session["id"],
        "post": serialize_post(state, post, current_actor_profile_id),
        "favoritePostIds": sorted(
            str(item.get("postId") or "")
            for item in state.get("postFavorites", [])
            if item.get("sourceProfileId") in current_actor_alias_ids and item.get("postId")
        ),
    }


def compact_follow_response(state, session, source_profile_id, target_profile_id):
    source_profile_id = resolve_canonical_profile_id(state, source_profile_id)
    target_profile_id = resolve_canonical_profile_id(state, target_profile_id)
    return {
        "ok": True,
        "session": {
            "id": session["id"],
            "selectedRole": session["selectedRole"],
            "currentActorProfileId": session.get("currentActorProfileId"),
        },
        "follow": {
            "sourceProfileId": source_profile_id,
            "targetProfileId": target_profile_id,
            "following": target_profile_id in get_follow_set(state, source_profile_id),
            "followSet": sorted(get_follow_set(state, source_profile_id)),
            "followerSet": sorted(get_follower_set(state, source_profile_id)),
        },
    }


def compact_message_response(state, session, target_profile_id):
    current_actor_profile_id = session.get("currentActorProfileId")
    target_profile_id = resolve_canonical_profile_id(state, target_profile_id) or target_profile_id
    thread = next(
        (item for item in serialize_threads(state, current_actor_profile_id) if item.get("withProfileId") == target_profile_id),
        None,
    )
    return {
        "ok": True,
        "sessionId": session["id"],
        "thread": thread,
    }


def build_profile_payload(role, payload, existing_profile, session):
    base_position = session["userPosition"]
    avatar_image = payload.get("avatarImage") or (existing_profile or {}).get("avatarImage") or default_avatar_for_role(role)
    city = payload.get("city") or base_position["city"]
    location_label = payload.get("locationLabel") or payload.get("location") or base_position["label"]
    lat = payload.get("lat", base_position["lat"])
    lng = payload.get("lng", base_position["lng"])

    if role == "gym":
        name = payload.get("gymName") or payload.get("name") or (existing_profile or {}).get("name") or f"{city} 新场馆"
        facilities = payload.get("facilities", "")
        tags = [item for item in str(facilities).replace("/", " ").replace("，", " ").replace("、", " ").split() if item][:4] or ["器械", "团课", "恢复区"]
        return {
            **(existing_profile or {}),
            "id": (existing_profile or {}).get("id", f"gym-{uuid.uuid4().hex[:8]}"),
            "owner_session_id": (existing_profile or {}).get("owner_session_id") or session["id"],
            "role": role,
            "name": name,
            "handle": (existing_profile or {}).get("handle", f"@gym.{uuid.uuid4().hex[:4]}"),
            "avatar": (existing_profile or {}).get("avatar", name[:1]),
            "avatarImage": avatar_image,
            "city": city,
            "locationLabel": location_label,
            "lat": lat,
            "lng": lng,
            "bio": payload.get("intro") or f"{name} 已完成入驻，欢迎预约到店训练。",
            "shortDesc": payload.get("intro") or facilities or "设备齐全，欢迎到店体验。",
            "price": payload.get("price") or (existing_profile or {}).get("price") or "¥99/月起",
            "tags": tags,
            "hours": payload.get("hours", ""),
            "contactName": payload.get("contactName", ""),
            "phone": payload.get("phone", ""),
            "pricingPlans": payload.get("pricingPlans") or (existing_profile or {}).get("pricingPlans") or [
                {"title": "会员卡", "detail": "到店训练 / 团课预约", "price": payload.get("price") or "¥99/月起"}
            ],
            "availabilitySlots": payload.get("availabilitySlots") or (existing_profile or {}).get("availabilitySlots", []),
            "healthHistory": payload.get("healthHistory") or (existing_profile or {}).get("healthHistory", []),
            "reviews": payload.get("reviews") or (existing_profile or {}).get("reviews", []),
            "checkins": payload.get("checkins") or (existing_profile or {}).get("checkins", []),
            "listed": True,
            "createdAt": (existing_profile or {}).get("createdAt", iso_at()),
        }

    if role == "coach":
        name = payload.get("name") or (existing_profile or {}).get("name") or "新教练"
        specialties = payload.get("specialties", "")
        tags = [item for item in str(specialties).replace("/", " ").replace("，", " ").replace("、", " ").split() if item][:4] or ["减脂", "力量", "私教"]
        certifications = [item for item in str(payload.get("certifications", "")).replace("/", " ").replace("，", " ").replace("、", " ").split() if item]
        return {
            **(existing_profile or {}),
            "id": (existing_profile or {}).get("id", f"coach-{uuid.uuid4().hex[:8]}"),
            "owner_session_id": (existing_profile or {}).get("owner_session_id") or session["id"],
            "role": role,
            "name": name,
            "handle": (existing_profile or {}).get("handle", f"@coach.{uuid.uuid4().hex[:4]}"),
            "avatar": (existing_profile or {}).get("avatar", name[:1]),
            "avatarImage": avatar_image,
            "city": city,
            "locationLabel": location_label,
            "lat": lat,
            "lng": lng,
            "bio": payload.get("intro") or f"{name} 已入驻平台，支持一对一训练和课程预约。",
            "shortDesc": payload.get("intro") or specialties or "擅长减脂塑形、力量提升。",
            "price": payload.get("price") or (existing_profile or {}).get("price") or "¥220/小时",
            "tags": tags,
            "years": str(payload.get("years", "")),
            "phone": payload.get("phone") or (existing_profile or {}).get("phone", ""),
            "certifications": certifications,
            "pricingPlans": payload.get("pricingPlans") or (existing_profile or {}).get("pricingPlans") or [
                {"title": "私教课程", "detail": "一对一训练服务", "price": payload.get("price") or "¥220/小时"}
            ],
            "availabilitySlots": payload.get("availabilitySlots") or (existing_profile or {}).get("availabilitySlots", []),
            "healthHistory": payload.get("healthHistory") or (existing_profile or {}).get("healthHistory", []),
            "reviews": payload.get("reviews") or (existing_profile or {}).get("reviews", []),
            "checkins": payload.get("checkins") or (existing_profile or {}).get("checkins", []),
            "listed": True,
            "createdAt": (existing_profile or {}).get("createdAt", iso_at()),
        }

    name = payload.get("name") or (existing_profile or {}).get("name") or "新用户"
    level = payload.get("level") or (existing_profile or {}).get("level") or "新手入门"
    goal = payload.get("goal") or (existing_profile or {}).get("goal") or "保持规律训练"
    gender = payload.get("gender") or (existing_profile or {}).get("gender") or ""
    height_cm = parse_optional_int(payload.get("heightCm"))
    if height_cm is None:
        height_cm = parse_optional_int((existing_profile or {}).get("heightCm"))
    weight_kg = parse_optional_float(payload.get("weightKg"))
    if weight_kg is None:
        weight_kg = parse_optional_float((existing_profile or {}).get("weightKg"))
    if not gender or not height_cm or not weight_kg:
        raise ValueError("健身爱好者注册需要填写性别、身高和体重。")
    bmi = calculate_bmi(height_cm, weight_kg)
    existing_body_fat = parse_optional_float((existing_profile or {}).get("bodyFat"))
    body_fat = existing_body_fat if existing_body_fat is not None else estimate_body_fat(gender, bmi)
    return {
        **(existing_profile or {}),
        "id": (existing_profile or {}).get("id", f"enthusiast-{uuid.uuid4().hex[:8]}"),
        "owner_session_id": (existing_profile or {}).get("owner_session_id") or session["id"],
        "role": role,
        "name": name,
        "handle": (existing_profile or {}).get("handle", f"@user.{uuid.uuid4().hex[:4]}"),
        "avatar": (existing_profile or {}).get("avatar", name[:1]),
        "avatarImage": avatar_image,
        "city": city,
        "locationLabel": location_label,
        "lat": lat,
        "lng": lng,
        "bio": payload.get("intro") or f"{name} 正在进行 {level} 训练，目标是 {goal}。",
        "shortDesc": payload.get("intro") or goal or "开始记录自己的健身生活。",
        "price": "",
        "tags": [level, city, "训练日记"],
        "level": level,
        "goal": goal,
        "phone": payload.get("phone") or (existing_profile or {}).get("phone", ""),
        "gender": gender,
        "heightCm": height_cm,
        "weightKg": weight_kg,
        "favoriteSports": payload.get("favoriteSports") or (existing_profile or {}).get("favoriteSports", []),
        "connectedDevices": payload.get("connectedDevices") or (existing_profile or {}).get("connectedDevices", []),
        "healthSource": payload.get("healthSource") or (existing_profile or {}).get("healthSource", ""),
        "deviceSyncedAt": payload.get("deviceSyncedAt") or (existing_profile or {}).get("deviceSyncedAt", ""),
        "healthSnapshot": payload.get("healthSnapshot") or (existing_profile or {}).get("healthSnapshot", {}),
        "healthHistory": payload.get("healthHistory") or (existing_profile or {}).get("healthHistory", []),
        "restingHeartRate": payload.get("restingHeartRate") or (existing_profile or {}).get("restingHeartRate"),
        "bodyFat": parse_optional_float(payload.get("bodyFat")) or body_fat,
        "externalWorkoutIds": (existing_profile or {}).get("externalWorkoutIds", []),
        "reviews": payload.get("reviews") or (existing_profile or {}).get("reviews", []),
        "checkins": payload.get("checkins") or (existing_profile or {}).get("checkins", []),
        "listed": True,
        "createdAt": (existing_profile or {}).get("createdAt", iso_at()),
    }


def restore_cached_checkins(profile, items):
    restored = 0
    existing_keys = {
        str(item.get("externalId") or item.get("id") or "").strip()
        for item in profile.get("checkins", [])
        if str(item.get("externalId") or item.get("id") or "").strip()
    }

    for item in items or []:
        if not isinstance(item, dict):
            continue
        created_at = item.get("createdAt") or now_utc().isoformat()
        started_at = item.get("startedAt") or created_at
        ended_at = item.get("endedAt") or created_at
        key = str(item.get("externalId") or item.get("id") or f"checkin-{uuid.uuid4().hex[:10]}").strip()
        if key in existing_keys:
            continue

        profile.setdefault("checkins", []).append(
            {
                "id": str(item.get("id") or f"checkin-{uuid.uuid4().hex[:10]}"),
                "externalId": key,
                "source": str(item.get("source") or "FitHub 本机恢复"),
                "sportId": str(item.get("sportId") or "strength"),
                "sportLabel": str(item.get("sportLabel") or "训练打卡"),
                "duration": max(0, parse_optional_int(item.get("duration")) or 0),
                "distance": round(max(0, parse_optional_float(item.get("distance")) or 0), 2),
                "calories": max(0, parse_optional_int(item.get("calories")) or 0),
                "note": str(item.get("note") or ""),
                "createdAt": created_at,
                "startedAt": started_at,
                "endedAt": ended_at,
            }
        )
        existing_keys.add(key)
        restored += 1

    profile["checkins"] = sorted(profile.get("checkins", []), key=lambda value: value.get("createdAt", ""), reverse=True)[:60]
    return restored


def restore_cached_posts(state, profile_id, items):
    restored = 0
    existing_keys = {
        (
            post.get("createdAt", ""),
            post.get("content", ""),
            post.get("authorProfileId", ""),
        )
        for post in state.get("posts", {}).values()
    }

    for item in items or []:
        if not isinstance(item, dict):
            continue
        created_at = item.get("createdAt") or now_utc().isoformat()
        content = str(item.get("content") or "").strip()
        if not content:
            continue
        dedupe_key = (created_at, content, profile_id)
        if dedupe_key in existing_keys:
            continue

        post_id = str(item.get("id") or f"post-{uuid.uuid4().hex[:10]}")
        if post_id in state.get("posts", {}):
            post_id = f"post-{uuid.uuid4().hex[:10]}"

        state["posts"][post_id] = {
            "id": post_id,
            "authorProfileId": profile_id,
            "createdAt": created_at,
            "content": content,
            "meta": str(item.get("meta") or "FitHub 本机恢复"),
            "media": [compact_media_item(media) for media in item.get("media", []) if isinstance(media, dict)],
            "likes": [],
            "comments": [],
            "checkin": deepcopy(item.get("checkin")) if isinstance(item.get("checkin"), dict) else None,
        }
        existing_keys.add(dedupe_key)
        restored += 1

    return restored


def native_device_label(source):
    return NATIVE_DEVICE_LABELS.get(str(source or "").strip().lower(), "健康设备")


def merge_device_labels(existing_labels, new_labels):
    merged = []
    for label in list(existing_labels or []) + list(new_labels or []):
        clean = str(label or "").strip()
        if clean and clean not in merged:
            merged.append(clean)
    return merged


def normalize_native_workout_kind(raw_kind):
    return str(raw_kind or "").strip().lower().replace("_", "").replace("-", "").replace(" ", "")


def resolve_native_workout_sport(workout):
    sport_id = str(workout.get("sportId") or "").strip()
    sport_label = str(workout.get("sportLabel") or workout.get("label") or "").strip()
    raw_kind = (
        workout.get("workoutType")
        or workout.get("activityType")
        or workout.get("type")
        or workout.get("activity")
        or ""
    )
    mapped = NATIVE_WORKOUT_SPORT_MAP.get(normalize_native_workout_kind(raw_kind))
    if mapped:
        return sport_id or mapped[0], sport_label or mapped[1]
    return sport_id or "strength", sport_label or "训练打卡"


def normalize_native_distance_km(workout):
    direct_distance = parse_optional_float(workout.get("distance"))
    if direct_distance is not None:
        return round(max(0, direct_distance), 2)
    distance_km = parse_optional_float(workout.get("distanceKm"))
    if distance_km is not None:
        return round(max(0, distance_km), 2)
    distance_m = parse_optional_float(workout.get("distanceMeters"))
    if distance_m is not None:
        return round(max(0, distance_m) / 1000, 2)
    return 0


def normalize_native_calories(workout):
    calories = (
        parse_optional_float(workout.get("calories"))
        or parse_optional_float(workout.get("activeEnergyBurned"))
        or parse_optional_float(workout.get("energy"))
    )
    if calories is None:
        return 0
    return int(round(max(0, calories)))


def normalize_native_duration_minutes(workout):
    direct_minutes = parse_optional_int(workout.get("duration") or workout.get("durationMinutes") or workout.get("minutes"))
    if direct_minutes and direct_minutes > 0:
        return direct_minutes

    seconds = parse_optional_float(workout.get("durationSeconds") or workout.get("elapsedSeconds"))
    if seconds and seconds > 0:
        return max(1, int(round(seconds / 60)))
    return 0


def normalize_native_workout_id(source, workout, started_at, duration):
    candidate = str(workout.get("externalId") or workout.get("id") or workout.get("uuid") or "").strip()
    if candidate:
        return candidate
    sport_id, _ = resolve_native_workout_sport(workout)
    start_key = started_at.isoformat() if started_at else "unknown"
    return f"{source}:{sport_id}:{start_key}:{duration}"


def build_native_checkin_payload(source, workout):
    duration = normalize_native_duration_minutes(workout)
    if duration <= 0:
        return None

    started_at = parse_optional_iso_datetime(workout.get("startedAt") or workout.get("startDate")) or now_utc()
    ended_at = parse_optional_iso_datetime(workout.get("endedAt") or workout.get("endDate")) or (started_at + timedelta(minutes=duration))
    sport_id, sport_label = resolve_native_workout_sport(workout)

    return {
        "id": f"checkin-{uuid.uuid4().hex[:10]}",
        "externalId": normalize_native_workout_id(source, workout, started_at, duration),
        "source": native_device_label(source),
        "sportId": sport_id,
        "sportLabel": sport_label,
        "duration": duration,
        "distance": normalize_native_distance_km(workout),
        "calories": normalize_native_calories(workout),
        "note": (workout.get("note") or "").strip(),
        "createdAt": ended_at.isoformat(),
        "startedAt": started_at.isoformat(),
        "endedAt": ended_at.isoformat(),
    }


def local_date_key(value=None):
    parsed = parse_optional_iso_datetime(value) if isinstance(value, str) else value
    current = parsed or now_utc()
    return current.astimezone(timezone(timedelta(hours=8))).strftime("%Y-%m-%d")


def ensure_health_history_entry(profile, date_key=None):
    history = profile.setdefault("healthHistory", [])
    target_date = str(date_key or local_date_key()).strip()
    target_id = f"health-{target_date}"
    for item in history:
        if str(item.get("id") or "") == target_id or str(item.get("date") or "") == target_date:
            item["id"] = target_id
            item["date"] = target_date
            item.setdefault("createdAt", now_utc().isoformat())
            return item

    entry = {
        "id": target_id,
        "date": target_date,
        "createdAt": now_utc().isoformat(),
        "updatedAt": now_utc().isoformat(),
        "totalMinutes": 0,
        "totalCalories": 0,
        "totalDistance": 0,
        "runDistance": 0,
        "walkDistance": 0,
        "cyclingDistance": 0,
        "yogaMinutes": 0,
        "stepCount": 0,
        "activeEnergyBurned": 0,
        "vo2Max": None,
        "restingHeartRate": None,
        "bodyFat": None,
        "bmi": None,
        "weightKg": None,
    }
    history.append(entry)
    return entry


def finalize_health_history(profile):
    history = profile.setdefault("healthHistory", [])
    history.sort(key=lambda item: (str(item.get("date") or ""), str(item.get("updatedAt") or item.get("createdAt") or "")), reverse=True)
    del history[180:]


def update_health_history_entry(profile, date_key=None, add=None, set_values=None):
    entry = ensure_health_history_entry(profile, date_key)
    add = add or {}
    set_values = set_values or {}

    for key, value in add.items():
        numeric = parse_optional_float(value)
        if numeric is None:
            continue
        entry[key] = round(float(entry.get(key) or 0) + numeric, 2)

    for key, value in set_values.items():
        if value is None:
            continue
        entry[key] = value

    bmi = calculate_bmi(profile.get("heightCm"), profile.get("weightKg"))
    if bmi is not None:
        entry["bmi"] = bmi
    if profile.get("weightKg") is not None:
        entry["weightKg"] = round(float(profile.get("weightKg")), 1)
    if profile.get("bodyFat") is not None:
        entry["bodyFat"] = round(float(profile.get("bodyFat")), 1)
    if profile.get("restingHeartRate") is not None:
        entry["restingHeartRate"] = int(profile.get("restingHeartRate"))

    entry["updatedAt"] = now_utc().isoformat()
    finalize_health_history(profile)
    return entry


def merge_snapshot_fields(existing_snapshot, updates):
    merged = dict(existing_snapshot or {})
    for key, value in (updates or {}).items():
        if value is None or value == "":
            continue
        merged[key] = value
    return merged


def record_checkin_health_metrics(profile, checkin):
    created_at = checkin.get("createdAt") or now_utc().isoformat()
    duration = max(0, parse_optional_int(checkin.get("duration")) or 0)
    calories = max(0, parse_optional_float(checkin.get("calories")) or 0)
    distance = max(0, parse_optional_float(checkin.get("distance")) or 0)
    sport_id = str(checkin.get("sportId") or "").strip()

    additive = {
        "totalMinutes": duration,
        "totalCalories": calories,
        "totalDistance": distance,
    }
    if sport_id in {"run", "treadmill", "trail-run", "outdoor-run"}:
        additive["runDistance"] = distance
    if sport_id in {"outdoor-walk", "walking", "hiking"}:
        additive["walkDistance"] = distance
    if sport_id in {"outdoor-cycling", "cycling", "indoor-cycling"}:
        additive["cyclingDistance"] = distance
    if sport_id in {"yoga", "pilates"}:
        additive["yogaMinutes"] = duration

    update_health_history_entry(profile, local_date_key(created_at), add=additive)


def synthesize_device_health_snapshot(profile, source):
    today_key = local_date_key()
    today_entry = ensure_health_history_entry(profile, today_key)
    today_minutes = max(0, parse_optional_int(today_entry.get("totalMinutes")) or 0)
    today_distance = max(0, parse_optional_float(today_entry.get("totalDistance")) or 0)
    today_calories = max(0, parse_optional_float(today_entry.get("totalCalories")) or 0)
    gender = profile.get("gender") or ""
    bmi = calculate_bmi(profile.get("heightCm"), profile.get("weightKg"))

    if source == "xiaomi-scale":
        return {
            "bodyFat": profile.get("bodyFat") or estimate_body_fat(gender, bmi),
            "weightKg": profile.get("weightKg"),
            "bmi": bmi,
        }

    base_steps = int(max(1800, 3200 + today_minutes * 115 + today_distance * 1150))
    active_energy = round(max(120, today_calories or (today_minutes * 6.2)), 1)
    resting_heart_rate = profile.get("restingHeartRate") or (58 if gender == "男" else 62)
    cardio_fitness = round(max(28, min(58, 42 + today_distance * 0.8 + today_minutes * 0.03 - max(0, (bmi or 22) - 23) * 0.6)), 1)

    return {
        "stepCount": base_steps,
        "activeEnergyBurned": active_energy,
        "restingHeartRate": int(resting_heart_rate),
        "vo2Max": cardio_fitness,
        "weightKg": profile.get("weightKg"),
        "bmi": bmi,
        "bodyFat": profile.get("bodyFat"),
    }


def apply_native_health_sync(state, session, payload):
    profile_id = payload.get("profileId") or session.get("currentActorProfileId")
    allowed, profile_id = session_manages_profile(state, session, profile_id)
    if not allowed:
        raise ValueError("请先登录自己的训练者身份，再同步真实设备数据。")

    profile = state["profiles"].get(profile_id)
    if not profile or profile.get("role") != "enthusiast":
        raise ValueError("当前只有健身爱好者身份支持真实健康数据同步。")

    source = str(payload.get("source") or "apple-healthkit").strip()
    source_label = native_device_label(source)
    device_name = str(payload.get("deviceName") or "").strip()
    devices = [source_label]
    if device_name:
        devices.append(device_name)
    for item in payload.get("devices", []):
        clean = str(item or "").strip()
        if clean:
            devices.append(clean)

    metrics = payload.get("metrics") or {}
    height_cm = parse_optional_int(metrics.get("heightCm") or metrics.get("height"))
    weight_kg = parse_optional_float(metrics.get("weightKg") or metrics.get("weight"))
    body_fat = parse_optional_float(metrics.get("bodyFat"))
    resting_heart_rate = parse_optional_int(metrics.get("restingHeartRate"))
    step_count = parse_optional_int(metrics.get("stepCount") or metrics.get("steps"))
    active_energy = parse_optional_float(metrics.get("activeEnergyBurned") or metrics.get("activeEnergy"))
    vo2_max = parse_optional_float(metrics.get("vo2Max") or metrics.get("maxOxygenUptake") or metrics.get("cardioFitness"))

    if height_cm and height_cm > 0:
        profile["heightCm"] = height_cm
    if weight_kg and weight_kg > 0:
        profile["weightKg"] = round(weight_kg, 1)
    if body_fat is not None and 0 < body_fat < 100:
        profile["bodyFat"] = round(body_fat, 1)
    elif profile.get("gender") and profile.get("heightCm") and profile.get("weightKg"):
        bmi = calculate_bmi(profile.get("heightCm"), profile.get("weightKg"))
        if bmi:
            profile["bodyFat"] = estimate_body_fat(profile.get("gender"), bmi)

    if resting_heart_rate and resting_heart_rate > 0:
        profile["restingHeartRate"] = resting_heart_rate

    profile["connectedDevices"] = merge_device_labels(profile.get("connectedDevices", []), devices)
    profile["healthSource"] = source_label
    profile["deviceSyncedAt"] = local_time_label()
    profile["healthSnapshot"] = merge_snapshot_fields(
        profile.get("healthSnapshot") or {},
        {
            "source": source_label,
            "deviceName": device_name,
            "bmi": calculate_bmi(profile.get("heightCm"), profile.get("weightKg")),
            "heightCm": profile.get("heightCm"),
            "weightKg": profile.get("weightKg"),
            "bodyFat": profile.get("bodyFat"),
            "restingHeartRate": profile.get("restingHeartRate"),
            "stepCount": step_count,
            "activeEnergyBurned": round(active_energy, 1) if active_energy is not None else None,
            "vo2Max": round(vo2_max, 1) if vo2_max is not None else None,
            "syncedAt": now_utc().isoformat(),
        },
    )
    update_health_history_entry(
        profile,
        local_date_key(),
        set_values={
            "stepCount": step_count,
            "activeEnergyBurned": round(active_energy, 1) if active_energy is not None else None,
            "vo2Max": round(vo2_max, 1) if vo2_max is not None else None,
        },
    )

    imported_workout_ids = set(profile.get("externalWorkoutIds", []))
    imported_count = 0

    for workout in payload.get("workouts", []):
        checkin = build_native_checkin_payload(source, workout or {})
        if not checkin or checkin["externalId"] in imported_workout_ids:
            continue

        imported_workout_ids.add(checkin["externalId"])
        profile.setdefault("checkins", []).insert(0, checkin)
        record_checkin_health_metrics(profile, checkin)
        post_id = f"post-{uuid.uuid4().hex[:10]}"
        state["posts"][post_id] = {
            "id": post_id,
            "authorProfileId": profile_id,
            "createdAt": checkin["createdAt"],
            "content": f"通过 {source_label} 同步了一次 {checkin['sportLabel']} 训练，持续 {checkin['duration']} 分钟，消耗 {checkin['calories']} kcal。",
            "meta": f"{source_label} · {profile.get('locationLabel', DEFAULT_POSITION['label'])}",
            "media": [],
            "likes": [],
            "comments": [],
            "checkin": deepcopy(checkin),
        }
        imported_count += 1

    profile["externalWorkoutIds"] = list(sorted(imported_workout_ids))[-400:]
    session["currentActorProfileId"] = profile_id

    response = bootstrap_response(state, session)
    response["nativeSyncSummary"] = {
        "source": source_label,
        "importedWorkoutCount": imported_count,
        "connectedDevices": profile.get("connectedDevices", []),
        "syncedAt": profile.get("deviceSyncedAt", ""),
    }
    return response


class FitHubHandler(BaseHTTPRequestHandler):
    server_version = "FitHubHTTP/0.1"

    def do_OPTIONS(self):
        parsed = urlparse(self.path)
        if parsed.path == "/healthz":
            self.send_response(HTTPStatus.NO_CONTENT)
            self._send_common_headers("text/plain; charset=utf-8")
            self.end_headers()
            return
        self.send_response(HTTPStatus.NO_CONTENT)
        self._send_common_headers("application/json; charset=utf-8")
        self.end_headers()

    def do_HEAD(self):
        parsed = urlparse(self.path)
        if parsed.path == "/healthz":
            self.send_response(HTTPStatus.OK)
            self._send_common_headers("text/plain; charset=utf-8")
            self.end_headers()
            return
        if parsed.path.startswith(f"{API_PREFIX}/") or parsed.path == f"{API_PREFIX}/bootstrap":
            self.send_response(HTTPStatus.METHOD_NOT_ALLOWED)
            self._send_common_headers("application/json; charset=utf-8")
            self.end_headers()
            return
        self._serve_static(parsed.path, head_only=True)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/healthz":
            encoded = b"ok"
            self.send_response(HTTPStatus.OK)
            self._send_common_headers("text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)
            return
        if parsed.path.startswith(f"{API_PREFIX}/") or parsed.path == f"{API_PREFIX}/bootstrap":
            self._handle_api_get(parsed)
            return
        self._serve_static(parsed.path)

    def do_POST(self):
        parsed = urlparse(self.path)
        if not (parsed.path.startswith(f"{API_PREFIX}/") or parsed.path == f"{API_PREFIX}/bootstrap"):
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        self._handle_api_post(parsed)

    def _send_common_headers(self, content_type):
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")

    def _read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw.decode("utf-8") or "{}")

    def _write_json(self, payload, status=HTTPStatus.OK):
        encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self._send_common_headers("application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _with_state(self, mutator):
        global STATE_CACHE
        with STORE_LOCK:
            if STATE_CACHE is None:
                STATE_CACHE = load_state()
            elif STATE_RUNTIME_META.get("loaded_from") == "local-fallback":
                refresh_state_cache_from_supabase()
            state = STATE_CACHE
            result = mutator(state)
            save_state(state)
            return result

    def _read_state(self, reader):
        global STATE_CACHE
        with STORE_LOCK:
            if STATE_CACHE is None:
                STATE_CACHE = load_state()
            elif STATE_RUNTIME_META.get("loaded_from") == "local-fallback":
                refresh_state_cache_from_supabase()
            return reader(STATE_CACHE)

    def _handle_api_get(self, parsed):
        if parsed.path == f"{API_PREFIX}/bootstrap":
            query = parse_qs(parsed.query)
            session_id = query.get("session_id", [None])[0]

            def action(state):
                session = ensure_session(state, session_id)
                reconcile_account_registry(state)
                normalize_session_profiles(state, session)
                return bootstrap_response(state, session)

            self._write_json(self._with_state(action))
            return
        if parsed.path == f"{API_PREFIX}/storage/status":
            query = parse_qs(parsed.query)
            include_remote = str(query.get("remote", [""])[0]).strip().lower() in {"1", "true", "yes"}

            def action(state):
                response = storage_runtime_status(state)
                if include_remote:
                    try:
                        response["remoteRows"] = supabase_state_rows_report()
                    except Exception as exc:
                        response["remoteRows"] = {
                            "reachable": False,
                            "error": str(exc),
                        }
                        response["status"] = "degraded"
                        response["ok"] = False
                        response.setdefault("warnings", []).append("Supabase 远端行诊断失败，请检查数据库或网络。")
                return response

            self._write_json(self._read_state(action))
            return
        if parsed.path == f"{API_PREFIX}/admin/moderation":
            query = parse_qs(parsed.query)
            if not moderation_admin_authorized(self.headers, query=query):
                self._write_json({"error": "没有权限查看审核后台。"}, status=HTTPStatus.FORBIDDEN)
                return

            self._write_json(self._read_state(build_moderation_dashboard))
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def _handle_api_post(self, parsed):
        payload = self._read_json()
        session_id = payload.get("sessionId")

        if parsed.path == f"{API_PREFIX}/auth/lookup-phone":
            def action(state):
                ensure_session(state, session_id)
                reconcile_account_registry(state)
                phone = normalize_phone(payload.get("phone"))
                if not phone:
                    raise ValueError("请输入注册时填写的手机号。")
                matches = serialize_phone_matches(state, phone)
                if not matches and restore_phone_identity_from_supabase(state, phone):
                    matches = serialize_phone_matches(state, phone)
                return {
                    "phone": phone,
                    "matches": matches,
                }

            try:
                self._write_json(self._with_state(action))
            except ValueError as exc:
                self._write_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return

        if parsed.path == f"{API_PREFIX}/auth/send-code":
            def action(state):
                session = ensure_session(state, session_id)
                reconcile_account_registry(state)
                phone = validate_phone_or_raise(payload.get("phone"))
                purpose = str(payload.get("purpose") or "login").strip() or "login"
                response = send_sms_code(state, session, phone, purpose)
                response["smsEnabled"] = sms_verification_enabled()
                return response

            try:
                self._write_json(self._with_state(action))
            except ValueError as exc:
                self._write_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return

        if parsed.path == f"{API_PREFIX}/auth/login":
            def action(state):
                session = ensure_session(state, session_id)
                reconcile_account_registry(state)
                role = str(payload.get("role") or "").strip()
                phone = normalize_phone(payload.get("phone"))
                account = find_account_by_token(state, payload.get("accountId"), payload.get("restoreToken"))

                if account:
                    preferred_role = role if role in {"enthusiast", "gym", "coach"} else ""
                    attach_account_to_session(state, session, account, preferred_role)
                    return bootstrap_response(state, session)

                if sms_verification_enabled():
                    verify_sms_code(state, session, phone, payload.get("verificationCode"))

                account = resolve_account_by_phone(state, phone)
                if not account and restore_phone_identity_from_supabase(state, phone):
                    account = resolve_account_by_phone(state, phone)
                if account:
                    preferred_role = role if role in {"enthusiast", "gym", "coach"} else ""
                    attach_account_to_session(state, session, account, preferred_role)
                    return bootstrap_response(state, session)

                if role not in {"enthusiast", "gym", "coach"}:
                    raise ValueError("请输入手机号后选择要登录的身份。")

                profile = None
                profile = find_profile_by_role_phone(state, role, phone)
                if not profile:
                    raise ValueError("没有找到这个身份，请先注册后再登录。")

                account = ensure_profile_account(state, profile, phone)
                attach_account_to_session(state, session, account, role)
                return bootstrap_response(state, session)

            try:
                self._write_json(self._with_state(action))
            except ValueError as exc:
                self._write_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return

        if parsed.path == f"{API_PREFIX}/auth/wechat-mini-login":
            def action(state):
                if not wechat_miniapp_login_enabled():
                    raise ValueError("微信小程序登录还没有开启。")
                session = ensure_session(state, session_id)
                reconcile_account_registry(state)
                login_info = exchange_wechat_miniapp_code(payload.get("code"), payload.get("devOpenId"))
                provider_identifier = login_info.get("unionid") or login_info.get("openid")
                account = find_account_by_identity_provider(state, "wechat", provider_identifier)
                if not account:
                    account = create_account_record("")
                    account["primaryProvider"] = "wechat"
                    ensure_account_registry(state)[account["id"]] = account
                bind_account_identity_provider(
                    account,
                    "wechat",
                    provider_identifier,
                    openid=login_info.get("openid", ""),
                    unionid=login_info.get("unionid", ""),
                    source=login_info.get("source", "wechat"),
                )
                attach_account_to_session(state, session, account, str(payload.get("role") or "").strip())
                response = bootstrap_response(state, session)
                response["wechatLogin"] = {
                    "ok": True,
                    "provider": login_info.get("source", "wechat"),
                    "hasProfiles": bool(session.get("managedProfileIds")),
                }
                return response

            try:
                self._write_json(self._with_state(action))
            except ValueError as exc:
                self._write_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return

        if parsed.path == f"{API_PREFIX}/auth/restore":
            def action(state):
                session = ensure_session(state, session_id)
                reconcile_account_registry(state)
                for account in payload.get("accounts", []):
                    item = account or {}
                    matched_account = find_account_by_token(state, item.get("accountId") or item.get("id"), item.get("restoreToken"))
                    if matched_account:
                        attach_account_to_session(state, session, matched_account, str(item.get("role") or "").strip())
                        continue

                    role = str(item.get("role") or "").strip()
                    phone = item.get("phone")
                    matched_account = resolve_account_by_phone(state, phone)
                    if not matched_account and restore_phone_identity_from_supabase(state, phone):
                        matched_account = resolve_account_by_phone(state, phone)
                    if matched_account:
                        preferred_role = role if role in {"enthusiast", "gym", "coach"} else ""
                        attach_account_to_session(state, session, matched_account, preferred_role)
                        continue
                    if role not in {"enthusiast", "gym", "coach"}:
                        continue
                    profile = find_profile_by_role_phone(state, role, phone)
                    if not profile:
                        continue
                    matched_account = ensure_profile_account(state, profile, phone)
                    attach_account_to_session(state, session, matched_account, role)

                selected_role = str(payload.get("selectedRole") or session["selectedRole"]).strip()
                if selected_role in {"enthusiast", "gym", "coach"}:
                    session["selectedRole"] = selected_role

                requested_profile_id = payload.get("currentActorProfileId")
                canonical_requested_profile_id = resolve_canonical_profile_id(state, requested_profile_id)
                if canonical_requested_profile_id in session["managedProfileIds"]:
                    session["currentActorProfileId"] = canonical_requested_profile_id
                else:
                    session["currentActorProfileId"] = None
                    for profile_id in session["managedProfileIds"]:
                        profile = state["profiles"].get(profile_id)
                        if profile and profile["role"] == session["selectedRole"]:
                            session["currentActorProfileId"] = profile_id
                            break
                    if not session["currentActorProfileId"] and session["managedProfileIds"]:
                        session["currentActorProfileId"] = session["managedProfileIds"][0]
                        first_profile = state["profiles"].get(session["currentActorProfileId"])
                        if first_profile:
                            session["selectedRole"] = first_profile["role"]

                return bootstrap_response(state, session)

            self._write_json(self._with_state(action))
            return

        if parsed.path == f"{API_PREFIX}/auth/logout":
            def action(state):
                session = ensure_session(state, session_id)
                session["managedProfileIds"] = []
                session["managedAccountIds"] = []
                session["currentActorProfileId"] = None
                session["selectedRole"] = "enthusiast"
                return bootstrap_response(state, session)

            self._write_json(self._with_state(action))
            return

        if parsed.path == f"{API_PREFIX}/auth/recover-local":
            def action(state):
                session = ensure_session(state, session_id)
                reconcile_account_registry(state)
                role = str(payload.get("role") or "").strip()
                profile_payload = payload.get("profile") or {}
                if role not in {"enthusiast", "gym", "coach"}:
                    raise ValueError("请选择要恢复的身份。")

                phone = profile_payload.get("phone") or payload.get("phone")
                if not normalize_phone(phone):
                    raise ValueError("本机缓存里没有可恢复的手机号。")

                existing_profile = find_profile_by_role_phone(state, role, phone)
                account = find_account_by_phone(state, phone, role)
                if not account and existing_profile:
                    account = ensure_profile_account(state, existing_profile, phone)
                if not account:
                    account = create_account_record(phone)
                    ensure_account_registry(state)[account["id"]] = account

                profile_data = build_profile_payload(role, profile_payload, existing_profile, session)
                profile_data["accountId"] = account["id"]
                state["profiles"][profile_data["id"]] = profile_data
                ensure_profile_account(state, profile_data, phone)

                restored_checkins = restore_cached_checkins(
                    profile_data,
                    payload.get("checkins") or profile_payload.get("checkins") or [],
                )
                restored_posts = restore_cached_posts(
                    state,
                    profile_data["id"],
                    payload.get("posts") or profile_payload.get("posts") or [],
                )

                attach_account_to_session(state, session, account, role)
                response = bootstrap_response(state, session)
                response["recoverySummary"] = {
                    "restoredProfileId": profile_data["id"],
                    "restoredPosts": restored_posts,
                    "restoredCheckins": restored_checkins,
                }
                return response

            try:
                self._write_json(self._with_state(action))
            except ValueError as exc:
                self._write_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return

        if parsed.path == f"{API_PREFIX}/session/select":
            def action(state):
                session = ensure_session(state, session_id)
                session["selectedRole"] = payload.get("selectedRole", session["selectedRole"])
                requested_profile_id = payload.get("currentActorProfileId")
                canonical_requested_profile_id = resolve_canonical_profile_id(state, requested_profile_id)
                if canonical_requested_profile_id in session["managedProfileIds"]:
                    session["currentActorProfileId"] = canonical_requested_profile_id
                else:
                    for profile_id in session["managedProfileIds"]:
                        profile = state["profiles"].get(profile_id)
                        if profile and profile["role"] == session["selectedRole"]:
                            session["currentActorProfileId"] = profile_id
                            break
                return bootstrap_response(state, session)
            self._write_json(self._with_state(action))
            return

        if parsed.path == f"{API_PREFIX}/session/location":
            def action(state):
                session = ensure_session(state, session_id)
                session["userPosition"] = payload.get("userPosition", session["userPosition"])
                session["locationStatus"] = payload.get("locationStatus", session["locationStatus"])
                return bootstrap_response(state, session)
            self._write_json(self._with_state(action))
            return

        if parsed.path == f"{API_PREFIX}/register":
            def action(state):
                session = ensure_session(state, session_id)
                reconcile_account_registry(state)
                role = payload["role"]
                phone = validate_phone_or_raise((payload.get("profile") or {}).get("phone"))
                if sms_verification_enabled() and not is_session_phone_verified(session, phone):
                    verify_sms_code(state, session, phone, payload.get("verificationCode"))
                existing_profile = None
                for profile_id in session["managedProfileIds"]:
                    profile = state["profiles"].get(profile_id)
                    if profile and profile["role"] == role:
                        existing_profile = profile
                        break
                if not existing_profile:
                    existing_profile = find_profile_by_role_phone(state, role, phone)
                account = None
                account_payload = payload.get("account") or {}
                account = find_account_by_token(state, account_payload.get("accountId") or account_payload.get("id"), account_payload.get("restoreToken"))
                if not account:
                    for profile_id in session["managedProfileIds"]:
                        managed_profile = state["profiles"].get(profile_id)
                        if not managed_profile:
                            continue
                        account = ensure_profile_account(state, managed_profile)
                        break
                if not account:
                    account = resolve_account_by_phone(state, phone)
                if not account and existing_profile:
                    account = ensure_profile_account(state, existing_profile, phone)
                if not account:
                    account = create_account_record(phone)
                    ensure_account_registry(state)[account["id"]] = account
                preferred_existing = state["profiles"].get((account.get("profilesByRole") or {}).get(role, ""))
                if preferred_existing:
                    existing_profile = preferred_existing
                payload["profile"]["phone"] = phone
                profile_data = build_profile_payload(role, payload["profile"], existing_profile, session)
                profile_data["accountId"] = account["id"]
                profile_data["phone"] = phone
                state["profiles"][profile_data["id"]] = profile_data
                ensure_profile_account(state, profile_data, phone)
                attach_account_to_session(state, session, account, role)
                return bootstrap_response(state, session)
            try:
                self._write_json(self._with_state(action))
            except ValueError as exc:
                self._write_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return

        if parsed.path == f"{API_PREFIX}/profile/preferences":
            def action(state):
                session = ensure_session(state, session_id)
                profile_id = payload.get("profileId") or session.get("currentActorProfileId")
                allowed, profile_id = session_manages_profile(state, session, profile_id)
                if not allowed:
                    raise ValueError("请先注册自己的训练者身份。")

                profile = state["profiles"].get(profile_id)
                if not profile or profile.get("role") != "enthusiast":
                    raise ValueError("只有健身爱好者身份支持设置常规运动项目。")

                favorite_sports = []
                for sport_id in payload.get("favoriteSports", []):
                    if isinstance(sport_id, str) and sport_id.strip() and sport_id not in favorite_sports:
                        favorite_sports.append(sport_id)
                if not favorite_sports:
                    raise ValueError("请至少选择一个常规运动项目。")

                profile["favoriteSports"] = favorite_sports[:6]
                session["currentActorProfileId"] = profile_id
                return bootstrap_response(state, session)

            try:
                self._write_json(self._with_state(action))
            except ValueError as exc:
                self._write_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return

        if parsed.path == f"{API_PREFIX}/health/device-sync":
            def action(state):
                session = ensure_session(state, session_id)
                profile_id = payload.get("profileId") or session.get("currentActorProfileId")
                allowed, profile_id = session_manages_profile(state, session, profile_id)
                if not allowed:
                    raise ValueError("请先注册自己的训练者身份。")

                profile = state["profiles"].get(profile_id)
                if not profile or profile.get("role") != "enthusiast":
                    raise ValueError("只有健身爱好者身份支持健康设备同步。")

                gender = profile.get("gender") or ""
                height_cm = parse_optional_int(profile.get("heightCm"))
                weight_kg = parse_optional_float(profile.get("weightKg"))
                if not gender or not height_cm or not weight_kg:
                    raise ValueError("请先完善性别、身高和体重，再同步健康设备。")

                source = payload.get("source") or "device"
                source_label = {
                    "apple-watch": "Apple Watch",
                    "xiaomi-watch": "小米手表",
                    "xiaomi-scale": "小米智能秤",
                }.get(source, "智能设备")
                bmi = calculate_bmi(height_cm, weight_kg)
                body_fat = estimate_body_fat(gender, bmi)

                connected_devices = list(profile.get("connectedDevices", []))
                if source_label not in connected_devices:
                    connected_devices.append(source_label)

                profile["connectedDevices"] = connected_devices
                profile["healthSource"] = source_label
                profile["deviceSyncedAt"] = local_time_label()
                if source == "xiaomi-scale":
                    profile["bodyFat"] = body_fat
                mock_snapshot = synthesize_device_health_snapshot(profile, source)
                profile["healthSnapshot"] = merge_snapshot_fields(
                    profile.get("healthSnapshot") or {},
                    {
                        "source": source_label,
                        "bmi": bmi,
                        "heightCm": height_cm,
                        "weightKg": weight_kg,
                        "bodyFat": profile.get("bodyFat"),
                        "restingHeartRate": mock_snapshot.get("restingHeartRate"),
                        "stepCount": mock_snapshot.get("stepCount"),
                        "activeEnergyBurned": mock_snapshot.get("activeEnergyBurned"),
                        "vo2Max": mock_snapshot.get("vo2Max"),
                        "syncedAt": now_utc().isoformat(),
                    },
                )
                update_health_history_entry(
                    profile,
                    local_date_key(),
                    set_values={
                        "stepCount": mock_snapshot.get("stepCount"),
                        "activeEnergyBurned": mock_snapshot.get("activeEnergyBurned"),
                        "vo2Max": mock_snapshot.get("vo2Max"),
                    },
                )
                session["currentActorProfileId"] = profile_id
                return bootstrap_response(state, session)

            try:
                self._write_json(self._with_state(action))
            except ValueError as exc:
                self._write_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return

        if parsed.path == f"{API_PREFIX}/health/native-sync":
            def action(state):
                session = ensure_session(state, session_id)
                return apply_native_health_sync(state, session, payload)

            try:
                self._write_json(self._with_state(action))
            except ValueError as exc:
                self._write_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return

        if parsed.path == f"{API_PREFIX}/follow/toggle":
            def action(state):
                session = ensure_session(state, session_id)
                requested_source_profile_id = payload.get("sourceProfileId") or session.get("currentActorProfileId")
                preferred_role = str(payload.get("selectedRole") or session.get("selectedRole") or "").strip()
                allowed, source_profile_id = ensure_session_identity(
                    state,
                    session,
                    preferred_role=preferred_role,
                    requested_profile_id=requested_source_profile_id,
                )
                target_profile_id = resolve_canonical_profile_id(state, payload["targetProfileId"])
                if not allowed or not source_profile_id:
                    raise ValueError("请先注册后再关注。")
                if not target_profile_id or target_profile_id not in state.get("profiles", {}):
                    raise ValueError("没有找到要关注的对象。")
                if target_profile_id == source_profile_id:
                    raise ValueError("不能关注当前身份自己。")
                if is_blocking_profile(state, source_profile_id, target_profile_id) or is_blocking_profile(state, target_profile_id, source_profile_id):
                    raise ValueError("当前无法关注这个用户，请先解除拉黑。")
                source_profile = state.get("profiles", {}).get(source_profile_id)
                if source_profile:
                    session["currentActorProfileId"] = source_profile_id
                    session["selectedRole"] = source_profile.get("role") or session.get("selectedRole") or "enthusiast"
                source_alias_ids = collect_profile_alias_ids(state, source_profile_id)
                target_alias_ids = collect_profile_alias_ids(state, target_profile_id)
                follows = state["follows"]
                existing = [
                    item
                    for item in follows
                    if item["sourceProfileId"] in source_alias_ids and item["targetProfileId"] in target_alias_ids
                ]
                desired_following = payload.get("desiredFollowing")
                if desired_following is None:
                    should_follow = not existing
                else:
                    should_follow = bool(desired_following)

                if existing and not should_follow:
                    for item in existing:
                        follows.remove(item)
                elif not existing and should_follow:
                    follows.append({"sourceProfileId": source_profile_id, "targetProfileId": target_profile_id, "createdAt": iso_at()})
                elif len(existing) > 1:
                    for item in existing[1:]:
                        follows.remove(item)
                if payload.get("compact"):
                    return compact_follow_response(state, session, source_profile_id, target_profile_id)
                return bootstrap_response(state, session)
            try:
                self._write_json(self._with_state(action))
            except ValueError as exc:
                self._write_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return

        if parsed.path == f"{API_PREFIX}/block/toggle":
            def action(state):
                session = ensure_session(state, session_id)
                requested_source_profile_id = payload.get("sourceProfileId") or session.get("currentActorProfileId")
                preferred_role = str(payload.get("selectedRole") or session.get("selectedRole") or "").strip()
                allowed, source_profile_id = ensure_session_identity(
                    state,
                    session,
                    preferred_role=preferred_role,
                    requested_profile_id=requested_source_profile_id,
                )
                target_profile_id = resolve_canonical_profile_id(state, payload.get("targetProfileId"))
                if not allowed or not source_profile_id:
                    raise ValueError("请先登录后再操作。")
                if not target_profile_id or target_profile_id not in state.get("profiles", {}):
                    raise ValueError("没有找到要拉黑的对象。")
                if target_profile_id == source_profile_id:
                    raise ValueError("不能拉黑当前身份自己。")

                source_profile = state.get("profiles", {}).get(source_profile_id)
                if source_profile:
                    session["currentActorProfileId"] = source_profile_id
                    session["selectedRole"] = source_profile.get("role") or session.get("selectedRole") or "enthusiast"

                source_alias_ids = collect_profile_alias_ids(state, source_profile_id)
                target_alias_ids = collect_profile_alias_ids(state, target_profile_id)
                existing = [
                    item for item in state.get("blocks", [])
                    if item.get("sourceProfileId") in source_alias_ids and item.get("targetProfileId") in target_alias_ids
                ]
                desired_blocked = payload.get("desiredBlocked")
                should_block = (not existing) if desired_blocked is None else bool(desired_blocked)

                if existing and not should_block:
                    state["blocks"] = [item for item in state.get("blocks", []) if item not in existing]
                elif not existing and should_block:
                    state.setdefault("blocks", []).append({
                        "sourceProfileId": source_profile_id,
                        "targetProfileId": target_profile_id,
                        "createdAt": iso_at(),
                    })
                    remove_relationship_between_profiles(state, source_profile_id, target_profile_id)
                elif len(existing) > 1:
                    state["blocks"] = [item for item in state.get("blocks", []) if item not in existing[1:]]

                normalize_blocks(state)
                normalize_follows(state)
                return bootstrap_response(state, session)
            try:
                self._write_json(self._with_state(action))
            except ValueError as exc:
                self._write_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return

        if parsed.path == f"{API_PREFIX}/auth/restore-follows":
            def action(state):
                session = ensure_session(state, session_id)
                profile_id = payload.get("profileId") or session.get("currentActorProfileId")
                allowed, profile_id = ensure_session_identity(
                    state,
                    session,
                    preferred_role="enthusiast",
                    requested_profile_id=profile_id,
                )
                if not allowed:
                    raise ValueError("请先登录原来的账号后再恢复关注。")

                target_profile_ids = canonicalize_profile_ids(state, payload.get("targetProfileIds", []))
                if not target_profile_ids:
                    response = bootstrap_response(state, session)
                    response["followRestoreSummary"] = {"restoredCount": 0}
                    return response

                existing_targets = get_follow_set(state, profile_id)
                restored_count = 0
                for target_profile_id in target_profile_ids:
                    if not target_profile_id or target_profile_id == profile_id:
                        continue
                    if target_profile_id not in state.get("profiles", {}):
                        continue
                    if target_profile_id in existing_targets:
                        continue
                    state["follows"].append({
                        "sourceProfileId": profile_id,
                        "targetProfileId": target_profile_id,
                        "createdAt": iso_at()
                    })
                    existing_targets.add(target_profile_id)
                    restored_count += 1

                normalize_follows(state)
                response = bootstrap_response(state, session)
                response["followRestoreSummary"] = {"restoredCount": restored_count}
                return response

            try:
                self._write_json(self._with_state(action))
            except ValueError as exc:
                self._write_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return

        if parsed.path == f"{API_PREFIX}/post/create":
            def action(state):
                session = ensure_session(state, session_id)
                allowed, profile_id = ensure_session_identity(
                    state,
                    session,
                    preferred_role=str(session.get("selectedRole") or "").strip(),
                    requested_profile_id=payload["profileId"],
                )
                if not allowed:
                    raise ValueError("只能用当前设备已注册的身份发布动态。")
                media_items = [deepcopy(item) for item in (payload.get("media") or []) if isinstance(item, dict)]
                post_id = f"post-{uuid.uuid4().hex[:10]}"
                content = payload.get("content") or "分享了一条新的动态。"
                post_record = {
                    "id": post_id,
                    "authorProfileId": profile_id,
                    "createdAt": iso_at(),
                    "content": content,
                    "meta": payload.get("meta") or state["profiles"][profile_id]["locationLabel"],
                    "media": media_items,
                    "likes": [],
                    "comments": [],
                }
                attach_text_moderation(state, post_record, content, "post", profile_id, "post-create")
                state["posts"][post_id] = post_record
                release_session_draft_media(session, media_items)
                session["currentActorProfileId"] = profile_id
                return bootstrap_response(state, session)
            try:
                self._write_json(self._with_state(action))
            except ValueError as exc:
                self._write_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return

        if parsed.path == f"{API_PREFIX}/media/upload":
            def action(state):
                session = ensure_session(state, session_id) if session_id else None
                try:
                    media = upload_media_asset(
                        payload.get("dataUrl"),
                        file_name=payload.get("fileName") or "upload",
                        category=str(payload.get("category") or "posts"),
                        asset_type=str(payload.get("assetType") or "image"),
                    )
                    thumbnail_data_url = payload.get("thumbnailDataUrl")
                    if thumbnail_data_url:
                        thumb_name = payload.get("thumbnailName") or payload.get("fileName") or "thumb.jpg"
                        thumb_media = upload_media_asset(
                            thumbnail_data_url,
                            file_name=thumb_name,
                            category=f"{str(payload.get('category') or 'posts')}-thumbs",
                            asset_type="image",
                            max_bytes_override=MEDIA_THUMB_LIMIT_BYTES,
                        )
                        media["thumbnailUrl"] = thumb_media.get("url", "")
                        media["thumbnailName"] = thumb_media.get("name", "")
                        media["thumbnailContentType"] = thumb_media.get("contentType", "")
                        media["thumbnailStorageProvider"] = thumb_media.get("storageProvider", "")
                        media["thumbnailStoragePath"] = thumb_media.get("storagePath", "")
                        media["thumbnailSizeBytes"] = thumb_media.get("sizeBytes", 0)
                    if session:
                        remember_session_draft_media(session, media)
                    return {"media": media, "config": runtime_config()}
                except Exception as exc:  # noqa: BLE001
                    storage_log(f"Media upload failed, falling back to inline storage: {exc}")
                    fallback = upload_media_asset(
                        payload.get("dataUrl"),
                        file_name=payload.get("fileName") or "upload",
                        category=str(payload.get("category") or "posts"),
                        asset_type=str(payload.get("assetType") or "image"),
                        force_inline=True,
                    )
                    thumbnail_data_url = payload.get("thumbnailDataUrl")
                    if thumbnail_data_url:
                        thumb_name = payload.get("thumbnailName") or payload.get("fileName") or "thumb.jpg"
                        thumb_fallback = upload_media_asset(
                            thumbnail_data_url,
                            file_name=thumb_name,
                            category=f"{str(payload.get('category') or 'posts')}-thumbs",
                            asset_type="image",
                            force_inline=True,
                            max_bytes_override=MEDIA_THUMB_LIMIT_BYTES,
                        )
                        fallback["thumbnailUrl"] = thumb_fallback.get("url", "")
                        fallback["thumbnailName"] = thumb_fallback.get("name", "")
                        fallback["thumbnailContentType"] = thumb_fallback.get("contentType", "")
                        fallback["thumbnailStorageProvider"] = thumb_fallback.get("storageProvider", "")
                        fallback["thumbnailStoragePath"] = thumb_fallback.get("storagePath", "")
                        fallback["thumbnailSizeBytes"] = thumb_fallback.get("sizeBytes", 0)
                    if session:
                        remember_session_draft_media(session, fallback)
                    return {"media": fallback, "config": runtime_config()}

            try:
                self._write_json(self._with_state(action))
            except ValueError as exc:
                self._write_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return

        if parsed.path == f"{API_PREFIX}/media/delete":
            def action(state):
                session = ensure_session(state, session_id)
                media_items = payload.get("items")
                if not isinstance(media_items, list):
                    single = payload.get("media")
                    media_items = [single] if isinstance(single, dict) else []
                deleted_paths = []
                for item in media_items:
                    if not isinstance(item, dict) or not session_allows_media_delete(session, item):
                        continue
                    deleted_paths.extend(delete_media_asset(item))
                release_session_draft_media(session, media_items)
                return {"deletedPaths": deleted_paths, "config": runtime_config()}

            self._write_json(self._with_state(action))
            return

        if parsed.path == f"{API_PREFIX}/media/maintenance":
            expected_token = MEDIA_MAINTENANCE_TOKEN
            provided_token = str(payload.get("token") or "").strip()
            auth_header = str(self.headers.get("Authorization") or "").strip()
            if auth_header.lower().startswith("bearer "):
                provided_token = auth_header[7:].strip()
            if not expected_token or provided_token != expected_token:
                self._write_json({"error": "没有权限执行媒体维护。"}, status=HTTPStatus.FORBIDDEN)
                return

            def action(state):
                return build_media_maintenance_report(
                    state,
                    stale_after_hours=int(payload.get("ageHours") or 24),
                    delete=bool(payload.get("delete")),
                )

            self._write_json(self._with_state(action))
            return

        if parsed.path == f"{API_PREFIX}/report/create":
            def action(state):
                session = ensure_session(state, session_id)
                reporter_id = session.get("currentActorProfileId")
                if not reporter_id:
                    raise ValueError("请先登录后再举报。")
                target_type = str(payload.get("targetType") or "").strip()
                target_id = str(payload.get("targetId") or "").strip()
                if target_type not in {"profile", "post", "comment", "message"}:
                    raise ValueError("举报对象类型不正确。")
                target = find_report_target(state, target_type, target_id)
                if not target:
                    raise ValueError("没有找到需要举报的内容。")
                reason = str(payload.get("reason") or "不适内容").strip()[:80]
                detail = str(payload.get("detail") or "").strip()[:500]
                reports = state.setdefault("reports", [])
                existing = next(
                    (
                        item
                        for item in reports
                        if item.get("reporterProfileId") == reporter_id
                        and item.get("targetType") == target_type
                        and item.get("targetId") == target["id"]
                        and item.get("status", "open") == "open"
                    ),
                    None,
                )
                if existing:
                    existing["reason"] = reason
                    existing["detail"] = detail
                    existing["updatedAt"] = iso_at()
                    report = existing
                else:
                    report = {
                        "id": f"report-{uuid.uuid4().hex[:10]}",
                        "reporterProfileId": reporter_id,
                        "targetType": target_type,
                        "targetId": target["id"],
                        "targetOwnerProfileId": target["ownerProfileId"],
                        "postId": target.get("postId", ""),
                        "threadId": target.get("threadId", ""),
                        "reason": reason,
                        "detail": detail,
                        "status": "open",
                        "createdAt": iso_at(),
                        "updatedAt": iso_at(),
                    }
                    reports.insert(0, report)
                    del reports[300:]
                excerpt = ""
                target_record = target.get("record") or {}
                if isinstance(target_record, dict):
                    excerpt = target_record.get("content") or target_record.get("text") or target_record.get("name") or ""
                queue_moderation_item(
                    state,
                    {
                        "type": target_type,
                        "targetId": target["id"],
                        "targetOwnerProfileId": target["ownerProfileId"],
                        "reporterProfileId": reporter_id,
                        "source": "user-report",
                        "flags": [reason],
                        "excerpt": excerpt or detail,
                    },
                )
                if payload.get("compact"):
                    return {"ok": True, "report": report}
                return bootstrap_response(state, session)

            try:
                self._write_json(self._with_state(action))
            except ValueError as exc:
                self._write_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return

        if parsed.path == f"{API_PREFIX}/admin/moderation/resolve":
            if not moderation_admin_authorized(self.headers, payload=payload):
                self._write_json({"error": "没有权限处理审核项。"}, status=HTTPStatus.FORBIDDEN)
                return

            def action(state):
                target_id = str(payload.get("id") or "").strip()
                target_kind = str(payload.get("kind") or "report").strip()
                status = str(payload.get("status") or "resolved").strip()
                if status not in {"resolved", "dismissed"}:
                    status = "resolved"
                collection_name = "moderationQueue" if target_kind == "queue" else "reports"
                collection = state.setdefault(collection_name, [])
                target = next((item for item in collection if item.get("id") == target_id), None)
                if not target:
                    raise ValueError("没有找到这个审核项。")
                target["status"] = status
                target["resolvedAt"] = iso_at()
                target["resolutionNote"] = str(payload.get("note") or "").strip()[:300]
                state.setdefault("adminActions", []).insert(
                    0,
                    {
                        "id": f"admin-action-{uuid.uuid4().hex[:10]}",
                        "kind": target_kind,
                        "targetId": target_id,
                        "status": status,
                        "createdAt": iso_at(),
                    },
                )
                del state["adminActions"][100:]
                return build_moderation_dashboard(state)

            try:
                self._write_json(self._with_state(action))
            except ValueError as exc:
                self._write_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return

        if parsed.path == f"{API_PREFIX}/checkin/create":
            def action(state):
                session = ensure_session(state, session_id)
                profile_id = payload.get("profileId") or session.get("currentActorProfileId")
                allowed, profile_id = ensure_session_identity(
                    state,
                    session,
                    preferred_role="enthusiast",
                    requested_profile_id=profile_id,
                )
                if not allowed:
                    raise ValueError("请先注册后再打卡。")
                profile = state["profiles"][profile_id]
                if profile.get("role") != "enthusiast":
                    raise ValueError("当前只有健身爱好者身份支持训练打卡。")

                duration = int(payload.get("duration") or 0)
                if duration <= 0:
                    raise ValueError("训练时长需要大于 0。")

                checkin = {
                    "id": f"checkin-{uuid.uuid4().hex[:10]}",
                    "sportId": payload.get("sportId") or "strength",
                    "sportLabel": payload.get("sportLabel") or "训练打卡",
                    "duration": duration,
                    "distance": payload.get("distance") or 0,
                    "calories": payload.get("calories") or 0,
                    "paceLabel": payload.get("paceLabel") or "",
                    "bestPaceLabel": payload.get("bestPaceLabel") or "",
                    "heartRateAvg": payload.get("heartRateAvg") or 0,
                    "elevationGain": payload.get("elevationGain") or 0,
                    "route": deepcopy(payload.get("route")) if isinstance(payload.get("route"), dict) else None,
                    "note": (payload.get("note") or "").strip(),
                    "createdAt": iso_at(),
                }
                profile.setdefault("checkins", []).insert(0, checkin)
                record_checkin_health_metrics(profile, checkin)

                post_id = f"post-{uuid.uuid4().hex[:10]}"
                state["posts"][post_id] = {
                    "id": post_id,
                    "authorProfileId": profile_id,
                    "createdAt": checkin["createdAt"],
                    "content": payload.get("content") or f"完成了一次 {checkin['sportLabel']} 打卡。",
                    "meta": f"训练打卡 · {profile.get('locationLabel', DEFAULT_POSITION['label'])}",
                    "media": [],
                    "likes": [],
                    "comments": [],
                    "checkin": deepcopy(checkin),
                }

                session["currentActorProfileId"] = profile_id
                return bootstrap_response(state, session)

            try:
                self._write_json(self._with_state(action))
            except ValueError as exc:
                self._write_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return

        if parsed.path == f"{API_PREFIX}/post/like":
            def action(state):
                session = ensure_session(state, session_id)
                actor = session.get("currentActorProfileId")
                if not actor:
                    raise ValueError("请先注册后再点赞。")
                post = state["posts"][payload["postId"]]
                likes = post.setdefault("likes", [])
                if actor in likes:
                    likes.remove(actor)
                else:
                    likes.append(actor)
                if payload.get("compact"):
                    return compact_post_interaction_response(state, session, post)
                return bootstrap_response(state, session)
            try:
                self._write_json(self._with_state(action))
            except ValueError as exc:
                self._write_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return

        if parsed.path == f"{API_PREFIX}/post/favorite-toggle":
            def action(state):
                session = ensure_session(state, session_id)
                actor = session.get("currentActorProfileId")
                if not actor:
                    raise ValueError("请先注册后再收藏。")
                post = state["posts"][payload["postId"]]
                favorites = state.setdefault("postFavorites", [])
                existing = next(
                    (
                        item
                        for item in favorites
                        if item.get("sourceProfileId") == actor and item.get("postId") == post["id"]
                    ),
                    None,
                )
                if existing:
                    favorites.remove(existing)
                else:
                    favorites.append(
                        {
                            "sourceProfileId": actor,
                            "postId": post["id"],
                            "createdAt": iso_at(),
                        }
                    )
                normalize_post_favorites(state)
                if payload.get("compact"):
                    return compact_post_interaction_response(state, session, post)
                return bootstrap_response(state, session)

            try:
                self._write_json(self._with_state(action))
            except ValueError as exc:
                self._write_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return

        if parsed.path == f"{API_PREFIX}/post/comment":
            def action(state):
                session = ensure_session(state, session_id)
                actor = session.get("currentActorProfileId")
                if not actor:
                    raise ValueError("请先注册后再评论。")
                text = (payload.get("text") or "").strip()
                if not text:
                    raise ValueError("评论内容不能为空。")
                post = state["posts"][payload["postId"]]
                comment = {
                    "id": f"comment-{uuid.uuid4().hex[:10]}",
                    "authorProfileId": actor,
                    "text": text,
                    "createdAt": iso_at(),
                }
                attach_text_moderation(state, comment, text, "comment", actor, "post-comment")
                post.setdefault("comments", []).append(comment)
                if payload.get("compact"):
                    return compact_post_interaction_response(state, session, post)
                return bootstrap_response(state, session)
            try:
                self._write_json(self._with_state(action))
            except ValueError as exc:
                self._write_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return

        if parsed.path == f"{API_PREFIX}/message/send":
            def action(state):
                session = ensure_session(state, session_id)
                actor = session.get("currentActorProfileId")
                target_profile_id = resolve_canonical_profile_id(state, payload.get("targetProfileId"))
                if not actor:
                    raise ValueError("请先注册后再发送私信。")
                if not target_profile_id or target_profile_id not in state.get("profiles", {}):
                    raise ValueError("没有找到私信对象。")
                if is_blocking_profile(state, actor, target_profile_id):
                    raise ValueError("你已拉黑对方，解除拉黑后才能继续私信。")
                if is_blocking_profile(state, target_profile_id, actor):
                    raise ValueError("对方暂不接收你的私信。")
                text = (payload.get("text") or "").strip()
                if not text:
                    raise ValueError("私信内容不能为空。")
                thread = find_or_create_thread(state, actor, target_profile_id)
                message = {
                    "id": f"msg-{uuid.uuid4().hex[:10]}",
                    "senderProfileId": actor,
                    "text": text,
                    "createdAt": iso_at(),
                }
                attach_text_moderation(state, message, text, "message", actor, "message-send")
                thread["messages"].append(message)
                if payload.get("compact"):
                    return compact_message_response(state, session, target_profile_id)
                return bootstrap_response(state, session)
            try:
                self._write_json(self._with_state(action))
            except ValueError as exc:
                self._write_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return

        if parsed.path == f"{API_PREFIX}/rate":
            def action(state):
                session = ensure_session(state, session_id)
                actor = session.get("currentActorProfileId")
                if not actor:
                    raise ValueError("请先注册后再评分。")
                target_profile = state["profiles"][payload["targetProfileId"]]
                score = int(payload.get("score", 0))
                if score < 1 or score > 5:
                    raise ValueError("评分需要 1 到 5 星。")
                text = (payload.get("text") or "").strip() or "刚刚完成评分。"
                reviews = target_profile.setdefault("reviews", [])
                reviews[:] = [item for item in reviews if item.get("authorProfileId") != actor]
                reviews.insert(
                    0,
                    {
                        "id": f"review-{uuid.uuid4().hex[:10]}",
                        "authorProfileId": actor,
                        "score": score,
                        "text": text,
                        "createdAt": iso_at(),
                    },
                )
                return bootstrap_response(state, session)
            try:
                self._write_json(self._with_state(action))
            except ValueError as exc:
                self._write_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return

        if parsed.path == f"{API_PREFIX}/availability/create":
            def action(state):
                session = ensure_session(state, session_id)
                requested_profile_id = resolve_canonical_profile_id(state, payload.get("profileId"))
                allowed, actor = ensure_session_identity(
                    state,
                    session,
                    preferred_role=str(session.get("selectedRole") or "").strip(),
                    requested_profile_id=requested_profile_id,
                )
                if not allowed or not actor:
                    raise ValueError("请先登录对应身份后再发布可预约时间。")
                profile = state["profiles"].get(actor)
                if not profile or profile.get("role") not in {"coach", "gym"}:
                    raise ValueError("只有健身教练和健身房可以发布可预约时间。")

                date_value = str(payload.get("date") or "").strip()
                time_value = str(payload.get("time") or "").strip()
                if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_value):
                    raise ValueError("请选择正确的预约日期。")
                if not re.fullmatch(r"\d{2}:\d{2}", time_value):
                    raise ValueError("请选择正确的预约时间。")
                duration_minutes = parse_optional_int(payload.get("durationMinutes")) or 60
                duration_minutes = min(240, max(30, duration_minutes))
                note = str(payload.get("note") or "").strip()[:80]

                profile.setdefault("availabilitySlots", []).insert(
                    0,
                    {
                        "id": f"slot-{uuid.uuid4().hex[:10]}",
                        "date": date_value,
                        "time": time_value,
                        "durationMinutes": duration_minutes,
                        "note": note,
                        "status": "open",
                        "createdAt": iso_at(),
                    },
                )
                return bootstrap_response(state, session)
            try:
                self._write_json(self._with_state(action))
            except ValueError as exc:
                self._write_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return

        if parsed.path == f"{API_PREFIX}/availability/delete":
            def action(state):
                session = ensure_session(state, session_id)
                requested_profile_id = resolve_canonical_profile_id(state, payload.get("profileId"))
                allowed, actor = ensure_session_identity(
                    state,
                    session,
                    preferred_role=str(session.get("selectedRole") or "").strip(),
                    requested_profile_id=requested_profile_id,
                )
                if not allowed or not actor:
                    raise ValueError("请先登录对应身份后再管理可预约时间。")
                profile = state["profiles"].get(actor)
                if not profile or profile.get("role") not in {"coach", "gym"}:
                    raise ValueError("只有健身教练和健身房可以管理可预约时间。")

                slot_id = str(payload.get("slotId") or "").strip()
                if not slot_id:
                    raise ValueError("请选择要取消的时间。")
                updated_slots = []
                removed = False
                for slot in profile.get("availabilitySlots", []) or []:
                    if str(slot.get("id") or "") != slot_id:
                        updated_slots.append(slot)
                        continue
                    removed = True
                    if str(slot.get("status") or "open") == "booked":
                        slot["status"] = "cancelled"
                        slot["cancelledAt"] = iso_at()
                        updated_slots.append(slot)
                if not removed:
                    raise ValueError("没有找到这个可预约时间。")
                profile["availabilitySlots"] = updated_slots
                return bootstrap_response(state, session)
            try:
                self._write_json(self._with_state(action))
            except ValueError as exc:
                self._write_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return

        if parsed.path == f"{API_PREFIX}/booking/create":
            def action(state):
                session = ensure_session(state, session_id)
                allowed, actor = ensure_session_identity(
                    state,
                    session,
                    preferred_role=str(session.get("selectedRole") or "").strip(),
                )
                if not allowed or not actor:
                    raise ValueError("请先注册后再预约。")
                target_profile_id = resolve_canonical_profile_id(state, payload.get("targetProfileId"))
                target_profile = state["profiles"].get(target_profile_id)
                if not target_profile:
                    raise ValueError("没有找到可预约对象。")
                plan = payload.get("plan") or (target_profile.get("pricingPlans") or [{}])[0]
                slot = None
                slot_id = str(payload.get("availabilitySlotId") or "").strip()
                if slot_id:
                    for candidate in target_profile.setdefault("availabilitySlots", []):
                        if str(candidate.get("id") or "") == slot_id:
                            slot = candidate
                            break
                    if not slot:
                        raise ValueError("这个可预约时间不存在，请刷新后再试。")
                    if str(slot.get("status") or "open") != "open":
                        raise ValueError("这个时间已被预约，请选择其他时间。")
                    slot["status"] = "booked"
                    slot["bookedByProfileId"] = actor
                    slot["bookedAt"] = iso_at()
                scheduled_date = slot.get("date") if slot else ""
                scheduled_time = slot.get("time") if slot else ""
                duration_minutes = parse_optional_int(slot.get("durationMinutes")) if slot else None
                state["bookings"].insert(
                    0,
                    {
                        "id": f"booking-{uuid.uuid4().hex[:10]}",
                        "createdAt": iso_at(),
                        "createdByProfileId": actor,
                        "targetProfileId": target_profile["id"],
                        "title": f"{target_profile['name']} · {plan.get('title', '立即预约')}",
                        "place": target_profile.get("locationLabel", DEFAULT_POSITION["label"]),
                        "time": payload.get("time") or (f"{scheduled_date} {scheduled_time}".strip() if slot else "待确认"),
                        "scheduledDate": scheduled_date,
                        "scheduledTime": scheduled_time,
                        "durationMinutes": duration_minutes,
                        "availabilitySlotId": slot_id,
                        "slotNote": slot.get("note") if slot else "",
                        "status": "已预约",
                        "action": "查看主页",
                        "price": plan.get("price", target_profile.get("price", "待确认")),
                    },
                )
                return bootstrap_response(state, session)
            try:
                self._write_json(self._with_state(action))
            except ValueError as exc:
                self._write_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return

        self.send_error(HTTPStatus.NOT_FOUND)

    def _serve_static(self, path, head_only=False):
        if path == "/":
            if URL_PREFIX:
                self.send_response(HTTPStatus.FOUND)
                self.send_header("Location", url_with_prefix("/"))
                self.end_headers()
                return
            relative = ""
        else:
            stripped = strip_url_prefix(path)
            if stripped is None:
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            relative = stripped.lstrip("/")

        if not relative:
            file_path = ROOT / "index.html"
        else:
            requested = Path(unquote(relative))
            safe_parts = [part for part in requested.parts if part not in ("..", "")]
            file_path = ROOT.joinpath(*safe_parts)

        if relative == "config.js":
            encoded_config = json.dumps(client_runtime_config(), ensure_ascii=False, indent=2)
            data = (
                "window.__FITHUB_CONFIG__ = Object.assign(\n"
                f"  {encoded_config},\n"
                "  window.__FITHUB_CONFIG__ || {}\n"
                ");\n"
            ).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self._send_common_headers("application/javascript; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            if not head_only:
                self.wfile.write(data)
            return

        if not file_path.exists() or file_path.is_dir():
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        content_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        data = file_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self._send_common_headers(content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        if not head_only:
            self.wfile.write(data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8010")))
    args = parser.parse_args()

    ensure_data_file()
    server = ThreadingHTTPServer((args.host, args.port), FitHubHandler)
    print(f"FitHub server listening on http://{args.host}:{args.port}{url_with_prefix('/')}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
