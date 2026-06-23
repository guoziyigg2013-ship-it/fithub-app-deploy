import json
import importlib.util
import unittest
from copy import deepcopy
from pathlib import Path

import server
from tests.api.support import FitHubApiTestCase


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_PATH = ROOT / "scripts" / "production_snapshot.py"
SNAPSHOT_SPEC = importlib.util.spec_from_file_location("production_snapshot", SNAPSHOT_PATH)
production_snapshot = importlib.util.module_from_spec(SNAPSHOT_SPEC)
SNAPSHOT_SPEC.loader.exec_module(production_snapshot)


class PersistenceRecoveryTests(FitHubApiTestCase):
    def test_storage_status_endpoint_exposes_safe_runtime_diagnostics(self):
        client = self.make_client()
        status = client.storage_status()

        self.assertIn(status["status"], {"ok", "local-only", "degraded"})
        self.assertIn("storage", status)
        self.assertIn("metrics", status)
        self.assertEqual(status["storage"]["loadedFrom"], "local-file")
        self.assertFalse(status["storage"]["supabaseConfigured"])
        self.assertEqual(status["media"]["storageProvider"], "inline")
        serialized = json.dumps(status, ensure_ascii=False)
        self.assertNotIn("service_role", serialized)
        self.assertNotIn("SUPABASE_SERVICE_ROLE_KEY", serialized)

    def test_phone_recovery_slice_restores_social_and_content_state(self):
        author_phone = self.make_phone(70)
        viewer_phone = self.make_phone(71)

        author_client = self.make_client()
        author_code = author_client.send_code(author_phone, purpose="register")["debugCode"]
        author_payload = author_client.register_enthusiast(author_phone, "恢复作者", author_code)
        author_profile = self.current_profile(author_payload)

        viewer_client = self.make_client()
        viewer_code = viewer_client.send_code(viewer_phone, purpose="register")["debugCode"]
        viewer_payload = viewer_client.register_enthusiast(viewer_phone, "恢复用户", viewer_code)
        viewer_profile = self.current_profile(viewer_payload)

        author_post_payload = author_client.create_post(author_profile["id"], "这条动态用于恢复测试。")
        target_post = next(
            item
            for item in self.current_profile(author_post_payload).get("posts", [])
            if item["content"] == "这条动态用于恢复测试。"
        )

        viewer_client.toggle_follow(author_profile["id"])
        viewer_client.toggle_like(target_post["id"])
        viewer_client.toggle_favorite(target_post["id"])
        viewer_client.comment_post(target_post["id"], "恢复评论。")
        viewer_client.send_message(author_profile["id"], "恢复私信。")

        with (self.data_dir / "shared_state.json").open("r", encoding="utf-8") as handle:
            full_state = server.sanitize_state(json.load(handle))

        recovery_payload = server.build_phone_recovery_slice(full_state, viewer_phone)
        self.assertIsNotNone(recovery_payload)

        degraded_state = deepcopy(full_state)
        degraded_state["profiles"].pop(viewer_profile["id"], None)
        degraded_state["accounts"] = {
            account_id: account
            for account_id, account in degraded_state.get("accounts", {}).items()
            if server.normalize_phone(account.get("phone")) != viewer_phone
        }
        degraded_state["follows"] = [
            item
            for item in degraded_state.get("follows", [])
            if item.get("sourceProfileId") != viewer_profile["id"] and item.get("targetProfileId") != viewer_profile["id"]
        ]
        degraded_state["postFavorites"] = [
            item
            for item in degraded_state.get("postFavorites", [])
            if item.get("sourceProfileId") != viewer_profile["id"]
        ]
        degraded_post = degraded_state["posts"][target_post["id"]]
        degraded_post["likes"] = [item for item in degraded_post.get("likes", []) if item != viewer_profile["id"]]
        degraded_post["comments"] = [
            item
            for item in degraded_post.get("comments", [])
            if item.get("authorProfileId") != viewer_profile["id"]
        ]
        for thread in degraded_state.get("threads", []):
            thread["messages"] = [
                item
                for item in thread.get("messages", [])
                if item.get("senderProfileId") != viewer_profile["id"]
            ]

        self.assertTrue(server.merge_phone_recovery_slice(degraded_state, recovery_payload))
        server.reconcile_account_registry(degraded_state)

        restored_account = server.resolve_account_by_phone(degraded_state, viewer_phone)
        self.assertIsNotNone(restored_account)
        restored_profile_id = restored_account["profilesByRole"]["enthusiast"]
        self.assertIn(restored_profile_id, degraded_state["profiles"])
        self.assertIn(author_profile["id"], server.get_follow_set(degraded_state, restored_profile_id))

        restored_post = degraded_state["posts"][target_post["id"]]
        self.assertIn(restored_profile_id, restored_post["likes"])
        self.assertTrue(
            any(item.get("authorProfileId") == restored_profile_id and item.get("text") == "恢复评论。" for item in restored_post.get("comments", []))
        )
        self.assertTrue(
            any(item.get("sourceProfileId") == restored_profile_id and item.get("postId") == target_post["id"] for item in degraded_state.get("postFavorites", []))
        )
        self.assertTrue(
            any(
                any(message.get("senderProfileId") == restored_profile_id and message.get("text") == "恢复私信。" for message in thread.get("messages", []))
                for thread in degraded_state.get("threads", [])
            )
        )

    def test_admin_export_requires_token_and_contains_full_snapshot_metrics(self):
        client = self.make_client()
        phone = self.make_phone(72)
        code = client.send_code(phone, purpose="register")["debugCode"]
        registered = client.register_enthusiast(phone, "生产快照用户", code)
        profile = self.current_profile(registered)
        client.create_post(profile["id"], "这条动态用于生产快照。")

        forbidden = client.admin_export(token="wrong-token", expected_status=403)
        self.assertIn("error", forbidden)

        exported = client.admin_export()
        self.assertTrue(exported["ok"])
        self.assertIn("exportedAt", exported)
        self.assertGreaterEqual(exported["metrics"]["real_profiles"], 1)
        self.assertGreaterEqual(exported["metrics"]["real_posts"], 1)
        self.assertIn("state", exported)
        self.assertIn(profile["id"], exported["state"]["profiles"])
        serialized = json.dumps(exported, ensure_ascii=False)
        self.assertNotIn("test-maintenance-token", serialized)

    def test_production_snapshot_metric_comparison_rejects_regressions(self):
        baseline = {
            "metrics": {
                "real_profiles": 3,
                "phone_profiles": 3,
                "accounts": 3,
                "real_follows": 4,
                "real_posts": 2,
                "real_bookings": 1,
                "real_threads": 1,
                "real_checkins": 2,
            }
        }
        current = {
            "metrics": {
                "real_profiles": 3,
                "phone_profiles": 3,
                "accounts": 3,
                "real_follows": 2,
                "real_posts": 2,
                "real_bookings": 1,
                "real_threads": 0,
                "real_checkins": 2,
            }
        }

        failures = production_snapshot.compare_metrics(
            production_snapshot.extract_metrics(current),
            production_snapshot.extract_metrics(baseline),
        )
        self.assertTrue(any("real_follows" in item for item in failures))
        self.assertTrue(any("real_threads" in item for item in failures))

        allowed = production_snapshot.compare_metrics(
            production_snapshot.extract_metrics(current),
            production_snapshot.extract_metrics(baseline),
            allowances={"real_follows": 2, "real_threads": 1},
        )
        self.assertEqual(allowed, [])


