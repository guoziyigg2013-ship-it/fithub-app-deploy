import base64
import importlib
import unittest


server = importlib.import_module("server")


class TencentCosMediaTests(unittest.TestCase):
    def setUp(self):
        self.originals = {
            "MEDIA_STORAGE_PROVIDER": server.MEDIA_STORAGE_PROVIDER,
            "TENCENT_COS_SECRET_ID": server.TENCENT_COS_SECRET_ID,
            "TENCENT_COS_SECRET_KEY": server.TENCENT_COS_SECRET_KEY,
            "TENCENT_COS_REGION": server.TENCENT_COS_REGION,
            "TENCENT_COS_BUCKET": server.TENCENT_COS_BUCKET,
            "TENCENT_COS_PUBLIC_BASE_URL": server.TENCENT_COS_PUBLIC_BASE_URL,
            "upload_cos_media_asset": server.upload_cos_media_asset,
        }

    def tearDown(self):
        for key, value in self.originals.items():
            setattr(server, key, value)

    def enable_cos(self):
        server.MEDIA_STORAGE_PROVIDER = "cos"
        server.TENCENT_COS_SECRET_ID = "AKIDEXAMPLE"
        server.TENCENT_COS_SECRET_KEY = "secret-key-example"
        server.TENCENT_COS_REGION = "ap-guangzhou"
        server.TENCENT_COS_BUCKET = "fithub-media-1250000000"
        server.TENCENT_COS_PUBLIC_BASE_URL = "https://media.fithub.example.cn"

    def test_runtime_config_prefers_tencent_cos_when_configured(self):
        self.enable_cos()

        config = server.runtime_config()

        self.assertEqual(config["mediaStorageProvider"], "cos")
        self.assertEqual(config["mediaBucket"], "fithub-media-1250000000")

    def test_upload_media_asset_uses_cos_provider_and_public_url(self):
        self.enable_cos()
        captured = {}

        def fake_upload(binary, *, object_path, content_type):
            captured["binary"] = binary
            captured["object_path"] = object_path
            captured["content_type"] = content_type
            return server.build_cos_public_media_url(object_path)

        server.upload_cos_media_asset = fake_upload
        data_url = "data:image/png;base64," + base64.b64encode(b"fake-png").decode("ascii")

        media = server.upload_media_asset(
            data_url,
            file_name="头像.png",
            category="avatars",
            asset_type="image",
        )

        self.assertEqual(media["storageProvider"], "cos")
        self.assertEqual(media["contentType"], "image/png")
        self.assertEqual(captured["binary"], b"fake-png")
        self.assertTrue(captured["object_path"].startswith("avatars/"))
        self.assertTrue(media["url"].startswith("https://media.fithub.example.cn/avatars/"))

    def test_cos_authorization_contains_required_v5_fields(self):
        self.enable_cos()

        auth = server.cos_authorization(
            "PUT",
            "avatars/2026/06/24/demo.png",
            {"Host": server.cos_storage_host(), "Content-Type": "image/png"},
        )

        self.assertIn("q-sign-algorithm=sha1", auth)
        self.assertIn("q-ak=AKIDEXAMPLE", auth)
        self.assertIn("q-header-list=content-type;host", auth)
        self.assertIn("q-signature=", auth)


if __name__ == "__main__":
    unittest.main()
