"""Tests for machine-readable status output."""

from __future__ import annotations

import argparse
from contextlib import redirect_stdout
import io
import json
import subprocess
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
            self.assertIsNone(payload["project"]["gitRevision"])
            self.assertFalse(payload["project"]["governedDirty"])
            self.assertEqual(payload["project"]["governedStatus"], [])
            self.assertEqual(payload["validation"]["status"], "ok")
            self.assertEqual(payload["validation"]["errors"], [])
            self.assertIn("project-knowledge-steward", {item["id"] for item in payload["capabilities"]})
            self.assertEqual(payload["adapters"], ["codex"])
            self.assertEqual(payload["installState"]["codex"]["status"], "missing")
            self.assertEqual(payload["installState"]["codex"]["materializedCapabilities"], [])
            self.assertEqual(payload["skillUpdates"]["state"], "not-applied")
            self.assertFalse(payload["skillUpdates"]["pendingLocalMemory"]["available"])

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
            self.assertEqual(payload["skillUpdates"]["state"], "current")
            self.assertEqual(payload["skillUpdates"]["appliedRevision"], "json-status-test")

    def test_status_json_reports_learned_local_memory_updates(self) -> None:
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
            local_memory = (
                codex_home
                / "skills"
                / "govkb-demo-project-project-knowledge-steward"
                / "references"
                / "long-term-memory.md"
            )
            addition = "- Track repeated billing work as a candidate governed capability."
            local_memory.write_text(local_memory.read_text(encoding="utf-8").rstrip() + f"\n{addition}\n", encoding="utf-8")

            _, _, payload = build_status_payload(project_root, codex_home)
            pending = payload["skillUpdates"]["pendingLocalMemory"]
            self.assertEqual(payload["skillUpdates"]["state"], "learned-updates")
            self.assertTrue(pending["available"])
            self.assertEqual(pending["safePromotionCount"], 1)
            self.assertEqual(pending["rejectedCount"], 0)
            self.assertEqual(pending["items"][0]["capabilityId"], "project-knowledge-steward")
            self.assertEqual(pending["items"][0]["additions"], 1)

    def test_status_json_reports_git_revision_and_governed_dirty_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "DemoProject"
            codex_home = Path(temp_dir) / "codex-home"
            project_root.mkdir()
            run_init(argparse.Namespace(dest=project_root, project_id="demo-project", project_name="Demo Project"))
            subprocess.run(["git", "init"], cwd=project_root, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "govkb@example.local"], cwd=project_root, check=True)
            subprocess.run(["git", "config", "user.name", "GovKB Test"], cwd=project_root, check=True)
            subprocess.run(["git", "add", ".governed"], cwd=project_root, check=True)
            subprocess.run(["git", "commit", "-m", "initial governed package"], cwd=project_root, check=True, capture_output=True)
            head = subprocess.run(
                ["git", "rev-parse", "--verify", "HEAD"],
                cwd=project_root,
                check=True,
                text=True,
                capture_output=True,
            ).stdout.strip()
            apply_exit = run_codex_apply(
                argparse.Namespace(
                    project_root=project_root,
                    release=None,
                    revision=head,
                    codex_home=codex_home,
                    preview=False,
                )
            )
            self.assertEqual(apply_exit, 0)

            _, _, clean_payload = build_status_payload(project_root)
            self.assertTrue(clean_payload["project"]["gitRevision"])
            self.assertFalse(clean_payload["project"]["governedDirty"])
            _, _, installed_payload = build_status_payload(project_root, codex_home)
            self.assertEqual(installed_payload["skillUpdates"]["state"], "current")

            memory = project_root / ".governed" / "capabilities" / "project-knowledge-steward" / "references" / "long-term-memory.md"
            memory.write_text(memory.read_text(encoding="utf-8") + "\n- Stable Workflows: status dirty test.\n", encoding="utf-8")

            _, _, dirty_payload = build_status_payload(project_root)
            self.assertTrue(dirty_payload["project"]["governedDirty"])
            self.assertTrue(any("long-term-memory.md" in line for line in dirty_payload["project"]["governedStatus"]))
            self.assertEqual(dirty_payload["skillUpdates"]["state"], "unknown")
            _, _, dirty_installed_payload = build_status_payload(project_root, codex_home)
            self.assertEqual(dirty_installed_payload["skillUpdates"]["state"], "workspace-changes")

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
