import importlib.util
import unittest
from pathlib import Path

from tests.api.support import FitHubApiTestCase


ROOT = Path(__file__).resolve().parents[2]
ACCEPTANCE_PATH = ROOT / "scripts" / "production_write_acceptance.py"
SPEC = importlib.util.spec_from_file_location("production_write_acceptance", ACCEPTANCE_PATH)
production_write_acceptance = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(production_write_acceptance)


class ProductionWriteAcceptanceTests(FitHubApiTestCase):
    def test_write_acceptance_covers_persistence_critical_paths(self):
        result = production_write_acceptance.run_acceptance(
            backend_url=self.base_url,
            phone=self.make_phone(991),
            allow_debug_code=True,
            allow_local_storage=True,
            min_real_profiles=0,
        )

        self.assertTrue(result.profile_id)
        self.assertTrue(result.target_profile_id)
        self.assertTrue(result.post_id)
        self.assertGreaterEqual(result.booking_count, 1)
        self.assertGreaterEqual(result.thread_count, 1)


if __name__ == "__main__":
    unittest.main()
