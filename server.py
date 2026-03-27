import argparse
import json
import mimetypes
import os
import threading
import uuid
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlparse


ROOT = Path(__file__).resolve().parent


def normalize_url_prefix(raw_value):
    value = (raw_value or "").strip()
    if not value or value == "/":
        return ""
    return "/" + value.strip("/")


URL_PREFIX = normalize_url_prefix(os.getenv("FITHUB_URL_PREFIX", "/fitness-app-prototype"))
DATA_DIR = Path(os.getenv("FITHUB_DATA_DIR", str(ROOT / "data"))).expanduser().resolve()
STATE_FILE = DATA_DIR / "shared_state.json"


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
MAX_INLINE_AVATAR_CHARS = 120_000
MAX_INLINE_MEDIA_CHARS = 180_000


def now_utc():
    return datetime.now(timezone.utc)


def iso_at(minutes_ago=0):
    return (now_utc() - timedelta(minutes=minutes_ago)).isoformat()


def data_uri_svg(svg):
    return f"data:image/svg+xml;charset=UTF-8,{quote(svg)}"


def demo_image(title, accent_a, accent_b):
    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="800" height="520" viewBox="0 0 800 520">
      <defs>
        <linearGradient id="g" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stop-color="{accent_a}"/>
          <stop offset="100%" stop-color="{accent_b}"/>
        </linearGradient>
      </defs>
      <rect width="800" height="520" rx="36" fill="url(#g)"/>
      <circle cx="664" cy="132" r="92" fill="rgba(255,255,255,0.16)"/>
      <circle cx="152" cy="392" r="116" fill="rgba(255,255,255,0.14)"/>
      <text x="60" y="246" fill="white" font-size="56" font-family="Arial, PingFang SC, sans-serif" font-weight="700">{title}</text>
      <text x="60" y="306" fill="rgba(255,255,255,0.88)" font-size="28" font-family="Arial, PingFang SC, sans-serif">FitHub Moments Demo</text>
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
      <ellipse cx="248" cy="78" rx="52" ry="36" fill="rgba(255,255,255,0.18)"/>
      <ellipse cx="74" cy="256" rx="96" ry="62" fill="rgba(255,255,255,0.10)"/>
      <circle cx="160" cy="116" r="58" fill="{skin}"/>
      <path d="M101 120c2-42 28-66 59-66 35 0 61 22 63 65-18-18-44-26-62-26-23 0-41 7-60 27z" fill="{hair}"/>
      <rect x="112" y="161" width="96" height="46" rx="20" fill="{skin}"/>
      <path d="M74 304c8-55 42-87 86-87 44 0 78 32 86 87z" fill="url(#shirt)"/>
      <circle cx="140" cy="119" r="4" fill="#38251c"/>
      <circle cx="180" cy="119" r="4" fill="#38251c"/>
      <path d="M143 146c8 8 26 8 34 0" fill="none" stroke="#bc7a63" stroke-width="5" stroke-linecap="round"/>
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
      </defs>
      <rect width="320" height="320" rx="52" fill="url(#bg)"/>
      <rect x="54" y="66" width="212" height="170" rx="22" fill="rgba(18,22,28,0.68)"/>
      <rect x="72" y="86" width="58" height="20" rx="10" fill="{accent}"/>
      <rect x="78" y="138" width="18" height="64" rx="8" fill="#d9dee7"/>
      <rect x="112" y="126" width="18" height="76" rx="8" fill="#d9dee7"/>
      <rect x="154" y="118" width="18" height="84" rx="8" fill="#d9dee7"/>
      <rect x="190" y="132" width="18" height="70" rx="8" fill="#d9dee7"/>
      <rect x="226" y="144" width="18" height="58" rx="8" fill="#d9dee7"/>
      <rect x="64" y="248" width="192" height="24" rx="12" fill="rgba(255,255,255,0.14)"/>
      <path d="M74 214h172" stroke="rgba(255,255,255,0.2)" stroke-width="6" stroke-linecap="round"/>
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
    if role == "gym":
        return gym_avatar()
    if role == "coach":
        return portrait_avatar(skin="#efc1a1", hair="#2f241d", shirt="#1f2125", bg_a="#dfe5ef", bg_b="#8d9bb3")
    return portrait_avatar(skin="#f4ccb2", hair="#674632", shirt="#f28c28", bg_a="#f7e0c6", bg_b="#d8a06f")


