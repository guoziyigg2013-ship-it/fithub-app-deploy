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
