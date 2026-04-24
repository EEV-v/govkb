"""Tests for contract-derived memory-review helpers."""

from __future__ import annotations

import argparse
import importlib.machinery
import importlib.util
import json
import os
import shutil
import tempfile
from pathlib import Path
import sys
from unittest.mock import patch
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

[bootstrap]
profile = "workflow"
repo_roots = ["."]
authority_paths = []
seed_paths = []

[kb_health]
requires_verification_commands = true
requires_repo_map = true
required_sections = ["Working Agreement"]
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

[bootstrap]
profile = "workflow"
repo_roots = ["."]
authority_paths = []
seed_paths = []

[kb_health]
requires_verification_commands = true
requires_repo_map = true
required_sections = ["Working Agreement"]
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

[bootstrap]
profile = "steward"
repo_roots = ["."]
authority_paths = ["README.md"]
seed_paths = ["README.md", "docs", "src", "tests"]

[kb_health]
requires_verification_commands = false
requires_repo_map = true
required_sections = ["Working Agreement"]
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

    def test_collect_session_signals_marks_verified_implementation_sessions_as_generically_relevant(self) -> None:
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

[bootstrap]
profile = "steward"
repo_roots = ["."]
authority_paths = ["README.md"]
seed_paths = ["README.md", "docs", "src", "tests"]

