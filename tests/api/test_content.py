from server import build_supabase_public_media_url, collect_referenced_media_paths, extract_storage_path_from_public_url, initial_state
from tests.api.support import FitHubApiTestCase


class ContentRegressionTests(FitHubApiTestCase):
    def test_media_upload_returns_reusable_asset_payload(self):
        client = self.make_client()
        tiny_png = (
            "data:image/png;base64,"
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wn0n8kAAAAASUVORK5CYII="
        )
        payload = client.upload_media(
            tiny_png,
            file_name="tiny.png",
            asset_type="image",
            category="posts",
            thumbnail_data_url=tiny_png,
            thumbnail_name="tiny-thumb.png",
        )
        media = payload.get("media") or {}
        self.assertEqual(media.get("name"), "tiny.png")
        self.assertEqual(media.get("contentType"), "image/png")
        self.assertIn(media.get("storageProvider"), {"inline", "supabase"})
        self.assertTrue(str(media.get("url") or "").startswith(("data:image/png", "https://")))
        self.assertTrue(str(media.get("thumbnailUrl") or "").startswith(("data:image/png", "https://")))
        self.assertEqual(media.get("thumbnailName"), "tiny-thumb.png")
        deleted = client.delete_media([media])
        self.assertIn("deletedPaths", deleted)

    def test_post_persists_media_thumbnail_metadata(self):
        phone = self.make_phone(42)
        client = self.make_client()
        code = client.send_code(phone, purpose="register")["debugCode"]
        payload = client.register_enthusiast(phone, "媒体元数据用户", code)
        profile = self.current_profile(payload)

        tiny_png = (
            "data:image/png;base64,"
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wn0n8kAAAAASUVORK5CYII="
        )
        uploaded = client.upload_media(
            tiny_png,
            file_name="detail.png",
            asset_type="image",
            category="posts",
            thumbnail_data_url=tiny_png,
            thumbnail_name="detail-thumb.png",
        )["media"]

        post_payload = client.create_post(
            profile["id"],
            "带封面图的媒体动态。",
            media=[uploaded],
        )
        post = next(item for item in self.current_profile(post_payload).get("posts", []) if item["content"] == "带封面图的媒体动态。")
        self.assertEqual(post["media"][0]["name"], "detail.png")
        self.assertEqual(post["media"][0]["thumbnailName"], "detail-thumb.png")
        self.assertTrue(str(post["media"][0]["thumbnailUrl"] or "").startswith(("data:image/png", "https://")))

    def test_collect_referenced_media_paths_understands_public_urls(self):
        state = {
            "profiles": {
                "enthusiast-test": {
                    "avatarImage": build_supabase_public_media_url("avatars/2026/04/23/avatar-test.png"),
                }
            },
            "posts": {
                "post-test": {
                    "media": [
                        {
                            "storagePath": "posts/2026/04/23/post-test.png",
                            "thumbnailStoragePath": "posts-thumbs/2026/04/23/post-test-thumb.png",
                            "url": build_supabase_public_media_url("posts/2026/04/23/post-test.png"),
                            "thumbnailUrl": build_supabase_public_media_url("posts-thumbs/2026/04/23/post-test-thumb.png"),
                        }
                    ]
                }
            },
        }

        referenced = collect_referenced_media_paths(state)
        self.assertIn("avatars/2026/04/23/avatar-test.png", referenced)
        self.assertIn("posts/2026/04/23/post-test.png", referenced)
        self.assertIn("posts-thumbs/2026/04/23/post-test-thumb.png", referenced)
        self.assertEqual(
            extract_storage_path_from_public_url(build_supabase_public_media_url("posts/2026/04/23/post-test.png")),
            "posts/2026/04/23/post-test.png",
        )

    def test_demo_media_does_not_depend_on_external_pexels_assets(self):
        encoded_state = str(initial_state())
        self.assertNotIn("images.pexels.com", encoded_state)

    def test_media_maintenance_endpoint_is_token_protected(self):
        client = self.make_client()
        denied = client.post(
            "/api/media/maintenance",
            {"token": "wrong-token", "ageHours": 24},
            expected_status=403,
        )
        self.assertIn("error", denied)

        report = client.post(
            "/api/media/maintenance",
            {"token": "test-maintenance-token", "ageHours": 24, "delete": False},
        )
        self.assertFalse(report["enabled"])
        self.assertIn("summary", report)

    def test_post_checkin_and_message_surface_in_bootstrap(self):
        phone = self.make_phone(4)
        client = self.make_client()
        code = client.send_code(phone, purpose="register")["debugCode"]
        payload = client.register_enthusiast(phone, "内容回归用户", code)
        profile = self.current_profile(payload)
        target = self.find_demo_target(payload, role="coach")

        client.toggle_follow(target["id"])
        post_payload = client.create_post(
            profile["id"],
            "这是一条 API 回归测试动态。",
            media=[{"type": "image", "url": "https://example.com/test.jpg", "name": "test.jpg"}],
        )
        current_after_post = self.current_profile(post_payload)
        self.assertTrue(any(item["content"] == "这是一条 API 回归测试动态。" for item in current_after_post.get("posts", [])))

        checkin_payload = client.create_checkin(profile["id"])
        current_after_checkin = self.current_profile(checkin_payload)
        self.assertTrue(any(item["sportId"] == "outdoor-walk" for item in current_after_checkin.get("checkins", [])))
        self.assertTrue(any((item.get("checkin") or {}).get("sportId") == "outdoor-walk" for item in current_after_checkin.get("posts", [])))

        message_payload = client.send_message(target["id"], "这是一条自动化测试私信。")
        threads = message_payload.get("threads", [])
        thread = next((item for item in threads if item.get("withProfileId") == target["id"]), None)
        self.assertIsNotNone(thread)
        self.assertEqual(thread["lastMessage"]["text"], "这是一条自动化测试私信。")

    def test_like_favorite_comment_and_notifications_surface(self):
        phone_a = self.make_phone(40)
        phone_b = self.make_phone(41)

        author_client = self.make_client()
        author_code = author_client.send_code(phone_a, purpose="register")["debugCode"]
        author_payload = author_client.register_enthusiast(phone_a, "动态作者", author_code)
        author_profile = self.current_profile(author_payload)

        viewer_client = self.make_client()
        viewer_code = viewer_client.send_code(phone_b, purpose="register")["debugCode"]
        viewer_payload = viewer_client.register_enthusiast(phone_b, "互动用户", viewer_code)
        viewer_profile = self.current_profile(viewer_payload)

        author_post_payload = author_client.create_post(
            author_profile["id"],
            "带图片的健身讲解动态。",
            media=[{"type": "image", "url": "https://example.com/demo.jpg", "name": "demo.jpg"}],
        )
        author_current = self.current_profile(author_post_payload)
        target_post = next(item for item in author_current.get("posts", []) if item["content"] == "带图片的健身讲解动态。")

        viewer_client.toggle_follow(author_profile["id"])
        liked_payload = viewer_client.toggle_like(target_post["id"])
        author_from_viewer = self.find_profile(liked_payload, author_profile["id"])
        liked_post = next(item for item in author_from_viewer.get("posts", []) if item["id"] == target_post["id"])
        self.assertTrue(liked_post["likedByCurrentActor"])

        favorite_payload = viewer_client.toggle_favorite(target_post["id"])
        self.assertIn(target_post["id"], favorite_payload["favoritePostIds"])
        favorite_entry = next(
            item for item in favorite_payload.get("favoritePosts", [])
            if (item.get("post") or {}).get("id") == target_post["id"]
        )
        favorite_post = favorite_entry.get("post") or {}
        self.assertTrue(favorite_post.get("media"))
        self.assertEqual(favorite_post["media"][0]["type"], "image")

        commented_payload = viewer_client.comment_post(target_post["id"], "这条讲解很清楚。")
        author_after_comment = self.find_profile(commented_payload, author_profile["id"])
        viewer_visible_post = next(item for item in author_after_comment.get("posts", []) if item["id"] == target_post["id"])
        self.assertEqual(viewer_visible_post["likeCount"], 1)
        self.assertEqual(len(viewer_visible_post["comments"]), 1)

        author_refreshed = author_client.bootstrap()
        author_post = next(item for item in self.current_profile(author_refreshed).get("posts", []) if item["id"] == target_post["id"])
        self.assertEqual(author_post["likeCount"], 1)
        self.assertEqual(len(author_post["comments"]), 1)
        notification_types = [item["type"] for item in author_refreshed.get("notifications", []) if item.get("actorProfileId") == viewer_profile["id"]]
        self.assertIn("like", notification_types)
        self.assertIn("comment", notification_types)

    def test_text_post_can_be_favorited_and_serialized(self):
        phone_a = self.make_phone(48)
        phone_b = self.make_phone(49)

        author_client = self.make_client()
        author_code = author_client.send_code(phone_a, purpose="register")["debugCode"]
        author_payload = author_client.register_enthusiast(phone_a, "文字收藏作者", author_code)
        author_profile = self.current_profile(author_payload)

        viewer_client = self.make_client()
        viewer_code = viewer_client.send_code(phone_b, purpose="register")["debugCode"]
        viewer_client.register_enthusiast(phone_b, "文字收藏用户", viewer_code)

        author_post_payload = author_client.create_post(
            author_profile["id"],
            "这是一条没有图片视频但值得收藏的训练心得。",
            media=[],
        )
        target_post = next(
            item for item in self.current_profile(author_post_payload).get("posts", [])
            if item["content"] == "这是一条没有图片视频但值得收藏的训练心得。"
        )

        viewer_client.toggle_follow(author_profile["id"])
        favorite_payload = viewer_client.toggle_favorite(target_post["id"])
        self.assertIn(target_post["id"], favorite_payload["favoritePostIds"])
        favorite_entry = next(
            item for item in favorite_payload.get("favoritePosts", [])
            if (item.get("post") or {}).get("id") == target_post["id"]
        )
        favorite_post = favorite_entry.get("post") or {}
        self.assertEqual(favorite_post["content"], target_post["content"])
        self.assertEqual(favorite_post.get("media"), [])