def compact_avatar_image(url, role):
    if not url:
        return default_avatar_for_role(role)
    if isinstance(url, str) and url.startswith("data:") and len(url) > MAX_INLINE_AVATAR_CHARS:
        return default_avatar_for_role(role)
    return url


def compact_media_item(item):
    url = item.get("url", "")
    if isinstance(url, str) and url.startswith("data:") and len(url) > MAX_INLINE_MEDIA_CHARS:
        label = "已压缩图片" if item.get("type") != "video" else "视频预览"
        return {
            "type": "image",
            "url": demo_image(label, "#d8d8d8", "#a7a7a7"),
            "name": item.get("name") or label,
        }
    return item


def sanitize_state(state):
    for profile in state.get("profiles", {}).values():
        profile["avatarImage"] = compact_avatar_image(profile.get("avatarImage"), profile.get("role", "enthusiast"))
    for post in state.get("posts", {}).values():
        post["media"] = [compact_media_item(item) for item in post.get("media", [])]
    return state


def make_profile(**kwargs):
    profile = {
        "id": kwargs["id"],
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
        "pricingPlans": kwargs.get("pricingPlans", []),
        "years": kwargs.get("years", ""),
        "certifications": kwargs.get("certifications", []),
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


def merge_demo_state(state):
    seed = initial_state()
    demo_profile_ids = set(seed["profiles"].keys())
    changed = False

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

    return changed


def make_post(post_id, author_profile_id, minutes_ago, content, meta, media=None, likes=None, comments=None):
    return {
        "id": post_id,
        "authorProfileId": author_profile_id,
        "createdAt": iso_at(minutes_ago),
        "content": content,
        "meta": meta,
        "media": media or [],
        "likes": likes or [],
        "comments": comments or [],
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
            "avatarImage": "https://images.pexels.com/photos/6046979/pexels-photo-6046979.png?auto=compress&cs=tinysrgb&fit=crop&w=160&h=160&dpr=1",
            "coverImage": "https://images.pexels.com/photos/6046979/pexels-photo-6046979.png?auto=compress&cs=tinysrgb&fit=crop&w=640&h=360&dpr=1",
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
            "avatarImage": "https://images.pexels.com/photos/35215412/pexels-photo-35215412.jpeg?auto=compress&cs=tinysrgb&fit=crop&w=160&h=160&dpr=1",
            "coverImage": "https://images.pexels.com/photos/35215412/pexels-photo-35215412.jpeg?auto=compress&cs=tinysrgb&fit=crop&w=640&h=360&dpr=1",
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
            "avatarImage": "https://images.pexels.com/photos/28455437/pexels-photo-28455437.jpeg?auto=compress&cs=tinysrgb&fit=crop&w=180&h=180&dpr=1",
            "coverImage": "https://images.pexels.com/photos/28455437/pexels-photo-28455437.jpeg?auto=compress&cs=tinysrgb&fit=crop&w=640&h=360&dpr=1",
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
            "avatarImage": "https://images.pexels.com/photos/14055666/pexels-photo-14055666.jpeg?auto=compress&cs=tinysrgb&fit=crop&w=180&h=180&dpr=1",
            "coverImage": "https://images.pexels.com/photos/14055666/pexels-photo-14055666.jpeg?auto=compress&cs=tinysrgb&fit=crop&w=640&h=360&dpr=1",
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
        avatarImage="https://images.pexels.com/photos/29149075/pexels-photo-29149075.jpeg?auto=compress&cs=tinysrgb&fit=crop&w=160&h=160&dpr=1",
        coverImage="https://images.pexels.com/photos/29149075/pexels-photo-29149075.jpeg?auto=compress&cs=tinysrgb&fit=crop&w=640&h=360&dpr=1",
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
        avatarImage="https://images.pexels.com/photos/4716817/pexels-photo-4716817.jpeg?auto=compress&cs=tinysrgb&fit=crop&w=160&h=160&dpr=1",
        coverImage="https://images.pexels.com/photos/4716817/pexels-photo-4716817.jpeg?auto=compress&cs=tinysrgb&fit=crop&w=640&h=360&dpr=1",
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
        avatarImage="https://images.pexels.com/photos/11327778/pexels-photo-11327778.jpeg?auto=compress&cs=tinysrgb&fit=crop&w=180&h=180&dpr=1",
        coverImage="https://images.pexels.com/photos/11327778/pexels-photo-11327778.jpeg?auto=compress&cs=tinysrgb&fit=crop&w=640&h=360&dpr=1",
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
        avatarImage="https://images.pexels.com/photos/20418608/pexels-photo-20418608.jpeg?auto=compress&cs=tinysrgb&fit=crop&w=180&h=180&dpr=1",
        coverImage="https://images.pexels.com/photos/20418608/pexels-photo-20418608.jpeg?auto=compress&cs=tinysrgb&fit=crop&w=640&h=360&dpr=1",
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
                {"type": "image", "url": "https://images.pexels.com/photos/6046979/pexels-photo-6046979.png?auto=compress&cs=tinysrgb&fit=crop&w=640&h=640&dpr=1", "name": "demo-gym-a-1.jpg"},
                {"type": "image", "url": "https://images.pexels.com/photos/6050745/pexels-photo-6050745.png?auto=compress&cs=tinysrgb&fit=crop&w=640&h=640&dpr=1", "name": "demo-gym-a-2.jpg"},
            ],
            likes=["enthusiast-demo-a", "enthusiast-demo-b"],
        ),
        "post-gym-b-1": make_post("post-gym-b-1", "gym-demo-b", 185, "模拟健身房 B 的周末亲子游泳课已开放预约。", "模拟动态 · 课程更新"),
        "post-gym-c-1": make_post(
            "post-gym-c-1",
            "gym-demo-c",
            75,
            "海景跑步区今晚延长到 23:30，适合测试夜间训练场景。",
            "模拟动态 · 夜场开放",
            media=[{"type": "image", "url": "https://images.pexels.com/photos/29149075/pexels-photo-29149075.jpeg?auto=compress&cs=tinysrgb&fit=crop&w=640&h=640&dpr=1", "name": "demo-gym-c.jpg"}],
            likes=["enthusiast-demo-a"],
        ),
        "post-gym-d-1": make_post(
            "post-gym-d-1",
            "gym-demo-d",
            160,
            "自由重量区新调了灯光和动线，方便测试真实门店展示效果。",
            "模拟动态 · 场馆升级",
            media=[{"type": "image", "url": "https://images.pexels.com/photos/4716817/pexels-photo-4716817.jpeg?auto=compress&cs=tinysrgb&fit=crop&w=640&h=640&dpr=1", "name": "demo-gym-d.jpg"}],
        ),
        "post-coach-a-1": make_post("post-coach-a-1", "coach-demo-a", 30, "模拟教练 A 今晚开放两个私教档期，方便测试即时预约。", "模拟动态 · 即时空闲", likes=["enthusiast-demo-a"]),
        "post-coach-a-2": make_post(
            "post-coach-a-2",
            "coach-demo-a",
            24 * 60,
            "整理了一份模拟学员常见动作错误清单。",
            "模拟动态 · 训练干货",
            media=[{"type": "image", "url": "https://images.pexels.com/photos/28455437/pexels-photo-28455437.jpeg?auto=compress&cs=tinysrgb&fit=crop&w=640&h=640&dpr=1", "name": "demo-coach-a.jpg"}],
            comments=[{"id": "comment-coach-a-1", "authorProfileId": "enthusiast-demo-a", "text": "这个清单很实用，已收藏。", "createdAt": iso_at(20 * 60)}],
        ),
        "post-coach-b-1": make_post("post-coach-b-1", "coach-demo-b", 6 * 60, "今天新增了两个康复评估时段，可以直接预约。", "模拟动态 · 档期开放"),
        "post-coach-c-1": make_post("post-coach-c-1", "coach-demo-c", 45, "本周新开了一组 4 人力量训练营，方便测试多种定价模式。", "模拟动态 · 训练营上新", likes=["enthusiast-demo-a"]),
        "post-coach-d-1": make_post("post-coach-d-1", "coach-demo-d", 120, "新增了 20:30 的晚间塑形档期，方便测试即时预约和私信咨询。", "模拟动态 · 晚间时段"),
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
        "bookings": bookings,
        "threads": threads,
        "sessions": {},
    }


