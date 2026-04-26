import json
import unittest
from copy import deepcopy

import server
from tests.api.support import FitHubApiTestCase


class PersistenceRecoveryTests(FitHubApiTestCase):
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


class SupabaseRecoveryUnitTests(unittest.TestCase):
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
