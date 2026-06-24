import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
GATE_PATH = ROOT / "scripts" / "tencent_launch_gate.py"
SPEC = importlib.util.spec_from_file_location("tencent_launch_gate", GATE_PATH)
tencent_launch_gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tencent_launch_gate)


def write_app(root: Path, *, api_origin: str, api_base: str, appid: str) -> None:
    mini = root / "wechat-miniprogram"
    mini.mkdir(parents=True, exist_ok=True)
    (root / "config.js").write_text(
        f'window.__FITHUB_CONFIG__ = {{ apiOrigin: "{api_origin}" }};\n',
        encoding="utf-8",
    )
    (mini / "config.js").write_text(f'module.exports = {{ apiBase: "{api_base}" }};\n', encoding="utf-8")
    (mini / "project.config.json").write_text(
        '{"appid": "' + appid + '", "projectname": "fithub-miniprogram"}\n',
        encoding="utf-8",
    )


def write_cos_env(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "PORT=10000",
                "FITHUB_URL_PREFIX=/",
                "FITHUB_DATA_DIR=/data/fithub",
                "FITHUB_PUBLIC_API_ORIGIN=https://api.fithub.example.cn",
                "FITHUB_STATE_STORAGE_PROVIDER=supabase",
                "SUPABASE_URL=https://abcdefghijklmnopqrst.supabase.co",
                "SUPABASE_SERVICE_ROLE_KEY=" + "s" * 80,
                "FITHUB_SUPABASE_TABLE=fithub_app_state",
                "FITHUB_SUPABASE_ROW_ID=primary",
                "FITHUB_ADMIN_TOKEN=" + "a" * 32,
                "FITHUB_MEDIA_MAINTENANCE_TOKEN=" + "b" * 32,
                "FITHUB_MEDIA_STORAGE_PROVIDER=cos",
                "FITHUB_MEDIA_BUCKET=fithub-media",
                "FITHUB_TENCENT_COS_SECRET_ID=AKIDEXAMPLE",
                "FITHUB_TENCENT_COS_SECRET_KEY=cos-secret-key-example",
                "FITHUB_TENCENT_COS_REGION=ap-guangzhou",
                "FITHUB_TENCENT_COS_BUCKET=fithub-media-1250000000",
                "FITHUB_TENCENT_COS_PUBLIC_BASE_URL=https://media.fithub.example.cn",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


class TencentLaunchGateTests(unittest.TestCase):
    def test_gate_blocks_current_prelaunch_shape(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_app(
                root,
                api_origin="https://fithub-app-1btg.onrender.com",
                api_base="https://fithub-app-1btg.onrender.com/api",
                appid="touristappid",
            )

            report = tencent_launch_gate.build_gate(
                root=root,
                env_file=root / "deploy" / "tencent-cloud" / ".env.production",
            )

        self.assertFalse(report["ready"])
        self.assertGreaterEqual(report["blockerCount"], 3)
        details = "\n".join(phase["detail"] for phase in report["phases"])
        self.assertIn("onrender.com", details)
        self.assertIn("touristappid", details)
        self.assertIn("cutover:tencent", "\n".join(report["nextSteps"]))
        self.assertIn("真实小程序 AppID", "\n".join(report["nextSteps"]))
        self.assertTrue(report["blockedDetails"])

    def test_gate_passes_ready_static_configs_and_mocked_domain_network(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_app(
                root,
                api_origin="https://api.fithub.example.cn",
                api_base="https://api.fithub.example.cn/api",
                appid="wx1234567890abcdef",
            )
            env_file = root / "deploy" / "tencent-cloud" / ".env.production"
            write_cos_env(env_file)

            with mock.patch.object(
                tencent_launch_gate.tencent_domain_readiness,
                "build_report",
                return_value={"ready": True, "status": "ready", "blockerCount": 0, "domains": []},
            ):
                report = tencent_launch_gate.build_gate(
                    root=root,
                    env_file=env_file,
                    api_origin="https://api.fithub.example.cn",
                    web_origin="https://app.fithub.example.cn",
                    media_origin="https://media.fithub.example.cn",
                    check_domain_network=True,
                )

        self.assertTrue(report["ready"])
        self.assertEqual(report["blockerCount"], 0)
        self.assertEqual([phase["name"] for phase in report["phases"]], ["domestic-migration", "wechat-domains", "fixed-domains", "domain-network"])

    def test_gate_requires_web_and_media_domains(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_app(
                root,
                api_origin="https://api.fithub.example.cn",
                api_base="https://api.fithub.example.cn/api",
                appid="wx1234567890abcdef",
            )
            env_file = root / "deploy" / "tencent-cloud" / ".env.production"
            write_cos_env(env_file)

            report = tencent_launch_gate.build_gate(
                root=root,
                env_file=env_file,
                api_origin="https://api.fithub.example.cn",
            )

        self.assertFalse(report["ready"])
        details = "\n".join(phase["detail"] for phase in report["phases"])
        self.assertIn("用户访问固定域名 is missing", details)
        self.assertIn("media.yourdomain.com", details)
        next_steps = "\n".join(report["nextSteps"])
        self.assertIn("Web 固定域名", next_steps)
        self.assertIn("媒体固定域名", next_steps)


if __name__ == "__main__":
    unittest.main()
