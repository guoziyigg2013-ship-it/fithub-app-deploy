import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "scripts" / "check_miniprogram.py"
SPEC = importlib.util.spec_from_file_location("check_miniprogram", SCRIPT_PATH)
check_miniprogram = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check_miniprogram)


class MiniProgramCheckTests(unittest.TestCase):
    def test_discover_instant_interactions_accepts_optimistic_updates(self):
        discover_js = """
        Page({
          applyOptimisticPostMutation() {},
          mergeConfirmedPost() {},
          async follow() {
            await api.post("/follow/toggle", { desiredFollowing: true, compact: true });
          },
          async like() {
            this.applyOptimisticPostMutation("post-1", (post) => post);
            await api.post("/post/like", { compact: true });
          },
          async favorite() {
            this.applyOptimisticPostMutation("post-1", (post) => ({ ...post, favoritedByCurrentActor: true }));
            await api.post("/post/favorite-toggle", { compact: true });
          },
        });
        """

        self.assertEqual(check_miniprogram.validate_discover_instant_interactions(discover_js), [])

    def test_discover_instant_interactions_rejects_full_reload_after_tap(self):
        discover_js = """
        Page({
          applyOptimisticPostMutation() {},
          mergeConfirmedPost() {},
          async follow() {
            await api.post("/follow/toggle", { desiredFollowing: true, compact: true });
          },
          async like() {
            await api.post("/post/like", { compact: true });
            this.load();
          },
          async favorite() {
            await api.post("/post/favorite-toggle", { compact: true });
            this.load();
          },
          favoritedByCurrentActor: true
        });
        """

        missing = check_miniprogram.validate_discover_instant_interactions(discover_js)

        self.assertIn("like must not call this.load() after tap", missing)
        self.assertIn("favorite must not call this.load() after tap", missing)


if __name__ == "__main__":
    unittest.main()
