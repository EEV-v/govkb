"""Tests for Codex materialization and install-state tracking."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
import unittest

from govkb.commands.apply import run_codex_apply
from govkb.commands.create_capability import run_create_capability
from govkb.commands.init import run_init
from govkb.core.install_state import install_state_path
from govkb.core.install_state import load_install_state


class ApplyCommandTests(unittest.TestCase):
    """Codex materialization behavior."""

    def test_preview_does_not_write_install_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "DemoProject"
            codex_home = Path(temp_dir) / "codex-home"
            project_root.mkdir(parents=True, exist_ok=True)
            run_init(argparse.Namespace(dest=project_root, project_id="demo-project", project_name="Demo Project"))
            run_create_capability(argparse.Namespace(capability_id="Workflow Review", project_root=project_root))

            exit_code = run_codex_apply(
                argparse.Namespace(
                    project_root=project_root,
                    release=None,
                    revision=None,
                    codex_home=codex_home,
                    preview=True,
                )
            )
            self.assertEqual(exit_code, 0)
            self.assertFalse((codex_home / "skills").exists())
            self.assertFalse(install_state_path(codex_home, "demo-project", "codex").exists())

    def test_apply_materializes_skill_and_install_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "DemoProject"
            codex_home = Path(temp_dir) / "codex-home"
            project_root.mkdir(parents=True, exist_ok=True)
            run_init(argparse.Namespace(dest=project_root, project_id="demo-project", project_name="Demo Project"))
            run_create_capability(argparse.Namespace(capability_id="Workflow Review", project_root=project_root))

            release_dir = project_root / ".governed" / "releases"
            (release_dir / "2026.04.22.toml").write_text(
                """[release]
id = "2026.04.22"
git_revision = "abc1234"
adapters = ["codex"]
notes = "initial rollout"
""",
                encoding="utf-8",
            )

            exit_code = run_codex_apply(
                argparse.Namespace(
                    project_root=project_root,
                    release="2026.04.22",
                    revision=None,
                    codex_home=codex_home,
                    preview=False,
                )
            )
            self.assertEqual(exit_code, 0)

            skill_root = codex_home / "skills" / "govkb-demo-project-workflow-review"
            self.assertTrue((skill_root / "SKILL.md").is_file())
            self.assertTrue((skill_root / "references" / "long-term-memory.md").is_file())
            self.assertTrue((skill_root / "prompts" / "initialize-kb.md").is_file())
            self.assertIn("name: govkb-demo-project-workflow-review", (skill_root / "SKILL.md").read_text(encoding="utf-8"))
            self.assertIn(
                "Capability: `workflow-review`",
                (skill_root / "prompts" / "initialize-kb.md").read_text(encoding="utf-8"),
            )
            metadata = json.loads((skill_root / ".govkb-materialized.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["project_id"], "demo-project")
            self.assertEqual(metadata["materialized_skill_id"], "govkb-demo-project-workflow-review")
            self.assertEqual(metadata["revision"], "abc1234")

            state = load_install_state(install_state_path(codex_home, "demo-project", "codex"))
            self.assertIsNotNone(state)
            self.assertEqual(state["release"], "2026.04.22")
            self.assertEqual(state["revision"], "abc1234")
            self.assertTrue(Path(state["govkb_import_root"]).is_dir())
            self.assertEqual(
                {capability["capability_id"] for capability in state["capabilities"]},
                {"project-knowledge-steward", "workflow-review"},
            )
            self.assertEqual(
                {capability["materialized_skill_id"] for capability in state["capabilities"]},
                {"govkb-demo-project-project-knowledge-steward", "govkb-demo-project-workflow-review"},
            )

    def test_apply_uses_migration_fallback_when_repo_files_are_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "DemoProject"
            codex_home = Path(temp_dir) / "codex-home"
            legacy_skill_root = Path(temp_dir) / "legacy-skill"
            project_root.mkdir(parents=True, exist_ok=True)
            legacy_skill_root.mkdir(parents=True, exist_ok=True)
            (legacy_skill_root / "references").mkdir(parents=True, exist_ok=True)
            (legacy_skill_root / "SKILL.md").write_text(
                "---\nname: migrated-capability\ndescription: legacy\n---\n\n# Legacy Skill\n",
                encoding="utf-8",
            )
            (legacy_skill_root / "references" / "long-term-memory.md").write_text(
                "# Legacy\n\n## Working Agreement\n\n- existing legacy note.\n",
                encoding="utf-8",
            )

            run_init(argparse.Namespace(dest=project_root, project_id="demo-project", project_name="Demo Project"))
            capability_root = project_root / ".governed" / "capabilities" / "migrated-capability"
            capability_root.mkdir(parents=True, exist_ok=True)
            (capability_root / "capability.contract.toml").write_text(
                f"""contract_version = 1

[capability]
id = "migrated-capability"
name = "Migrated Capability"
governed = true
description = "migrated from local codex skill"

[routing]
aliases = []
hints = ["migrated capability"]
negative_hints = []

[memory]
enabled = true
auto_apply_min_confidence = 0.85
requires_explicit_acceptance = false

[memory.targets.main]
path = "references/long-term-memory.md"
sections = ["Working Agreement"]

[migration]
source_adapter = "codex"
source_path = "{legacy_skill_root}"
status = "legacy-fallback"
""",
                encoding="utf-8",
            )

            exit_code = run_codex_apply(
                argparse.Namespace(
                    project_root=project_root,
                    release=None,
                    revision="fallback-test",
                    codex_home=codex_home,
                    preview=False,
                )
            )
            self.assertEqual(exit_code, 0)
            skill_root = codex_home / "skills" / "govkb-demo-project-migrated-capability"
            self.assertIn("Legacy Skill", (skill_root / "SKILL.md").read_text(encoding="utf-8"))
            self.assertIn("name: govkb-demo-project-migrated-capability", (skill_root / "SKILL.md").read_text(encoding="utf-8"))
            self.assertIn(
                "existing legacy note",
                (skill_root / "references" / "long-term-memory.md").read_text(encoding="utf-8"),
            )

    def test_apply_keeps_same_capability_ids_separate_across_projects(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            codex_home = Path(temp_dir) / "codex-home"
            first_root = Path(temp_dir) / "FirstProject"
            second_root = Path(temp_dir) / "SecondProject"
            first_root.mkdir(parents=True, exist_ok=True)
            second_root.mkdir(parents=True, exist_ok=True)

            run_init(argparse.Namespace(dest=first_root, project_id="first-project", project_name="First Project"))
            run_init(argparse.Namespace(dest=second_root, project_id="second-project", project_name="Second Project"))

            first_exit = run_codex_apply(
                argparse.Namespace(project_root=first_root, release=None, revision="first", codex_home=codex_home, preview=False)
            )
            second_exit = run_codex_apply(
                argparse.Namespace(project_root=second_root, release=None, revision="second", codex_home=codex_home, preview=False)
            )

            self.assertEqual(first_exit, 0)
            self.assertEqual(second_exit, 0)
            self.assertTrue((codex_home / "skills" / "govkb-first-project-project-knowledge-steward").is_dir())
            self.assertTrue((codex_home / "skills" / "govkb-second-project-project-knowledge-steward").is_dir())
            self.assertTrue(install_state_path(codex_home, "first-project", "codex").is_file())
            self.assertTrue(install_state_path(codex_home, "second-project", "codex").is_file())


if __name__ == "__main__":
    unittest.main()