def ensure_data_file():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not STATE_FILE.exists():
        STATE_FILE.write_text(json.dumps(initial_state(), ensure_ascii=False, indent=2), encoding="utf-8")


def load_state():
    ensure_data_file()
    with STATE_FILE.open("r", encoding="utf-8") as handle:
        state = sanitize_state(json.load(handle))
    if merge_demo_state(state):
        save_state(state)
    return sanitize_state(state)


def save_state(state):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with STATE_FILE.open("w", encoding="utf-8") as handle:
        json.dump(state, handle, ensure_ascii=False, indent=2)


def create_session_record():
    return {
        "id": f"session-{uuid.uuid4().hex[:12]}",
        "selectedRole": "enthusiast",
        "managedProfileIds": [],
        "currentActorProfileId": None,
        "userPosition": deepcopy(DEFAULT_POSITION),
        "locationStatus": DEFAULT_LOCATION_STATUS,
        "createdAt": iso_at(),
    }


def ensure_session(state, session_id=None):
    sessions = state.setdefault("sessions", {})
    if session_id and session_id in sessions:
        return sessions[session_id]
    session = create_session_record()
    sessions[session["id"]] = session
    return session


def author_name(state, profile_id):
    profile = state["profiles"].get(profile_id)
    return profile["name"] if profile else "平台用户"


