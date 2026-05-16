"""Use-case tests for Agentic Architecture Refactoring."""

from __future__ import annotations

import argparse
from contextlib import redirect_stdout
import io
import json
import tempfile
from pathlib import Path
import unittest

from govkb.commands.init import run_init
from govkb.commands.promotions import build_promotion_cleanup_payload
from govkb.commands.promotions import build_promotions_payload
from govkb.commands.promotions import run_promotions
from govkb.core.promotion_lifecycle import applied_promotion_metadata
from govkb.core.promotion_lifecycle import archived_promotion_metadata
from govkb.core.promotion_lifecycle import initial_promotion_metadata
from govkb.core.promotion_lifecycle import promotion_metadata_path
from govkb.core.promotion_lifecycle import read_promotion_metadata
from govkb.core.promotion_lifecycle import reviewed_promotion_metadata
from govkb.core.promotion_lifecycle import write_promotion_metadata


class AgenticArchitectureRefactoringUseCaseTests(unittest.TestCase):
    """Promotion lifecycle and cleanup workflow coverage."""

    def _scaffold_project(self, temp_dir: str) -> tuple[Path, Path]:
        project_root = Path(temp_dir) / "DemoProject"
        codex_home = Path(temp_dir) / "codex-home"
        project_root.mkdir(parents=True, exist_ok=True)
        run_init(argparse.Namespace(dest=project_root, project_id="demo-project", project_name="Demo Project"))
        return project_root, codex_home

    def _write_promotion(self, project_root: Path, codex_home: Path, run_id: str, state: str) -> Path:
        worktree_root = codex_home / "memories" / "govkb" / "worktrees" / "demo-project" / run_id
        digest_path = worktree_root / ".governed" / "reports" / "promotions" / "latest-promotion-digest.md"
        report_path = worktree_root / ".governed" / "reports" / "promotions" / f"{run_id}-promote-report.md"
        digest_path.parent.mkdir(parents=True, exist_ok=True)
        digest_path.write_text("# Digest\n", encoding="utf-8")
        report_path.write_text("# Report\n", encoding="utf-8")
        metadata = initial_promotion_metadata(
            project_id="demo-project",
            project_root=project_root,
            codex_home=codex_home,
            run_id=run_id,
            branch=f"codex/govkb-auto-promote/demo-project/{run_id}",
            worktree_root=worktree_root,
            digest_path=digest_path,
            report_path=report_path,
        )
        if state == "accepted":
            metadata = reviewed_promotion_metadata(metadata, state="accepted", reviewer=None, reason="Accepted in test.")
        elif state == "rejected":
            metadata = reviewed_promotion_metadata(metadata, state="rejected", reviewer=None, reason="Rejected in test.")
        elif state == "applied":
            metadata = reviewed_promotion_metadata(metadata, state="accepted", reviewer=None, reason="Accepted in test.")
            metadata = applied_promotion_metadata(
                metadata,
                project_root=project_root,
                files=[".governed/capabilities/workflow-review/references/long-term-memory.md"],
            )
        elif state == "archived":
            metadata = archived_promotion_metadata(metadata, reason="Archived in test.")
        elif state != "ready-for-review":
            metadata["state"] = state
        write_promotion_metadata(promotion_metadata_path(codex_home, "demo-project", run_id), metadata)
        return worktree_root

    def test_uc_4_cleanup_preview_does_not_write_files_or_metadata(self) -> None:
        """UC-4: Cleanup previews stale and duplicate promotion worktrees."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root, codex_home = self._scaffold_project(temp_dir)
            applied_root = self._write_promotion(project_root, codex_home, "run-applied", "applied")
            ready_root = self._write_promotion(project_root, codex_home, "run-ready", "ready-for-review")
            metadata_path = promotion_metadata_path(codex_home, "demo-project", "run-applied")
            metadata_before = metadata_path.read_text(encoding="utf-8")

            payload = build_promotion_cleanup_payload(project_root, codex_home, apply=False)

            self.assertEqual(payload["mode"], "preview")
            self.assertEqual([item["runId"] for item in payload["eligible"]], ["run-applied"])
            self.assertEqual([item["runId"] for item in payload["skipped"]], ["run-ready"])
            self.assertTrue(applied_root.is_dir())
            self.assertTrue(ready_root.is_dir())
            self.assertEqual(metadata_path.read_text(encoding="utf-8"), metadata_before)

    def test_uc_5_cleanup_apply_removes_only_eligible_worktrees_and_preserves_metadata(self) -> None:
        """UC-5: Cleanup apply removes only eligible artifacts."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root, codex_home = self._scaffold_project(temp_dir)
            applied_root = self._write_promotion(project_root, codex_home, "run-applied", "applied")
            archived_root = self._write_promotion(project_root, codex_home, "run-archived", "archived")
            ready_root = self._write_promotion(project_root, codex_home, "run-ready", "ready-for-review")

            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = run_promotions(
                    argparse.Namespace(
                        promotion_action="cleanup",
                        project_root=project_root,
                        codex_home=codex_home,
                        preview=False,
                        apply=True,
                        reason="Test cleanup.",
                        json=True,
                    )
                )

            self.assertEqual(exit_code, 0)
            payload = json.loads(output.getvalue())
            self.assertEqual(payload["mode"], "apply")
            self.assertCountEqual([item["runId"] for item in payload["eligible"]], ["run-applied", "run-archived"])
            self.assertFalse(applied_root.exists())
            self.assertFalse(archived_root.exists())
            self.assertTrue(ready_root.is_dir())
            applied_metadata = read_promotion_metadata(promotion_metadata_path(codex_home, "demo-project", "run-applied"))
            archived_metadata = read_promotion_metadata(promotion_metadata_path(codex_home, "demo-project", "run-archived"))
            ready_metadata = read_promotion_metadata(promotion_metadata_path(codex_home, "demo-project", "run-ready"))
            self.assertEqual(applied_metadata["state"], "cleaned")
            self.assertEqual(archived_metadata["state"], "cleaned")
            self.assertEqual(ready_metadata["state"], "ready-for-review")
            self.assertIn(str(applied_root.resolve()), applied_metadata["cleanup"]["removedPaths"])
            self.assertEqual(applied_metadata["cleanup"]["reason"], "Test cleanup.")
            self.assertTrue((project_root / ".governed").is_dir())

            after = build_promotions_payload(project_root, codex_home)
            self.assertEqual([promotion["runId"] for promotion in after["promotions"]], ["run-ready"])

    def test_uc_5_cleanup_apply_is_idempotent_after_first_removal(self) -> None:
        """UC-5: Cleanup apply can be safely rerun."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root, codex_home = self._scaffold_project(temp_dir)
            self._write_promotion(project_root, codex_home, "run-applied", "applied")

            first = build_promotion_cleanup_payload(project_root, codex_home, apply=True, reason="First cleanup.")
            second = build_promotion_cleanup_payload(project_root, codex_home, apply=True, reason="Second cleanup.")

            self.assertEqual(
                first["removed"],
                [str((codex_home / "memories" / "govkb" / "worktrees" / "demo-project" / "run-applied").resolve())],
            )
            self.assertEqual(second["eligible"], [])
            self.assertEqual(second["removed"], [])
            metadata = read_promotion_metadata(promotion_metadata_path(codex_home, "demo-project", "run-applied"))
            self.assertEqual(metadata["state"], "cleaned")
            self.assertEqual(metadata["cleanup"]["reason"], "First cleanup.")


if __name__ == "__main__":
    unittest.main()
