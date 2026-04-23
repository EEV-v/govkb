"""Tests for contract-derived memory-review helpers."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import tempfile
from pathlib import Path
import sys
import unittest

import govkb

from govkb.adapters.codex.memory_review import collect_session_signals
from govkb.adapters.codex.memory_review import discover_governed_memory_targets
from govkb.adapters.codex.memory_review import prompt_targets_for_session
from govkb.adapters.codex.memory_review import resolve_session_project_root


def load_packaged_memory_review_script():
    """Import the packaged scheduler script as a module for policy tests."""
    script_path = Path(next(iter(govkb.__path__))).resolve() / "adapters" / "codex" / "bin" / "codex-memory-review"
    loader = importlib.machinery.SourceFileLoader("govkb_packaged_codex_memory_review", str(script_path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    if spec is None:
        raise AssertionError(f"Could not load scheduler spec from {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[loader.name] = module
    loader.exec_module(module)
    return module


class MemoryReviewHelperTests(unittest.TestCase):
    """Governed memory-review helper behavior."""

    def test_discover_governed_memory_targets_loads_repo_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "DemoProject"
            capability_root = project_root / ".governed" / "capabilities" / "review-capability"
            references_root = capability_root / "references"
            adapter_root = project_root / ".governed" / "adapters" / "codex"
            references_root.mkdir(parents=True, exist_ok=True)
            adapter_root.mkdir(parents=True, exist_ok=True)
            (project_root / ".governed" / "project.toml").write_text(
                """schema_version = 1

[project]
id = "demo-project"
name = "Demo Project"

[release]
current = "unreleased"

[adapters]
enabled = ["codex"]
""",
                encoding="utf-8",
            )
            (adapter_root / "adapter.toml").write_text(
                """[adapter]
id = "codex"
local_state_key = "demo-project/codex"
materialization_targets = ["skills", "memory-review"]

[governance]
min_confidence_floor = 0.85

[routing]
aliases = []
""",
                encoding="utf-8",
            )
            (capability_root / "capability.contract.toml").write_text(
                """contract_version = 1

[capability]
id = "review-capability"
name = "Review Capability"
governed = true
description = "review helper"

[routing]
aliases = ["$review-capability"]
hints = ["root cause", "implementation plan"]
negative_hints = ["cron schedule"]

[memory]
enabled = true
auto_apply_min_confidence = 0.85
requires_explicit_acceptance = false

[memory.targets.main]
path = "references/long-term-memory.md"
sections = ["Working Agreement"]
""",
                encoding="utf-8",
            )
            (references_root / "long-term-memory.md").write_text(
                "# Review Capability\n\n## Working Agreement\n\n- durable note\n",
                encoding="utf-8",
            )

            targets, result = discover_governed_memory_targets(project_root)
            self.assertFalse(result.errors)
            self.assertIn("review-capability", targets)
            self.assertEqual(targets["review-capability"].headings, ("Working Agreement",))

    def test_collect_session_signals_uses_aliases_hints_and_negative_hints(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "DemoProject"
            capability_root = project_root / ".governed" / "capabilities" / "review-capability"
            references_root = capability_root / "references"
            adapter_root = project_root / ".governed" / "adapters" / "codex"
            references_root.mkdir(parents=True, exist_ok=True)
            adapter_root.mkdir(parents=True, exist_ok=True)
            (project_root / ".governed" / "project.toml").write_text(
                """schema_version = 1

[project]
id = "demo-project"
name = "Demo Project"

[release]
current = "unreleased"

[adapters]
enabled = ["codex"]
""",
                encoding="utf-8",
            )
            (adapter_root / "adapter.toml").write_text(
                """[adapter]
id = "codex"
local_state_key = "demo-project/codex"
materialization_targets = ["skills", "memory-review"]

[governance]
min_confidence_floor = 0.85

[routing]
aliases = []
""",
                encoding="utf-8",
            )
            (capability_root / "capability.contract.toml").write_text(
                """contract_version = 1

[capability]
id = "review-capability"
name = "Review Capability"
governed = true
description = "review helper"

[routing]
aliases = ["$review-capability", "review capability"]
hints = ["root cause", "implementation plan"]
negative_hints = ["cron schedule"]

[memory]
enabled = true
auto_apply_min_confidence = 0.85
requires_explicit_acceptance = false