def profile_posts(state, profile_id):
    posts = [post for post in state["posts"].values() if post["authorProfileId"] == profile_id]
    return sorted(posts, key=lambda item: item["createdAt"], reverse=True)


def get_follow_set(state, current_actor_profile_id):
    if not current_actor_profile_id:
        return set()
    return {
        item["targetProfileId"]
        for item in state["follows"]
        if item["sourceProfileId"] == current_actor_profile_id
    }


def follower_count(state, profile_id):
    return sum(1 for item in state["follows"] if item["targetProfileId"] == profile_id)


def following_count(state, profile_id):
    return sum(1 for item in state["follows"] if item["sourceProfileId"] == profile_id)


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


def serialize_post(state, post, current_actor_profile_id):
    return {
        "id": post["id"],
        "authorProfileId": post["authorProfileId"],
        "createdAt": post["createdAt"],
        "time": relative_time_label(post["createdAt"]),
        "content": post["content"],
        "meta": post["meta"],
        "media": [compact_media_item(item) for item in post.get("media", [])],
        "likeCount": len(post.get("likes", [])),
        "likedByCurrentActor": current_actor_profile_id in post.get("likes", []),
        "comments": [serialize_comment(state, item) for item in sorted(post.get("comments", []), key=lambda value: value["createdAt"])],
    }


def serialize_profile(state, profile_id, current_actor_profile_id):
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
    return profile


