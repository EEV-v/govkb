"""Tests for local Codex skill governed conversion."""

from __future__ import annotations

import argparse
from contextlib import redirect_stderr, redirect_stdout
import io
import json
import tempfile
from pathlib import Path
import unittest

from govkb.commands.apply import run_codex_apply
from govkb.commands.convert import run_convert
from govkb.commands.init import run_init
from govkb.core.contracts import load_project_bundle
from govkb.core.governed_skill import validate_governed_skill_package
from govkb.core.skill_conversion import build_conversion_plan


def _seed_project(root: Path) -> Path:
    project_root = root / "DemoProject"
    project_root.mkdir(parents=True, exist_ok=True)
    (project_root / "README.md").write_text("# Demo Project\n", encoding="utf-8")
    exit_code = run_init(argparse.Namespace(dest=project_root, project_id="demo-project", project_name="Demo Project"))
    assert exit_code == 0
    return project_root


def _memory_text() -> str:
    return """# Release Helper

## Working Agreement

- Keep release checks grounded in reusable repository evidence.

## Stable Workflows

- Review release notes, run verification, and preserve signoff evidence.

## Commands And Verification

- Run `python3 -m unittest tests.test_skill_conversion -v` from the repository root.

## Code And Docs Map

- Use `README.md` as the project entry point.

## Authority Rules

- Prefer governed release helper memory over local skill notes after conversion.
"""


def _seed_skill(codex_home: Path, name: str = "release-helper") -> Path:
    skill_root = codex_home / "skills" / name
    (skill_root / "references").mkdir(parents=True, exist_ok=True)
    (skill_root / "prompts").mkdir(parents=True, exist_ok=True)
    (skill_root / "scripts").mkdir(parents=True, exist_ok=True)
    (skill_root / "SKILL.md").write_text(
        """---
name: release-helper
description: Release helper skill.
---

# Release Helper

Use this skill for repeatable release validation.
""",
        encoding="utf-8",
    )
    (skill_root / "references" / "long-term-memory.md").write_text(_memory_text(), encoding="utf-8")
    (skill_root / "prompts" / "release-check.md").write_text("# Release Check\n\nCollect signoff evidence.\n", encoding="utf-8")
    (skill_root / "scripts" / "check.sh").write_text("#!/usr/bin/env bash\necho checking release\n", encoding="utf-8")
    return skill_root