[kb_health]
requires_verification_commands = false
requires_repo_map = true
required_sections = ["Working Agreement"]
""",
                encoding="utf-8",
            )
            (references_root / "long-term-memory.md").write_text(
                "# Project Knowledge Steward\n\n## Working Agreement\n\n- durable note\n",
                encoding="utf-8",
            )

            targets, _ = discover_governed_memory_targets(project_root)
            signals = collect_session_signals(
                user_text="Implement EmployeeRepository to satisfy the integration tests.",
                assistant_text="",
                task_complete_text=(
                    "Implemented EmployeeRepository with recursive PostgreSQL queries. "
                    "Verification: `dotnet test src/tests/OrgChart.IntegrationTests/OrgChart.IntegrationTests.csproj --no-restore` "
                    "passed with 12/12 tests green."
                ),
                targets=targets,
            )
            self.assertTrue(signals.generic_relevance)

    def test_packaged_scheduler_falls_back_to_file_only_sessions_when_index_is_missing(self) -> None:
        module = load_packaged_memory_review_script()
        with tempfile.TemporaryDirectory() as temp_dir:
            codex_home = Path(temp_dir) / ".codex"
            sessions_root = codex_home / "sessions" / "2026" / "04" / "24"
            sessions_root.mkdir(parents=True, exist_ok=True)
            session_path = sessions_root / "rollout-2026-04-24T10-56-31-019dbe7d-8951-74e2-b65c-120f4d9e21ee.jsonl"
            session_path.write_text(
                json.dumps(
                    {
                        "type": "session_meta",
                        "payload": {
                            "id": "019dbe7d-8951-74e2-b65c-120f4d9e21ee",
                            "timestamp": "2026-04-24T07:56:31.457Z",
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            original_sessions_dir = module.SESSIONS_DIR
            original_session_index = module.SESSION_INDEX
            original_log = module.log
            try:
                module.SESSIONS_DIR = codex_home / "sessions"
                module.SESSION_INDEX = codex_home / "session_index.jsonl"
                module.log = lambda _message: None
                sessions, stats = module.load_sessions(
                    argparse.Namespace(
                        session_file=None,
                        lookback_days=30,
                        max_sessions=None,
                    ),
                    {"processed_sessions": {}},
                )
            finally:
                module.SESSIONS_DIR = original_sessions_dir
                module.SESSION_INDEX = original_session_index
                module.log = original_log

            self.assertEqual(len(sessions), 1)
            self.assertEqual(sessions[0].id, "019dbe7d-8951-74e2-b65c-120f4d9e21ee")
            self.assertFalse(sessions[0].indexed)
            self.assertEqual(stats.indexed_rows, 0)
            self.assertEqual(stats.selected_file_only, 1)

    def test_installed_scheduler_infers_codex_home_from_script_location(self) -> None:
        packaged_script = Path(next(iter(govkb.__path__))).resolve() / "adapters" / "codex" / "bin" / "codex-memory-review"
        with tempfile.TemporaryDirectory() as temp_dir:
            codex_home = Path(temp_dir) / "codex-home"
            script_path = codex_home / "bin" / "codex-memory-review"
            script_path.parent.mkdir(parents=True, exist_ok=True)
            (codex_home / "skills").mkdir(parents=True, exist_ok=True)
            shutil.copy2(packaged_script, script_path)

            loader = importlib.machinery.SourceFileLoader(
                "govkb_installed_codex_memory_review",
                str(script_path),
            )
            spec = importlib.util.spec_from_loader(loader.name, loader)
            if spec is None:
                raise AssertionError(f"Could not load scheduler spec from {script_path}")
            module = importlib.util.module_from_spec(spec)
            sys.modules[loader.name] = module
            with patch.dict(os.environ, {}, clear=True):
                loader.exec_module(module)

            self.assertEqual(module.CODEX_HOME, codex_home)

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

    def test_packaged_scheduler_prescreens_verified_implementation_sessions(self) -> None:
        scheduler = load_packaged_memory_review_script()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            project_root = root / "OrgChart"
            session_path = root / "session.jsonl"
            memory_path = root / "long-term-memory.md"
            project_root.mkdir(parents=True, exist_ok=True)
            (project_root / ".governed").mkdir(parents=True, exist_ok=True)
            memory_path.write_text("# Project Knowledge Steward\n\n## Working Agreement\n\n- durable note\n", encoding="utf-8")
            session_path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "type": "session_meta",
                                "payload": {
                                    "id": "session-1",
                                    "timestamp": "2026-04-24T09:12:57.865Z",
                                    "cwd": str(project_root),
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "type": "event_msg",
                                "payload": {
                                    "type": "user_message",
                                    "message": "Implement EmployeeRepository to satisfy the integration tests.",
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "type": "event_msg",
                                "payload": {
                                    "type": "task_complete",
                                    "last_agent_message": (
                                        "Implemented EmployeeRepository with recursive PostgreSQL queries. "
                                        "Verification: `dotnet test src/tests/OrgChart.IntegrationTests/OrgChart.IntegrationTests.csproj --no-restore` "
                                        "passed with 12/12 tests green."
                                    ),
                                },
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            session = scheduler.SessionRef(
                id="session-1",
                thread_name="session.jsonl",
                updated_at="2026-04-24T09:12:57.865Z",
                path=session_path,
                indexed=False,
            )
            target = scheduler.MemoryTarget(
                skill="govkb-orgchart-project-knowledge-steward",
                capability_id="project-knowledge-steward",
                project_id="orgchart",
                path=memory_path,
                requires_explicit_acceptance=False,
                headings=("Working Agreement",),
                content=memory_path.read_text(encoding="utf-8"),
                aliases=("$project-knowledge-steward",),
                hints=("project workflow",),
                negative_hints=(),
                project_root=project_root,
            )

            signals = scheduler.collect_session_signals(session, {"project-knowledge-steward": target})
            keep, reason = scheduler.prescreen_session(session, signals)

            self.assertTrue(keep)
            self.assertEqual(reason, "generic durable-signal match")

    def test_packaged_scheduler_prescreens_unhinted_non_coding_session_from_semantic_outcome(self) -> None:
        scheduler = load_packaged_memory_review_script()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            project_root = root / "ExampleProject"
            session_path = root / "session.jsonl"
            memory_path = root / "long-term-memory.md"
            project_root.mkdir(parents=True, exist_ok=True)
            (project_root / ".governed").mkdir(parents=True, exist_ok=True)
            memory_path.write_text("# Project Knowledge Steward\n\n## Working Agreement\n\n- durable note\n", encoding="utf-8")
            session_path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "type": "session_meta",
                                "payload": {
                                    "id": "session-1",
                                    "timestamp": "2026-04-24T11:12:57.865Z",
                                    "cwd": str(project_root),
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "type": "event_msg",
                                "payload": {
                                    "type": "user_message",
                                    "message": "Update the release signoff note for this project.",
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "type": "event_msg",
                                "payload": {
                                    "type": "task_complete",
                                    "last_agent_message": (
                                        "Updated docs/release/signoff.md with durable release checkpoints, owner handoff, "
                                        "and deployment notes for future runs."
                                    ),
                                },
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            session = scheduler.SessionRef(
                id="session-1",
                thread_name="session.jsonl",
                updated_at="2026-04-24T11:12:57.865Z",
                path=session_path,
                indexed=False,
            )
            target = scheduler.MemoryTarget(
                skill="govkb-example-project-project-knowledge-steward",
                capability_id="project-knowledge-steward",
                project_id="example-project",
                path=memory_path,
                requires_explicit_acceptance=False,
                headings=("Working Agreement",),
                content=memory_path.read_text(encoding="utf-8"),
                aliases=("$project-knowledge-steward",),
                hints=(),
                negative_hints=(),
                project_root=project_root,
            )

            signals = scheduler.collect_session_signals(session, {"project-knowledge-steward": target})
            keep, reason = scheduler.prescreen_session(session, signals)

            self.assertTrue(keep)
            self.assertEqual(reason, "semantic outcome evidence")

    def test_packaged_scheduler_does_not_stage_candidate_when_classification_fails(self) -> None:
        scheduler = load_packaged_memory_review_script()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            project_root = root / "OrgChart"
            reports_root = root / "reports"
            logs_root = root / "logs"
            state_dir = root / "state-dir"
            session_path = root / "session.jsonl"
            memory_path = root / "long-term-memory.md"
            reports_root.mkdir(parents=True, exist_ok=True)
            logs_root.mkdir(parents=True, exist_ok=True)
            state_dir.mkdir(parents=True, exist_ok=True)
            project_root.mkdir(parents=True, exist_ok=True)
            (project_root / ".governed").mkdir(parents=True, exist_ok=True)
            memory_path.write_text("# Project Knowledge Steward\n\n## Working Agreement\n\n- durable note\n", encoding="utf-8")
            session_path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "type": "session_meta",
                                "payload": {
                                    "id": "session-1",
                                    "timestamp": "2026-04-24T08:15:04.645Z",
                                    "cwd": str(project_root),
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "type": "event_msg",
                                "payload": {
                                    "type": "user_message",
                                    "message": "Capture the reusable workflow and verification command for this OrgChart task.",
                                },
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            session = scheduler.SessionRef(
                id="session-1",
                thread_name="session.jsonl",
                updated_at="2026-04-24T08:15:04.645Z",
                path=session_path,
                indexed=False,
            )
            target = scheduler.MemoryTarget(
                skill="govkb-orgchart-project-knowledge-steward",
                capability_id="project-knowledge-steward",
                project_id="orgchart",
                path=memory_path,
                requires_explicit_acceptance=False,
                headings=("Working Agreement",),
                content=memory_path.read_text(encoding="utf-8"),
                aliases=("$project-knowledge-steward",),
                hints=("workflow", "verification command"),
                negative_hints=(),
                project_root=project_root,
            )

            original_state_dir = scheduler.STATE_DIR
            original_report_dir = scheduler.REPORT_DIR
            original_log_dir = scheduler.LOG_DIR
            original_state_file = scheduler.STATE_FILE
            original_log = scheduler.log
            staged_calls: list[list[dict[str, object]]] = []
            try:
                scheduler.STATE_DIR = state_dir
                scheduler.REPORT_DIR = reports_root
                scheduler.LOG_DIR = logs_root
                scheduler.STATE_FILE = state_dir / "state.json"
                scheduler.log = lambda _message: None

                with patch.object(
                    scheduler,
                    "load_sessions",
                    return_value=(
                        [session],
                        scheduler.DiscoveryStats(
                            indexed_rows=0,
                            indexed_missing_files=0,
                            file_only_recent_unprocessed=1,
                            selected_indexed=0,
                            selected_file_only=1,
                        ),
                    ),
                ), patch.object(
                    scheduler,
                    "discover_memory_targets",
                    return_value={target.skill: target},
                ), patch.object(
                    scheduler,
                    "classify_session",
                    side_effect=RuntimeError("codex exec failed with exit 1: malformed classifier output"),
                ), patch.object(
                    scheduler,
                    "run_candidate_staging",
                    side_effect=lambda rows: staged_calls.append(list(rows)) or 0,
                ), patch.object(
                    scheduler,
                    "run_candidate_auto_create",
                    return_value=(0, []),
                ), patch.object(
                    scheduler,
                    "write_patch",
                    return_value=None,
                ), patch.object(
                    scheduler,
                    "write_report",
                    return_value=None,
                ):
                    exit_code = scheduler.process(
                        argparse.Namespace(
                            dry_run=False,
                            lookback_days=30,
                            max_sessions=20,
                            verbose=False,
                            codex_timeout=30,
                            session_file=None,
                            resolved_project_root=project_root,
                            auto_promote=False,
                        )
                    )
            finally:
                scheduler.STATE_DIR = original_state_dir
                scheduler.REPORT_DIR = original_report_dir
                scheduler.LOG_DIR = original_log_dir
                scheduler.STATE_FILE = original_state_file
                scheduler.log = original_log

            self.assertEqual(exit_code, 1)
            self.assertEqual(staged_calls, [])

    def test_packaged_scheduler_defers_sessions_when_classifier_hits_usage_limit(self) -> None:
        scheduler = load_packaged_memory_review_script()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            project_root = root / "OrgChart"
            reports_root = root / "reports"
            logs_root = root / "logs"
            state_dir = root / "state-dir"
            session_path = root / "session.jsonl"
            memory_path = root / "long-term-memory.md"
            reports_root.mkdir(parents=True, exist_ok=True)
            logs_root.mkdir(parents=True, exist_ok=True)
            state_dir.mkdir(parents=True, exist_ok=True)
            project_root.mkdir(parents=True, exist_ok=True)
            (project_root / ".governed").mkdir(parents=True, exist_ok=True)
            memory_path.write_text("# Project Knowledge Steward\n\n## Working Agreement\n\n- durable note\n", encoding="utf-8")
            session_path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "type": "session_meta",
                                "payload": {
                                    "id": "session-1",
                                    "timestamp": "2026-04-24T08:15:04.645Z",
                                    "cwd": str(project_root),
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "type": "event_msg",
                                "payload": {
                                    "type": "user_message",
                                    "message": "Capture the reusable workflow and verification command for this OrgChart task.",
                                },
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            session = scheduler.SessionRef(
                id="session-1",
                thread_name="session.jsonl",
                updated_at="2026-04-24T08:15:04.645Z",
                path=session_path,
                indexed=False,
            )
            target = scheduler.MemoryTarget(
                skill="govkb-orgchart-project-knowledge-steward",
                capability_id="project-knowledge-steward",
                project_id="orgchart",
                path=memory_path,
                requires_explicit_acceptance=False,
                headings=("Working Agreement",),
                content=memory_path.read_text(encoding="utf-8"),
                aliases=("$project-knowledge-steward",),
                hints=("workflow", "verification command"),
                negative_hints=(),
                project_root=project_root,
            )

            original_state_dir = scheduler.STATE_DIR
            original_report_dir = scheduler.REPORT_DIR
            original_log_dir = scheduler.LOG_DIR
            original_state_file = scheduler.STATE_FILE
            original_log = scheduler.log
            staged_calls: list[list[dict[str, object]]] = []
            report_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []
            try:
                scheduler.STATE_DIR = state_dir
                scheduler.REPORT_DIR = reports_root
                scheduler.LOG_DIR = logs_root
                scheduler.STATE_FILE = state_dir / "state.json"
                scheduler.log = lambda _message: None

                with patch.object(
                    scheduler,
                    "load_sessions",
                    return_value=(
                        [session],
                        scheduler.DiscoveryStats(
                            indexed_rows=0,
                            indexed_missing_files=0,
                            file_only_recent_unprocessed=1,
                            selected_indexed=0,
                            selected_file_only=1,
                        ),
                    ),
                ), patch.object(
                    scheduler,
                    "discover_memory_targets",
                    return_value={target.skill: target},
                ), patch.object(
                    scheduler,
                    "classify_session",
                    side_effect=scheduler.UsageLimitClassificationError("codex classifier usage limit reached; retry after quota resets"),
                ), patch.object(
                    scheduler,
                    "run_candidate_staging",
                    side_effect=lambda rows: staged_calls.append(list(rows)) or 0,
                ), patch.object(
                    scheduler,
                    "run_candidate_auto_create",
                    return_value=(0, []),
                ), patch.object(
                    scheduler,
                    "write_patch",
                    return_value=None,
                ), patch.object(
                    scheduler,
                    "write_report",
                    side_effect=lambda *args, **kwargs: report_calls.append((args, kwargs)) or None,
                ):
                    exit_code = scheduler.process(
                        argparse.Namespace(
                            dry_run=False,
                            lookback_days=30,
                            max_sessions=20,
                            verbose=False,
                            codex_timeout=30,
                            session_file=None,
                            resolved_project_root=project_root,
                            auto_promote=False,
                        )
                    )
            finally:
                scheduler.STATE_DIR = original_state_dir
                scheduler.REPORT_DIR = original_report_dir
                scheduler.LOG_DIR = original_log_dir
                scheduler.STATE_FILE = original_state_file
                scheduler.log = original_log

            self.assertEqual(exit_code, 0)
            self.assertEqual(staged_calls, [])
            self.assertGreaterEqual(len(report_calls), 1)
            deferred_rows = report_calls[-1][0][4]
            self.assertEqual(len(deferred_rows), 1)
            self.assertIn("usage limit", deferred_rows[0]["error"])

    def test_packaged_scheduler_defers_sessions_when_classifier_transport_fails(self) -> None:
        scheduler = load_packaged_memory_review_script()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            project_root = root / "OrgChart"
            reports_root = root / "reports"
            logs_root = root / "logs"
            state_dir = root / "state-dir"
            session_path = root / "session.jsonl"
            memory_path = root / "long-term-memory.md"
            reports_root.mkdir(parents=True, exist_ok=True)
            logs_root.mkdir(parents=True, exist_ok=True)
            state_dir.mkdir(parents=True, exist_ok=True)
            project_root.mkdir(parents=True, exist_ok=True)
            (project_root / ".governed").mkdir(parents=True, exist_ok=True)
            memory_path.write_text("# Project Knowledge Steward\n\n## Working Agreement\n\n- durable note\n", encoding="utf-8")
            session_path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "type": "session_meta",
                                "payload": {
                                    "id": "session-1",
                                    "timestamp": "2026-04-24T08:15:04.645Z",
                                    "cwd": str(project_root),
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "type": "event_msg",
                                "payload": {
                                    "type": "user_message",
                                    "message": "Capture the reusable workflow and verification command for this OrgChart task.",
                                },
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            session = scheduler.SessionRef(
                id="session-1",
                thread_name="session.jsonl",
                updated_at="2026-04-24T08:15:04.645Z",
                path=session_path,
                indexed=False,
            )
            target = scheduler.MemoryTarget(
                skill="govkb-orgchart-project-knowledge-steward",
                capability_id="project-knowledge-steward",
                project_id="orgchart",
                path=memory_path,
                requires_explicit_acceptance=False,
                headings=("Working Agreement",),
                content=memory_path.read_text(encoding="utf-8"),
                aliases=("$project-knowledge-steward",),
                hints=("workflow", "verification command"),
                negative_hints=(),
                project_root=project_root,
            )

            original_state_dir = scheduler.STATE_DIR
            original_report_dir = scheduler.REPORT_DIR
            original_log_dir = scheduler.LOG_DIR
            original_state_file = scheduler.STATE_FILE
            original_log = scheduler.log
            report_calls: list[tuple[tuple[object, ...], dict[str, object]]] = []
            try:
                scheduler.STATE_DIR = state_dir
                scheduler.REPORT_DIR = reports_root
                scheduler.LOG_DIR = logs_root
                scheduler.STATE_FILE = state_dir / "state.json"
                scheduler.log = lambda _message: None

                with patch.object(
                    scheduler,
                    "load_sessions",
                    return_value=(
                        [session],
                        scheduler.DiscoveryStats(
                            indexed_rows=0,
                            indexed_missing_files=0,
                            file_only_recent_unprocessed=1,
                            selected_indexed=0,
                            selected_file_only=1,
                        ),
                    ),
                ), patch.object(
                    scheduler,
                    "discover_memory_targets",
                    return_value={target.skill: target},
                ), patch.object(
                    scheduler,
                    "classify_session",
                    side_effect=scheduler.ConnectivityClassificationError("codex classifier transport failed; retry when connectivity recovers"),
                ), patch.object(
                    scheduler,
                    "run_candidate_staging",
                    return_value=0,
                ), patch.object(
                    scheduler,
                    "run_candidate_auto_create",
                    return_value=(0, []),
                ), patch.object(
                    scheduler,
                    "write_patch",
                    return_value=None,
                ), patch.object(
                    scheduler,
                    "write_report",
                    side_effect=lambda *args, **kwargs: report_calls.append((args, kwargs)) or None,
                ):
                    exit_code = scheduler.process(
                        argparse.Namespace(
                            dry_run=False,
                            lookback_days=30,
                            max_sessions=20,
                            verbose=False,
                            codex_timeout=30,
                            session_file=None,
                            resolved_project_root=project_root,
                            auto_promote=False,
                        )
                    )
            finally:
                scheduler.STATE_DIR = original_state_dir
                scheduler.REPORT_DIR = original_report_dir
                scheduler.LOG_DIR = original_log_dir
                scheduler.STATE_FILE = original_state_file
                scheduler.log = original_log

            self.assertEqual(exit_code, 0)
            self.assertGreaterEqual(len(report_calls), 1)
            deferred_rows = report_calls[-1][0][4]
            self.assertEqual(len(deferred_rows), 1)
            self.assertIn("transport failed", deferred_rows[0]["error"])

    def test_packaged_scheduler_passes_semantic_candidate_seed_to_candidate_staging(self) -> None:
        scheduler = load_packaged_memory_review_script()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            project_root = root / "OrgChart"
            reports_root = root / "reports"
            logs_root = root / "logs"
            state_dir = root / "state-dir"
            session_path = root / "session.jsonl"
            memory_path = root / "long-term-memory.md"
            reports_root.mkdir(parents=True, exist_ok=True)
            logs_root.mkdir(parents=True, exist_ok=True)
            state_dir.mkdir(parents=True, exist_ok=True)
            project_root.mkdir(parents=True, exist_ok=True)
            (project_root / ".governed").mkdir(parents=True, exist_ok=True)
            memory_path.write_text("# Project Knowledge Steward\n\n## Working Agreement\n\n- durable note\n", encoding="utf-8")
            session_path.write_text(
                "\n".join(
                    [
                        json.dumps(
                            {
                                "type": "session_meta",
                                "payload": {
                                    "id": "session-1",
                                    "timestamp": "2026-04-24T12:15:04.645Z",
                                    "cwd": str(project_root),
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "type": "event_msg",
                                "payload": {
                                    "type": "user_message",
                                    "message": "Capture the durable release signoff workflow for this repo.",
                                },
                            }
                        ),
                        json.dumps(
                            {
                                "type": "event_msg",
                                "payload": {
                                    "type": "task_complete",
                                    "last_agent_message": (
                                        "Updated docs/release/signoff.md with stable checkpoints and delivery notes."
                                    ),
                                },
                            }
                        ),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            session = scheduler.SessionRef(
                id="session-1",
                thread_name="session.jsonl",
                updated_at="2026-04-24T12:15:04.645Z",
                path=session_path,
                indexed=False,
            )
            target = scheduler.MemoryTarget(
                skill="govkb-orgchart-project-knowledge-steward",
                capability_id="project-knowledge-steward",
                project_id="orgchart",
                path=memory_path,
                requires_explicit_acceptance=False,
                headings=("Working Agreement",),
                content=memory_path.read_text(encoding="utf-8"),
                aliases=("$project-knowledge-steward",),
                hints=(),
                negative_hints=(),
                project_root=project_root,
            )

            original_state_dir = scheduler.STATE_DIR
            original_report_dir = scheduler.REPORT_DIR
            original_log_dir = scheduler.LOG_DIR
            original_state_file = scheduler.STATE_FILE
            original_log = scheduler.log
            staged_calls: list[list[dict[str, object]]] = []
            try:
                scheduler.STATE_DIR = state_dir
                scheduler.REPORT_DIR = reports_root
                scheduler.LOG_DIR = logs_root
                scheduler.STATE_FILE = state_dir / "state.json"
                scheduler.log = lambda _message: None

                with patch.object(
                    scheduler,
                    "load_sessions",
                    return_value=(
                        [session],
                        scheduler.DiscoveryStats(
                            indexed_rows=0,
                            indexed_missing_files=0,
                            file_only_recent_unprocessed=1,
                            selected_indexed=0,
                            selected_file_only=1,
                        ),
                    ),
                ), patch.object(
                    scheduler,
                    "discover_memory_targets",
                    return_value={target.skill: target},
                ), patch.object(
                    scheduler,
                    "classify_session",
                    return_value={
                        "session_id": "session-1",
                        "candidates": [],
                        "semantic_candidate": {
                            "candidate_id": "release-validation-workflow",
                            "default_capability_id": "release-validation-workflow",
                            "summary": "Repeated release validation work may need a dedicated governed capability.",
                            "routing_hints": ["release validation", "signoff", "smoke checks"],
                            "scope_summary": "Release validation workflow, signoff checkpoints, and smoke-check evidence.",
                            "in_scope": ["stable signoff checkpoints and smoke-check commands"],
                            "out_of_scope": ["feature implementation unrelated to release validation"],
                            "facts": [
                                {
                                    "section": "Code And Docs Map",
                                    "fact": "Keep release signoff notes in docs/release/signoff.md.",
                                    "confidence": 0.88,
                                    "repo_paths": ["docs/release/signoff.md"],
                                }
                            ],
                        },
                    },
                ), patch.object(
                    scheduler,
                    "run_candidate_staging",
                    side_effect=lambda rows: staged_calls.append(list(rows)) or 0,
                ), patch.object(
                    scheduler,
                    "run_candidate_auto_create",
                    return_value=(0, []),
                ), patch.object(
                    scheduler,
                    "write_patch",
                    return_value=None,
                ), patch.object(
                    scheduler,
                    "write_report",
                    return_value=None,
                ):
                    exit_code = scheduler.process(
                        argparse.Namespace(
                            dry_run=False,
                            lookback_days=30,
                            max_sessions=20,
                            verbose=False,
                            codex_timeout=30,
                            session_file=None,
                            resolved_project_root=project_root,
                            auto_promote=False,
                        )
                    )
            finally:
                scheduler.STATE_DIR = original_state_dir
                scheduler.REPORT_DIR = original_report_dir
                scheduler.LOG_DIR = original_log_dir
                scheduler.STATE_FILE = original_state_file
                scheduler.log = original_log

            self.assertEqual(exit_code, 0)
            self.assertEqual(len(staged_calls), 1)
            self.assertEqual(len(staged_calls[0]), 1)
            semantic_seed = staged_calls[0][0].get("semantic_seed")
            self.assertIsInstance(semantic_seed, dict)
            self.assertEqual(semantic_seed["candidate_id"], "release-validation-workflow")
            self.assertEqual(semantic_seed["facts"][0]["repo_paths"], ["docs/release/signoff.md"])

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
