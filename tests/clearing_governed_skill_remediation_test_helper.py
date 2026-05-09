"""Helper utilities for Clearing governed skill remediation tests."""

from __future__ import annotations

import argparse
from contextlib import redirect_stderr
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import subprocess
from typing import Any

from govkb.commands.init import run_init
from govkb.commands.remediate import run_remediate
from govkb.core.remediation import RemediationReport
from govkb.core.remediation import build_remediation_report


class ClearingGovernedSkillRemediationTestHelper:
    """Feature-specific helper API."""

    def __init__(self, test_case: Any, root: Path | None = None) -> None:
        self.test_case = test_case
        self.root = root
        self.steps: list[str] = []
        self.project_root: Path | None = None

    def record_step(self, step: str) -> None:
        self.steps.append(step)

    def seed_project(self, *, git: bool = False, auto_create: bool = False, min_occurrences: int = 2) -> Path:
        if self.root is None:
            raise ValueError("root is required to seed a project")
        project_root = self.root / "Clearing"
        project_root.mkdir(parents=True, exist_ok=True)
        (project_root / "README.md").write_text("# Clearing\n", encoding="utf-8")
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = run_init(argparse.Namespace(dest=project_root, project_id="clearing", project_name="Clearing"))
        self.test_case.assertEqual(exit_code, 0)
        self.project_root = project_root
        self.make_steward_strict_ready()
        if auto_create:
            self.set_auto_create_policy(enabled=True, min_occurrences=min_occurrences)
        if git:
            subprocess.run(["git", "init"], cwd=project_root, check=True, capture_output=True, text=True)
        return project_root

    def make_steward_strict_ready(self) -> None:
        project_root = self._require_project_root()
        capability_root = project_root / ".governed" / "capabilities" / "project-knowledge-steward"
        contract_path = capability_root / "capability.contract.toml"
        contract_text = contract_path.read_text(encoding="utf-8")
        if "[lifecycle]" not in contract_text:
            contract_path.write_text(
                contract_text.rstrip()
                + self.lifecycle_block(scope_justification="Project-wide Clearing memory stewardship.")
                + "\n",
                encoding="utf-8",
            )
        memory_path = capability_root / "references" / "long-term-memory.md"
        memory_path.write_text(
            """# Project Knowledge Steward

## Project Working Agreement

- Preserve useful Clearing project memory unless strict validation identifies a concrete issue.

## Stable Workflows

- Review governed package changes before applying durable writes.

## Commands And Verification

- Run `python3 -m unittest tests.test_validate -v` from the repository root for validation checks.

## Repo Conventions

- Keep governed package state under `.governed`.

## Code And Docs Map

- Use `README.md` as the local project entry point.

## Authority Rules

- Treat `.governed/project.toml` as the source for project automation policy.

## Candidate Skill Signals

- Stage repeated specialized work as a candidate before activating a new capability.
""",
            encoding="utf-8",
        )

    def set_auto_create_policy(self, *, enabled: bool, min_occurrences: int) -> None:
        project_root = self._require_project_root()
        project_manifest = project_root / ".governed" / "project.toml"
        project_manifest.write_text(
            """schema_version = 1

[project]
id = "clearing"
name = "Clearing"

[release]
current = "unreleased"

[adapters]
enabled = ["codex"]

[automation]
"""
            + f"auto_create_capabilities = {'true' if enabled else 'false'}\n"
            + f"auto_create_min_occurrences = {min_occurrences}\n",
            encoding="utf-8",
        )

    def seed_local_stack_workflow(
        self,
        *,
        capability_id: str = "local-stack-workflow",
        scope_justification: str | None = None,
        command_bullet: str = "- Run `docs/missing-runbook.md` before changing the local stack.",
    ) -> Path:
        project_root = self._require_project_root()
        capability_root = project_root / ".governed" / "capabilities" / capability_id
        references_root = capability_root / "references"
        prompts_root = capability_root / "prompts"
        references_root.mkdir(parents=True, exist_ok=True)
        prompts_root.mkdir(parents=True, exist_ok=True)
        sections = [
            "Working Agreement",
            "Stable Workflows",
            "Commands And Verification",
            "Code And Docs Map",
            "Authority Rules",
        ]
        contract_path = capability_root / "capability.contract.toml"
        contract_path.write_text(
            f"""contract_version = 1

[capability]
id = "{capability_id}"
name = "{capability_id.replace("-", " ").title()}"
governed = true
description = "Reusable local stack workflow."

[routing]
aliases = ["{capability_id}"]
hints = ["local stack", "workflow"]
negative_hints = []

[memory]
enabled = true
auto_apply_min_confidence = 0.85
requires_explicit_acceptance = false

[memory.targets.main]
path = "references/long-term-memory.md"
sections = {json.dumps(sections)}

[bootstrap]
profile = "workflow"
repo_roots = ["."]
authority_paths = ["README.md"]
seed_paths = ["README.md"]

[kb_health]
requires_verification_commands = true
requires_repo_map = true
required_sections = ["Working Agreement", "Stable Workflows", "Commands And Verification", "Code And Docs Map"]
"""
            + self.lifecycle_block(scope_justification=scope_justification),
            encoding="utf-8",
        )
        (capability_root / "instructions.md").write_text(
            f"""# {capability_id.replace("-", " ").title()}

Load `references/long-term-memory.md` before local stack workflow work.

## Workflow

- Keep remediation evidence in governed package review reports.
""",
            encoding="utf-8",
        )
        (references_root / "long-term-memory.md").write_text(
            f"""# {capability_id.replace("-", " ").title()}

## Working Agreement

- Keep the capability focused on durable Clearing local stack behavior.

## Stable Workflows

- Review strict validation findings before editing package memory.

## Commands And Verification

{command_bullet}

## Code And Docs Map

- Use `README.md` as the repository entry point.

## Authority Rules

- Require maintainer approval before rewriting governed capability files.
""",
            encoding="utf-8",
        )
        (prompts_root / "initialize-kb.md").write_text(
            f"# Initialize {capability_id}\n\nReview strict remediation evidence before activation.\n",
            encoding="utf-8",
        )
        return capability_root

    def lifecycle_block(
        self,
        *,
        scope_justification: str | None = None,
        state: str = "active",
    ) -> str:
        justification = f'scope_justification = "{scope_justification}"\n' if scope_justification else ""
        return f"""

[lifecycle]
state = "{state}"
{justification}
[lifecycle.approval]
status = "approved"
reviewer = "test-reviewer"
approved_at = "2026-05-02T00:00:00Z"
"""

    def build_report(self) -> RemediationReport:
        return build_remediation_report(self._require_project_root())

    def run_remediate_project(
        self,
        *,
        write_report: bool = False,
        json_output: bool = False,
        report_root: Path | None = None,
    ) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = run_remediate(
                argparse.Namespace(
                    remediation_action="project",
                    project_root=self._require_project_root(),
                    write_report=write_report,
                    report_root=report_root,
                    json=json_output,
                )
            )
        return exit_code, stdout.getvalue(), stderr.getvalue()

    def capability_file_snapshot(self) -> dict[str, str]:
        project_root = self._require_project_root()
        capabilities_root = project_root / ".governed" / "capabilities"
        return {
            str(path.relative_to(capabilities_root)): path.read_text(encoding="utf-8")
            for path in sorted(capabilities_root.rglob("*"))
            if path.is_file()
        }

    def _require_project_root(self) -> Path:
        if self.project_root is None:
            raise ValueError("project has not been seeded")
        return self.project_root
