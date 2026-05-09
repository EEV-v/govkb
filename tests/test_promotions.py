"""Tests for isolated promotion review commands."""

from __future__ import annotations

import argparse
from contextlib import redirect_stdout, redirect_stderr
import io
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
import unittest

from govkb.commands.apply import run_codex_apply
from govkb.commands.create_capability import run_create_capability
from govkb.commands.init import run_init
from govkb.commands.promote import run_promote
from govkb.commands.promotions import build_promotion_detail_payload
from govkb.commands.promotions import build_promotions_payload
from govkb.commands.promotions import run_promotions


def _scaffold_promoted_worktree(temp_dir: str) -> tuple[Path, Path, str]:
    project_root = Path(temp_dir) / "DemoProject"
    codex_home = Path(temp_dir) / "codex-home"
    project_root.mkdir(parents=True, exist_ok=True)
    run_init(argparse.Namespace(dest=project_root, project_id="demo-project", project_name="Demo Project"))
    run_create_capability(argparse.Namespace(capability_id="Workflow Review", project_root=project_root))
    run_codex_apply(
        argparse.Namespace(
            project_root=project_root,
            release=None,
            revision="promotions-test",
            codex_home=codex_home,
            preview=False,
        )
    )
    subprocess.run(["git", "init"], cwd=project_root, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "govkb@example.local"], cwd=project_root, check=True)
    subprocess.run(["git", "config", "user.name", "GovKB Test"], cwd=project_root, check=True)
    subprocess.run(["git", "add", ".governed"], cwd=project_root, check=True)
    subprocess.run(["git", "commit", "-m", "initial governed package"], cwd=project_root, check=True, capture_output=True)

    local_memory = codex_home / "skills" / "govkb-demo-project-workflow-review" / "references" / "long-term-memory.md"
    lesson = "- Keep promotion review worktrees visible from the CLI."
    local_memory.write_text(local_memory.read_text(encoding="utf-8").rstrip() + f"\n{lesson}\n", encoding="utf-8")
    exit_code = run_promote(
        argparse.Namespace(
            project_root=project_root,
            release=None,
            assistant="codex",
            codex_home=codex_home,
            preview=False,
            auto=True,
        )
    )
    if exit_code != 0:
        raise AssertionError(f"auto promotion failed with exit code {exit_code}")
    return project_root, codex_home, lesson


