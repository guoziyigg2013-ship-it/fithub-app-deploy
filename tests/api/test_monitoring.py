import json
import unittest

import server

try:
    from .support import FitHubApiTestCase
except ImportError:  # unittest discover imports modules without package context.
    from support import FitHubApiTestCase


class MonitoringRegressionTests(FitHubApiTestCase):
    def test_monitor_event_endpoint_records_sanitized_event_and_requires_admin_token(self):
        client = self.make_client()

        denied = client.admin_monitor(token="wrong-token", expected_status=403)
        self.assertIn("error", denied)

        result = client.report_monitor_event(
            type="api-slow",
            severity="warn",
            path="/api/bootstrap?token=secret",
            durationMs=3210,
            status=504,
            message="bootstrap 慢请求",
        )
        self.assertTrue(result["ok"])
        self.assertTrue(result["eventId"])

        dashboard = client.admin_monitor()
        serialized = json.dumps(dashboard, ensure_ascii=False)

        self.assertEqual(dashboard["summary"]["totalEvents"], 1)
        self.assertEqual(dashboard["summary"]["slowEvents"], 1)
        self.assertEqual(dashboard["summary"]["byType"]["api-slow"], 1)
        self.assertEqual(dashboard["summary"]["bySeverity"]["warn"], 1)
        self.assertNotIn("token=secret", serialized)

        event = dashboard["events"][0]
        self.assertEqual(event["path"], "/api/bootstrap")
        self.assertEqual(event["severity"], "warn")
        self.assertEqual(event["status"], 504)
        self.assertGreaterEqual(event["durationMs"], 3210)

    def test_monitor_events_are_capped_and_classified(self):
        state = server.initial_state()

        for index in range(205):
            server.record_monitor_event(
                state,
                {
                    "type": "media-upload-failed" if index % 2 == 0 else "frontend-error",
                    "severity": "error",
                    "durationMs": index,
                    "path": f"/api/media/upload-file?debug={index}",
                    "message": f"event {index}",
                },
            )

        dashboard = server.build_monitor_dashboard(state)
        serialized = json.dumps(dashboard, ensure_ascii=False)

        self.assertEqual(dashboard["summary"]["totalEvents"], 200)
        self.assertEqual(len(dashboard["events"]), 80)
        self.assertGreater(dashboard["summary"]["mediaEvents"], 0)
        self.assertEqual(dashboard["summary"]["bySeverity"]["error"], 200)
        self.assertNotIn("debug=", serialized)
        self.assertEqual(dashboard["events"][0]["message"], "event 204")


if __name__ == "__main__":
    unittest.main()
