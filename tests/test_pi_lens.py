"""Pi lens: npm:pi-lens declared at user scope for every repo, its read-only stance merged under ~/.pi-lens/config.json."""

import json
import unittest

from support import ROOT, HomeCase

BASE = json.loads((ROOT / "agents/.pi/settings.base.json").read_text())
LENS_BASE = ROOT / "agents/.pi/pi-lens.base.json"


class PiLensTest(HomeCase):
    """install.sh against a temp HOME: the global pi-lens activation and config merge."""

    def lens_path(self):
        return self.home / ".pi-lens" / "config.json"

    def settings_path(self):
        return self.home / ".pi" / "agent" / "settings.json"

    def test_the_tracked_base_declares_pi_lens_for_every_project(self):
        self.assertIn("npm:pi-lens", BASE["packages"])

    def test_a_new_home_gets_the_global_lens_config_where_pi_lens_looks(self):
        self.install()
        self.assertTrue(self.lens_path().is_file(), "pi-lens reads ~/.pi-lens/config.json")
        self.assertEqual(json.loads(self.lens_path().read_text()), json.loads(LENS_BASE.read_text()))

    def test_the_tracked_stance_is_disabled_and_read_only(self):
        stance = json.loads(LENS_BASE.read_text())
        self.assertIs(stance["lens"]["enabled"], False, "benchmark: no LSP calls, warmup + read-guard cost only")
        self.assertIn("typos", stance["lsp"]["disabledServers"])
        self.assertIs(stance["format"]["enabled"], False)
        self.assertIs(stance["autofix"]["enabled"], False)
        self.assertIs(stance["actionableWarnings"]["autoFix"]["enabled"], False)

    def test_the_users_own_values_win_over_the_tracked_stance(self):
        lens = self.lens_path()
        lens.parent.mkdir(parents=True, exist_ok=True)
        lens.write_text(json.dumps({"format": {"enabled": True}, "ignore": ["scratch/**"]}))
        self.install()
        merged = json.loads(lens.read_text())
        self.assertIs(merged["format"]["enabled"], True, "the user's own value wins")
        self.assertEqual(merged["ignore"], ["scratch/**"])
        tracked = json.loads(LENS_BASE.read_text())
        self.assertIs(merged["autofix"]["enabled"], tracked["autofix"]["enabled"],
                      "the tracked default still fills the gap")
        self.assertEqual(merged["lsp"]["disabledServers"], tracked["lsp"]["disabledServers"])

    def test_a_live_settings_file_keeps_its_own_packages_and_gains_pi_lens(self):
        settings = self.settings_path()
        settings.parent.mkdir(parents=True, exist_ok=True)
        settings.write_text(json.dumps({"packages": ["npm:pi-starline"], "defaultModel": "mine"}))
        self.install()
        merged = json.loads(settings.read_text())
        self.assertIn("npm:pi-starline", merged["packages"])
        self.assertIn("npm:pi-lens", merged["packages"])
        self.assertEqual(merged["defaultModel"], "mine")

    def test_rerunning_the_installer_leaves_the_lens_config_alone(self):
        self.install()
        first = self.lens_path().read_bytes()
        self.install()
        self.assertEqual(self.lens_path().read_bytes(), first)
        self.assertEqual(list(self.lens_path().parent.glob("config.json.bak-*")), [])

    def test_an_invalid_live_lens_config_is_backed_up_and_left_untouched(self):
        lens = self.lens_path()
        lens.parent.mkdir(parents=True, exist_ok=True)
        lens.write_text("{not json")
        done = self.install()
        self.assertEqual(lens.read_text(), "{not json")
        self.assertEqual(len(list(lens.parent.glob("config.json.bak-*"))), 1)
        self.assertIn("not valid JSON", done.stdout + done.stderr)

    def test_neither_base_nor_generated_config_holds_a_credential(self):
        for path in (LENS_BASE,):
            text = path.read_text().lower()
            for secret in ("api_key", "apikey", "bearer", "password", "secret"):
                self.assertNotIn(secret, text, f"{path.name}: {secret}")
        self.install()
        text = self.lens_path().read_text().lower()
        for secret in ("api_key", "apikey", "bearer", "password", "secret"):
            self.assertNotIn(secret, text, f"config.json: {secret}")


if __name__ == "__main__":
    unittest.main()
