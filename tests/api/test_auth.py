from tests.api.support import FitHubApiTestCase


class AuthRegressionTests(FitHubApiTestCase):
    def test_register_and_login_roundtrip_for_enthusiast(self):
        phone = self.make_phone(1)
        register_client = self.make_client()
        code = register_client.send_code(phone, purpose="register")["debugCode"]
        register_payload = register_client.register_enthusiast(phone, "回归用户A", code)

        profile = self.current_profile(register_payload)
        self.assertEqual(profile["role"], "enthusiast")
        self.assertEqual(profile["phone"], phone)
        self.assertIn(profile["id"], register_payload["session"]["managedProfileIds"])

        fresh_client = self.make_client()
        login_code = fresh_client.send_code(phone, purpose="login")["debugCode"]
        login_payload = fresh_client.login(phone, "enthusiast", login_code)
        self.assertEqual(login_payload["session"]["currentActorProfileId"], profile["id"])

        lookup = fresh_client.lookup_phone(phone)
        self.assertEqual(len(lookup["matches"]), 1)
        self.assertEqual(lookup["matches"][0]["profileId"], profile["id"])

    def test_same_phone_same_role_reuses_existing_profile(self):
        phone = self.make_phone(2)
        client_a = self.make_client()
        code_a = client_a.send_code(phone, purpose="register")["debugCode"]
        payload_a = client_a.register_enthusiast(phone, "同号用户A", code_a)
        profile_id_a = self.current_profile(payload_a)["id"]

        client_b = self.make_client()
        code_b = client_b.send_code(phone, purpose="register")["debugCode"]
        payload_b = client_b.register_enthusiast(phone, "同号用户B", code_b, goal="提升心肺")
        profile_b = self.current_profile(payload_b)

        self.assertEqual(profile_b["id"], profile_id_a)
        lookup = client_b.lookup_phone(phone)
        self.assertEqual(len(lookup["matches"]), 1)
