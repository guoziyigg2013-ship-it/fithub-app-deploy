import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "scripts" / "wechat_domain_manifest.py"
SPEC = importlib.util.spec_from_file_location("wechat_domain_manifest", MANIFEST_PATH)
wechat_domain_manifest = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(wechat_domain_manifest)


def write_app(root: Path, *, api_base: str, appid: str) -> None:
    mini = root / "wechat-miniprogram"
    mini.mkdir(parents=True, exist_ok=True)
    (mini / "config.js").write_text(f'module.exports = {{ apiBase: "{api_base}" }};\n', encoding="utf-8")
    (mini / "project.config.json").write_text('{"appid": "' + appid + '"}\n', encoding="utf-8")


def write_cos_env(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "FITHUB_MEDIA_STORAGE_PROVIDER=cos",
                "FITHUB_TENCENT_COS_PUBLIC_BASE_URL=https://media.fithub.example.cn",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


class WeChatDomainManifestTests(unittest.TestCase):
    def test_manifest_blocks_tourist_appid_and_render_domain(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_app(root, api_base="https://fithub-app-1btg.onrender.com/api", appid="touristappid")

            manifest = wechat_domain_manifest.build_manifest(
                root=root,
                env_file=root / "deploy" / "tencent-cloud" / ".env.production",
                require_cos_media=False,
            )

        self.assertFalse(manifest["ready"])
        details = "\n".join(str(item["detail"]) for item in manifest["items"])
        self.assertIn("touristappid", details)
        self.assertIn("onrender.com", details)

    def test_manifest_accepts_custom_api_and_cos_download_domain(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_app(root, api_base="https://api.fithub.example.cn/api", appid="wx1234567890abcdef")
            env_file = root / "deploy" / "tencent-cloud" / ".env.production"
            write_cos_env(env_file)

            manifest = wechat_domain_manifest.build_manifest(root=root, env_file=env_file)

        self.assertTrue(manifest["ready"])
        self.assertEqual(manifest["domains"]["request"], ["https://api.fithub.example.cn"])
        self.assertEqual(manifest["domains"]["uploadFile"], ["https://api.fithub.example.cn"])
        self.assertEqual(manifest["domains"]["downloadFile"], ["https://media.fithub.example.cn"])

    def test_origin_from_url_strips_path_query_and_trailing_slash(self):
        self.assertEqual(
            wechat_domain_manifest.origin_from_url("https://api.fithub.example.cn/api?x=1"),
            "https://api.fithub.example.cn",
        )


if __name__ == "__main__":
    unittest.main()
