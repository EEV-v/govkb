"""Helper utilities for governed skill quality gate tests."""

from __future__ import annotations

import argparse
from contextlib import redirect_stderr, redirect_stdout
import io
from pathlib import Path
from typing import Any

from govkb.commands.init import run_init
from govkb.commands.validate import run_validate
from govkb.core.contracts import load_project_bundle
from govkb.core.governed_skill import StrictValidationResult
from govkb.core.governed_skill import validate_governed_skill_package


class GovernedSkillQualityGatesTestHelper:
    """Feature-specific helper API."""

    def __init__(self, test_case: Any, root: Path | None = None) -> None:
        self.test_case = test_case
        self.root = root
        self.steps: list[str] = []
        self.project_root: Path | None = None

    def record_step(self, step: str) -> None:
        self.steps.append(step)

    def seed_project(self) -> Path:
        if self.root is None:
            raise ValueError("root is required to seed a project")
        project_root = self.root / "DemoProject"
        project_root.mkdir(parents=True, exist_ok=True)
        (project_root / "README.md").write_text("# Demo Project\n", encoding="utf-8")
        exit_code = run_init(
            argparse.Namespace(dest=project_root, project_id="demo-project", project_name="Demo Project")
        )
        self.test_case.assertEqual(exit_code, 0)
        self.project_root = project_root
        self.make_capability_strict_ready("project-knowledge-steward")
        return project_root

    def make_capability_strict_ready(self, capability_id: str) -> Path:
        project_root = self._require_project_root()
        capability_root = project_root / ".governed" / "capabilities" / capability_id
        contract_path = capability_root / "capability.contract.toml"
        contract_text = contract_path.read_text(encoding="utf-8")
        if "[lifecycle]" not in contract_text:
            contract_path.write_text(contract_text.rstrip() + self.lifecycle_block() + "\n", encoding="utf-8")
        memory_path = capability_root / "references" / "long-term-memory.md"
        if memory_path.is_file():
            memory_path.write_text(
                """# Project Knowledge Steward

## Project Working Agreement

- Keep durable project knowledge in `.governed` so it can be reviewed, versioned, and shared.

## Stable Workflows

- Review governed capability changes with strict validation before activation.

## Commands And Verification

- Run `python3 -m unittest tests.test_validate -v` from the repository root for validation regressions.

## Repo Conventions

- Keep source packages under src/govkb and tests under the repository test root.

## Code And Docs Map

- Use `README.md` as the project entry point.

## Authority Rules

- Treat `.governed` contract files as the source of truth for capability metadata.

## Candidate Skill Signals

- Stage repeated specialized work as a candidate before adding an active governed capability.
""",
                encoding="utf-8",
            )
        return capability_root

    def seed_capability(
        self,
        capability_id: str = "release-validation-workflow",
        *,
        approved: bool = True,
        lifecycle_state: str = "active",
        scope_justification: str | None = "Release validation workflow and reusable signoff evidence.",
        memory_body: str | None = None,
        instructions_body: str | None = None,
    ) -> Path:
        project_root = self._require_project_root()
        capability_root = project_root / ".governed" / "capabilities" / capability_id
        references_root = capability_root / "references"
        prompts_root = capability_root / "prompts"
        references_root.mkdir(parents=True, exist_ok=True)
        prompts_root.mkdir(parents=True, exist_ok=True)
        sections = (
            "Working Agreement",
            "Stable Workflows",
            "Commands And Verification",
            "Code And Docs Map",
            "Authority Rules",
        )
        lifecycle = (
            self.lifecycle_block(state=lifecycle_state, scope_justification=scope_justification)
            if approved
            else ""
        )
        (capability_root / "capability.contract.toml").write_text(
            f"""contract_version = 1

[capability]
id = "{capability_id}"
name = "{capability_id.replace("-", " ").title()}"
governed = true
description = "Reusable release validation workflow."

[routing]
aliases = ["{capability_id}"]
hints = ["release validation", "signoff evidence"]
negative_hints = []

[memory]
enabled = true
auto_apply_min_confidence = 0.85
requires_explicit_acceptance = false

[memory.targets.main]
path = "references/long-term-memory.md"
sections = {list(sections)!r}

[bootstrap]
profile = "workflow"
repo_roots = ["."]
authority_paths = ["README.md"]
seed_paths = ["README.md"]

[kb_health]
requires_verification_commands = true
requires_repo_map = true
required_sections = ["Working Agreement", "Stable Workflows", "Commands And Verification", "Code And Docs Map"]
{lifecycle}
""",
            encoding="utf-8",
        )
        (capability_root / "instructions.md").write_text(
            instructions_body
            or f"""# {capability_id.replace("-", " ").title()}

Use this governed capability for repeatable release validation tasks.

## Load References First

- Read `references/long-term-memory.md` before acting.

## Workflow

- Ground validation work in repository-owned release notes, tests, and signoff evidence.
""",
            encoding="utf-8",
        )
        (references_root / "long-term-memory.md").write_text(
            memory_body
            or self.memory_text(
                title=capability_id.replace("-", " ").title(),
                command_bullet="- Run `python3 -m unittest tests.test_validate -v` from the repository root before signoff.",
            ),
            encoding="utf-8",
        )
        (prompts_root / "initialize-kb.md").write_text(
            f"# Initialize {capability_id}\n\nReview candidate facts and keep only durable governed knowledge.\n",
            encoding="utf-8",
        )
        return capability_root

    def lifecycle_block(
        self,
        *,
        state: str = "active",
        scope_justification: str | None = "Reviewer approved this governed capability scope for activation.",
    ) -> str:
        justification_line = f'scope_justification = "{scope_justification}"\n' if scope_justification else ""
        return f"""

[lifecycle]
state = "{state}"
{justification_line}
[lifecycle.approval]
status = "approved"
reviewer = "test-reviewer"
approved_at = "2026-05-01T00:00:00Z"
"""

    def memory_text(self, *, title: str, command_bullet: str) -> str:
        return f"""# {title}

## Working Agreement

- Keep the capability focused on durable release validation decisions.

## Stable Workflows

- Review release notes, run verification commands, and preserve reusable signoff evidence.

## Commands And Verification

{command_bullet}

## Code And Docs Map

- Use `README.md` as the repository entry point for local verification context.

## Authority Rules

- Prefer governed capability memory over broader notes when release validation procedures conflict.
"""

    def strict_result(self, capability_id: str, *, activation_required: bool = False) -> StrictValidationResult:
        project_root = self._require_project_root()
        bundle, result = load_project_bundle(project_root)
        self.test_case.assertFalse(result.errors, [message.message for message in result.errors])
        return validate_governed_skill_package(
            project_root,
            bundle.capabilities[capability_id],
            activation_required=activation_required,
        )

    def run_validate(self, *, strict: bool = False) -> tuple[int, str, str]:
        project_root = self._require_project_root()
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = run_validate(argparse.Namespace(project_root=project_root, strict=strict, json=False))
        return exit_code, stdout.getvalue(), stderr.getvalue()

    def _require_project_root(self) -> Path:
        if self.project_root is None:
            raise ValueError("project has not been seeded")
        return self.project_root
