"""Pi extension configs: rtk-optimizer, ollama-cloud and permission-system bases merged under the user's live files."""

import json
import unittest

from support import ROOT, HomeCase

BASE = json.loads((ROOT / "agents/.pi/settings.base.json").read_text())
RTK_BASE = ROOT / "agents/.pi/rtk-optimizer.base.json"
OLLAMA_BASE = ROOT / "agents/.pi/ollama-cloud.base.json"
PERMISSION_BASE = ROOT / "agents/.pi/permission-system.base.json"


class PiExtensionConfigsTest(HomeCase):
    """install.sh against a temp HOME: the three extension config merges only."""

    def agent_dir(self):
        return self.home / ".pi" / "agent"

    def rtk_path(self):
        return self.agent_dir() / "extensions" / "pi-rtk-optimizer" / "config.json"

    def ollama_path(self):
        return self.agent_dir() / "ollama-cloud.json"

    def permission_path(self):
        return self.agent_dir() / "extensions" / "pi-permission-system" / "config.json"

    def all_paths(self):
        return (self.rtk_path(), self.ollama_path(), self.permission_path())

    def test_the_tracked_base_declares_the_packages(self):
        self.assertIn("npm:pi-rtk-optimizer@0.9.0", BASE["packages"])
        self.assertIn("npm:pi-ollama-cloud", BASE["packages"])
        self.assertIn("npm:@gotgenes/pi-permission-system", BASE["packages"])

    def test_a_new_home_gets_the_configs_where_the_extensions_look(self):
        self.install()
        for path, base in ((self.rtk_path(), RTK_BASE), (self.ollama_path(), OLLAMA_BASE),
                           (self.permission_path(), PERMISSION_BASE)):
            self.assertTrue(path.is_file(), f"the extension reads {path}")
            self.assertEqual(json.loads(path.read_text()), json.loads(base.read_text()))

    def test_the_users_own_values_win_over_the_tracked_defaults(self):
        rtk = self.rtk_path()
        rtk.parent.mkdir(parents=True, exist_ok=True)
        rtk.write_text(json.dumps({"enabled": False, "outputCompaction": {"truncate": {"maxChars": 5000}}}))
        ollama = self.ollama_path()
        ollama.parent.mkdir(parents=True, exist_ok=True)
        ollama.write_text(json.dumps({"webTools": True}))
        permission = self.permission_path()
        permission.parent.mkdir(parents=True, exist_ok=True)
        permission.write_text(json.dumps({"permission": {"bash": {"sudo *": "deny"}}}))
        self.install()
        merged = json.loads(rtk.read_text())
        self.assertIs(merged["enabled"], False, "the user's own value wins")
        self.assertEqual(merged["outputCompaction"]["truncate"]["maxChars"], 5000)
        tracked = json.loads(RTK_BASE.read_text())
        self.assertEqual(merged["mode"], tracked["mode"], "the tracked default still fills the gap")
        self.assertEqual(merged["outputCompaction"]["aggregateTestOutput"],
                         tracked["outputCompaction"]["aggregateTestOutput"])
        merged_ollama = json.loads(ollama.read_text())
        self.assertIs(merged_ollama["webTools"], True)
        self.assertIs(merged_ollama["usageStatus"], json.loads(OLLAMA_BASE.read_text())["usageStatus"])
        merged_permission = json.loads(permission.read_text())
        self.assertEqual(merged_permission["permission"]["bash"]["sudo *"], "deny", "the user's own rule wins")
        tracked_permission = json.loads(PERMISSION_BASE.read_text())
        self.assertEqual(merged_permission["permission"]["path"], tracked_permission["permission"]["path"],
                         "the tracked denylist still fills the gap")
        self.assertEqual(merged_permission["permission"]["bash"]["rm -rf *"], "ask")

    def test_rerunning_the_installer_leaves_the_configs_alone(self):
        self.install()
        first = {path: path.read_bytes() for path in self.all_paths()}
        self.install()
        for path in self.all_paths():
            self.assertEqual(path.read_bytes(), first[path])
            self.assertEqual(list(path.parent.glob(path.name + ".bak-*")), [])

    def test_invalid_live_configs_are_backed_up_and_left_untouched(self):
        for path in self.all_paths():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("{not json")
        done = self.install()
        for path in self.all_paths():
            self.assertEqual(path.read_text(), "{not json")
            self.assertEqual(len(list(path.parent.glob(path.name + ".bak-*"))), 1)
        self.assertIn("not valid JSON", done.stdout + done.stderr)

    def test_neither_base_nor_generated_config_holds_a_credential(self):
        for base in (RTK_BASE, OLLAMA_BASE, PERMISSION_BASE):
            text = base.read_text().lower()
            for secret in ("api_key", "apikey", "bearer", "password", "secret", "ollama_api_key"):
                self.assertNotIn(secret, text, f"{base.name}: {secret}")
        self.install()
        for path in self.all_paths():
            text = path.read_text().lower()
            for secret in ("api_key", "apikey", "bearer", "password", "secret", "ollama_api_key"):
                self.assertNotIn(secret, text, f"{path.name}: {secret}")

    def test_the_permission_denylist_keeps_the_catch_all_first(self):
        """Last-match-wins: a catch-all after the denies would shadow them."""
        policy = json.loads(PERMISSION_BASE.read_text())["permission"]
        for surface in ("path", "bash", "external_directory"):
            keys = list(policy[surface].keys())
            self.assertEqual(keys[0], "*", f"{surface}: the catch-all must come first")
        path = policy["path"]
        self.assertEqual(path["*.env.example"], "allow", "templates stay readable")
        self.assertEqual(path["~/.pi/agent/auth.json"], "deny")

    def test_outside_cwd_asks_except_the_work_hubs(self):
        config = json.loads(PERMISSION_BASE.read_text())
        ext = config["permission"]["external_directory"]
        self.assertEqual(ext["*"], "ask")
        for hub in ("~/developer/*", "~/claude/*", "~/ulixee-cloud/*", "~/ocr-test/*", "~/.agents/*"):
            self.assertEqual(ext[hub], "allow", hub)
        self.assertNotIn("~/Library/*", ext, "personal dirs stay behind the prompt")
        self.assertEqual(config["promptTimeoutMs"], 60000, "unanswered prompts deny, not hang")
        self.assertIn("~/.pi/agent/*.json", config["piInfrastructureReadPaths"])


if __name__ == "__main__":
    unittest.main()
