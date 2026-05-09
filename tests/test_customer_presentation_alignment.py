"""End-to-end checks for the customer-facing GovKB presentation claims."""

from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path
import unittest

from govkb.commands.apply import run_codex_apply
from govkb.commands.init import run_init
from govkb.commands.promote import run_promote
from govkb.commands.remediate import run_remediate
from govkb.commands.validate import run_validate


def _append_lifecycle(contract_path: Path) -> None:
    contract_path.write_text(
        contract_path.read_text(encoding="utf-8").rstrip()
        + """

[lifecycle]
state = "active"
scope_justification = "Approved for customer presentation alignment fixture."

[lifecycle.approval]
status = "approved"
reviewer = "customer-demo-maintainer"
approved_at = "2026-05-09T00:00:00Z"
""",
        encoding="utf-8",
    )


def _make_scaffold_strict_valid(project_root: Path) -> None:
    steward_root = project_root / ".governed" / "capabilities" / "project-knowledge-steward"
    _append_lifecycle(steward_root / "capability.contract.toml")
    (steward_root / "references" / "long-term-memory.md").write_text(
        """# Project Knowledge Steward

## Project Working Agreement

- Keep durable project knowledge in `.governed` so it can be reviewed and shared.

## Stable Workflows

- Use `govkb validate --strict` before materializing governed project knowledge.

## Commands And Verification

- Use `python3 -m unittest tests.test_customer_presentation_alignment -v` for this customer demo fixture.

## Repo Conventions

- Treat `.governed/` as the repo-owned source for project AI knowledge.

## Code And Docs Map

- Use `README.md` as the customer demo project entry point.

## Authority Rules

- Prefer repo-governed memory over local assistant outputs after promotion.

## Candidate Skill Signals

- Stage repeated unmatched workflows as candidates before creating active capabilities.
""",
        encoding="utf-8",
    )


def _write_customer_demo_capability(project_root: Path) -> None:
    capability_root = project_root / ".governed" / "capabilities" / "workflow-review"
    (capability_root / "references").mkdir(parents=True, exist_ok=True)
    (capability_root / "prompts").mkdir(parents=True, exist_ok=True)
    (capability_root / "capability.contract.toml").write_text(
        """contract_version = 1

[capability]
id = "workflow-review"
name = "Workflow Review"
governed = true
description = "Customer-demo workflow review capability."

[routing]
aliases = ["$workflow-review", "workflow review"]
hints = ["workflow review", "customer demo"]
negative_hints = ["cron schedule"]

[memory]
enabled = true
auto_apply_min_confidence = 0.85
requires_explicit_acceptance = false

[memory.targets.main]
path = "references/long-term-memory.md"
sections = [
  "Working Agreement",
  "Stable Workflows",
  "Commands And Verification",
  "Code And Docs Map",
  "Authority Rules",
]

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
scope_justification = "Approved customer demo capability for repo-governed AI workflow reuse."

[lifecycle.approval]
status = "approved"
reviewer = "customer-demo-maintainer"
approved_at = "2026-05-09T00:00:00Z"
""",
        encoding="utf-8",
    )
    (capability_root / "instructions.md").write_text(
        """# Workflow Review

Use this governed capability for customer-demo workflow review tasks.

## Load References First

- Read `references/long-term-memory.md` before acting.

## Workflow

- Keep workflow guidance grounded in repo-owned evidence and verification commands.
""",
        encoding="utf-8",
    )
    (capability_root / "references" / "long-term-memory.md").write_text(
        """# Workflow Review

## Working Agreement

- Keep workflow review guidance short, durable, and grounded in repo evidence.

## Stable Workflows

- Review the repo-owned capability contract before changing assistant-local behavior.

## Commands And Verification

- Use `govkb validate --strict` before applying the customer demo capability.

## Code And Docs Map

- Use `README.md` as the stable demo project entry point.

## Authority Rules

- Treat `.governed/capabilities/workflow-review/capability.contract.toml` as the capability authority.
""",
        encoding="utf-8",
    )
    (capability_root / "prompts" / "initialize-kb.md").write_text(
        "# Initialize Workflow Review\n\nRead the contract and memory, then add only durable repo-grounded facts.\n",
        encoding="utf-8",
    )


def _workflow_memory(codex_home: Path, project_id: str = "customer-demo") -> Path:
    return (
        codex_home
        / "skills"
        / f"govkb-{project_id}-workflow-review"
        / "references"
        / "long-term-memory.md"
    )


class CustomerPresentationAlignmentTests(unittest.TestCase):
    """Executable proof for the customer presentation demo flow."""

    def test_customer_demo_flow_promotes_and_redistributes_governed_memory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            project_root = root / "CustomerDemo"
            first_codex_home = root / "codex-one"
            second_codex_home = root / "codex-two"
            project_root.mkdir(parents=True, exist_ok=True)
            (project_root / "README.md").write_text("# Customer Demo\n", encoding="utf-8")
            subprocess.run(["git", "init"], cwd=project_root, check=True, capture_output=True)

            self.assertEqual(
                run_init(
                    argparse.Namespace(
                        dest=project_root,
                        project_id="customer-demo",
                        project_name="Customer Demo",
                    )
                ),
                0,
            )
            _make_scaffold_strict_valid(project_root)
            _write_customer_demo_capability(project_root)

            self.assertEqual(
                run_validate(argparse.Namespace(project_root=project_root, strict=True, json=True)),
                0,
            )
            self.assertEqual(
                run_codex_apply(
                    argparse.Namespace(
                        project_root=project_root,
                        release=None,
                        revision="customer-demo-a",
                        codex_home=first_codex_home,
                        preview=False,
                    )
                ),
                0,
            )

            local_memory = _workflow_memory(first_codex_home)
            self.assertTrue(local_memory.is_file())
            addition = "- Capture customer-demo rollout evidence before changing assistant setup."
            local_memory.write_text(local_memory.read_text(encoding="utf-8").rstrip() + f"\n{addition}\n", encoding="utf-8")

            self.assertEqual(
                run_promote(
                    argparse.Namespace(
                        project_root=project_root,
                        release=None,
                        assistant="codex",
                        codex_home=first_codex_home,
                        preview=False,
                        auto=False,
                    )
                ),
                0,
            )
            repo_memory = (
                project_root
                / ".governed"
                / "capabilities"
                / "workflow-review"
                / "references"
                / "long-term-memory.md"
            )
            self.assertIn(addition, repo_memory.read_text(encoding="utf-8"))

            self.assertEqual(
                run_remediate(
                    argparse.Namespace(
                        remediation_action="project",
                        project_root=project_root,
                        write_report=True,
                        report_root=None,
                        json=False,
                    )
                ),
                0,
            )
            latest_report = project_root / ".governed" / "reports" / "remediation" / "latest-remediation-report.md"
            self.assertIn("Status: `clean`", latest_report.read_text(encoding="utf-8"))

            self.assertEqual(
                run_codex_apply(
                    argparse.Namespace(
                        project_root=project_root,
                        release=None,
                        revision="customer-demo-b",
                        codex_home=second_codex_home,
                        preview=False,
                    )
                ),
                0,
            )
            self.assertIn(addition, _workflow_memory(second_codex_home).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
