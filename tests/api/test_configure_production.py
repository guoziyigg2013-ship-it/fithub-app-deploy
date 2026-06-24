import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONFIGURE_PATH = ROOT / "scripts" / "configure_production.py"
SPEC = importlib.util.spec_from_file_location("configure_production", CONFIGURE_PATH)
configure_production = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(configure_production)


def write_minimal_repo(root: Path) -> None:
    (root / "wechat-miniprogram").mkdir(parents=True)
    (root / "config.js").write_text(
        'window.__FITHUB_CONFIG__ = { apiOrigin: "https://fithub-app-1btg.onrender.com" };\n',
        encoding="utf-8",
    )
    (root / "wechat-miniprogram" / "config.js").write_text(
        'module.exports = { apiBase: "https://fithub-app-1btg.onrender.com/api", defaultCity: "厦门 · 思明区" };\n',
        encoding="utf-8",
    )
    (root / "wechat-miniprogram" / "project.config.json").write_text(
        json.dumps({"appid": "touristappid", "projectname": "fithub-miniprogram"}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


class ConfigureProductionTests(unittest.TestCase):
    def test_rejects_temporary_api_origin(self):
        with self.assertRaisesRegex(ValueError, "临时域名"):
            configure_production.normalize_api_origin("https://fithub-app-1btg.onrender.com")

    def test_rejects_invalid_miniapp_appid(self):
        with self.assertRaisesRegex(ValueError, "touristappid"):
            configure_production.normalize_appid("touristappid")

    def test_configure_updates_web_miniapp_and_project_appid(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_minimal_repo(root)

            previews = configure_production.configure(
                root,
                "https://api.fithub.example.com",
                "wx1234567890abcdef",
            )

            self.assertTrue(any("config.js" in item for item in previews))
            self.assertIn(
                'apiOrigin: "https://api.fithub.example.com"',
                (root / "config.js").read_text(encoding="utf-8"),
            )
            self.assertIn(
                'apiBase: "https://api.fithub.example.com/api"',
                (root / "wechat-miniprogram" / "config.js").read_text(encoding="utf-8"),
            )
            project = json.loads((root / "wechat-miniprogram" / "project.config.json").read_text(encoding="utf-8"))
            self.assertEqual(project["appid"], "wx1234567890abcdef")

    def test_dry_run_does_not_write_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_minimal_repo(root)
            before = (root / "config.js").read_text(encoding="utf-8")

            configure_production.configure(
                root,
                "https://api.fithub.example.com",
                "wx1234567890abcdef",
                dry_run=True,
            )

            self.assertEqual((root / "config.js").read_text(encoding="utf-8"), before)


if __name__ == "__main__":
    unittest.main()