def serialize_bookings(state, session):
    managed = set(session["managedProfileIds"])
    bookings = [
        item for item in state["bookings"]
        if item["createdByProfileId"] in managed
    ]
    bookings.sort(key=lambda item: item["createdAt"], reverse=True)
    return bookings


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
    threads = []
    for thread in state["threads"]:
        if current_actor_profile_id not in thread["participants"]:
            continue
        other_profile_id = next((item for item in thread["participants"] if item != current_actor_profile_id), None)
        other_profile = state["profiles"].get(other_profile_id)
        messages = [
            {
                "id": message["id"],
                "senderProfileId": message["senderProfileId"],
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


def bootstrap_response(state, session):
    current_actor_profile_id = session.get("currentActorProfileId")
    profiles = [serialize_profile(state, profile_id, current_actor_profile_id) for profile_id in state["profiles"]]
    return {
        "session": {
            "id": session["id"],
            "selectedRole": session["selectedRole"],
            "managedProfileIds": session["managedProfileIds"],
            "currentActorProfileId": current_actor_profile_id,
            "userPosition": session["userPosition"],
            "locationStatus": session["locationStatus"],
        },
        "profiles": profiles,
        "followSet": sorted(get_follow_set(state, current_actor_profile_id)),
        "bookings": serialize_bookings(state, session),
        "threads": serialize_threads(state, current_actor_profile_id),
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
            "owner_session_id": session["id"],
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
            "reviews": (existing_profile or {}).get("reviews", []),
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
            "owner_session_id": session["id"],
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
            "certifications": certifications,
            "pricingPlans": payload.get("pricingPlans") or (existing_profile or {}).get("pricingPlans") or [
                {"title": "私教课程", "detail": "一对一训练服务", "price": payload.get("price") or "¥220/小时"}
            ],
            "reviews": (existing_profile or {}).get("reviews", []),
            "listed": True,
            "createdAt": (existing_profile or {}).get("createdAt", iso_at()),
        }

    name = payload.get("name") or (existing_profile or {}).get("name") or "新用户"
    level = payload.get("level") or (existing_profile or {}).get("level") or "新手入门"
    goal = payload.get("goal") or (existing_profile or {}).get("goal") or "保持规律训练"
    return {
        **(existing_profile or {}),
        "id": (existing_profile or {}).get("id", f"enthusiast-{uuid.uuid4().hex[:8]}"),
        "owner_session_id": session["id"],
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
        "reviews": [],
        "listed": True,
        "createdAt": (existing_profile or {}).get("createdAt", iso_at()),
    }


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
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
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
            state = STATE_CACHE
            result = mutator(state)
            save_state(state)
            return result

    def _handle_api_get(self, parsed):
        if parsed.path == f"{API_PREFIX}/bootstrap":
            query = parse_qs(parsed.query)
            session_id = query.get("session_id", [None])[0]

            def action(state):
                session = ensure_session(state, session_id)
                return bootstrap_response(state, session)

            self._write_json(self._with_state(action))
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def _handle_api_post(self, parsed):
        payload = self._read_json()
        session_id = payload.get("sessionId")

        if parsed.path == f"{API_PREFIX}/session/select":
            def action(state):
                session = ensure_session(state, session_id)
                session["selectedRole"] = payload.get("selectedRole", session["selectedRole"])
                requested_profile_id = payload.get("currentActorProfileId")
                if requested_profile_id in session["managedProfileIds"]:
                    session["currentActorProfileId"] = requested_profile_id
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
                role = payload["role"]
                existing_profile = None
                for profile_id in session["managedProfileIds"]:
                    profile = state["profiles"].get(profile_id)
                    if profile and profile["role"] == role:
                        existing_profile = profile
                        break
                profile_data = build_profile_payload(role, payload["profile"], existing_profile, session)
                state["profiles"][profile_data["id"]] = profile_data
                if not existing_profile:
                    session["managedProfileIds"].append(profile_data["id"])
                    seed_post = make_post(
                        f"post-{profile_data['id']}-seed",
                        profile_data["id"],
                        0,
                        f"{profile_data['name']} 已加入 FitHub，开始体验健身圈互动。",
                        "入驻动态" if role in {"gym", "coach"} else "加入社区",
                    )
                    state["posts"][seed_post["id"]] = seed_post
                session["selectedRole"] = role
                session["currentActorProfileId"] = profile_data["id"]
                return bootstrap_response(state, session)
            self._write_json(self._with_state(action))
            return

        if parsed.path == f"{API_PREFIX}/follow/toggle":
            def action(state):
                session = ensure_session(state, session_id)
                source_profile_id = session.get("currentActorProfileId")
                target_profile_id = payload["targetProfileId"]
                if not source_profile_id:
                    raise ValueError("请先注册后再关注。")
                follows = state["follows"]
                existing = next((item for item in follows if item["sourceProfileId"] == source_profile_id and item["targetProfileId"] == target_profile_id), None)
                if existing:
                    follows.remove(existing)
                else:
                    follows.append({"sourceProfileId": source_profile_id, "targetProfileId": target_profile_id, "createdAt": iso_at()})
                return bootstrap_response(state, session)
            try:
                self._write_json(self._with_state(action))
            except ValueError as exc:
                self._write_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return

        if parsed.path == f"{API_PREFIX}/post/create":
            def action(state):
                session = ensure_session(state, session_id)
                profile_id = payload["profileId"]
                if profile_id not in session["managedProfileIds"]:
                    raise ValueError("只能用当前设备已注册的身份发布动态。")
                post_id = f"post-{uuid.uuid4().hex[:10]}"
                state["posts"][post_id] = {
                    "id": post_id,
                    "authorProfileId": profile_id,
                    "createdAt": iso_at(),
                    "content": payload.get("content") or "分享了一条新的动态。",
                    "meta": payload.get("meta") or state["profiles"][profile_id]["locationLabel"],
                    "media": payload.get("media", []),
                    "likes": [],
                    "comments": [],
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
                post.setdefault("comments", []).append(
                    {
                        "id": f"comment-{uuid.uuid4().hex[:10]}",
                        "authorProfileId": actor,
                        "text": text,
                        "createdAt": iso_at(),
                    }
                )
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
                target_profile_id = payload["targetProfileId"]
                if not actor:
                    raise ValueError("请先注册后再发送私信。")
                if target_profile_id not in get_follow_set(state, actor):
                    raise ValueError("请先关注对方，再发送私信。")
                text = (payload.get("text") or "").strip()
                if not text:
                    raise ValueError("私信内容不能为空。")
                thread = find_or_create_thread(state, actor, target_profile_id)
                thread["messages"].append(
                    {
                        "id": f"msg-{uuid.uuid4().hex[:10]}",
                        "senderProfileId": actor,
                        "text": text,
                        "createdAt": iso_at(),
                    }
                )
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

        if parsed.path == f"{API_PREFIX}/booking/create":
            def action(state):
                session = ensure_session(state, session_id)
                actor = session.get("currentActorProfileId")
                if not actor:
                    raise ValueError("请先注册后再预约。")
                target_profile = state["profiles"][payload["targetProfileId"]]
                plan = payload.get("plan") or (target_profile.get("pricingPlans") or [{}])[0]
                state["bookings"].insert(
                    0,
                    {
                        "id": f"booking-{uuid.uuid4().hex[:10]}",
                        "createdAt": iso_at(),
                        "createdByProfileId": actor,
                        "targetProfileId": target_profile["id"],
                        "title": f"{target_profile['name']} · {plan.get('title', '立即预约')}",
                        "place": target_profile.get("locationLabel", DEFAULT_POSITION["label"]),
                        "time": payload.get("time") or "待确认",
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