@unittest.skipIf(shutil.which("git") is None, "git is not installed")
class PromotionsCommandTests(unittest.TestCase):
    """Read-only review surface for isolated promotion worktrees."""

    def test_promotions_list_reports_isolated_worktree(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root, codex_home, _ = _scaffold_promoted_worktree(temp_dir)

            payload = build_promotions_payload(project_root, codex_home)

            self.assertEqual(payload["schemaVersion"], 1)
            self.assertEqual(len(payload["promotions"]), 1)
            promotion = payload["promotions"][0]
            self.assertEqual(promotion["state"], "ready-for-review")
            self.assertTrue(promotion["branch"].startswith("codex/govkb-auto-promote/demo-project/"))
            self.assertTrue(promotion["digestPath"].endswith("latest-promotion-digest.md"))
            self.assertTrue(promotion["metadataPath"].endswith(f"{promotion['runId']}.json"))
            self.assertIsNone(promotion["review"])
            self.assertTrue(any("long-term-memory.md" in line for line in promotion["status"]))

    def test_promotions_list_json_and_show_text_are_user_visible(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root, codex_home, lesson = _scaffold_promoted_worktree(temp_dir)

            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = run_promotions(
                    argparse.Namespace(
                        promotion_action="list",
                        project_root=project_root,
                        codex_home=codex_home,
                        json=True,
                    )
                )

            self.assertEqual(exit_code, 0)
            payload = json.loads(output.getvalue())
            run_id = payload["promotions"][0]["runId"]
            self.assertEqual(payload["promotions"][0]["state"], "ready-for-review")

            show_output = io.StringIO()
            with redirect_stdout(show_output):
                show_exit = run_promotions(
                    argparse.Namespace(
                        promotion_action="show",
                        promotion=run_id,
                        project_root=project_root,
                        codex_home=codex_home,
                        json=False,
                    )
                )

            self.assertEqual(show_exit, 0)
            text = show_output.getvalue()
            self.assertIn("State: ready-for-review", text)
            self.assertIn("Git status:", text)
            self.assertIn(lesson, text)

    def test_promotions_show_json_reports_missing_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "DemoProject"
            codex_home = Path(temp_dir) / "codex-home"
            project_root.mkdir()
            run_init(argparse.Namespace(dest=project_root, project_id="demo-project", project_name="Demo Project"))

            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = run_promotions(
                    argparse.Namespace(
                        promotion_action="show",
                        promotion="missing-run",
                        project_root=project_root,
                        codex_home=codex_home,
                        json=True,
                    )
                )

            payload = json.loads(output.getvalue())
            self.assertEqual(exit_code, 1)
            self.assertIsNone(payload["promotion"])
            self.assertIn("missing-run", payload["error"])

    def test_promotions_show_text_reports_missing_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "DemoProject"
            codex_home = Path(temp_dir) / "codex-home"
            project_root.mkdir()
            run_init(argparse.Namespace(dest=project_root, project_id="demo-project", project_name="Demo Project"))

            error = io.StringIO()
            with redirect_stderr(error):
                exit_code = run_promotions(
                    argparse.Namespace(
                        promotion_action="show",
                        promotion="missing-run",
                        project_root=project_root,
                        codex_home=codex_home,
                        json=False,
                    )
                )

            self.assertEqual(exit_code, 1)
            self.assertIn("promotion not found", error.getvalue())

    def test_build_promotion_detail_payload_resolves_by_branch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root, codex_home, lesson = _scaffold_promoted_worktree(temp_dir)
            listed = build_promotions_payload(project_root, codex_home)
            branch = listed["promotions"][0]["branch"]

            detail = build_promotion_detail_payload(project_root, branch, codex_home)

            self.assertIsNone(detail["error"])
            self.assertEqual(detail["promotion"]["branch"], branch)
            self.assertIn(lesson, detail["digestText"])

    def test_mark_reviewed_records_lifecycle_without_changing_git_diff(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root, codex_home, _ = _scaffold_promoted_worktree(temp_dir)
            listed = build_promotions_payload(project_root, codex_home)
            promotion = listed["promotions"][0]
            worktree_root = Path(promotion["worktreeRoot"])
            before = subprocess.run(
                ["git", "status", "--short", "--", ".governed"],
                cwd=worktree_root,
                text=True,
                capture_output=True,
                check=False,
            ).stdout

            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = run_promotions(
                    argparse.Namespace(
                        promotion_action="mark-reviewed",
                        promotion=promotion["runId"],
                        project_root=project_root,
                        codex_home=codex_home,
                        decision="accepted",
                        reason="Looks durable and scoped.",
                        reviewer="maintainer@example.local",
                        json=True,
                    )
                )

            self.assertEqual(exit_code, 0)
            detail = json.loads(output.getvalue())
            reviewed = detail["promotion"]
            self.assertEqual(reviewed["state"], "accepted")
            self.assertEqual(reviewed["review"]["decision"], "accepted")
            self.assertEqual(reviewed["review"]["reviewer"], "maintainer@example.local")
            self.assertEqual(reviewed["review"]["reason"], "Looks durable and scoped.")
            metadata_path = Path(reviewed["metadataPath"])
            self.assertTrue(metadata_path.is_file())
            self.assertFalse(str(metadata_path).startswith(str(worktree_root)))
            after = subprocess.run(
                ["git", "status", "--short", "--", ".governed"],
                cwd=worktree_root,
                text=True,
                capture_output=True,
                check=False,
            ).stdout
            self.assertEqual(after, before)
            active = subprocess.run(
                ["git", "status", "--short", "--", ".governed"],
                cwd=project_root,
                text=True,
                capture_output=True,
                check=False,
            ).stdout
            self.assertEqual(active.strip(), "")

    def test_archive_records_lifecycle_without_removing_worktree(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root, codex_home, _ = _scaffold_promoted_worktree(temp_dir)
            promotion = build_promotions_payload(project_root, codex_home)["promotions"][0]
            worktree_root = Path(promotion["worktreeRoot"])

            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = run_promotions(
                    argparse.Namespace(
                        promotion_action="archive",
                        promotion=promotion["runId"],
                        project_root=project_root,
                        codex_home=codex_home,
                        reason="Handled outside GovKB.",
                        json=True,
                    )
                )

            self.assertEqual(exit_code, 0)
            detail = json.loads(output.getvalue())
            archived = detail["promotion"]
            self.assertEqual(archived["state"], "archived")
            self.assertEqual(archived["archive"]["reason"], "Handled outside GovKB.")
            self.assertTrue(worktree_root.is_dir())


if __name__ == "__main__":
    unittest.main()
