from tests.api.support import FitHubApiTestCase


class HealthRegressionTests(FitHubApiTestCase):
    def test_native_health_sync_persists_metrics_and_dedupes_workouts(self):
        phone = self.make_phone(60)
        client = self.make_client()
        code = client.send_code(phone, purpose="register")["debugCode"]
        payload = client.register_enthusiast(
            phone,
            "健康同步用户",
            code,
            gender="男",
            heightCm=171,
            weightKg=60,
        )
        profile = self.current_profile(payload)

        native_payload = {
            "profileId": profile["id"],
            "source": "apple-healthkit",
            "deviceName": "Apple Watch Series 9",
            "metrics": {
                "heightCm": 171,
                "weightKg": 60.2,
                "bodyFat": 18.4,
                "restingHeartRate": 57,
                "stepCount": 8421,
                "activeEnergyBurned": 312.5,
                "vo2Max": 45.2,
            },
            "workouts": [
                {
                    "externalId": "apple-run-regression-001",
                    "workoutType": "running",
                    "startedAt": "2026-04-25T07:30:00+08:00",
                    "durationSeconds": 1860,
                    "distanceMeters": 5200,
                    "activeEnergyBurned": 366.2,
                    "note": "来自 HealthKit 的自动化回归训练。",
                }
            ],
        }

        synced = client.post("/api/health/native-sync", native_payload)
        self.assertEqual(synced["nativeSyncSummary"]["source"], "Apple Health")
        self.assertEqual(synced["nativeSyncSummary"]["importedWorkoutCount"], 1)

        current = self.current_profile(synced)
        self.assertIn("Apple Health", current["connectedDevices"])
        self.assertIn("Apple Watch Series 9", current["connectedDevices"])
        self.assertEqual(current["healthSource"], "Apple Health")
        self.assertEqual(current["weightKg"], 60.2)
        self.assertEqual(current["bodyFat"], 18.4)
        self.assertEqual(current["restingHeartRate"], 57)

        snapshot = current["healthSnapshot"]
        self.assertEqual(snapshot["source"], "Apple Health")
        self.assertEqual(snapshot["deviceName"], "Apple Watch Series 9")
        self.assertEqual(snapshot["stepCount"], 8421)
        self.assertEqual(snapshot["activeEnergyBurned"], 312.5)
        self.assertEqual(snapshot["vo2Max"], 45.2)

        self.assertTrue(
            any(item.get("stepCount") == 8421 for item in current["healthHistory"]),
            "device metrics should be written to health history",
        )
        self.assertTrue(
            any(item.get("runDistance", 0) >= 5.2 and item.get("totalCalories", 0) >= 366 for item in current["healthHistory"]),
            "imported workout should be reflected in health history totals",
        )
        imported_checkins = [
            item
            for item in current.get("checkins", [])
            if item.get("source") == "Apple Health" and item.get("sportId") == "run"
        ]
        self.assertEqual(len(imported_checkins), 1)
        self.assertEqual(imported_checkins[0]["duration"], 31)
        self.assertEqual(imported_checkins[0]["distance"], 5.2)
        self.assertEqual(imported_checkins[0]["calories"], 366)

        duplicate = client.post("/api/health/native-sync", native_payload)
        self.assertEqual(duplicate["nativeSyncSummary"]["importedWorkoutCount"], 0)
        duplicate_current = self.current_profile(duplicate)
        duplicate_checkins = [
            item
            for item in duplicate_current.get("checkins", [])
            if item.get("source") == "Apple Health" and item.get("sportId") == "run"
        ]
        self.assertEqual(len(duplicate_checkins), 1)

    def test_manual_device_sync_requires_complete_body_profile(self):
        phone = self.make_phone(61)
        client = self.make_client()
        code = client.send_code(phone, purpose="register")["debugCode"]
        payload = client.register_enthusiast(phone, "设备同步用户", code, gender="女", heightCm=166, weightKg=55)
        profile = self.current_profile(payload)

        synced = client.post(
            "/api/health/device-sync",
            {"profileId": profile["id"], "source": "xiaomi-scale"},
        )
        current = self.current_profile(synced)
        self.assertIn("小米智能秤", current["connectedDevices"])
        self.assertEqual(current["healthSource"], "小米智能秤")
        self.assertEqual(current["healthSnapshot"]["weightKg"], 55)
        self.assertIsNotNone(current["healthSnapshot"]["bmi"])
        self.assertIsNotNone(current["healthSnapshot"]["bodyFat"])
