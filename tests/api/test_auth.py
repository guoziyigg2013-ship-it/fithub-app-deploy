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

    def test_same_phone_three_roles_share_one_formal_account(self):
        phone = self.make_phone(6)
        client = self.make_client()

        code_enthusiast = client.send_code(phone, purpose="register")["debugCode"]
        enthusiast_payload = client.register_enthusiast(phone, "三端账号用户", code_enthusiast)
        enthusiast_account_id = enthusiast_payload["session"]["managedAccounts"][0]["id"]

        code_coach = client.send_code(phone, purpose="register")["debugCode"]
        coach_payload = client.register_coach(phone, "三端账号教练", code_coach)
        coach_account = next(item for item in coach_payload["session"]["managedAccounts"] if item["id"] == enthusiast_account_id)

        code_gym = client.send_code(phone, purpose="register")["debugCode"]
        gym_payload = client.register_gym(phone, "三端账号场馆", code_gym)
        formal_account = next(item for item in gym_payload["session"]["managedAccounts"] if item["id"] == enthusiast_account_id)

        self.assertEqual(sorted(formal_account["roles"]), ["coach", "enthusiast", "gym"])
        self.assertEqual(formal_account["phone"], phone)
        self.assertEqual(formal_account["phoneMasked"], "132****0006")
        self.assertEqual(formal_account["primaryProvider"], "phone")
        self.assertIn("wechat", formal_account["pendingProviderBindings"])
        self.assertIn("apple", formal_account["pendingProviderBindings"])
        self.assertTrue(any(item["type"] == "phone" and item["verified"] for item in formal_account["identityProviders"]))
        self.assertEqual(coach_account["id"], formal_account["id"])

        fresh_client = self.make_client()
        login_code = fresh_client.send_code(phone, purpose="login")["debugCode"]
        login_payload = fresh_client.login(phone, "gym", login_code)
        login_account = next(item for item in login_payload["session"]["managedAccounts"] if item["id"] == enthusiast_account_id)
        self.assertEqual(sorted(login_account["roles"]), ["coach", "enthusiast", "gym"])
        self.assertEqual(login_payload["session"]["selectedRole"], "gym")
