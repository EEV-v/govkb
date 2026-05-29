"""Helper utilities for memory-review capability-evolution tests."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from govkb.commands.init import run_init


class MemoryReviewCapabilityEvolutionTestHelper:
    """Feature-specific temp project helpers."""

    def __init__(self, test_case: Any, root: Path) -> None:
        self.test_case = test_case
        self.root = root
        self.steps: list[str] = []
        self.project_root: Path | None = None

    def record_step(self, step: str) -> None:
        self.steps.append(step)

    def seed_project(self) -> Path:
        project_root = self.root / "DemoProject"
        project_root.mkdir(parents=True, exist_ok=True)
        (project_root / "README.md").write_text("# Demo Project\n", encoding="utf-8")
        exit_code = run_init(
            argparse.Namespace(dest=project_root, project_id="demo-project", project_name="Demo Project")
        )
        self.test_case.assertEqual(exit_code, 0)
        self.project_root = project_root
        return project_root

    def seed_capability(self, capability_id: str = "release-validation-workflow") -> Path:
        project_root = self._require_project_root()
        capability_root = project_root / ".governed" / "capabilities" / capability_id
        references_root = capability_root / "references"
        prompts_root = capability_root / "prompts"
        references_root.mkdir(parents=True, exist_ok=True)
        prompts_root.mkdir(parents=True, exist_ok=True)
        (capability_root / "capability.contract.toml").write_text(
            f"""contract_version = 1

[capability]
id = "{capability_id}"
name = "{capability_id.replace("-", " ").title()}"
governed = true
description = "Reusable release validation workflow."

[routing]
aliases = ["{capability_id}"]
hints = ["release validation", "script proposal"]
negative_hints = []

[memory]
enabled = true
auto_apply_min_confidence = 0.85
requires_explicit_acceptance = false

[memory.targets.main]
path = "references/long-term-memory.md"
sections = ["Working Agreement", "Stable Workflows", "Commands And Verification", "Code And Docs Map"]

[bootstrap]
profile = "workflow"
repo_roots = ["."]
authority_paths = ["README.md"]
seed_paths = ["README.md"]

[kb_health]
requires_verification_commands = true
requires_repo_map = true
required_sections = ["Working Agreement", "Stable Workflows", "Commands And Verification", "Code And Docs Map"]

[lifecycle]
state = "active"
scope_justification = "Reviewer approved this capability scope for tests."

[lifecycle.approval]
status = "approved"
reviewer = "test-reviewer"
approved_at = "2026-05-28T00:00:00Z"
""",
            encoding="utf-8",
        )
        (capability_root / "instructions.md").write_text(
            f"""# {capability_id.replace("-", " ").title()}

Use this governed capability for repeatable release validation tasks.

## Workflow

- Ground reusable helper proposals in repo-owned evidence.
""",
            encoding="utf-8",
        )
        (references_root / "long-term-memory.md").write_text(
            f"""# {capability_id.replace("-", " ").title()}

## Working Agreement

- Keep helper artifacts scoped to this capability.

## Stable Workflows

- Review proposal metadata before writing governed package files.

## Commands And Verification

- Run GovKB validation before accepting generated helper artifacts.

## Code And Docs Map

- Use `README.md` as the project entry point.
""",
            encoding="utf-8",
        )
        (prompts_root / "initialize-kb.md").write_text(
            f"# Initialize {capability_id}\n\nKeep only durable governed knowledge.\n",
            encoding="utf-8",
        )
        return capability_root

    def proposal_payload(
        self,
        *,
        proposal_id: str = "release-validation-script",
        target_capability: str = "release-validation-workflow",
        proposal_type: str = "script",
        output_path: str | None = None,
        safety_class: str = "read_only",
        draft_output: str | None = None,
    ) -> dict[str, object]:
        output_path = output_path or (
            f".governed/capabilities/{target_capability}/tools/scripts/check_release.py"
        )
        draft_output = draft_output or (
            "#!/usr/bin/env python3\n"
            "\"\"\"Read-only release validation helper.\"\"\"\n\n"
            "def main() -> int:\n"
            "    print('release validation ok')\n"
            "    return 0\n\n"
            "if __name__ == '__main__':\n"
            "    raise SystemExit(main())\n"
        )
        return {
            "proposal_id": proposal_id,
            "target_capability": target_capability,
            "proposal_type": proposal_type,
            "output_paths": [output_path],
            "purpose": "Create a reusable read-only release validation helper.",
            "inputs": ["release notes"],
            "outputs": ["validation summary"],
            "safety_class": safety_class,
            "evidence": "Synthetic session showed repeated release validation helper steps.",
            "verification_command": "PYTHONPATH=src python3 -m govkb.cli validate --strict <project-root> --json",
            "confidence": 0.94,
            "sensitivity": "clean",
            "cron_apply_reason": "Cron stages this proposal only; maintainer approval is required before writing files.",
            "draft_output": draft_output,
        }

    def approve_proposal(self, proposal_id: str) -> Path:
        project_root = self._require_project_root()
        proposal_path = project_root / ".governed" / "review-proposals" / proposal_id / "proposal.toml"
        text = proposal_path.read_text(encoding="utf-8")
        text = text.replace('status = "staged"', 'status = "approved"', 1)
        text = text.replace('status = "pending"', 'status = "approved"', 1)
        text = text.replace('approver = ""', 'approver = "test-reviewer"', 1)
        text = text.replace('approved_at = ""', 'approved_at = "2026-05-28T00:00:00Z"', 1)
        proposal_path.write_text(text, encoding="utf-8")
        return proposal_path

    def _require_project_root(self) -> Path:
        if self.project_root is None:
            raise ValueError("project has not been seeded")
        return self.project_root
