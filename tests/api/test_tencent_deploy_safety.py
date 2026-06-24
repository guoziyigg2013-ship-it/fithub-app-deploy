import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class TencentDeploySafetyTests(unittest.TestCase):
    def test_docker_compose_uses_stable_named_data_volume(self):
        compose = (ROOT / "deploy" / "tencent-cloud" / "docker-compose.yml").read_text(encoding="utf-8")

        self.assertIn("fithub-data:/data/fithub", compose)
        self.assertIn("name: fithub-data", compose)

    def test_deploy_script_backs_up_volume_before_compose_up(self):
        deploy = (ROOT / "deploy" / "tencent-cloud" / "deploy.sh").read_text(encoding="utf-8")
        backup_index = deploy.index("backup_data_volume")
        compose_up_index = deploy.index('"${COMPOSE[@]}" up -d --build')

        self.assertLess(backup_index, compose_up_index)
        self.assertIn("fithub-data-predeploy-", deploy)
        self.assertIn("FITHUB_DEPLOY_BACKUP_RETENTION", deploy)
        self.assertIn("FITHUB_SKIP_VOLUME_BACKUP", deploy)
        self.assertIn("legacy FitHub data volume", deploy)
        self.assertIn("fithub-storage-status-postdeploy-", deploy)


if __name__ == "__main__":
    unittest.main()
