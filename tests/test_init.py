"""Tests for project scaffolding and capability creation."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path
import unittest

from govkb.commands.create_capability import run_create_capability
from govkb.commands.init import run_init
from govkb.commands.validate import run_validate
from govkb.core.contracts import load_project_bundle


class InitCommandTests(unittest.TestCase):
    """Scaffold and validate the packaged project template."""

    def test_init_scaffolds_a_valid_project(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "DemoProject"
            project_root.mkdir(parents=True, exist_ok=True)

            init_exit = run_init(
                argparse.Namespace(
                    dest=project_root,
                    project_id="demo-project",
                    project_name="Demo Project",
                )
            )
            self.assertEqual(init_exit, 0)
            self.assertTrue((project_root / ".governed" / "project.toml").is_file())
            self.assertTrue(
                (
                    project_root
                    / ".governed"
                    / "capabilities"
                    / "project-knowledge-steward"
                    / "capability.contract.toml"
                ).is_file()
            )

            validate_exit = run_validate(argparse.Namespace(project_root=project_root))
            self.assertEqual(validate_exit, 0)

            bundle, result = load_project_bundle(project_root)
            self.assertFalse(result.errors)
            self.assertEqual(bundle.project_id, "demo-project")
            self.assertIn("codex", bundle.adapters)
            self.assertIn("project-knowledge-steward", bundle.capabilities)

    def test_create_capability_scaffolds_a_valid_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "DemoProject"
            project_root.mkdir(parents=True, exist_ok=True)
            run_init(argparse.Namespace(dest=project_root, project_id="demo-project", project_name="Demo Project"))

            create_exit = run_create_capability(
                argparse.Namespace(capability_id="Workflow Review", project_root=project_root, from_candidate=None)
            )
            self.assertEqual(create_exit, 0)
            self.assertTrue((project_root / ".governed" / "capabilities" / "workflow-review" / "instructions.md").is_file())
            prompt_path = project_root / ".governed" / "capabilities" / "workflow-review" / "prompts" / "initialize-kb.md"
            self.assertTrue(prompt_path.is_file())
            prompt_text = prompt_path.read_text(encoding="utf-8")
            self.assertIn("Capability: `workflow-review`", prompt_text)
            self.assertIn("govkb validate", prompt_text)
            self.assertIn("Do not store secrets", prompt_text)

            bundle, result = load_project_bundle(project_root)
            self.assertFalse(result.errors)
            self.assertIn("workflow-review", bundle.capabilities)


if __name__ == "__main__":
    unittest.main()
