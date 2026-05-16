"""Tests for the public review-memory command wrapper."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch
import unittest

from govkb.commands.review_memory import run_review_memory


class ReviewMemoryCommandTests(unittest.TestCase):
    """Command wrapper behavior for the Codex memory-review adapter."""

    def test_review_memory_passes_low_cost_classifier_options(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            project_root = root / "Project"
            codex_home = root / "codex-home"
            classifier_home = root / "classifier-codex-home"
            script = root / "codex-memory-review"
            project_root.mkdir()
            codex_home.mkdir()
            classifier_home.mkdir()
            script.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")

            captured: dict[str, object] = {}

            def fake_run(cmd, **kwargs):
                captured["cmd"] = list(cmd)
                captured["env"] = dict(kwargs["env"])
                return subprocess.CompletedProcess(cmd, 0)

            args = argparse.Namespace(
                assistant="codex",
                project_root=project_root,
                dry_run=True,
                lookback_days=0.25,
                max_sessions=1,
                verbose=False,
                codex_timeout=120,
                classifier_codex_home=classifier_home,
                codex_model="gpt-5.4-mini",
                codex_reasoning="low",
                session_file=root / "session.jsonl",
                auto_promote=False,
            )

            with patch.dict(
                os.environ,
                {
                    "CODEX_HOME": str(codex_home),
                    "GOVKB_CODEX_MEMORY_REVIEW": str(script),
                },
            ), patch("govkb.commands.review_memory.subprocess.run", side_effect=fake_run):
                exit_code = run_review_memory(args)

            self.assertEqual(exit_code, 0)
            cmd = captured["cmd"]
            self.assertIn("--codex-model", cmd)
            self.assertEqual(cmd[cmd.index("--codex-model") + 1], "gpt-5.4-mini")
            self.assertIn("--codex-reasoning", cmd)
            self.assertEqual(cmd[cmd.index("--codex-reasoning") + 1], "low")
            self.assertIn("--codex-timeout", cmd)
            self.assertIn("--classifier-codex-home", cmd)
            self.assertEqual(cmd[cmd.index("--classifier-codex-home") + 1], str(classifier_home))
            self.assertIn("--no-auto-promote", cmd)
            self.assertEqual(captured["env"]["GOVKB_PROJECT_ROOT"], str(project_root.resolve()))

    def test_review_memory_runs_python_script_with_current_interpreter(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            project_root = root / "Project"
            codex_home = root / "codex-home"
            script = root / "codex-memory-review"
            project_root.mkdir()
            codex_home.mkdir()
            script.write_text("#!/usr/bin/env python3\nraise SystemExit(0)\n", encoding="utf-8")

            captured: dict[str, object] = {}

            def fake_run(cmd, **kwargs):
                captured["cmd"] = list(cmd)
                return subprocess.CompletedProcess(cmd, 0)

            args = argparse.Namespace(
                assistant="codex",
                project_root=project_root,
                dry_run=True,
                lookback_days=None,
                max_sessions=1,
                verbose=False,
                codex_timeout=120,
                classifier_codex_home=None,
                codex_model=None,
                codex_reasoning=None,
                session_file=None,
                auto_promote=True,
            )

            with patch.dict(
                os.environ,
                {
                    "CODEX_HOME": str(codex_home),
                    "GOVKB_CODEX_MEMORY_REVIEW": str(script),
                },
            ), patch("govkb.commands.review_memory.subprocess.run", side_effect=fake_run):
                exit_code = run_review_memory(args)

            self.assertEqual(exit_code, 0)
            self.assertEqual(captured["cmd"][0], sys.executable)
            self.assertEqual(captured["cmd"][1], str(script))

    def test_review_memory_forwards_inventory_and_progress_flags(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            project_root = root / "Project"
            codex_home = root / "codex-home"
            script = root / "codex-memory-review"
            project_root.mkdir()
            codex_home.mkdir()
            script.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")

            captured: dict[str, object] = {}

            def fake_run(cmd, **kwargs):
                captured["cmd"] = list(cmd)
                return subprocess.CompletedProcess(cmd, 0)

            args = argparse.Namespace(
                assistant="codex",
                project_root=project_root,
                dry_run=True,
                inventory_json=True,
                progress_jsonl=True,
                lookback_days=90,
                max_sessions=5,
                verbose=False,
                codex_timeout=120,
                classifier_codex_home=None,
                codex_model=None,
                codex_reasoning=None,
                session_file=None,
                auto_promote=True,
            )

            with patch.dict(
                os.environ,
                {
                    "CODEX_HOME": str(codex_home),
                    "GOVKB_CODEX_MEMORY_REVIEW": str(script),
                },
            ), patch("govkb.commands.review_memory.subprocess.run", side_effect=fake_run):
                exit_code = run_review_memory(args)

            self.assertEqual(exit_code, 0)
            cmd = captured["cmd"]
            self.assertIn("--inventory-json", cmd)
            self.assertIn("--progress-jsonl", cmd)


if __name__ == "__main__":
    unittest.main()
