from tests.api.support import FitHubApiTestCase


class SocialRegressionTests(FitHubApiTestCase):
    def test_follow_state_survives_login_and_server_restart(self):
        phone = self.make_phone(3)
        client = self.make_client()
        code = client.send_code(phone, purpose="register")["debugCode"]
        payload = client.register_enthusiast(phone, "关注回归用户", code)
        target = self.find_demo_target(payload, role="coach")

        followed_payload = client.toggle_follow(target["id"])
        self.assertIn(target["id"], followed_payload["followSet"])

        relogin_client = self.make_client()
        login_code = relogin_client.send_code(phone, purpose="login")["debugCode"]
        relogin_payload = relogin_client.login(phone, "enthusiast", login_code)
        self.assertIn(target["id"], relogin_payload["followSet"])

        self.__class__._restart_server()

        restarted_client = self.make_client()
        restart_code = restarted_client.send_code(phone, purpose="login")["debugCode"]
        restarted_payload = restarted_client.login(phone, "enthusiast", restart_code)
        self.assertIn(target["id"], restarted_payload["followSet"])

    def test_follower_set_and_reciprocal_follow_surface_correctly(self):
        phone_a = self.make_phone(30)
        phone_b = self.make_phone(31)

        client_a = self.make_client()
        code_a = client_a.send_code(phone_a, purpose="register")["debugCode"]
        payload_a = client_a.register_enthusiast(phone_a, "训练者A", code_a)
        profile_a = self.current_profile(payload_a)

        client_b = self.make_client()
        code_b = client_b.send_code(phone_b, purpose="register")["debugCode"]
        payload_b = client_b.register_enthusiast(phone_b, "训练者B", code_b)
        profile_b = self.current_profile(payload_b)

        a_follow_payload = client_a.toggle_follow(profile_b["id"])
        self.assertIn(profile_b["id"], a_follow_payload["followSet"])

        b_bootstrap = client_b.bootstrap()
        self.assertIn(profile_a["id"], b_bootstrap["followerSet"])

        b_follow_payload = client_b.toggle_follow(profile_a["id"])
        self.assertIn(profile_a["id"], b_follow_payload["followSet"])

        a_bootstrap = client_a.bootstrap()
        self.assertIn(profile_b["id"], a_bootstrap["followerSet"])

    def test_multi_identity_threads_are_scoped_to_current_identity(self):
        owner_phone = self.make_phone(32)
        sender_phone = self.make_phone(33)

        owner_client = self.make_client()
        code_enthusiast = owner_client.send_code(owner_phone, purpose="register")["debugCode"]
        enthusiast_payload = owner_client.register_enthusiast(owner_phone, "双身份消息训练者", code_enthusiast)
        enthusiast_profile = self.current_profile(enthusiast_payload)

        code_coach = owner_client.send_code(owner_phone, purpose="register")["debugCode"]
        coach_payload = owner_client.register_coach(owner_phone, "双身份消息教练", code_coach)
        coach_profile = self.current_profile(coach_payload)

        sender_client = self.make_client()
        sender_code = sender_client.send_code(sender_phone, purpose="register")["debugCode"]
        sender_client.register_enthusiast(sender_phone, "双身份消息发送者", sender_code)
        sender_client.send_message(enthusiast_profile["id"], "发给训练者身份的私信")
        sender_client.send_message(coach_profile["id"], "发给教练身份的私信")

        enthusiast_view = owner_client.post(
            "/api/session/select",
            {
                "selectedRole": "enthusiast",
                "currentActorProfileId": enthusiast_profile["id"],
            },
        )
        enthusiast_texts = [
            message.get("text")
            for thread in enthusiast_view.get("threads", [])
            for message in thread.get("messages", [])
        ]
        self.assertIn("发给训练者身份的私信", enthusiast_texts)
        self.assertNotIn("发给教练身份的私信", enthusiast_texts)

        coach_view = owner_client.post(
            "/api/session/select",
            {
                "selectedRole": "coach",
                "currentActorProfileId": coach_profile["id"],
            },
        )
        coach_texts = [
            message.get("text")
            for thread in coach_view.get("threads", [])
            for message in thread.get("messages", [])
        ]
        self.assertIn("发给教练身份的私信", coach_texts)
        self.assertNotIn("发给训练者身份的私信", coach_texts)
