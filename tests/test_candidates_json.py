"""Tests for machine-readable candidate listing output."""

from __future__ import annotations

import argparse
from contextlib import redirect_stdout
import io
import json
import tempfile
from pathlib import Path
import unittest

from govkb.commands.candidates import build_candidates_payload
from govkb.commands.candidates import run_candidates
from govkb.commands.init import run_init


def _write_candidate(project_root: Path, candidate_id: str, *, status: str = "ready-for-review") -> None:
    candidate_root = project_root / ".governed" / "candidates" / candidate_id
    candidate_root.mkdir(parents=True, exist_ok=True)
    candidate_root.joinpath("candidate.toml").write_text(
        f"""candidate_version = 1
id = "{candidate_id}"
status = "{status}"
occurrences = 2
created_at = "2026-04-25T12:00:00Z"
updated_at = "2026-04-25T12:00:00Z"

[proposal]
capability_id = "backend-local-stack-workflow"
summary = "Local backend stack workflow."
rationale = "Repeated setup and verification work."
routing_hints = ["backend", "workflow"]

[source]
assistant = "codex"
sessions = ["synthetic-session"]
""",
        encoding="utf-8",
    )


class CandidatesJsonTests(unittest.TestCase):
    """Machine-readable candidate listing contract behavior."""

    def test_candidates_json_reports_empty_list(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "DemoProject"
            project_root.mkdir()
            run_init(argparse.Namespace(dest=project_root, project_id="demo-project", project_name="Demo Project"))

            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = run_candidates(
                    argparse.Namespace(candidate_action="list", project_root=project_root, json=True)
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(exit_code, 0)
            self.assertEqual(payload["schemaVersion"], 1)
            self.assertEqual(payload["projectRoot"], str(project_root.resolve()))
            self.assertEqual(payload["candidates"], [])

    def test_candidates_json_reports_candidate_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "DemoProject"
            project_root.mkdir()
            run_init(argparse.Namespace(dest=project_root, project_id="demo-project", project_name="Demo Project"))
            _write_candidate(project_root, "backend-workflow")

            payload = build_candidates_payload(project_root)

            self.assertEqual(len(payload["candidates"]), 1)
            candidate = payload["candidates"][0]
            self.assertEqual(candidate["id"], "backend-workflow")
            self.assertEqual(candidate["status"], "ready-for-review")
            self.assertEqual(candidate["occurrences"], 2)
            self.assertEqual(candidate["suggestedCapabilityId"], "backend-local-stack-workflow")
            self.assertEqual(candidate["activationState"], "not-activated")
            self.assertTrue(str(candidate["path"]).endswith(".governed/candidates/backend-workflow"))

    def test_candidates_json_reports_activated_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "DemoProject"
            project_root.mkdir()
            run_init(argparse.Namespace(dest=project_root, project_id="demo-project", project_name="Demo Project"))
            _write_candidate(project_root, "backend-workflow", status="activated")

            payload = build_candidates_payload(project_root)

            self.assertEqual(payload["candidates"][0]["activationState"], "activated")

    def test_candidates_text_output_remains_default(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "DemoProject"
            project_root.mkdir()
            run_init(argparse.Namespace(dest=project_root, project_id="demo-project", project_name="Demo Project"))
            _write_candidate(project_root, "backend-workflow")

            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = run_candidates(
                    argparse.Namespace(candidate_action="list", project_root=project_root, json=False)
                )

            self.assertEqual(exit_code, 0)
            text = output.getvalue()
            self.assertIn("backend-workflow status=ready-for-review occurrences=2", text)
            self.assertFalse(text.lstrip().startswith("{"))


if __name__ == "__main__":
    unittest.main()

