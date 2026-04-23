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
