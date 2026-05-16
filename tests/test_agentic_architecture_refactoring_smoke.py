"""Smoke tests for the Agentic Architecture Refactoring feature."""

from __future__ import annotations

from pathlib import Path
import unittest


class AgenticArchitectureRefactoringSmokeTests(unittest.TestCase):
    """Traceable smoke coverage for the ownership contract."""

    def test_uc_1_agentic_state_ownership_map_is_present(self) -> None:
        """UC-1: Maintainer can inspect the agentic state ownership map."""
        repo_root = Path(__file__).resolve().parents[1]
        doc_path = (
            repo_root
            / "docs"
            / "governed-skill-knowledge-framework"
            / "architecture"
            / "agentic-state-ownership.md"
        )

        text = doc_path.read_text(encoding="utf-8")

        self.assertIn("Authoritative repo source", text)
        self.assertIn("Derived assistant-local output", text)
        self.assertIn("Generated lifecycle audit metadata", text)
        self.assertIn("Disposable review store", text)
        self.assertIn("VS Code extension in-memory state", text)
        self.assertIn("Temporary test directories", text)
        self.assertIn("Mutation Owners", text)
        self.assertIn("Cleanup Policy", text)
        self.assertIn("Test Isolation", text)
        self.assertIn("must not copy Caveman", text)


if __name__ == "__main__":
    unittest.main()
