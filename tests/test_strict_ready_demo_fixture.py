"""Regression coverage for the customer-demo strict-ready fixture."""

from __future__ import annotations

import argparse
from contextlib import redirect_stdout
import io
import json
import shutil
import tempfile
from pathlib import Path
import unittest

from govkb.commands.apply import run_codex_apply
from govkb.commands.status import run_status
from govkb.commands.validate import run_validate


REPO_ROOT = Path(__file__).resolve().parents[1]
STRICT_READY_DEMO = (
    REPO_ROOT
    / "docs"
    / "governed-skill-knowledge-framework"
    / "examples"
    / "strict-ready-demo-project"
)


class StrictReadyDemoFixtureTests(unittest.TestCase):
    """The static fixture should support the complete customer-demo happy path."""

    def test_strict_ready_demo_validates_applies_and_reports_current_status(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "strict-ready-demo-project"
            codex_home = Path(temp_dir) / "codex-home"
            shutil.copytree(STRICT_READY_DEMO, project_root)

            validate_output = io.StringIO()
            with redirect_stdout(validate_output):
                validate_exit = run_validate(
                    argparse.Namespace(project_root=project_root, strict=True, json=True)
                )
            self.assertEqual(validate_exit, 0, validate_output.getvalue())
            validate_payload = json.loads(validate_output.getvalue())
            self.assertTrue(validate_payload["valid"])
            self.assertEqual(validate_payload["strictIssues"], [])

            apply_exit = run_codex_apply(
                argparse.Namespace(
                    project_root=project_root,
                    release=None,
                    revision="strict-ready-demo",
                    codex_home=codex_home,
                    preview=False,
                )
            )
            self.assertEqual(apply_exit, 0)

            status_output = io.StringIO()
            with redirect_stdout(status_output):
                status_exit = run_status(
                    argparse.Namespace(
                        project_root=project_root,
                        codex_home=codex_home,
                        json=True,
                    )
                )
            self.assertEqual(status_exit, 0, status_output.getvalue())
            status_payload = json.loads(status_output.getvalue())
            self.assertEqual(status_payload["validation"]["status"], "ok")
            self.assertEqual(status_payload["installState"]["codex"]["status"], "present")
            self.assertEqual(status_payload["skillUpdates"]["state"], "current")


if __name__ == "__main__":
    unittest.main()
