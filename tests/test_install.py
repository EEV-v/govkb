"""Tests for one-command project install."""

from __future__ import annotations

import argparse
from contextlib import redirect_stdout
import io
import os
import tempfile
from pathlib import Path
from unittest.mock import patch
import unittest

from govkb.commands.install import _cron_line
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
            self.assertIn(f'os.environ["CODEX_HOME"] = {str(codex_home.resolve())!r}', script_path.read_text(encoding="utf-8"))
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

    def test_install_cron_updates_existing_project_job_when_codex_home_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "DemoProject"
            old_home = Path(temp_dir) / "old-codex-home"
            new_home = Path(temp_dir) / "new-codex-home"
            project_root.mkdir(parents=True, exist_ok=True)

            existing_cron = _cron_line(project_root, old_home, "15 8 * * *") + "\n"
            captured_crontab: dict[str, str] = {}

            def fake_run(cmd, **kwargs):
                if cmd == ["crontab", "-l"]:
                    return type("Completed", (), {"returncode": 0, "stdout": existing_cron, "stderr": ""})()
                if cmd == ["crontab", "-"]:
                    captured_crontab["input"] = kwargs["input"]
                    return type("Completed", (), {"returncode": 0, "stdout": "", "stderr": ""})()
                if cmd[:3] == ["git", "-C", str(project_root)] and cmd[3:] == ["rev-parse", "HEAD"]:
                    return type("Completed", (), {"returncode": 1, "stdout": "", "stderr": ""})()
                raise AssertionError(f"unexpected command: {cmd}")

            output = io.StringIO()
            with patch("govkb.commands.install.subprocess.run", side_effect=fake_run):
                with redirect_stdout(output):
                    exit_code = run_install(
                        argparse.Namespace(
                            project_root=project_root,
                            project_id="demo-project",
                            project_name="Demo Project",
                            codex_home=new_home,
                            release=None,
                            revision=None,
                            preview=False,
                            cron=True,
                            schedule="15 8 * * *",
                        )
                    )

            self.assertEqual(exit_code, 0)
            self.assertIn(f"CODEX_HOME={new_home}", captured_crontab["input"])
            self.assertIn(str(new_home / "bin" / "codex-memory-review"), captured_crontab["input"])
            self.assertNotIn(str(old_home / "bin" / "codex-memory-review"), captured_crontab["input"])
            self.assertIn("Cron: updated project-scoped memory-review job", output.getvalue())


if __name__ == "__main__":
    unittest.main()
