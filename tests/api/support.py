import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SERVER_FILE = ROOT / "server.py"


def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class ApiClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")
        self.session_id = None
        self.last_bootstrap = self.bootstrap()

    def request(self, method, path, body=None, expected_status=200):
        url = f"{self.base_url}{path}"
        payload = None
        headers = {"Connection": "close"}
        if body is not None:
            payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json; charset=utf-8"
        request = urllib.request.Request(url, data=payload, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                data = response.read().decode("utf-8")
                parsed = json.loads(data or "{}")
                if response.status != expected_status:
                    raise AssertionError(f"{method} {path} expected {expected_status}, got {response.status}: {parsed}")
                return parsed
        except urllib.error.HTTPError as exc:
            body_text = exc.read().decode("utf-8", errors="ignore")
            try:
                parsed = json.loads(body_text or "{}")
            except json.JSONDecodeError:
                parsed = {"raw": body_text}
            if exc.code != expected_status:
                raise AssertionError(f"{method} {path} expected {expected_status}, got {exc.code}: {parsed}") from exc
            return parsed

    def bootstrap(self):
        suffix = ""
        if self.session_id:
            suffix = f"?session_id={urllib.parse.quote(self.session_id)}"
        payload = self.request("GET", f"/api/bootstrap{suffix}")
        self.session_id = payload["session"]["id"]
        self.last_bootstrap = payload
        return payload

    def storage_status(self, remote=False):
        suffix = "?remote=1" if remote else ""
        return self.request("GET", f"/api/storage/status{suffix}")

    def post(self, path, body=None, expected_status=200):
        body = dict(body or {})
        body.setdefault("sessionId", self.session_id)
        payload = self.request("POST", path, body=body, expected_status=expected_status)
        if isinstance(payload, dict) and payload.get("session", {}).get("id"):
            self.session_id = payload["session"]["id"]
            self.last_bootstrap = payload
        return payload

    def send_code(self, phone, purpose="login"):
        return self.post("/api/auth/send-code", {"phone": phone, "purpose": purpose})

    def login(self, phone, role, verification_code):
        return self.post(
            "/api/auth/login",
            {
                "phone": phone,
                "role": role,
                "verificationCode": verification_code,
            },
        )

    def lookup_phone(self, phone):
        return self.post("/api/auth/lookup-phone", {"phone": phone})

    def register_enthusiast(self, phone, name, verification_code, **extra):
        profile = {
            "name": name,
            "phone": phone,
            "gender": extra.get("gender", "男"),
            "heightCm": extra.get("heightCm", 175),
            "weightKg": extra.get("weightKg", 68),
            "level": extra.get("level", "新手入门"),
            "goal": extra.get("goal", "保持规律训练"),
            "intro": extra.get("intro", "API 回归测试用户"),
        }
        return self.post(
            "/api/register",
            {
                "role": "enthusiast",
                "profile": profile,
                "verificationCode": verification_code,
            },
        )

    def register_coach(self, phone, name, verification_code, **extra):
        profile = {
            "name": name,
            "phone": phone,
            "gender": extra.get("gender", "男"),
            "specialties": extra.get("specialties", "减脂 力量 私教"),
            "years": extra.get("years", "3"),
            "price": extra.get("price", "¥220/小时"),
            "intro": extra.get("intro", "API 回归测试教练"),
        }
        return self.post(
            "/api/register",
            {
                "role": "coach",
                "profile": profile,
                "verificationCode": verification_code,
            },
        )

    def register_gym(self, phone, name, verification_code, **extra):
        profile = {
            "gymName": name,
            "name": name,
            "phone": phone,
            "facilities": extra.get("facilities", "力量区 团课区 淋浴"),
            "price": extra.get("price", "¥169/月起"),
            "intro": extra.get("intro", "API 回归测试场馆"),
        }
        return self.post(
            "/api/register",
            {
                "role": "gym",
                "profile": profile,
                "verificationCode": verification_code,
            },
        )

    def toggle_follow(self, target_profile_id):
        return self.post("/api/follow/toggle", {"targetProfileId": target_profile_id})

    def create_post(self, profile_id, content, meta="测试动态", media=None):
        return self.post(
            "/api/post/create",
            {
                "profileId": profile_id,
                "content": content,
                "meta": meta,
                "media": media or [],
            },
        )

    def upload_media(
        self,
        data_url,
        file_name="demo.jpg",
        asset_type="image",
        category="posts",
        thumbnail_data_url="",
        thumbnail_name="",
    ):
        return self.post(
            "/api/media/upload",
            {
                "dataUrl": data_url,
                "fileName": file_name,
                "assetType": asset_type,
                "category": category,
                "thumbnailDataUrl": thumbnail_data_url,
                "thumbnailName": thumbnail_name,
            },
        )

    def delete_media(self, items):
        return self.post("/api/media/delete", {"items": items})

    def create_checkin(self, profile_id, sport_id="outdoor-walk", sport_label="户外行走"):
        return self.post(
            "/api/checkin/create",
            {
                "profileId": profile_id,
                "sportId": sport_id,
                "sportLabel": sport_label,
                "duration": 18,
                "distance": 1.26,
                "calories": 133,
                "paceLabel": "14'17\"/km",
                "bestPaceLabel": "11'20\"/km",
                "heartRateAvg": 118,
                "elevationGain": 6,
                "content": "完成了一次自动化测试打卡。",
                "route": {
                    "source": "gps",
                    "points": [
                        {"lat": 24.4802, "lng": 118.0887},
                        {"lat": 24.4808, "lng": 118.0891},
                        {"lat": 24.4812, "lng": 118.0896},
                    ],
                },
            },
        )

    def toggle_like(self, post_id):
        return self.post("/api/post/like", {"postId": post_id})

    def toggle_favorite(self, post_id):
        return self.post("/api/post/favorite-toggle", {"postId": post_id})

    def comment_post(self, post_id, text):
        return self.post("/api/post/comment", {"postId": post_id, "text": text})

    def send_message(self, target_profile_id, text):
        return self.post("/api/message/send", {"targetProfileId": target_profile_id, "text": text})

    def create_booking(self, target_profile_id, time_label="本周六 20:00"):
        return self.post("/api/booking/create", {"targetProfileId": target_profile_id, "time": time_label})


class FitHubApiTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory(prefix="fithub-api-tests-")
        cls.data_dir = Path(cls.temp_dir.name) / "data"
        cls.port = None
        cls.server_process = None
        cls.base_url = None
        cls._start_server()

    @classmethod
    def tearDownClass(cls):
        cls._stop_server()
        cls.temp_dir.cleanup()

    @classmethod
    def _server_env(cls):
        env = os.environ.copy()
        env.update(
            {
                "FITHUB_DATA_DIR": str(cls.data_dir),
                "FITHUB_SMS_DEV_MODE": "true",
                "SUPABASE_URL": "",
                "SUPABASE_SERVICE_ROLE_KEY": "",
                "FITHUB_MEDIA_MAINTENANCE_TOKEN": "test-maintenance-token",
                "PYTHONUNBUFFERED": "1",
            }
        )
        return env

    @classmethod
    def _start_server(cls):
        cls.port = find_free_port()
        cls.base_url = f"http://127.0.0.1:{cls.port}"
        cls.server_process = subprocess.Popen(
            [sys.executable, str(SERVER_FILE), "--host", "127.0.0.1", "--port", str(cls.port)],
            cwd=str(ROOT),
            env=cls._server_env(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        cls._wait_for_server()

    @classmethod
    def _stop_server(cls):
        if not cls.server_process:
            return
        cls.server_process.terminate()
        try:
            cls.server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            cls.server_process.kill()
            cls.server_process.wait(timeout=5)
        if cls.server_process.stdout:
            cls.server_process.stdout.close()
        cls.server_process = None

    @classmethod
    def _restart_server(cls):
        cls._stop_server()
        cls._start_server()

    @classmethod
    def _wait_for_server(cls):
        deadline = time.time() + 15
        last_error = None
        while time.time() < deadline:
            if cls.server_process.poll() is not None:
                output = cls.server_process.stdout.read() if cls.server_process.stdout else ""
                raise RuntimeError(f"FitHub test server exited early.\n{output}")
            try:
                with urllib.request.urlopen(f"{cls.base_url}/healthz", timeout=2) as response:
                    if response.status == 200:
                        return
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                time.sleep(0.2)
        output = cls.server_process.stdout.read() if cls.server_process.stdout else ""
        raise RuntimeError(f"FitHub test server did not become ready: {last_error}\n{output}")

    def make_phone(self, suffix):
        return f"132159{suffix:05d}"

    def make_client(self):
        return ApiClient(self.base_url)

    def current_profile(self, payload):
        current_id = payload["session"]["currentActorProfileId"]
        for profile in payload.get("profiles", []):
            if profile.get("id") == current_id:
                return profile
        self.fail(f"Current profile {current_id} not found in bootstrap payload")

    def find_profile(self, payload, profile_id):
        for profile in payload.get("profiles", []):
            if profile.get("id") == profile_id:
                return profile
        self.fail(f"Profile {profile_id} not found in bootstrap payload")

    def find_demo_target(self, payload, role="coach"):
        for profile in payload.get("profiles", []):
            if profile.get("role") == role and profile.get("listed"):
                return profile
        self.fail(f"No demo profile found for role={role}")
