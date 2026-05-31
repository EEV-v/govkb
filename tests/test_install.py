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
            resolved_project_root = project_root.resolve()
            resolved_old_home = old_home.resolve()
            resolved_new_home = new_home.resolve()

            existing_cron = _cron_line(resolved_project_root, resolved_old_home, "15 8 * * *") + "\n"
            captured_crontab: dict[str, str] = {}

            def fake_run(cmd, **kwargs):
                if cmd == ["crontab", "-l"]:
                    return type("Completed", (), {"returncode": 0, "stdout": existing_cron, "stderr": ""})()
                if cmd == ["crontab", "-"]:
                    captured_crontab["input"] = kwargs["input"]
                    return type("Completed", (), {"returncode": 0, "stdout": "", "stderr": ""})()
                if cmd[:3] == ["git", "-C", str(resolved_project_root)] and cmd[3:] == ["rev-parse", "HEAD"]:
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
            self.assertIn(f"CODEX_HOME={resolved_new_home}", captured_crontab["input"])
            self.assertIn(str(resolved_new_home / "bin" / "codex-memory-review"), captured_crontab["input"])
            self.assertNotIn(str(resolved_old_home / "bin" / "codex-memory-review"), captured_crontab["input"])
            self.assertIn("Cron: updated project-scoped memory-review job", output.getvalue())

    def test_install_cron_preserves_existing_project_job_settings_when_not_overridden(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "DemoProject"
            old_home = Path(temp_dir) / "old-codex-home"
            new_home = Path(temp_dir) / "new-codex-home"
            project_root.mkdir(parents=True, exist_ok=True)
            resolved_project_root = project_root.resolve()
            resolved_old_home = old_home.resolve()
            resolved_new_home = new_home.resolve()

            existing_cron = (
                _cron_line(
                    resolved_project_root,
                    resolved_old_home,
                    "5 7 * * 1-5",
                    inherited_env={
                        "GOVKB_CODEX_REASONING": "xhigh",
                        "GOVKB_CODEX_MODEL": "gpt-5.4-mini",
                        "GOVKB_CLASSIFIER_CODEX_HOME": "/home/ev/.codex",
                    },
                )
                + "\n"
            )
            captured_crontab: dict[str, str] = {}

            def fake_run(cmd, **kwargs):
                if cmd == ["crontab", "-l"]:
                    return type("Completed", (), {"returncode": 0, "stdout": existing_cron, "stderr": ""})()
                if cmd == ["crontab", "-"]:
                    captured_crontab["input"] = kwargs["input"]
                    return type("Completed", (), {"returncode": 0, "stdout": "", "stderr": ""})()
                if cmd[:3] == ["git", "-C", str(resolved_project_root)] and cmd[3:] == ["rev-parse", "HEAD"]:
                    return type("Completed", (), {"returncode": 1, "stdout": "", "stderr": ""})()
                raise AssertionError(f"unexpected command: {cmd}")

            with patch("govkb.commands.install.subprocess.run", side_effect=fake_run):
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
                        schedule=None,
                    )
                )

            self.assertEqual(exit_code, 0)
            self.assertIn("5 7 * * 1-5", captured_crontab["input"])
            self.assertIn(f"CODEX_HOME={resolved_new_home}", captured_crontab["input"])
            self.assertIn("GOVKB_CODEX_REASONING=xhigh", captured_crontab["input"])
            self.assertIn("GOVKB_CODEX_MODEL=gpt-5.4-mini", captured_crontab["input"])
            self.assertIn("GOVKB_CLASSIFIER_CODEX_HOME=/home/ev/.codex", captured_crontab["input"])
            self.assertIn(str(resolved_new_home / "bin" / "codex-memory-review"), captured_crontab["input"])
            self.assertNotIn("15 8 * * *", captured_crontab["input"])

    def test_install_cron_preserves_existing_codex_home_when_not_overridden(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "DemoProject"
            codex_home = Path(temp_dir) / "existing-codex-home"
            project_root.mkdir(parents=True, exist_ok=True)
            resolved_project_root = project_root.resolve()
            resolved_codex_home = codex_home.resolve()

            existing_cron = (
                _cron_line(
                    resolved_project_root,
                    resolved_codex_home,
                    "5 7 * * 1-5",
                    inherited_env={"GOVKB_CODEX_REASONING": "xhigh"},
                )
                + "\n"
            )

            def fake_run(cmd, **kwargs):
                if cmd == ["crontab", "-l"]:
                    return type("Completed", (), {"returncode": 0, "stdout": existing_cron, "stderr": ""})()
                if cmd == ["git", "-C", str(resolved_project_root), "rev-parse", "HEAD"]:
                    return type("Completed", (), {"returncode": 1, "stdout": "", "stderr": ""})()
                raise AssertionError(f"unexpected command: {cmd}")

            output = io.StringIO()
            with patch.dict(os.environ, {"HOME": temp_dir}, clear=True):
                with patch("govkb.commands.install.subprocess.run", side_effect=fake_run):
                    with redirect_stdout(output):
                        exit_code = run_install(
                            argparse.Namespace(
                                project_root=project_root,
                                project_id=None,
                                project_name=None,
                                codex_home=None,
                                release=None,
                                revision=None,
                                preview=False,
                                cron=True,
                                schedule=None,
                            )
                        )

            self.assertEqual(exit_code, 0)
            self.assertIn(f"Codex home: {resolved_codex_home}", output.getvalue())
            self.assertIn("Cron: project-scoped memory-review job already exists", output.getvalue())
            self.assertIn("GOVKB_CODEX_REASONING=xhigh", existing_cron)


if __name__ == "__main__":
    unittest.main()
