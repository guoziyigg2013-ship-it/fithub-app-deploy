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
        self.assertEqual(media.get("type"), "image")
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

    def test_post_and_comment_mentions_surface_as_notifications(self):
        phone_target = self.make_phone(64)
        phone_actor = self.make_phone(65)

        target_client = self.make_client()
        target_code = target_client.send_code(phone_target, purpose="register")["debugCode"]
        target_payload = target_client.register_enthusiast(phone_target, "被提及用户", target_code)
        target_profile = self.current_profile(target_payload)

        actor_client = self.make_client()
        actor_code = actor_client.send_code(phone_actor, purpose="register")["debugCode"]
        actor_payload = actor_client.register_enthusiast(phone_actor, "提及发起者", actor_code)
        actor_profile = self.current_profile(actor_payload)

        mention_post_text = f"{target_profile['handle']} 今天一起练背吗？"
        mention_post_payload = actor_client.create_post(
            actor_profile["id"],
            mention_post_text,
            meta="@我回归测试 · 厦门 · 思明区",
            media=[],
        )
        mention_post = next(
            item for item in self.current_profile(mention_post_payload).get("posts", [])
            if item["content"] == mention_post_text
        )

        target_after_post = target_client.bootstrap()
        post_mention = next(
            (
                item for item in target_after_post.get("notifications", [])
                if item.get("type") == "mention"
                and item.get("actorProfileId") == actor_profile["id"]
                and item.get("postId") == mention_post["id"]
            ),
            None,
        )
        self.assertIsNotNone(post_mention)
        self.assertIn("动态里 @ 了你", post_mention["text"])

        comment_text = f"{target_profile['handle']} 评论里也提醒你一下。"
        actor_client.comment_post(mention_post["id"], comment_text)

        target_after_comment = target_client.bootstrap()
        comment_mentions = [
            item for item in target_after_comment.get("notifications", [])
            if item.get("type") == "mention"
            and item.get("actorProfileId") == actor_profile["id"]
            and item.get("postId") == mention_post["id"]
        ]
        self.assertTrue(any("评论里 @ 了你" in item.get("text", "") for item in comment_mentions))

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

    def test_video_post_persists_thumbnail_and_can_be_favorited(self):
        phone_a = self.make_phone(62)
        phone_b = self.make_phone(63)

        author_client = self.make_client()
        author_code = author_client.send_code(phone_a, purpose="register")["debugCode"]
        author_payload = author_client.register_enthusiast(phone_a, "视频收藏作者", author_code)
        author_profile = self.current_profile(author_payload)

        viewer_client = self.make_client()
        viewer_code = viewer_client.send_code(phone_b, purpose="register")["debugCode"]
        viewer_client.register_enthusiast(phone_b, "视频收藏用户", viewer_code)

        tiny_png = (
            "data:image/png;base64,"
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wn0n8kAAAAASUVORK5CYII="
        )
        tiny_video = "data:video/mp4;base64,AAAA"
        uploaded = author_client.upload_media(
            tiny_video,
            file_name="training-demo.mp4",
            asset_type="video",
            category="posts",
            thumbnail_data_url=tiny_png,
            thumbnail_name="training-demo-poster.png",
        )["media"]
        self.assertEqual(uploaded["type"], "video")
        self.assertEqual(uploaded["contentType"], "video/mp4")
        self.assertEqual(uploaded["thumbnailName"], "training-demo-poster.png")

        author_post_payload = author_client.create_post(
            author_profile["id"],
            "这是一条带视频封面的训练讲解。",
            media=[uploaded],
        )
        target_post = next(
            item for item in self.current_profile(author_post_payload).get("posts", [])
            if item["content"] == "这是一条带视频封面的训练讲解。"
        )
        self.assertEqual(target_post["media"][0]["type"], "video")
        self.assertEqual(target_post["media"][0]["thumbnailName"], "training-demo-poster.png")

        viewer_client.toggle_follow(author_profile["id"])
        favorite_payload = viewer_client.toggle_favorite(target_post["id"])
        favorite_entry = next(
            item for item in favorite_payload.get("favoritePosts", [])
            if (item.get("post") or {}).get("id") == target_post["id"]
        )
        favorite_post = favorite_entry.get("post") or {}
        self.assertEqual(favorite_post["media"][0]["type"], "video")
        self.assertEqual(favorite_post["media"][0]["thumbnailName"], "training-demo-poster.png")

    def test_risky_post_comment_and_message_are_queued_for_moderation(self):
        phone_a = self.make_phone(70)
        phone_b = self.make_phone(71)

        author_client = self.make_client()
        author_code = author_client.send_code(phone_a, purpose="register")["debugCode"]
        author_payload = author_client.register_enthusiast(phone_a, "审核作者", author_code)
        author_profile = self.current_profile(author_payload)

        viewer_client = self.make_client()
        viewer_code = viewer_client.send_code(phone_b, purpose="register")["debugCode"]
        viewer_payload = viewer_client.register_enthusiast(phone_b, "审核互动用户", viewer_code)
        viewer_profile = self.current_profile(viewer_payload)

        post_payload = author_client.create_post(author_profile["id"], "这是一条加微信后私下付款的测试动态。")
        target_post = next(
            item for item in self.current_profile(post_payload).get("posts", [])
            if item["content"] == "这是一条加微信后私下付款的测试动态。"
        )

        viewer_client.toggle_follow(author_profile["id"])
        viewer_client.comment_post(target_post["id"], "评论里也提醒转账风险。")
        viewer_client.send_message(author_profile["id"], "私信里不要私下付款。")

        dashboard = viewer_client.admin_moderation()
        self.assertGreaterEqual(dashboard["summary"]["pendingReview"], 3)
        queued_types = {item["type"] for item in dashboard["moderationQueue"]}
        self.assertIn("post", queued_types)
        self.assertIn("comment", queued_types)
        self.assertIn("message", queued_types)
        self.assertTrue(any(item.get("targetOwnerProfileId") == author_profile["id"] for item in dashboard["moderationQueue"]))
        self.assertTrue(any(item.get("targetOwnerProfileId") == viewer_profile["id"] for item in dashboard["moderationQueue"]))

    def test_user_report_is_persisted_and_admin_endpoint_is_protected(self):
        phone_a = self.make_phone(72)
        phone_b = self.make_phone(73)

        author_client = self.make_client()
        author_code = author_client.send_code(phone_a, purpose="register")["debugCode"]
        author_payload = author_client.register_enthusiast(phone_a, "被举报作者", author_code)
        author_profile = self.current_profile(author_payload)

        viewer_client = self.make_client()
        viewer_code = viewer_client.send_code(phone_b, purpose="register")["debugCode"]
        viewer_client.register_enthusiast(phone_b, "举报用户", viewer_code)

        post_payload = author_client.create_post(author_profile["id"], "这是一条普通但可被举报的动态。")
        target_post = next(
            item for item in self.current_profile(post_payload).get("posts", [])
            if item["content"] == "这是一条普通但可被举报的动态。"
        )

        viewer_client.create_report("post", target_post["id"], reason="广告骚扰")
        denied = viewer_client.admin_moderation(token="wrong-token", expected_status=403)
        self.assertIn("error", denied)

        dashboard = viewer_client.admin_moderation()
        self.assertEqual(dashboard["summary"]["openReports"], 1)
        report = next(item for item in dashboard["reports"] if item["targetId"] == target_post["id"])
        self.assertEqual(report["reason"], "广告骚扰")
        self.assertEqual(report["targetOwnerProfileId"], author_profile["id"])
        self.assertTrue(any(item["source"] == "user-report" and item["targetId"] == target_post["id"] for item in dashboard["moderationQueue"]))
