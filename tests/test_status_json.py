"""Tests for machine-readable status output."""

from __future__ import annotations

import argparse
from contextlib import redirect_stdout
import io
import json
import tempfile
from pathlib import Path
import unittest

from govkb.commands.apply import run_codex_apply
from govkb.commands.init import run_init
from govkb.commands.status import build_status_payload
from govkb.commands.status import run_status


class StatusJsonTests(unittest.TestCase):
    """Machine-readable status contract behavior."""

    def test_status_json_reports_project_validation_and_missing_install_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "DemoProject"
            codex_home = Path(temp_dir) / "codex-home"
            project_root.mkdir()
            run_init(argparse.Namespace(dest=project_root, project_id="demo-project", project_name="Demo Project"))

            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = run_status(
                    argparse.Namespace(
                        project_root=project_root,
                        codex_home=codex_home,
                        json=True,
                    )
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["schemaVersion"], 1)
            self.assertEqual(payload["projectRoot"], str(project_root.resolve()))
            self.assertEqual(payload["project"]["id"], "demo-project")
            self.assertEqual(payload["validation"]["status"], "ok")
            self.assertEqual(payload["validation"]["errors"], [])
            self.assertIn("project-knowledge-steward", {item["id"] for item in payload["capabilities"]})
            self.assertEqual(payload["adapters"], ["codex"])
            self.assertEqual(payload["installState"]["codex"]["status"], "missing")
            self.assertEqual(payload["installState"]["codex"]["materializedCapabilities"], [])

    def test_status_json_reports_codex_install_state_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "DemoProject"
            codex_home = Path(temp_dir) / "codex-home"
            project_root.mkdir()
            run_init(argparse.Namespace(dest=project_root, project_id="demo-project", project_name="Demo Project"))
            apply_exit = run_codex_apply(
                argparse.Namespace(
                    project_root=project_root,
                    release=None,
                    revision="json-status-test",
                    codex_home=codex_home,
                    preview=False,
                )
            )
            self.assertEqual(apply_exit, 0)

            _, _, payload = build_status_payload(project_root, codex_home)
            install_state = payload["installState"]["codex"]
            self.assertEqual(install_state["status"], "present")
            self.assertEqual(install_state["appliedRevision"], "json-status-test")
            self.assertEqual(
                {item["capabilityId"] for item in install_state["materializedCapabilities"]},
                {"project-knowledge-steward"},
            )

    def test_status_json_reports_validation_errors_with_error_exit(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "MissingGoverned"
            project_root.mkdir()

            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = run_status(argparse.Namespace(project_root=project_root, codex_home=None, json=True))

            payload = json.loads(output.getvalue())
            self.assertEqual(exit_code, 1)
            self.assertEqual(payload["validation"]["status"], "error")
            self.assertEqual(payload["capabilities"], [])
            self.assertEqual(payload["adapters"], [])
            self.assertIn("missing governed root", payload["validation"]["errors"][0]["message"])

    def test_status_text_output_remains_default(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "DemoProject"
            project_root.mkdir()
            run_init(argparse.Namespace(dest=project_root, project_id="demo-project", project_name="Demo Project"))

            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = run_status(argparse.Namespace(project_root=project_root, codex_home=None, json=False))

            self.assertEqual(exit_code, 0)
            text = output.getvalue()
            self.assertIn("Project root:", text)
            self.assertIn("Validation status: ok", text)
            self.assertFalse(text.lstrip().startswith("{"))


if __name__ == "__main__":
    unittest.main()

