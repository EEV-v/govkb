"""Tests for governed memory promotion."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path
import unittest

from govkb.commands.apply import run_codex_apply
from govkb.commands.create_capability import run_create_capability
from govkb.commands.init import run_init
from govkb.commands.promote import run_promote
from govkb.core.promotion_lifecycle import promotion_metadata_path
from govkb.core.promotion_lifecycle import read_promotion_metadata
from govkb.core.promotion_lifecycle import reviewed_promotion_metadata
from govkb.core.promotion_lifecycle import write_promotion_metadata


class PromoteCommandTests(unittest.TestCase):
    """Promotion from materialized Codex memory back to repo source."""

    def _scaffold_project(self, temp_dir: str) -> tuple[Path, Path, Path, Path]:
        project_root = Path(temp_dir) / "DemoProject"
        codex_home = Path(temp_dir) / "codex-home"
        project_root.mkdir(parents=True, exist_ok=True)
        run_init(argparse.Namespace(dest=project_root, project_id="demo-project", project_name="Demo Project"))
        run_create_capability(argparse.Namespace(capability_id="Workflow Review", project_root=project_root))
        run_codex_apply(
            argparse.Namespace(
                project_root=project_root,
                release=None,
                revision="promote-test",
                codex_home=codex_home,
                preview=False,
            )
        )
        repo_memory = (
            project_root
            / ".governed"
            / "capabilities"
            / "workflow-review"
            / "references"
            / "long-term-memory.md"
        )
        local_memory = codex_home / "skills" / "govkb-demo-project-workflow-review" / "references" / "long-term-memory.md"
        return project_root, codex_home, repo_memory, local_memory

    def test_promote_applies_append_only_memory_addition(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root, codex_home, repo_memory, local_memory = self._scaffold_project(temp_dir)
            local_memory.write_text(
                local_memory.read_text(encoding="utf-8").rstrip()
                + "\n- Keep estimates anchored to reusable functional slices.\n",
                encoding="utf-8",
            )

            exit_code = run_promote(
                argparse.Namespace(
                    project_root=project_root,
                    release=None,
                    assistant="codex",
                    codex_home=codex_home,
                    preview=False,
                    auto=False,
                )
            )

            self.assertEqual(exit_code, 0)
            self.assertIn(
                "Keep estimates anchored to reusable functional slices.",
                repo_memory.read_text(encoding="utf-8"),
            )
            report_root = project_root / ".governed" / "reports" / "promotions"
            self.assertTrue(any(report_root.glob("*-promote-report.md")))
            self.assertTrue((report_root / "latest-promotion-digest.md").is_file())

    def test_promote_rejects_non_append_memory_change(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root, codex_home, repo_memory, local_memory = self._scaffold_project(temp_dir)
            original_repo = repo_memory.read_text(encoding="utf-8")
            local_memory.write_text(original_repo.replace("# Workflow Review", "# Changed Title"), encoding="utf-8")

            exit_code = run_promote(
                argparse.Namespace(
                    project_root=project_root,
                    release=None,
                    assistant="codex",
                    codex_home=codex_home,
                    preview=False,
                    auto=False,
                )
            )

            self.assertEqual(exit_code, 1)
            self.assertEqual(repo_memory.read_text(encoding="utf-8"), original_repo)

    def test_promote_ignores_scaffold_placeholder_bullets(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root, codex_home, repo_memory, local_memory = self._scaffold_project(temp_dir)
            original_repo = repo_memory.read_text(encoding="utf-8")
            local_memory.write_text(
                original_repo.rstrip()
                + "\n- Add authority rules here when one governed file should win over broader docs.\n",
                encoding="utf-8",
            )

            exit_code = run_promote(
                argparse.Namespace(
                    project_root=project_root,
                    release=None,
                    assistant="codex",
                    codex_home=codex_home,
                    preview=True,
                    auto=False,
                )
            )

            self.assertEqual(exit_code, 0)
            self.assertEqual(repo_memory.read_text(encoding="utf-8"), original_repo)

    def test_promote_allows_append_when_blank_lines_shift(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root, codex_home, repo_memory, local_memory = self._scaffold_project(temp_dir)
            original_repo = repo_memory.read_text(encoding="utf-8")
            local_memory.write_text(
                original_repo.replace(
                    "- Add stable workflow steps here after bootstrap or repeated evidence.\n\n## Commands And Verification",
                    "- Add stable workflow steps here after bootstrap or repeated evidence.\n- Prefer the root compose pair for routine local work.\n## Commands And Verification",
                ),
                encoding="utf-8",
            )

            exit_code = run_promote(
                argparse.Namespace(
                    project_root=project_root,
                    release=None,
                    assistant="codex",
                    codex_home=codex_home,
                    preview=False,
                    auto=False,
                )
            )

            self.assertEqual(exit_code, 0)
            self.assertIn(
                "Prefer the root compose pair for routine local work.",
                repo_memory.read_text(encoding="utf-8"),
            )

    @unittest.skipIf(shutil.which("git") is None, "git is not installed")
    def test_promote_digest_reports_git_status(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root, codex_home, _, local_memory = self._scaffold_project(temp_dir)
            subprocess.run(["git", "init"], cwd=project_root, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "govkb@example.local"], cwd=project_root, check=True)
            subprocess.run(["git", "config", "user.name", "GovKB Test"], cwd=project_root, check=True)
            subprocess.run(["git", "add", ".governed"], cwd=project_root, check=True)
            subprocess.run(["git", "commit", "-m", "initial governed package"], cwd=project_root, check=True, capture_output=True)

            local_memory.write_text(
                local_memory.read_text(encoding="utf-8").rstrip()
                + "\n- Surface promotion git status in the latest digest.\n",
                encoding="utf-8",
            )

            exit_code = run_promote(
                argparse.Namespace(
                    project_root=project_root,
                    release=None,
                    assistant="codex",
                    codex_home=codex_home,
                    preview=False,
                    auto=False,
                )
            )

            self.assertEqual(exit_code, 0)
            digest = (
                project_root
                / ".governed"
                / "reports"
                / "promotions"
                / "latest-promotion-digest.md"
            ).read_text(encoding="utf-8")
            self.assertIn("git .governed", digest)
            self.assertIn("long-term-memory.md", digest)
            self.assertIn("latest-promotion-digest.md", digest)

    @unittest.skipIf(shutil.which("git") is None, "git is not installed")
    def test_auto_promote_uses_isolated_worktree_without_mutating_active_worktree(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root, codex_home, repo_memory, local_memory = self._scaffold_project(temp_dir)
            subprocess.run(["git", "init"], cwd=project_root, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "govkb@example.local"], cwd=project_root, check=True)
            subprocess.run(["git", "config", "user.name", "GovKB Test"], cwd=project_root, check=True)
            subprocess.run(["git", "add", ".governed"], cwd=project_root, check=True)
            subprocess.run(["git", "commit", "-m", "initial governed package"], cwd=project_root, check=True, capture_output=True)
            original_repo = repo_memory.read_text(encoding="utf-8")
            local_memory.write_text(
                local_memory.read_text(encoding="utf-8").rstrip()
                + "\n- Keep automated learning out of the active checkout until maintainer review.\n",
                encoding="utf-8",
            )

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

            self.assertEqual(exit_code, 0)
            self.assertEqual(repo_memory.read_text(encoding="utf-8"), original_repo)
            proc = subprocess.run(
                ["git", "status", "--short", "--", ".governed"],
                cwd=project_root,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(proc.stdout.strip(), "")
            worktree_roots = sorted((codex_home / "memories" / "govkb" / "worktrees" / "demo-project").glob("*"))
            self.assertEqual(len(worktree_roots), 1)
            isolated_root = worktree_roots[0]
            isolated_memory = (
                isolated_root
                / ".governed"
                / "capabilities"
                / "workflow-review"
                / "references"
                / "long-term-memory.md"
            )
            self.assertIn(
                "Keep automated learning out of the active checkout until maintainer review.",
                isolated_memory.read_text(encoding="utf-8"),
            )
            branch_proc = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=isolated_root,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertTrue(branch_proc.stdout.strip().startswith("codex/govkb-auto-promote/demo-project/"))
            isolated_status = subprocess.run(
                ["git", "status", "--short", "--", ".governed"],
                cwd=isolated_root,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertIn("long-term-memory.md", isolated_status.stdout)
            self.assertTrue(
                (isolated_root / ".governed" / "reports" / "promotions" / "latest-promotion-digest.md").is_file()
            )

    @unittest.skipIf(shutil.which("git") is None, "git is not installed")
    def test_auto_promote_reuses_equivalent_isolated_worktree(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root, codex_home, _, local_memory = self._scaffold_project(temp_dir)
            subprocess.run(["git", "init"], cwd=project_root, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "govkb@example.local"], cwd=project_root, check=True)
            subprocess.run(["git", "config", "user.name", "GovKB Test"], cwd=project_root, check=True)
            subprocess.run(["git", "add", ".governed"], cwd=project_root, check=True)
            subprocess.run(["git", "commit", "-m", "initial governed package"], cwd=project_root, check=True, capture_output=True)
            local_memory.write_text(
                local_memory.read_text(encoding="utf-8").rstrip()
                + "\n- Reuse equivalent auto-promotion worktrees instead of duplicating them.\n",
                encoding="utf-8",
            )
            args = argparse.Namespace(
                project_root=project_root,
                release=None,
                assistant="codex",
                codex_home=codex_home,
                preview=False,
                auto=True,
            )

            first_exit = run_promote(args)
            second_exit = run_promote(args)

            self.assertEqual(first_exit, 0)
            self.assertEqual(second_exit, 0)
            worktree_roots = sorted((codex_home / "memories" / "govkb" / "worktrees" / "demo-project").glob("*"))
            self.assertEqual(len(worktree_roots), 1)

    @unittest.skipIf(shutil.which("git") is None, "git is not installed")
    def test_auto_promote_digest_separates_previously_accepted_additions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root, codex_home, _, local_memory = self._scaffold_project(temp_dir)
            subprocess.run(["git", "init"], cwd=project_root, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "govkb@example.local"], cwd=project_root, check=True)
            subprocess.run(["git", "config", "user.name", "GovKB Test"], cwd=project_root, check=True)
            subprocess.run(["git", "add", ".governed"], cwd=project_root, check=True)
            subprocess.run(["git", "commit", "-m", "initial governed package"], cwd=project_root, check=True, capture_output=True)
            local_memory.write_text(
                local_memory.read_text(encoding="utf-8").rstrip()
                + "\n- First accepted lesson stays pending until applied.\n",
                encoding="utf-8",
            )
            args = argparse.Namespace(
                project_root=project_root,
                release=None,
                assistant="codex",
                codex_home=codex_home,
                preview=False,
                auto=True,
            )

            self.assertEqual(run_promote(args), 0)
            first_worktree = sorted((codex_home / "memories" / "govkb" / "worktrees" / "demo-project").glob("*"))[0]
            first_metadata_path = promotion_metadata_path(codex_home, "demo-project", first_worktree.name)
            first_metadata = read_promotion_metadata(first_metadata_path)
            self.assertIsNotNone(first_metadata)
            write_promotion_metadata(
                first_metadata_path,
                reviewed_promotion_metadata(
                    first_metadata or {},
                    state="accepted",
                    reviewer=None,
                    reason="Accepted in test.",
                ),
            )
            local_memory.write_text(
                local_memory.read_text(encoding="utf-8").rstrip()
                + "\n- Second lesson is the only new review item.\n",
                encoding="utf-8",
            )

            self.assertEqual(run_promote(args), 0)

            worktree_roots = sorted((codex_home / "memories" / "govkb" / "worktrees" / "demo-project").glob("*"))
            self.assertEqual(len(worktree_roots), 2)
            second_digest = (
                worktree_roots[-1] / ".governed" / "reports" / "promotions" / "latest-promotion-digest.md"
            ).read_text(encoding="utf-8")
            self.assertIn("## New Additions To Review", second_digest)
            self.assertIn("Addition: - Second lesson is the only new review item.", second_digest)
            self.assertIn("## Previously Accepted Carry-Forward", second_digest)
            self.assertIn("Accepted earlier: - First accepted lesson stays pending until applied.", second_digest)


if __name__ == "__main__":
    unittest.main()
