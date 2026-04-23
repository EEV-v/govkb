"""Tests for one-command project install."""

from __future__ import annotations

import argparse
import os
import tempfile
from pathlib import Path
import unittest

from govkb.commands.install import run_install
from govkb.core.install_state import install_state_path
from govkb.core.install_state import load_install_state


class InstallCommandTests(unittest.TestCase):
    """Install orchestration behavior."""

    def test_install_scaffolds_validates_and_applies_codex(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "DemoProject"
            codex_home = Path(temp_dir) / "codex-home"
            project_root.mkdir(parents=True, exist_ok=True)

            exit_code = run_install(
                argparse.Namespace(
                    project_root=project_root,
                    project_id="demo-project",
                    project_name="Demo Project",
                    codex_home=codex_home,
                    release=None,
                    revision="install-test",
                    preview=False,
                    cron=False,
                    schedule="15 8 * * *",
                )
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue((project_root / ".governed" / "project.toml").is_file())
            script_path = codex_home / "bin" / "codex-memory-review"
            self.assertTrue(script_path.is_file())
            self.assertTrue(os.access(script_path, os.X_OK))
            self.assertTrue((codex_home / "skills" / "govkb-demo-project-project-knowledge-steward").is_dir())
            state = load_install_state(install_state_path(codex_home, "demo-project", "codex"))
            self.assertIsNotNone(state)
            self.assertEqual(state["revision"], "install-test")

    def test_install_preview_does_not_create_governed_package(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "DemoProject"
            codex_home = Path(temp_dir) / "codex-home"
            project_root.mkdir(parents=True, exist_ok=True)

            exit_code = run_install(
                argparse.Namespace(
                    project_root=project_root,
                    project_id="demo-project",
                    project_name="Demo Project",
                    codex_home=codex_home,
                    release=None,
                    revision=None,
                    preview=True,
                    cron=False,
                    schedule="15 8 * * *",
                )
            )

            self.assertEqual(exit_code, 0)
            self.assertFalse((project_root / ".governed").exists())
            self.assertFalse(codex_home.exists())


if __name__ == "__main__":
    unittest.main()
