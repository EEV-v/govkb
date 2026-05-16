"""Tests for governed capability management commands."""

from __future__ import annotations

import argparse
from contextlib import redirect_stderr, redirect_stdout
import io
import json
import tempfile
from pathlib import Path
import unittest

from govkb.commands.capabilities import run_capabilities
from govkb.commands.create_capability import run_create_capability
from govkb.commands.init import run_init
from govkb.commands.validate import run_validate
from govkb.core.contracts import load_project_bundle


def _seed_project(root: Path) -> Path:
    project_root = root / "DemoProject"
    project_root.mkdir(parents=True, exist_ok=True)
    (project_root / "README.md").write_text("# Demo Project\n", encoding="utf-8")
    exit_code = run_init(argparse.Namespace(dest=project_root, project_id="demo-project", project_name="Demo Project"))
    assert exit_code == 0
    return project_root


def _create_capability(project_root: Path, capability_id: str) -> None:
    exit_code = run_create_capability(
        argparse.Namespace(capability_id=capability_id, project_root=project_root, from_candidate=None)
    )
    assert exit_code == 0


def _run_capabilities(args: argparse.Namespace) -> tuple[int, str, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        exit_code = run_capabilities(args)
    return exit_code, stdout.getvalue(), stderr.getvalue()


def _write_memory(project_root: Path, capability_id: str, bullet: str) -> None:
    memory = project_root / ".governed" / "capabilities" / capability_id / "references" / "long-term-memory.md"
    memory.write_text(
        f"""# {capability_id.title()}

## Working Agreement

- {bullet}

## Stable Workflows

- Review reusable workflow evidence before changing governed instructions.

## Commands And Verification

- Run `README.md` review before activation.

## Code And Docs Map

- Use `README.md` as the project entry point.

## Authority Rules

- Prefer the active governed capability after merge review.
""",
        encoding="utf-8",
    )


class CapabilityManagementTests(unittest.TestCase):
    """List, rename, and merge governed capabilities."""

    def test_capabilities_list_reports_openable_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = _seed_project(Path(temp_dir))
            _create_capability(project_root, "Workflow Review")

            exit_code, stdout, stderr = _run_capabilities(
                argparse.Namespace(capability_action="list", project_root=project_root, json=True)
            )

            self.assertEqual(exit_code, 0, stderr)
            payload = json.loads(stdout)
            ids = {item["id"] for item in payload["capabilities"]}
            self.assertIn("workflow-review", ids)
            workflow = next(item for item in payload["capabilities"] if item["id"] == "workflow-review")
            self.assertTrue(workflow["instructionsPath"].endswith("instructions.md"))
            self.assertTrue(workflow["memoryTargets"][0]["absolutePath"].endswith("long-term-memory.md"))

    def test_rename_updates_contract_path_and_preserves_old_alias(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = _seed_project(Path(temp_dir))
            _create_capability(project_root, "Workflow Review")

            exit_code, stdout, stderr = _run_capabilities(
                argparse.Namespace(
                    capability_action="rename",
                    old_capability_id="workflow-review",
                    new_capability_id="release-review",
                    project_root=project_root,
                    json=True,
                )
            )

            self.assertEqual(exit_code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(payload["oldCapabilityId"], "workflow-review")
            self.assertEqual(payload["newCapabilityId"], "release-review")
            self.assertFalse((project_root / ".governed" / "capabilities" / "workflow-review").exists())
            self.assertTrue((project_root / ".governed" / "capabilities" / "release-review").is_dir())
            bundle, result = load_project_bundle(project_root)
            self.assertFalse(result.errors, [message.message for message in result.errors])
            renamed = bundle.capabilities["release-review"]
            self.assertIn("workflow-review", renamed.aliases)
            self.assertEqual(renamed.capability_name, "Release Review")

    def test_merge_combines_aliases_memory_and_removes_source(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = _seed_project(Path(temp_dir))
            _create_capability(project_root, "Feature Review")
            _create_capability(project_root, "Release Review")
            _write_memory(project_root, "release-review", "Keep release readiness checks grounded in sign-off evidence.")

            source_instructions = project_root / ".governed" / "capabilities" / "release-review" / "instructions.md"
            source_instructions.write_text(
                "# Release Review\n\nUse this governed capability for release readiness checks.\n",
                encoding="utf-8",
            )

            exit_code, stdout, stderr = _run_capabilities(
                argparse.Namespace(
                    capability_action="merge",
                    source_capability_id="release-review",
                    target_capability_id="feature-review",
                    project_root=project_root,
                    json=True,
                )
            )

            self.assertEqual(exit_code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(payload["sourceCapabilityId"], "release-review")
            self.assertEqual(payload["targetCapabilityId"], "feature-review")
            self.assertFalse((project_root / ".governed" / "capabilities" / "release-review").exists())
            self.assertTrue(Path(payload["reportPath"]).is_file())
            bundle, result = load_project_bundle(project_root)
            self.assertFalse(result.errors, [message.message for message in result.errors])
            target = bundle.capabilities["feature-review"]
            self.assertIn("release-review", target.aliases)
            target_memory = (target.capability_root / "references" / "long-term-memory.md").read_text(encoding="utf-8")
            self.assertIn("Merged from release-review: Keep release readiness checks grounded in sign-off evidence.", target_memory)
            target_instructions = (target.capability_root / "instructions.md").read_text(encoding="utf-8")
            self.assertIn("Merged Capability: Release Review", target_instructions)
            validate_exit = run_validate(argparse.Namespace(project_root=project_root, strict=False, json=False))
            self.assertEqual(validate_exit, 0)


if __name__ == "__main__":
    unittest.main()