[memory.targets.main]
path = "references/long-term-memory.md"
sections = ["Working Agreement"]
""",
                encoding="utf-8",
            )
            (references_root / "long-term-memory.md").write_text(
                "# Review Capability\n\n## Working Agreement\n\n- durable note\n",
                encoding="utf-8",
            )

            targets, _ = discover_governed_memory_targets(project_root)
            explicit = collect_session_signals(
                user_text="Please use $review-capability for this plan review.",
                assistant_text="",
                task_complete_text="",
                targets=targets,
            )
            self.assertEqual(explicit.explicit_skills, ("review-capability",))

            hinted = collect_session_signals(
                user_text="Need root cause and implementation plan feedback.",
                assistant_text="",
                task_complete_text="",
                targets=targets,
            )
            self.assertEqual(hinted.hinted_skills, ("review-capability",))

            suppressed = collect_session_signals(
                user_text="Need root cause feedback, also discuss cron schedule.",
                assistant_text="",
                task_complete_text="",
                targets=targets,
            )
            self.assertEqual(suppressed.hinted_skills, ())

            narrowed = prompt_targets_for_session(targets, hinted)
            self.assertEqual(tuple(narrowed), ("review-capability",))

    def test_collect_session_signals_marks_workflow_sessions_as_generically_relevant(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "DemoProject"
            capability_root = project_root / ".governed" / "capabilities" / "project-knowledge-steward"
            references_root = capability_root / "references"
            adapter_root = project_root / ".governed" / "adapters" / "codex"
            references_root.mkdir(parents=True, exist_ok=True)
            adapter_root.mkdir(parents=True, exist_ok=True)
            (project_root / ".governed" / "project.toml").write_text(
                """schema_version = 1

[project]
id = "demo-project"
name = "Demo Project"

[release]
current = "unreleased"

[adapters]
enabled = ["codex"]
""",
                encoding="utf-8",
            )
            (adapter_root / "adapter.toml").write_text(
                """[adapter]
id = "codex"
local_state_key = "demo-project/codex"
materialization_targets = ["skills", "memory-review"]

[governance]
min_confidence_floor = 0.85

[routing]
aliases = []
""",
                encoding="utf-8",
            )
            (capability_root / "capability.contract.toml").write_text(
                """contract_version = 1

[capability]
id = "project-knowledge-steward"
name = "Project Knowledge Steward"
governed = true
description = "project workflow helper"

[routing]
aliases = ["$project-knowledge-steward"]
hints = ["project workflow"]
negative_hints = ["cron schedule"]

[memory]
enabled = true
auto_apply_min_confidence = 0.85
requires_explicit_acceptance = false

[memory.targets.main]
path = "references/long-term-memory.md"
sections = ["Working Agreement"]
""",
                encoding="utf-8",
            )
            (references_root / "long-term-memory.md").write_text(
                "# Project Knowledge Steward\n\n## Working Agreement\n\n- durable note\n",
                encoding="utf-8",
            )

            targets, _ = discover_governed_memory_targets(project_root)
            signals = collect_session_signals(
                user_text="Capture the reusable backend workflow and effective ports for local startup.",
                assistant_text="",
                task_complete_text="",
                targets=targets,
            )
            self.assertTrue(signals.generic_relevance)

    def test_packaged_scheduler_rejects_assistant_runtime_lessons(self) -> None:
        scheduler = load_packaged_memory_review_script()

        reason = scheduler.environment_local_reason(
            "In read-only sessions, .NET test commands may fail before build because MSBuild writes temp/cache files even with --no-restore.",
            "MSBuild failed with System.IO.IOException: Read-only file system while creating temp/cache directories.",
        )

        self.assertEqual(reason, "lesson is about assistant runtime mode, not durable project behavior")

    def test_packaged_scheduler_allows_project_verification_command_lessons(self) -> None:
        scheduler = load_packaged_memory_review_script()

        reason = scheduler.environment_local_reason(
            "Use dotnet test backend-dotnet/StoryApp.StoryBook.Tests.Unit/StoryApp.StoryBook.Tests.Unit.csproj --filter GenerateStoryUseCaseTests --no-restore as the narrow verification command for story-generation validation changes.",
            "Session identified the command from the unit test project and focused test class.",
        )

        self.assertIsNone(reason)

    def test_resolve_session_project_root_from_session_meta(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "DemoProject"
            governed_root = project_root / ".governed"
            governed_root.mkdir(parents=True, exist_ok=True)
            session_path = Path(temp_dir) / "session.jsonl"
            session_path.write_text(
                json.dumps(
                    {
                        "type": "session_meta",
                        "payload": {
                            "id": "session-1",
                            "cwd": str(project_root / "subdir"),
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            resolved = resolve_session_project_root(session_path)
            self.assertEqual(resolved, project_root)


if __name__ == "__main__":
    unittest.main()