def _run_convert(args: argparse.Namespace) -> tuple[int, str, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        exit_code = run_convert(args)
    return exit_code, stdout.getvalue(), stderr.getvalue()


class SkillConversionTests(unittest.TestCase):
    """Preview and write behavior for one-skill conversion."""

    def test_preview_writes_no_files_and_reports_plan(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            project_root = _seed_project(root)
            codex_home = root / "codex-home"
            _seed_skill(codex_home)

            exit_code, stdout, stderr = _run_convert(
                argparse.Namespace(
                    convert_action="skill",
                    skill="release-helper",
                    project_root=project_root,
                    codex_home=codex_home,
                    capability_id=None,
                    write=False,
                    json=False,
                )
            )

            self.assertEqual(exit_code, 0, stderr)
            self.assertIn("Preview mode: no files were written.", stdout)
            self.assertIn("Target capability id: release-helper", stdout)
            self.assertFalse((project_root / ".governed" / "capabilities" / "release-helper").exists())

    def test_source_name_resolves_from_codex_home(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            project_root = _seed_project(root)
            codex_home = root / "codex-home"
            skill_root = _seed_skill(codex_home)

            plan = build_conversion_plan("release-helper", project_root=project_root, codex_home=codex_home)

            self.assertEqual(plan.source_path, skill_root.resolve())
            self.assertEqual(plan.capability_id, "release-helper")

    def test_direct_source_path_outside_codex_home_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            project_root = _seed_project(root)
            outside_home = root / "outside-skill"
            codex_home = root / "codex-home"
            skill_root = _seed_skill(root, name="outside-skill")
            skill_root.rename(outside_home)

            plan = build_conversion_plan(str(outside_home), project_root=project_root, codex_home=codex_home)

            self.assertEqual(plan.source_path, outside_home.resolve())
            self.assertEqual(plan.capability_id, "release-helper")

    def test_direct_skill_markdown_path_resolves_to_skill_folder(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            project_root = _seed_project(root)
            codex_home = root / "codex-home"
            skill_root = _seed_skill(codex_home)

            plan = build_conversion_plan(str(skill_root / "SKILL.md"), project_root=project_root, codex_home=codex_home)

            self.assertEqual(plan.source_path, skill_root.resolve())
            self.assertEqual(plan.capability_id, "release-helper")

    def test_json_write_failure_removes_non_strict_package(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            project_root = _seed_project(root)
            codex_home = root / "codex-home"
            skill_root = _seed_skill(codex_home)
            skill_file = skill_root / "SKILL.md"
            skill_file.write_text(
                skill_file.read_text(encoding="utf-8") + "\nUse `missing-release-check.md` before release.\n",
                encoding="utf-8",
            )

            exit_code, stdout, stderr = _run_convert(
                argparse.Namespace(
                    convert_action="skill",
                    skill="release-helper",
                    project_root=project_root,
                    codex_home=codex_home,
                    capability_id=None,
                    write=True,
                    json=True,
                )
            )

            payload = json.loads(stdout)
            self.assertEqual(exit_code, 1)
            self.assertEqual(stderr, "")
            self.assertEqual(payload["strictStatus"], "failed")
            self.assertEqual(payload["packageRemoved"], True)
            self.assertFalse((project_root / ".governed" / "capabilities" / "release-helper").exists())

    def test_conversion_repairs_moved_skill_paths_and_repo_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            project_root = _seed_project(root)
            grades_root = project_root / "clearing-docs" / "GRADES"
            grades_root.mkdir(parents=True, exist_ok=True)
            backend_matrix = grades_root / "backend-grading-matrix-full.md"
            qa_matrix = grades_root / "qa-grading-matrix-middle.md"
            backend_matrix.write_text("# Backend Matrix\n", encoding="utf-8")
            qa_matrix.write_text("# QA Matrix\n", encoding="utf-8")

            codex_home = root / "codex-home"
            skill_root = _seed_skill(codex_home, name="comparative-grade-screening")
            (skill_root / "SKILL.md").write_text(
                f"""---
name: comparative-grade-screening
description: Comparative grade screening.
---

# Comparative Grade Screening

Prefer `references/matrix-sources.md` for source matrices.
Default backend source is `backend-grading-matrix-full.md`.
Default QA source is `qa-grading-matrix-middle.md`.
Run `scripts/calc_screening_scores.py` for totals.
Use `calc_screening_scores.py`, `add_lesson.py`, `matrix-sources.md`, `output-style.md`, and `lessons.md` from this skill.
""",
                encoding="utf-8",
            )
            (skill_root / "references" / "matrix-sources.md").write_text(
                f"""# Matrix Sources

- Backend: `{backend_matrix}`
- QA: `{qa_matrix}`
""",
                encoding="utf-8",
            )
            (skill_root / "references" / "lessons.md").write_text("# Lessons\n", encoding="utf-8")
            (skill_root / "references" / "output-style.md").write_text("# Output Style\n", encoding="utf-8")
            (skill_root / "scripts" / "calc_screening_scores.py").write_text("print('score')\n", encoding="utf-8")
            (skill_root / "scripts" / "add_lesson.py").write_text("print('lesson')\n", encoding="utf-8")

            plan = build_conversion_plan(
                "comparative-grade-screening",
                project_root=project_root,
                codex_home=codex_home,
            )

            self.assertEqual(plan.strict_status, "passed", [issue.as_dict() for issue in plan.strict_issues])
            self.assertIn("tools/scripts/calc_screening_scores.py", plan.instructions_text)
            self.assertIn("tools/scripts/add_lesson.py", plan.instructions_text)
            self.assertIn("references/matrix-sources.md", plan.instructions_text)
            self.assertIn("clearing-docs/GRADES/backend-grading-matrix-full.md", plan.instructions_text)
            self.assertIn("clearing-docs/GRADES/qa-grading-matrix-middle.md", plan.instructions_text)

            exit_code, stdout, stderr = _run_convert(
                argparse.Namespace(
                    convert_action="skill",
                    skill="comparative-grade-screening",
                    project_root=project_root,
                    codex_home=codex_home,
                    capability_id=None,
                    write=True,
                    json=True,
                )
            )

            self.assertEqual(exit_code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(payload["strictStatus"], "passed")
            package_root = project_root / ".governed" / "capabilities" / "comparative-grade-screening"
            matrix_sources = (package_root / "references" / "matrix-sources.md").read_text(encoding="utf-8")
            self.assertNotIn(str(project_root), matrix_sources)
            self.assertIn("clearing-docs/GRADES/backend-grading-matrix-full.md", matrix_sources)

    def test_generated_memory_uses_existing_project_entrypoint(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            project_root = _seed_project(root)
            (project_root / "README.md").unlink()
            (project_root / "AGENTS.md").write_text("# Agent Instructions\n", encoding="utf-8")
            codex_home = root / "codex-home"
            skill_root = _seed_skill(codex_home)
            (skill_root / "references" / "long-term-memory.md").unlink()

            exit_code, stdout, stderr = _run_convert(
                argparse.Namespace(
                    convert_action="skill",
                    skill="release-helper",
                    project_root=project_root,
                    codex_home=codex_home,
                    capability_id=None,
                    write=True,
                    json=True,
                )
            )

            self.assertEqual(exit_code, 0, stderr)
            payload = json.loads(stdout)
            self.assertEqual(payload["strictStatus"], "passed")
            memory = (
                project_root
                / ".governed"
                / "capabilities"
                / "release-helper"
                / "references"
                / "long-term-memory.md"
            ).read_text(encoding="utf-8")
            self.assertIn("`AGENTS.md`", memory)
            self.assertNotIn("`README.md`", memory)

    def test_write_creates_strict_valid_package_and_apply_materializes_it(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            project_root = _seed_project(root)
            codex_home = root / "codex-home"
            skill_root = _seed_skill(codex_home)
            original_skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")

            exit_code, stdout, stderr = _run_convert(
                argparse.Namespace(
                    convert_action="skill",
                    skill="release-helper",
                    project_root=project_root,
                    codex_home=codex_home,
                    capability_id=None,
                    write=True,
                    json=False,
                )
            )

            self.assertEqual(exit_code, 0, stderr)
            capability_root = project_root / ".governed" / "capabilities" / "release-helper"
            self.assertTrue((capability_root / "capability.contract.toml").is_file())
            self.assertTrue((capability_root / "instructions.md").is_file())
            self.assertTrue((capability_root / "references" / "long-term-memory.md").is_file())
            self.assertTrue((capability_root / "prompts" / "release-check.md").is_file())
            self.assertTrue((capability_root / "tools" / "scripts" / "check.sh").is_file())
            self.assertTrue((capability_root / "tools" / "README.md").is_file())
            self.assertIn("Rollback: remove", stdout)
            self.assertEqual((skill_root / "SKILL.md").read_text(encoding="utf-8"), original_skill)

            bundle, result = load_project_bundle(project_root)
            self.assertFalse(result.errors, [message.message for message in result.errors])
            strict = validate_governed_skill_package(project_root, bundle.capabilities["release-helper"])
            self.assertTrue(strict.ok, [issue.as_dict() for issue in strict.issues])

            apply_exit = run_codex_apply(
                argparse.Namespace(
                    project_root=project_root,
                    release=None,
                    revision="conversion-test",
                    codex_home=codex_home,
                    preview=False,
                )
            )
            self.assertEqual(apply_exit, 0)
            materialized = codex_home / "skills" / "govkb-demo-project-release-helper"
            self.assertTrue((materialized / "SKILL.md").is_file())
            self.assertIn("Release Helper", (materialized / "SKILL.md").read_text(encoding="utf-8"))
            self.assertFalse((materialized / "references" / "unsafe.md").exists())

    def test_write_fails_when_target_package_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            project_root = _seed_project(root)
            codex_home = root / "codex-home"
            skill_root = _seed_skill(codex_home)
            target = project_root / ".governed" / "capabilities" / "release-helper"
            target.mkdir(parents=True, exist_ok=True)
            marker = target / "marker.txt"
            marker.write_text("keep me\n", encoding="utf-8")
            original_skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")

            exit_code, _, stderr = _run_convert(
                argparse.Namespace(
                    convert_action="skill",
                    skill="release-helper",
                    project_root=project_root,
                    codex_home=codex_home,
                    capability_id=None,
                    write=True,
                    json=False,
                )
            )

            self.assertEqual(exit_code, 1)
            self.assertIn("already exists", stderr)
            self.assertEqual(marker.read_text(encoding="utf-8"), "keep me\n")
            self.assertEqual((skill_root / "SKILL.md").read_text(encoding="utf-8"), original_skill)

    def test_unsafe_content_is_rejected_and_report_is_redacted(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            project_root = _seed_project(root)
            codex_home = root / "codex-home"
            skill_root = _seed_skill(codex_home)
            unsafe_value = "OPENAI_API_KEY=sk-proj-abcdefghijklmnopqrstuvwxyz1234567890"
            (skill_root / "references" / "unsafe.md").write_text(
                f"# Unsafe\n\nDo not copy {unsafe_value} or `~/.ssh/id_rsa`.\n",
                encoding="utf-8",
            )

            exit_code, stdout, stderr = _run_convert(
                argparse.Namespace(
                    convert_action="skill",
                    skill="release-helper",
                    project_root=project_root,
                    codex_home=codex_home,
                    capability_id=None,
                    write=True,
                    json=False,
                )
            )

            self.assertEqual(exit_code, 0, stderr)
            capability_root = project_root / ".governed" / "capabilities" / "release-helper"
            self.assertFalse((capability_root / "references" / "unsafe.md").exists())
            report = (capability_root / "docs" / "conversion-report.md").read_text(encoding="utf-8")
            self.assertIn("references/unsafe.md", report)
            self.assertIn("token-like or secret-like content", report)
            self.assertNotIn("sk-proj-", report)
            self.assertNotIn("~/.ssh/id_rsa", report)
            self.assertIn("references/unsafe.md", stdout)


if __name__ == "__main__":
    unittest.main()
