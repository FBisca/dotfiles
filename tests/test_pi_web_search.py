"""Pi web search: the declared package, the extension's own config file and the key prerequisite (S1-S5)."""

import json
import re
import subprocess
import unittest
from pathlib import Path

from support import ROOT, HomeCase

BASE = json.loads((ROOT / "agents/.pi/settings.base.json").read_text())
TRACKED_CONFIG = ROOT / "agents/.pi/pi-web-search-lite.config.json"


class PiWebSearchTest(HomeCase):
    """install.sh against a temp HOME: the web search path only."""

    def agent_dir(self):
        return self.home / ".pi" / "agent"

    def config_path(self):
        return self.agent_dir() / "pi-web-search-lite" / "config.json"

    def config(self):
        return json.loads(self.config_path().read_text())

    def tracked(self):
        return json.loads(TRACKED_CONFIG.read_text())

    # S1: the package is declared and Pi's on-demand discovery is on.
    def test_the_tracked_base_declares_the_package_and_the_tool_search(self):
        """S1 the tracked base declares the package and enables tool_search."""
        self.assertIn("npm:pi-web-search-lite", BASE["packages"])
        self.assertIn("+tool_search", BASE["defaultTools"])

    def test_the_installed_pi_settings_carry_the_package_and_the_tool_search(self):
        """S1 the merged live settings carry the package and the tool."""
        self.install()
        settings = json.loads((self.agent_dir() / "settings.json").read_text())
        self.assertIn("npm:pi-web-search-lite", settings["packages"])
        self.assertIn("+tool_search", settings["defaultTools"])

    # S2: the extension finds its config where it looks for it, and the user's values win.
    def test_the_extension_config_is_written_where_the_extension_looks_for_it(self):
        """S2 the config lands in the pi agent dir, with the tracked defaults."""
        self.install()
        self.assertTrue(self.config_path().is_file(), "the extension reads <pi agent dir>/pi-web-search-lite/config.json")
        config = self.config()
        tracked = self.tracked()
        self.assertEqual(config["provider"], tracked["provider"])
        self.assertEqual(config["activation"], tracked["activation"])
        self.assertEqual(config["search"], tracked["search"])
        self.assertEqual(config["context"], tracked["context"])

    def test_the_users_own_values_in_the_live_config_win_over_the_tracked_ones(self):
        """S2 the user's file is merged over the tracked base, not replaced by it."""
        path = self.config_path()
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({"provider": "brave", "search": {"defaultMaxResults": 9}}))
        self.install()
        config = self.config()
        self.assertEqual(config["provider"], "brave", "the user's own value wins")
        self.assertEqual(config["search"]["defaultMaxResults"], 9)
        self.assertEqual(config["search"]["maxResultsLimit"], self.tracked()["search"]["maxResultsLimit"],
                         "the tracked default still fills the gap")
        self.assertEqual(config["context"], self.tracked()["context"])

    def test_rerunning_the_installer_leaves_the_web_search_config_alone(self):
        """S2 the installer is idempotent for the web search config."""
        self.install()
        first = self.config_path().read_bytes()
        self.install()
        self.assertEqual(self.config_path().read_bytes(), first)
        self.assertEqual(list(self.config_path().parent.glob("config.json.bak-*")), [])

    # S3: a broken live file is backed up, not replaced.
    def test_an_invalid_web_search_config_is_backed_up_and_left_untouched(self):
        """S3 a broken live file is backed up, not replaced."""
        path = self.config_path()
        path.parent.mkdir(parents=True)
        path.write_text("{not json")
        done = self.install()
        self.assertEqual(path.read_text(), "{not json")
        self.assertEqual(len(list(self.config_path().parent.glob("config.json.bak-*"))), 1)
        self.assertIn("not valid JSON", done.stdout + done.stderr)

    # S4: the key is a reported prerequisite, never written.
    def test_the_missing_key_is_reported_and_the_install_still_succeeds(self):
        """S4 a missing key is a reported prerequisite, never a failure."""
        done = self.install()
        output = done.stdout + done.stderr
        self.assertIn("EXA_API_KEY", output)
        self.assertTrue(self.config_path().is_file())

    def test_the_key_in_the_environment_is_reported_without_its_value(self):
        """S4 the key is reported as resolved and never printed."""
        done = self.install(EXA_API_KEY="exa-secret-value")
        output = done.stdout + done.stderr
        self.assertIn("EXA_API_KEY", output)
        self.assertNotIn("exa-secret-value", output, "the key is never printed")

    def test_the_tracked_and_generated_configs_carry_no_credential(self):
        """S4 neither the tracked base nor the generated file holds a key."""
        tracked = TRACKED_CONFIG.read_text()
        self.assertNotIn("apiKeys", tracked, "the extension's own key holder stays empty")
        self.assertNotIn("EXA_API_KEY", tracked, "the key is read from the environment, not from the file")
        self.install()
        live = self.config_path().read_text()
        self.assertNotIn("apiKeys", live)
        self.assertNotIn("EXA_API_KEY", live)

    def test_no_tracked_file_carries_the_search_key(self):
        """S4 no tracked file assigns a value to the key's name; naming it is fine."""
        pattern = re.compile(r"exa_api_key\s*=\s*[\"']?[A-Za-z0-9][A-Za-z0-9_-]{7,}", re.IGNORECASE)
        tracked = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, text=True,
                                 check=True).stdout.split("\0")
        for path in tracked:
            if not path or path == Path(__file__).relative_to(ROOT).as_posix():
                continue  # this test carries a dummy value on purpose
            if not (ROOT / path).is_file():
                continue
            try:
                text = (ROOT / path).read_text()
            except (UnicodeDecodeError, OSError):
                continue
            self.assertIsNone(pattern.search(text), path)


if __name__ == "__main__":
    unittest.main()
