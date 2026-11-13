"""Shared helpers: run install.sh against a temp HOME with fixture repos."""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALL = ROOT / "install.sh"
RUNTIME_SRC = next((Path(p) for p in (os.environ.get("AGENT_RUNTIME_SRC"), str(Path.home() / "developer/agent-runtime"))
                    if p and (Path(p) / ".claude-plugin" / "marketplace.json").is_file()), None)


def git(*args, cwd):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *args], cwd=cwd,
                   check=True, capture_output=True)


def make_skills(repo, names):
    for name in names:
        skill = Path(repo) / "skills" / name
        skill.mkdir(parents=True, exist_ok=True)
        (skill / "SKILL.md").write_text(f"---\nname: {name}\n---\n")
    return Path(repo)


def make_repo(path, names=()):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    make_skills(path, names)
    (path / "README.md").write_text("fixture\n")
    git("init", "-q", "-b", "main", cwd=path)
    git("add", "-A", cwd=path)
    git("commit", "-q", "-m", "init", cwd=path)
    return path


def make_runtime_stub(path):
    """A runtime checkout whose install.sh records BIN_DIR and creates the three shims."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    (path / "install.sh").write_text(
        '#!/bin/sh\nmkdir -p "$BIN_DIR"\nfor n in agent-runtime agent-runtime-hook agent-runtime-mcp; do\n'
        '  printf "#!/bin/sh\\n" > "$BIN_DIR/$n"; chmod +x "$BIN_DIR/$n"\ndone\n')
    (path / "install.sh").chmod(0o755)
    # The MCP server the Pi entry names: a checkout install points at this file.
    server = path / "server" / "mcp_server.py"
    server.parent.mkdir(parents=True, exist_ok=True)
    server.write_text('"""The stub MCP server."""\n')
    return path


class HomeCase(unittest.TestCase):
    """A temp HOME with fixture skill and runtime repos already cloned."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.home = self.tmp / "home"
        self.home.mkdir()
        self.dev = self.home / "developer"
        self.skills = make_repo(self.dev / "agent-skills", ["alpha", "beta"])
        self.fleet = make_repo(self.dev / "agent-fleet", ["secret"])
        self.runtime = make_runtime_stub(self.dev / "agent-runtime")

    def env(self, **extra):
        env = {"PATH": os.environ["PATH"], "HOME": str(self.home),
               "AGENT_SKILLS_DIR": str(self.skills), "AGENT_FLEET_DIR": str(self.fleet),
               "AGENT_RUNTIME_DIR": str(self.runtime), "DOTFILES_PRIVATE": str(self.tmp / "no-overlay")}
        env.update({k: str(v) for k, v in extra.items()})
        return env

    def install(self, *args, check=True, **extra):
        done = subprocess.run([str(INSTALL), "--no-stow", *args], env=self.env(**extra), cwd=self.tmp,
                              capture_output=True, text=True, timeout=120)
        if check:
            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        return done
