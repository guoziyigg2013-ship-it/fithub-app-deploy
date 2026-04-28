from tests.api.support import FitHubApiTestCase


class BookingRegressionTests(FitHubApiTestCase):
    def test_booking_surfaces_for_both_outgoing_and_incoming_sides(self):
        phone_a = self.make_phone(50)
        phone_b = self.make_phone(51)

        buyer_client = self.make_client()
        buyer_code = buyer_client.send_code(phone_a, purpose="register")["debugCode"]
        buyer_payload = buyer_client.register_enthusiast(phone_a, "预约发起者", buyer_code)
        buyer_profile = self.current_profile(buyer_payload)

        provider_client = self.make_client()
        provider_code = provider_client.send_code(phone_b, purpose="register")["debugCode"]
        provider_payload = provider_client.register_enthusiast(phone_b, "预约接收者", provider_code)
        provider_profile = self.current_profile(provider_payload)

        booking_payload = buyer_client.create_booking(provider_profile["id"], time_label="周六 19:30")
        outgoing = next((item for item in booking_payload.get("bookings", []) if item.get("counterpartProfileId") == provider_profile["id"]), None)
        self.assertIsNotNone(outgoing)
        self.assertEqual(outgoing["direction"], "outgoing")
        self.assertEqual(outgoing["status"], "已预约")

        provider_refreshed = provider_client.bootstrap()
        incoming = next((item for item in provider_refreshed.get("bookings", []) if item.get("counterpartProfileId") == buyer_profile["id"]), None)
        self.assertIsNotNone(incoming)
        self.assertEqual(incoming["direction"], "incoming")

    def test_multi_identity_bookings_are_scoped_to_current_identity(self):
        owner_phone = self.make_phone(52)
        buyer_phone = self.make_phone(53)

        owner_client = self.make_client()
        code_enthusiast = owner_client.send_code(owner_phone, purpose="register")["debugCode"]
        enthusiast_payload = owner_client.register_enthusiast(owner_phone, "双身份预约训练者", code_enthusiast)
        enthusiast_profile = self.current_profile(enthusiast_payload)

        code_coach = owner_client.send_code(owner_phone, purpose="register")["debugCode"]
        coach_payload = owner_client.register_coach(owner_phone, "双身份预约教练", code_coach)
        coach_profile = self.current_profile(coach_payload)

        demo_target = self.find_demo_target(coach_payload, role="coach")
        owner_client.post(
            "/api/session/select",
            {
                "selectedRole": "enthusiast",
                "currentActorProfileId": enthusiast_profile["id"],
            },
        )
        enthusiast_booking_payload = owner_client.create_booking(demo_target["id"], time_label="周三 18:00")
        self.assertTrue(all(item.get("createdByProfileId") == enthusiast_profile["id"] for item in enthusiast_booking_payload.get("bookings", [])))

        buyer_client = self.make_client()
        buyer_code = buyer_client.send_code(buyer_phone, purpose="register")["debugCode"]
        buyer_payload = buyer_client.register_enthusiast(buyer_phone, "双身份预约买家", buyer_code)
        buyer_profile = self.current_profile(buyer_payload)
        buyer_client.create_booking(coach_profile["id"], time_label="周四 20:00")

        coach_view = owner_client.post(
            "/api/session/select",
            {
                "selectedRole": "coach",
                "currentActorProfileId": coach_profile["id"],
            },
        )
        self.assertTrue(coach_view.get("bookings"))
        self.assertTrue(all(item.get("targetProfileId") == coach_profile["id"] for item in coach_view.get("bookings", [])))
        self.assertTrue(any(item.get("counterpartProfileId") == buyer_profile["id"] for item in coach_view.get("bookings", [])))

        enthusiast_view = owner_client.post(
            "/api/session/select",
            {
                "selectedRole": "enthusiast",
                "currentActorProfileId": enthusiast_profile["id"],
            },
        )
        self.assertTrue(enthusiast_view.get("bookings"))
        self.assertTrue(all(item.get("createdByProfileId") == enthusiast_profile["id"] for item in enthusiast_view.get("bookings", [])))
        self.assertFalse(any(item.get("targetProfileId") == coach_profile["id"] for item in enthusiast_view.get("bookings", [])))
