#!/usr/bin/env python3
"""Run a write-path acceptance test against a production FitHub API.

The script uses one dedicated test phone number and idempotent operations where
possible. It is intended for final Tencent Cloud/domain acceptance, not for
every local development run.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, NamedTuple


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import deploy_smoke


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BACKEND = "https://fithub-app-1btg.onrender.com"
DEFAULT_PHONE = "13215929999"


class AcceptanceResult(NamedTuple):
    profile_id: str
    target_profile_id: str
    post_id: str
    booking_count: int
    thread_count: int


def read_default_backend() -> str:
    try:
        text = (ROOT / "config.js").read_text(encoding="utf-8")
        match = re.search(r"apiOrigin\s*:\s*[\"']([^\"']+)[\"']", text)
        if match:
            return match.group(1).strip().rstrip("/")
    except OSError:
        pass
    return DEFAULT_BACKEND


def normalize_backend_url(value: str) -> str:
    raw = str(value or "").strip().rstrip("/")
    parsed = urllib.parse.urlparse(raw)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("backend URL must be a complete URL, for example https://api.example.cn")
    return raw


def normalize_phone(value: str) -> str:
    digits = re.sub(r"\D+", "", str(value or ""))
    if digits.startswith("86") and len(digits) == 13:
        digits = digits[2:]
    if not re.fullmatch(r"1\d{10}", digits):
        raise ValueError("phone must be a mainland China mobile number.")
    return digits


class ApiSession:
    def __init__(self, backend_url: str, *, timeout: int = 20):
        self.backend_url = backend_url.rstrip("/")
        self.timeout = timeout
        self.session_id = ""

    def request(self, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = None
        headers = {"User-Agent": "FitHubProductionWriteAcceptance/1.0", "Connection": "close"}
        if body is not None:
            payload_body = dict(body)
            if self.session_id:
                payload_body.setdefault("sessionId", self.session_id)
            payload = json.dumps(payload_body, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json; charset=utf-8"
        request = urllib.request.Request(f"{self.backend_url}{path}", data=payload, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                parsed = json.loads(response.read().decode("utf-8") or "{}")
                if isinstance(parsed, dict):
                    session = parsed.get("session") or {}
                    if session.get("id"):
                        self.session_id = str(session["id"])
                return parsed
        except urllib.error.HTTPError as exc:
            body_text = exc.read().decode("utf-8", errors="replace")
            try:
                parsed = json.loads(body_text or "{}")
            except json.JSONDecodeError:
                parsed = {"raw": body_text}
            raise RuntimeError(f"{method} {path} failed with {exc.code}: {parsed}") from exc

    def bootstrap(self) -> dict[str, Any]:
        suffix = f"?session_id={urllib.parse.quote(self.session_id)}" if self.session_id else ""
        payload = self.request("GET", f"/api/bootstrap{suffix}")
        session = payload.get("session") or {}
        if session.get("id"):
            self.session_id = str(session["id"])
        return payload

    def post(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        return self.request("POST", path, body)


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def current_profile(payload: dict[str, Any]) -> dict[str, Any]:
    current_id = (payload.get("session") or {}).get("currentActorProfileId")
    for profile in payload.get("profiles") or []:
        if profile.get("id") == current_id:
            return profile
    raise RuntimeError(f"current profile {current_id or '<empty>'} not found")


def find_target_profile(payload: dict[str, Any], actor_id: str) -> dict[str, Any]:
    preferred_roles = ("coach", "gym", "enthusiast")
    profiles = payload.get("profiles") or []
    for role in preferred_roles:
        for profile in profiles:
            if profile.get("id") != actor_id and profile.get("role") == role and profile.get("listed"):
                return profile
    for profile in profiles:
        if profile.get("id") != actor_id:
            return profile
    raise RuntimeError("No target profile is available for follow/message/booking acceptance.")


def find_profile_post(payload: dict[str, Any], profile_id: str, marker: str) -> dict[str, Any]:
    for profile in payload.get("profiles") or []:
        if profile.get("id") != profile_id:
            continue
        for post in profile.get("posts") or []:
            if marker in str(post.get("content") or ""):
                return post
    raise RuntimeError("Created acceptance post was not returned in profile timeline.")


def send_code_and_resolve(
    client: ApiSession,
    *,
    phone: str,
    purpose: str,
    verification_code: str = "",
    allow_debug_code: bool = True,
) -> str:
    payload = client.post("/api/auth/send-code", {"phone": phone, "purpose": purpose})
    if verification_code:
        return verification_code.strip()
    debug_code = str(payload.get("debugCode") or "").strip()
    if allow_debug_code and debug_code:
        return debug_code
    raise RuntimeError(
        f"SMS code was sent for {purpose}. Re-run with --verification-code / --login-verification-code "
        "after entering the code received by the dedicated acceptance phone."
    )


def ensure_storage_ready(backend_url: str, *, allow_local_storage: bool, min_real_profiles: int) -> None:
    code, storage, elapsed = deploy_smoke.fetch_json(
        f"{backend_url}/api/storage/status?remote=1",
        attempts=2,
        timeout=30,
        delay=2,
    )
    ensure(code == 200, f"storage status returned {code}")
    deploy_smoke.validate_storage_status(
        storage,
        allow_local_storage=allow_local_storage,
        min_real_profiles=min_real_profiles,
    )
    print(f"  OK storage write readiness ({elapsed:.2f}s)")


def run_acceptance(
    *,
    backend_url: str,
    phone: str = DEFAULT_PHONE,
    verification_code: str = "",
    login_verification_code: str = "",
    allow_debug_code: bool = True,
    allow_local_storage: bool = False,
    min_real_profiles: int = 1,
) -> AcceptanceResult:
    backend_url = normalize_backend_url(backend_url)
    phone = normalize_phone(phone)
    ensure_storage_ready(backend_url, allow_local_storage=allow_local_storage, min_real_profiles=min_real_profiles)

    client = ApiSession(backend_url)
    client.bootstrap()
    register_code = send_code_and_resolve(
        client,
        phone=phone,
        purpose="register",
        verification_code=verification_code,
        allow_debug_code=allow_debug_code,
    )
    stamp = time.strftime("%m%d%H%M")
    payload = client.post(
        "/api/register",
        {
            "role": "enthusiast",
            "verificationCode": register_code,
            "profile": {
                "name": f"国内验收用户{phone[-4:]}",
                "phone": phone,
                "gender": "男",
                "heightCm": 175,
                "weightKg": 68,
                "level": "生产验收",
                "goal": "验证国内部署账号与互动持久化",
                "intro": "FitHub 国内生产写入验收账号。",
            },
        },
    )
    actor = current_profile(payload)
    actor_id = actor["id"]
    target = find_target_profile(payload, actor_id)
    target_id = target["id"]

    print(f"  Registered/logged actor: {actor.get('name')} ({actor_id})")
    print(f"  Acceptance target: {target.get('name')} ({target_id})")

    followed = client.post(
        "/api/follow/toggle",
        {
            "targetProfileId": target_id,
            "desiredFollowing": True,
            "compact": True,
        },
    )
    follow_info = followed.get("follow") or {}
    ensure(follow_info.get("following") is True or target_id in (follow_info.get("followSet") or []), "follow did not persist")

    marker = f"FitHub 国内生产验收 {stamp}"
    post_payload = client.post(
        "/api/post/create",
        {
            "profileId": actor_id,
            "content": marker,
            "meta": "生产验收 · 写入链路",
            "media": [],
        },
    )
    post = find_profile_post(post_payload, actor_id, marker)
    post_id = post["id"]

    liked = client.post("/api/post/like", {"postId": post_id, "compact": True})
    ensure((liked.get("post") or {}).get("likedByCurrentActor") is True, "like did not become active")
    favorited = client.post("/api/post/favorite-toggle", {"postId": post_id, "compact": True})
    ensure(post_id in favorited.get("favoritePostIds", []), "favorite did not become active")
    commented = client.post("/api/post/comment", {"postId": post_id, "text": "生产验收评论", "compact": True})
    ensure(len((commented.get("post") or {}).get("comments") or []) >= 1, "comment did not persist")

    message_payload = client.post(
        "/api/message/send",
        {
            "targetProfileId": target_id,
            "text": f"生产验收私信 {stamp}",
            "compact": True,
        },
    )
    ensure(message_payload.get("thread"), "message thread was not returned")

    booking_payload = client.post(
        "/api/booking/create",
        {
            "targetProfileId": target_id,
            "time": "生产验收待确认",
        },
    )
    ensure(any(item.get("targetProfileId") == target_id for item in booking_payload.get("bookings") or []), "booking did not persist")

    fresh = ApiSession(backend_url)
    fresh.bootstrap()
    login_code = send_code_and_resolve(
        fresh,
        phone=phone,
        purpose="login",
        verification_code=login_verification_code,
        allow_debug_code=allow_debug_code,
    )
    login_payload = fresh.post(
        "/api/auth/login",
        {
            "phone": phone,
            "role": "enthusiast",
            "verificationCode": login_code,
        },
    )
    ensure(target_id in login_payload.get("followSet", []), "follow state disappeared after fresh login")
    ensure(post_id in login_payload.get("favoritePostIds", []), "favorite state disappeared after fresh login")
    ensure(any(item.get("id") == post_id for item in (current_profile(login_payload).get("posts") or [])), "post disappeared after fresh login")
    ensure(any(thread.get("messages") for thread in login_payload.get("threads") or []), "message thread disappeared after fresh login")
    ensure(login_payload.get("bookings"), "booking list disappeared after fresh login")

    return AcceptanceResult(
        profile_id=actor_id,
        target_profile_id=target_id,
        post_id=post_id,
        booking_count=len(login_payload.get("bookings") or []),
        thread_count=len(login_payload.get("threads") or []),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run FitHub production write-path acceptance.")
    parser.add_argument("--backend-url", default=read_default_backend())
    parser.add_argument("--phone", default=DEFAULT_PHONE, help="Dedicated acceptance test phone number.")
    parser.add_argument("--verification-code", default="", help="Register SMS code if production SMS is enabled.")
    parser.add_argument("--login-verification-code", default="", help="Fresh-login SMS code if production SMS is enabled.")
    parser.add_argument("--no-debug-code", action="store_true", help="Do not use dev debugCode even if the backend returns it.")
    parser.add_argument("--allow-local-storage", action="store_true", help="Allow local JSON storage for local/dev testing only.")
    parser.add_argument("--min-real-profiles", type=int, default=1)
    args = parser.parse_args()

    try:
        print(f"Running production write acceptance against {args.backend_url.rstrip('/')}")
        result = run_acceptance(
            backend_url=args.backend_url,
            phone=args.phone,
            verification_code=args.verification_code,
            login_verification_code=args.login_verification_code,
            allow_debug_code=not args.no_debug_code,
            allow_local_storage=args.allow_local_storage,
            min_real_profiles=args.min_real_profiles,
        )
    except (RuntimeError, ValueError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"\nProduction write acceptance failed: {exc}", file=sys.stderr)
        return 1

    print("\nProduction write acceptance passed.")
    print(f"  profile: {result.profile_id}")
    print(f"  target: {result.target_profile_id}")
    print(f"  post: {result.post_id}")
    print(f"  bookings: {result.booking_count}")
    print(f"  threads: {result.thread_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
