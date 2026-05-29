"""Smoke tests for memory-review capability-evolution behavior."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import sys
import tempfile
from pathlib import Path
import unittest

import govkb

from govkb.core.proposals import stage_proposal

try:
    from memory_review_capability_evolution_test_helper import MemoryReviewCapabilityEvolutionTestHelper
except ModuleNotFoundError:  # pragma: no cover - supports module-style unittest invocation.
    from tests.memory_review_capability_evolution_test_helper import MemoryReviewCapabilityEvolutionTestHelper


def load_scheduler():
    script_path = Path(next(iter(govkb.__path__))).resolve() / "adapters" / "codex" / "bin" / "codex-memory-review"
    loader = importlib.machinery.SourceFileLoader("govkb_mrce_scheduler", str(script_path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    if spec is None:
        raise AssertionError(f"Could not load scheduler spec from {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[loader.name] = module
    loader.exec_module(module)
    return module


class MemoryReviewCapabilityEvolutionSmokeTests(unittest.TestCase):
    """Happy-path proposal smoke coverage."""

    def test_smoke_schema_and_core_staging(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            helper = MemoryReviewCapabilityEvolutionTestHelper(self, Path(temp_dir))
            helper.record_step("Given a governed project and an existing target capability")
            project_root = helper.seed_project()
            helper.seed_capability()
            scheduler = load_scheduler()

            helper.record_step("When memory review schema and proposal staging are used")
            self.assertIn("capability_evolution_proposals", scheduler.schema_text())
            result = stage_proposal(
                project_root,
                helper.proposal_payload(),
                source_run_id="run-1",
                source_session_id="session-1",
            )

            helper.record_step("Then a reviewable proposal exists and no final script has been written")
            self.assertTrue((result.proposal_root / "proposal.toml").is_file())
            final_script = (
                project_root
                / ".governed"
                / "capabilities"
                / "release-validation-workflow"
                / "tools"
                / "scripts"
                / "check_release.py"
            )
            self.assertFalse(final_script.exists())


if __name__ == "__main__":
    unittest.main()
