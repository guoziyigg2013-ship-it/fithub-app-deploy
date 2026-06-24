import importlib.util
import time
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
READINESS_PATH = ROOT / "scripts" / "tencent_domain_readiness.py"
SPEC = importlib.util.spec_from_file_location("tencent_domain_readiness", READINESS_PATH)
tencent_domain_readiness = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tencent_domain_readiness)


def fake_tcp_ok(host: str, port: int, timeout: float):
    return True, ""


def fake_tls_ok(host: str, timeout: float):
    return {
        "ok": True,
        "host": host,
        "subject": "CN=" + host,
        "sans": [host],
        "notAfter": "",
        "expiresAt": int(time.time()) + 90 * 86400,
        "daysRemaining": 90,
        "cipher": "TLS_AES_256_GCM_SHA384",
        "elapsedMs": 12,
    }


class TencentDomainReadinessTests(unittest.TestCase):
    def test_build_targets_rejects_render_domain(self):
        with self.assertRaisesRegex(ValueError, "onrender.com"):
            tencent_domain_readiness.build_targets("https://fithub-app-1btg.onrender.com")

    def test_report_ready_when_dns_ip_acme_and_tls_pass(self):
        report = tencent_domain_readiness.build_report(
            api_origin="https://api.fithub.example.cn",
            web_origin="https://app.fithub.example.cn",
            expected_ip="1.2.3.4",
            check_acme=True,
            check_tls=True,
            resolver=lambda host: ["1.2.3.4"],
            tcp_probe=fake_tcp_ok,
            tls_checker=fake_tls_ok,
        )

        self.assertTrue(report["ready"])
        self.assertEqual(report["blockerCount"], 0)
        self.assertEqual([domain["role"] for domain in report["domains"]], ["api", "web"])

    def test_report_blocks_expected_ip_mismatch(self):
        report = tencent_domain_readiness.build_report(
            api_origin="https://api.fithub.example.cn",
            expected_ip="1.2.3.4",
            resolver=lambda host: ["5.6.7.8"],
        )

        self.assertFalse(report["ready"])
        details = "\n".join(check["detail"] for domain in report["domains"] for check in domain["checks"])
        self.assertIn("expected 1.2.3.4", details)
        self.assertIn("5.6.7.8", details)

    def test_report_blocks_acme_port_failure(self):
        report = tencent_domain_readiness.build_report(
            api_origin="https://api.fithub.example.cn",
            check_acme=True,
            resolver=lambda host: ["1.2.3.4"],
            tcp_probe=lambda host, port, timeout: (False, "connection refused"),
        )

        self.assertFalse(report["ready"])
        details = "\n".join(check["detail"] for domain in report["domains"] for check in domain["checks"])
        self.assertIn("port 80 unreachable", details)


if __name__ == "__main__":
    unittest.main()