class SupabaseRecoveryUnitTests(unittest.TestCase):
    def test_supabase_url_diagnostics_rejects_placeholder_project_url(self):
        original_url = server.SUPABASE_URL
        original_key = server.SUPABASE_SERVICE_ROLE_KEY
        original_meta = deepcopy(server.STATE_RUNTIME_META)

        try:
            server.SUPABASE_URL = "https://你的项目ref.supabase.co"
            server.SUPABASE_SERVICE_ROLE_KEY = "service-role-secret"
            diagnostics = server.supabase_url_diagnostics()

            self.assertTrue(diagnostics["hostLooksPlaceholder"])
            self.assertIn("占位符", diagnostics["issue"])
            self.assertFalse(server.supabase_config_valid())
        finally:
            server.SUPABASE_URL = original_url
            server.SUPABASE_SERVICE_ROLE_KEY = original_key
            server.STATE_RUNTIME_META.clear()
            server.STATE_RUNTIME_META.update(original_meta)

    def test_supabase_url_diagnostics_exposes_safe_host_without_key(self):
        original_url = server.SUPABASE_URL
        original_key = server.SUPABASE_SERVICE_ROLE_KEY
        original_meta = deepcopy(server.STATE_RUNTIME_META)

        try:
            server.SUPABASE_URL = "https://abcdefghijklmnopqrst.supabase.co"
            server.SUPABASE_SERVICE_ROLE_KEY = "service-role-secret"
            diagnostics = server.supabase_url_diagnostics()
            serialized = json.dumps(server.storage_runtime_status(server.initial_state()), ensure_ascii=False)

            self.assertEqual(diagnostics["host"], "abcdefghijklmnopqrst.supabase.co")
            self.assertTrue(diagnostics["hostLooksSupabase"])
            self.assertEqual(diagnostics["issue"], "")
            self.assertNotIn("service-role-secret", serialized)
            self.assertIn("abcdefghijklmnopqrst.supabase.co", serialized)
        finally:
            server.SUPABASE_URL = original_url
            server.SUPABASE_SERVICE_ROLE_KEY = original_key
            server.STATE_RUNTIME_META.clear()
            server.STATE_RUNTIME_META.update(original_meta)

    def test_supabase_refresh_retry_is_rate_limited_after_fallback_failure(self):
        original_enabled = server.supabase_storage_enabled
        original_load = server.load_state_from_supabase
        original_cooldown = server.SUPABASE_REFRESH_COOLDOWN_SECONDS
        original_meta = deepcopy(server.STATE_RUNTIME_META)
        calls = []

        def fake_load():
            calls.append(server.iso_at())
            raise RuntimeError("dns failed")

        try:
            server.supabase_storage_enabled = lambda: True
            server.load_state_from_supabase = fake_load
            server.SUPABASE_REFRESH_COOLDOWN_SECONDS = 60
            server.STATE_RUNTIME_META.update(
                {
                    "loaded_from": "local-fallback",
                    "last_supabase_refresh_attempt": 0.0,
                    "last_supabase_refresh_attempt_at": "",
                    "last_supabase_refresh_error": "",
                }
            )

            self.assertFalse(server.refresh_state_cache_from_supabase())
            self.assertEqual(len(calls), 1)
            self.assertIn("dns failed", server.STATE_RUNTIME_META["last_supabase_refresh_error"])

            self.assertFalse(server.refresh_state_cache_from_supabase())
            self.assertEqual(len(calls), 1)

            self.assertFalse(server.refresh_state_cache_from_supabase(force=True))
            self.assertEqual(len(calls), 2)
        finally:
            server.supabase_storage_enabled = original_enabled
            server.load_state_from_supabase = original_load
            server.SUPABASE_REFRESH_COOLDOWN_SECONDS = original_cooldown
            server.STATE_RUNTIME_META.clear()
            server.STATE_RUNTIME_META.update(original_meta)

    def test_supabase_backup_pruning_keeps_latest_and_retention_window(self):
        original_enabled = server.supabase_storage_enabled
        original_request = server.supabase_request
        original_retention = server.SUPABASE_BACKUP_RETENTION
        original_last_prune = server.SUPABASE_LAST_BACKUP_PRUNE_TS
        deleted_paths = []
        rows = [
            {"id": f"{server.SUPABASE_BACKUP_PREFIX}-latest", "updated_at": "2026-04-26T10:00:00Z"},
            {"id": f"{server.SUPABASE_BACKUP_PREFIX}-2026042610", "updated_at": "2026-04-26T10:00:00Z"},
            {"id": f"{server.SUPABASE_BACKUP_PREFIX}-2026042609", "updated_at": "2026-04-26T09:00:00Z"},
            {"id": f"{server.SUPABASE_BACKUP_PREFIX}-2026042608", "updated_at": "2026-04-26T08:00:00Z"},
            {"id": f"{server.SUPABASE_BACKUP_PREFIX}-2026042607", "updated_at": "2026-04-26T07:00:00Z"},
            {"id": f"{server.SUPABASE_PHONE_RECOVERY_PREFIX}-13215990000", "updated_at": "2026-04-26T07:00:00Z"},
        ]

        def fake_request(method, path, payload=None, prefer=None):
            if method == "GET":
                self.assertIn("select=id,updated_at", path)
                return rows
            if method == "DELETE":
                deleted_paths.append(path)
                return None
            raise AssertionError(f"Unexpected request: {method} {path}")

        try:
            server.supabase_storage_enabled = lambda: True
            server.supabase_request = fake_request
            server.SUPABASE_BACKUP_RETENTION = 2
            server.SUPABASE_LAST_BACKUP_PRUNE_TS = 0
            result = server.prune_supabase_backup_rows(force=True)
        finally:
            server.supabase_storage_enabled = original_enabled
            server.supabase_request = original_request
            server.SUPABASE_BACKUP_RETENTION = original_retention
            server.SUPABASE_LAST_BACKUP_PRUNE_TS = original_last_prune

        self.assertEqual(result["deleted"], 2)
        self.assertTrue(any("2026042608" in path for path in deleted_paths))
        self.assertTrue(any("2026042607" in path for path in deleted_paths))
        self.assertFalse(any("latest" in path for path in deleted_paths))
        self.assertFalse(any("13215990000" in path for path in deleted_paths))

    def test_phone_recovery_rows_are_merged_without_restoring_stale_backup_rows(self):
        phone = "13215997100"
        state = server.initial_state()
        recovery_payload = {
            "phone": phone,
            "accountId": "acct-recovery",
            "profiles": {
                "enthusiast-recovery": server.make_profile(
                    id="enthusiast-recovery",
                    accountId="acct-recovery",
                    role="enthusiast",
                    name="远端恢复用户",
                    handle="@recovery",
                    phone=phone,
                )
            },
            "accounts": {
                "acct-recovery": {
                    "id": "acct-recovery",
                    "restoreToken": "restore-token",
                    "phone": phone,
                    "profilesByRole": {"enthusiast": "enthusiast-recovery"},
                    "createdAt": server.iso_at(),
                }
            },
            "follows": [{"sourceProfileId": "enthusiast-recovery", "targetProfileId": "coach-demo-a", "createdAt": server.iso_at()}],
            "posts": {},
            "bookings": [],
            "threads": [],
            "postFavorites": [],
            "profileAliases": {},
        }

        original_enabled = server.supabase_storage_enabled
        original_request = server.supabase_request

        def fake_request(method, path, payload=None, prefer=None):
            self.assertEqual(method, "GET")
            self.assertIn("select=id,payload,updated_at", path)
            return [
                {
                    "id": f"{server.SUPABASE_PHONE_RECOVERY_PREFIX}-{phone}",
                    "payload": recovery_payload,
                    "updated_at": server.iso_at(),
                },
                {
                    "id": f"{server.SUPABASE_BACKUP_PREFIX}-latest",
                    "payload": {"profiles": {"stale": {}}},
                    "updated_at": server.iso_at(),
                },
            ]

        try:
            server.supabase_storage_enabled = lambda: True
            server.supabase_request = fake_request
            self.assertTrue(server.merge_phone_recovery_rows_from_supabase(state))
        finally:
            server.supabase_storage_enabled = original_enabled
            server.supabase_request = original_request

        account = server.resolve_account_by_phone(state, phone)
        self.assertIsNotNone(account)
        self.assertEqual(account["profilesByRole"]["enthusiast"], "enthusiast-recovery")
        self.assertIn("coach-demo-a", server.get_follow_set(state, "enthusiast-recovery"))
