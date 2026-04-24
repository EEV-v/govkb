"""Tests for governed capability candidate staging."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
import tomllib
import unittest

from govkb.commands.candidates import run_candidates
from govkb.commands.create_capability import run_create_capability
from govkb.commands.init import run_init
from govkb.core.candidates import _compact
from govkb.core.install_state import install_state_path
from govkb.core.install_state import load_install_state
from govkb.core.candidates import load_candidate


def _write_session(
    path: Path,
    session_id: str,
    project_root: Path,
    request: str,
    assistant_message: str = "Implemented the reusable workflow and verification command.",
) -> None:
    rows = [
        {
            "type": "session_meta",
            "payload": {
                "id": session_id,
                "timestamp": "2026-04-23T10:00:00Z",
                "cwd": str(project_root),
            },
        },
        {
            "type": "event_msg",
            "payload": {
                "type": "user_message",
                "message": request,
            },
        },
        {
            "type": "event_msg",
            "payload": {
                "type": "agent_message",
                "message": assistant_message,
            },
        },
    ]
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def _set_auto_create_policy(project_root: Path, enabled: bool, min_occurrences: int) -> None:
    project_manifest = project_root / ".governed" / "project.toml"
    current = tomllib.loads(project_manifest.read_text(encoding="utf-8"))
    project = current["project"]
    release = current["release"]
    adapters = current["adapters"]
    automation_block = (
        "schema_version = 1\n\n"
        f"[project]\nid = \"{project['id']}\"\nname = \"{project['name']}\"\n\n"
        f"[release]\ncurrent = \"{release['current']}\"\n\n"
        f"[adapters]\nenabled = {json.dumps(adapters['enabled'])}\n\n"
        "[automation]\n"
        f"auto_create_capabilities = {'true' if enabled else 'false'}\n"
        f"auto_create_min_occurrences = {min_occurrences}\n"
    )
    project_manifest.write_text(automation_block, encoding="utf-8")


class CandidateCommandTests(unittest.TestCase):
    """Candidate staging and activation behavior."""

    def test_candidate_compact_redacts_api_keys(self) -> None:
        text = (
            "OPENAI_API_KEY=sk-proj-abcdefghijklmnopqrstuvwxyz1234567890\n"
            "GITHUB_API_KEY=ghp_abcdefghijklmnopqrstuvwxyz1234567890\n"
            "TOKEN=abc123\n"
        )
        compacted = _compact(text, limit=500)
        self.assertNotIn("sk-proj-", compacted)
        self.assertNotIn("ghp_", compacted)
        self.assertNotIn("abc123", compacted)
        self.assertEqual(compacted.count("[REDACTED]"), 3)

    def test_stage_candidate_prefers_structured_topic_name(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "ExampleApp"
            project_root.mkdir(parents=True, exist_ok=True)
            run_init(argparse.Namespace(dest=project_root, project_id="example-app", project_name="ExampleApp"))

            session_path = Path(temp_dir) / "backend-workflow.jsonl"
            _write_session(
                session_path,
                "backend-workflow",
                project_root,
                "Review this repo and extract the durable backend development workflow for ExampleApp.",
            )

            exit_code = run_candidates(
                argparse.Namespace(
                    candidate_action="stage",
                    project_root=project_root,
                    assistant="codex",
                    session_file=session_path,
                )
            )
            self.assertEqual(exit_code, 0)
            _, candidate = load_candidate(project_root, "backend-workflow")
            self.assertEqual(candidate["status"], "collecting")
            self.assertEqual(candidate["occurrences"], 1)
            self.assertEqual(candidate["proposal"]["capability_id"], "backend-workflow")

    def test_stage_candidate_merges_similar_topics(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "ExampleApp"
            project_root.mkdir(parents=True, exist_ok=True)
            run_init(argparse.Namespace(dest=project_root, project_id="example-app", project_name="ExampleApp"))

            first_session = Path(temp_dir) / "backend-workflow-one.jsonl"
            second_session = Path(temp_dir) / "backend-workflow-two.jsonl"
            _write_session(
                first_session,
                "backend-workflow-one",
                project_root,
                "Capture the reusable backend development workflow and local stack commands.",
            )
            _write_session(
                second_session,
                "backend-workflow-two",
                project_root,
                "Document the durable backend workflow and same local stack commands.",
            )

            first_exit = run_candidates(
                argparse.Namespace(
                    candidate_action="stage",
                    project_root=project_root,
                    assistant="codex",
                    session_file=first_session,
                )
            )
            second_exit = run_candidates(
                argparse.Namespace(
                    candidate_action="stage",
                    project_root=project_root,
                    assistant="codex",
                    session_file=second_session,
                )
            )

            self.assertEqual(first_exit, 0)
            self.assertEqual(second_exit, 0)
            _, candidate = load_candidate(project_root, "backend-workflow")
            self.assertEqual(candidate["status"], "ready-for-review")
            self.assertEqual(candidate["occurrences"], 2)
            self.assertEqual(candidate["proposal"]["capability_id"], "backend-local-stack-workflow")
            self.assertEqual(candidate["proposal"]["suggested_capability_ids"][0], "backend-local-stack-workflow")
            self.assertEqual(candidate["scope"]["summary"], "Local backend stack orchestration, compose entrypoints, effective ports, and startup/debug behavior.")
            facts_text = (
                project_root
                / ".governed"
                / "candidates"
                / "backend-workflow"
                / "candidate-facts.toml"
            ).read_text(encoding="utf-8")
            self.assertIn('section = "Working Agreement"', facts_text)
            self.assertIn('section = "Stable Workflows"', facts_text)
            self.assertNotIn("Capture the reusable backend development workflow", facts_text)
            self.assertFalse((project_root / ".governed" / "candidates" / "backend-workflow" / "evidence.md").exists())
            draft_contract = (project_root / ".governed" / "candidates" / "backend-workflow" / "draft-capability.contract.toml").read_text(encoding="utf-8")
            self.assertIn('"auth"', draft_contract)
            self.assertIn('"keycloak"', draft_contract)
            self.assertIn('"e2e"', draft_contract)

    def test_stage_candidate_rekeys_single_session_candidate_to_better_id(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "ExampleApp"
            project_root.mkdir(parents=True, exist_ok=True)
            run_init(argparse.Namespace(dest=project_root, project_id="example-app", project_name="ExampleApp"))

            session_path = Path(temp_dir) / "backend-workflow.jsonl"
            _write_session(
                session_path,
                "backend-workflow",
                project_root,
                "Review this repo and extract the durable backend development workflow for ExampleApp.",
            )

            legacy_root = project_root / ".governed" / "candidates" / "compose-backend-docker-repo-test"
            legacy_root.mkdir(parents=True, exist_ok=True)
            (legacy_root / "candidate.toml").write_text(
                """candidate_version = 1
id = "compose-backend-docker-repo-test"
status = "collecting"
occurrences = 1
created_at = "2026-04-23T12:05:18.644902Z"
updated_at = "2026-04-23T12:05:18.644902Z"

[proposal]
capability_id = "compose-backend-docker-repo-test"
summary = "Repeated unmatched project work may need a dedicated governed capability."
rationale = "No specialized governed capability matched repeated durable project work."
routing_hints = ["compose", "backend", "docker", "repo", "test", "workflow", "commands", "local", "stack"]

[source]
assistant = "codex"
sessions = ["backend-workflow"]
""",
                encoding="utf-8",
            )
            (legacy_root / "candidate-facts.toml").write_text("facts_version = 1\n", encoding="utf-8")
            (legacy_root / "draft-capability.contract.toml").write_text("contract_version = 1\n", encoding="utf-8")
            (legacy_root / "draft-instructions.md").write_text("# Draft\n", encoding="utf-8")

            exit_code = run_candidates(
                argparse.Namespace(
                    candidate_action="stage",
                    project_root=project_root,
                    assistant="codex",
                    session_file=session_path,
                )
            )

            self.assertEqual(exit_code, 0)
            self.assertFalse(legacy_root.exists())
            _, candidate = load_candidate(project_root, "backend-workflow")
            self.assertEqual(candidate["occurrences"], 1)

    def test_stage_candidate_ignores_investigation_prefix_for_auth_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "ExampleApp"
            project_root.mkdir(parents=True, exist_ok=True)
            run_init(argparse.Namespace(dest=project_root, project_id="example-app", project_name="ExampleApp"))

            first_session = Path(temp_dir) / "auth-workflow-one.jsonl"
            second_session = Path(temp_dir) / "auth-workflow-two.jsonl"
            _write_session(
                first_session,
                "auth-workflow-one",
                project_root,
                "Produce a brief repo-grounded note for the ExampleApp e2e and auth workflow. Include concrete commands, main files, required local services, and the first checks when login or API-backed tests fail.",
            )
            _write_session(
                second_session,
                "auth-workflow-two",
                project_root,
                "Read-only investigation. Confirm the durable auth e2e workflow for ExampleApp using only the auth and test files. Summarize stable entrypoints, local URLs, login credentials, and verification signals.",
            )

            self.assertEqual(
                run_candidates(
                    argparse.Namespace(
                        candidate_action="stage",
                        project_root=project_root,
                        assistant="codex",
                        session_file=first_session,
                    )
                ),
                0,
            )
            self.assertEqual(
                run_candidates(
                    argparse.Namespace(
                        candidate_action="stage",
                        project_root=project_root,
                        assistant="codex",
                        session_file=second_session,
                    )
                ),
                0,
            )

            _, candidate = load_candidate(project_root, "auth-e2e-workflow")
            self.assertEqual(candidate["status"], "ready-for-review")
            self.assertEqual(candidate["occurrences"], 2)
            self.assertEqual(candidate["proposal"]["capability_id"], "auth-e2e-workflow")
            self.assertIn("Auth and e2e verification workflow", candidate["scope"]["summary"])
            draft_prompt = (
                project_root
                / ".governed"
                / "candidates"
                / "auth-e2e-workflow"
                / "draft-initialize-kb.md"
            ).read_text(encoding="utf-8")
            self.assertIn("Candidate facts: `.governed/candidates/auth-e2e-workflow/candidate-facts.toml`", draft_prompt)
            self.assertIn("Do not store secrets", draft_prompt)

    def test_stage_candidate_uses_semantic_seed_for_id_scope_and_repo_facts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "ExampleApp"
            project_root.mkdir(parents=True, exist_ok=True)
            run_init(argparse.Namespace(dest=project_root, project_id="example-app", project_name="ExampleApp"))

            session_path = Path(temp_dir) / "delivery-note.jsonl"
            _write_session(
                session_path,
                "delivery-note",
                project_root,
                "Please summarize the work we just did and think about future reuse.",
            )
            seed_path = Path(temp_dir) / "semantic-seed.json"
            seed_path.write_text(
                json.dumps(
                    {
                        "candidate_id": "release-validation-workflow",
                        "default_capability_id": "release-validation-workflow",
                        "summary": "Repeated release validation work may need a dedicated governed capability.",
                        "routing_hints": ["release validation", "qa signoff", "smoke checks"],
                        "scope_summary": "Release validation workflow, signoff checkpoints, and stable smoke-test evidence.",
                        "in_scope": [
                            "stable pre-release smoke checks and signoff evidence",
                            "durable commands and repo paths used for release validation",
                        ],
                        "out_of_scope": [
                            "feature implementation details unrelated to release validation",
                        ],
                        "facts": [
                            {
                                "section": "Commands And Verification",
                                "fact": "Use dotnet test src/tests/ReleaseChecks/ReleaseChecks.csproj --no-restore before signoff.",
                                "confidence": 0.93,
                                "repo_paths": ["src/tests/ReleaseChecks/ReleaseChecks.csproj"],
                                "grouping_key": "release-check-command",
                            },
                            {
                                "section": "Code And Docs Map",
                                "fact": "Keep release notes in docs/release/release-notes.md and smoke-check evidence in docs/release/checklist.md.",
                                "confidence": 0.88,
                                "repo_paths": ["docs/release/release-notes.md", "docs/release/checklist.md"],
                            },
                        ],
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            exit_code = run_candidates(
                argparse.Namespace(
                    candidate_action="stage",
                    project_root=project_root,
                    assistant="codex",
                    session_file=session_path,
                    semantic_seed_file=seed_path,
                )
            )

            self.assertEqual(exit_code, 0)
            _, candidate = load_candidate(project_root, "release-validation-workflow")
            self.assertEqual(candidate["proposal"]["capability_id"], "release-validation-workflow")
            self.assertEqual(
                candidate["scope"]["summary"],
                "Release validation workflow, signoff checkpoints, and stable smoke-test evidence.",
            )
            facts_text = (
                project_root
                / ".governed"
                / "candidates"
                / "release-validation-workflow"
                / "candidate-facts.toml"
            ).read_text(encoding="utf-8")
            self.assertIn('repo_paths = ["src/tests/ReleaseChecks/ReleaseChecks.csproj"]', facts_text)
            self.assertIn('docs/release/release-notes.md', facts_text)
            self.assertNotIn("Please summarize the work we just did", facts_text)

    def test_stage_candidate_uses_repo_artifacts_for_mixed_language_non_coding_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "ExampleApp"
            project_root.mkdir(parents=True, exist_ok=True)
            run_init(argparse.Namespace(dest=project_root, project_id="example-app", project_name="ExampleApp"))

            session_path = Path(temp_dir) / "release-signoff.jsonl"
            _write_session(
                session_path,
                "release-signoff",
                project_root,
                "Подготовь повторно используемую заметку по релизному согласованию и проверкам.",
                assistant_message=(
                    "Обновил docs/release/signoff.md и docs/release/checklist.md. "
                    "Verification: `python3 -m unittest discover -s tests -v` passed."
                ),
            )
            second_session_path = Path(temp_dir) / "release-checklist.jsonl"
            _write_session(
                second_session_path,
                "release-checklist",
                project_root,
                "Повтори release signoff workflow: обнови чеклист и сохрани verification signals.",
                assistant_message=(
                    "Refined docs/release/checklist.md and docs/release/signoff.md. "
                    "Verification: `python3 -m unittest discover -s tests -v` passed."
                ),
            )

            exit_code = run_candidates(
                argparse.Namespace(
                    candidate_action="stage",
                    project_root=project_root,
                    assistant="codex",
                    session_file=session_path,
                )
            )

            self.assertEqual(exit_code, 0)
            second_exit_code = run_candidates(
                argparse.Namespace(
                    candidate_action="stage",
                    project_root=project_root,
                    assistant="codex",
                    session_file=second_session_path,
                )
            )
            self.assertEqual(second_exit_code, 0)
            _, candidate = load_candidate(project_root, "release-signoff-workflow")
            self.assertEqual(candidate["status"], "ready-for-review")
            self.assertEqual(candidate["occurrences"], 2)
            self.assertEqual(candidate["proposal"]["capability_id"], "release-signoff-workflow")
            self.assertEqual(
                candidate["proposal"]["summary"],
                "Repeated work around release signoff workflow may need a dedicated governed capability.",
            )
            facts_text = (
                project_root
                / ".governed"
                / "candidates"
                / "release-signoff-workflow"
                / "candidate-facts.toml"
            ).read_text(encoding="utf-8")
            self.assertIn('section = "Code And Docs Map"', facts_text)
            self.assertIn("before treating the workflow as complete", facts_text)
            self.assertIn('repo_paths = ["docs/release/signoff.md"]', facts_text)
            self.assertIn("durable release signoff workflow documentation", facts_text)
            self.assertIn('section = "Commands And Verification"', facts_text)
            self.assertIn("python3 -m unittest discover -s tests -v", facts_text)
            self.assertIn("release signoff workflow verification command", facts_text)
            self.assertNotIn("Stable release signoff workflow steps proven across sessions", facts_text)
            self.assertNotIn("Stable commands or conventions", facts_text)
            self.assertNotIn("for this candidate", facts_text)
            self.assertNotIn("Подготовь", facts_text)

    def test_auth_candidate_does_not_blacklist_own_domain_when_backend_hints_exist(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "ExampleApp"
            project_root.mkdir(parents=True, exist_ok=True)
            run_init(argparse.Namespace(dest=project_root, project_id="example-app", project_name="ExampleApp"))

            first_session = Path(temp_dir) / "auth-stack-one.jsonl"
            second_session = Path(temp_dir) / "auth-stack-two.jsonl"
            _write_session(
                first_session,
                "auth-stack-one",
                project_root,
                "Document the durable auth e2e workflow with backend compose, docker, dotnet test commands, and first login failure checks.",
            )
            _write_session(
                second_session,
                "auth-stack-two",
                project_root,
                "Capture the auth e2e workflow again, including backend ports, compose files, login verification, and playwright checks.",
            )

            self.assertEqual(
                run_candidates(
                    argparse.Namespace(
                        candidate_action="stage",
                        project_root=project_root,
                        assistant="codex",
                        session_file=first_session,
                    )
                ),
                0,
            )
            self.assertEqual(
                run_candidates(
                    argparse.Namespace(
                        candidate_action="stage",
                        project_root=project_root,
                        assistant="codex",
                        session_file=second_session,
                    )
                ),
                0,
            )

            draft_contract = tomllib.loads(
                (
                    project_root
                    / ".governed"
                    / "candidates"
                    / "auth-e2e-workflow"
                    / "draft-capability.contract.toml"
                ).read_text(encoding="utf-8")
            )
            hints = tuple(draft_contract["routing"]["hints"])
            negatives = tuple(draft_contract["routing"]["negative_hints"])
            self.assertIn("auth", hints)
            self.assertIn("e2e", hints)
            self.assertIn("login", hints)
            self.assertNotIn("backend", hints)
            self.assertNotIn("dotnet", hints)
            self.assertNotIn("auth", negatives)
            self.assertNotIn("login", negatives)
            self.assertNotIn("keycloak", negatives)
            self.assertNotIn("e2e", negatives)
            self.assertNotIn("playwright", negatives)

    def test_backend_session_does_not_merge_into_existing_auth_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "ExampleApp"
            project_root.mkdir(parents=True, exist_ok=True)
            run_init(argparse.Namespace(dest=project_root, project_id="example-app", project_name="ExampleApp"))

            auth_one = Path(temp_dir) / "auth-workflow-one.jsonl"
            auth_two = Path(temp_dir) / "auth-workflow-two.jsonl"
            backend_one = Path(temp_dir) / "backend-workflow-one.jsonl"
            _write_session(
                auth_one,
                "auth-workflow-one",
                project_root,
                "Document the durable auth e2e workflow with compose, login checks, Keycloak, and playwright verification.",
            )
            _write_session(
                auth_two,
                "auth-workflow-two",
                project_root,
                "Capture the auth e2e workflow again, including login flow, local URLs, Keycloak, and verification signals.",
            )
            _write_session(
                backend_one,
                "backend-workflow-one",
                project_root,
                "Capture the reusable backend local stack workflow with docker compose, dotnet commands, ports, and backend startup checks.",
            )

            self.assertEqual(
                run_candidates(
                    argparse.Namespace(candidate_action="stage", project_root=project_root, assistant="codex", session_file=auth_one)
                ),
                0,
            )
            self.assertEqual(
                run_candidates(
                    argparse.Namespace(candidate_action="stage", project_root=project_root, assistant="codex", session_file=auth_two)
                ),
                0,
            )
            self.assertEqual(
                run_candidates(
                    argparse.Namespace(candidate_action="stage", project_root=project_root, assistant="codex", session_file=backend_one)
                ),
                0,
            )

            _, auth_candidate = load_candidate(project_root, "auth-e2e-workflow")
            _, backend_candidate = load_candidate(project_root, "backend-stack-workflow")
            self.assertEqual(auth_candidate["occurrences"], 2)
            self.assertEqual(backend_candidate["occurrences"], 1)
            self.assertEqual(backend_candidate["proposal"]["capability_id"], "backend-local-stack-workflow")

    def test_stage_candidate_from_sessions_and_activate_capability(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "DemoProject"
            project_root.mkdir(parents=True, exist_ok=True)
            run_init(argparse.Namespace(dest=project_root, project_id="demo-project", project_name="Demo Project"))

            first_session = Path(temp_dir) / "session-one.jsonl"
            second_session = Path(temp_dir) / "session-two.jsonl"
            _write_session(
                first_session,
                "session-one",
                project_root,
                "Create docs/features/Workflow Audit/business.md and capture reusable review workflow.",
            )
            _write_session(
                second_session,
                "session-two",
                project_root,
                "Update docs/features/Workflow Audit/context.md with the same reusable workflow.",
            )

            first_exit = run_candidates(
                argparse.Namespace(
                    candidate_action="stage",
                    project_root=project_root,
                    assistant="codex",
                    session_file=first_session,
                )
            )
            self.assertEqual(first_exit, 0)
            _, first_candidate = load_candidate(project_root, "workflow-audit")
            self.assertEqual(first_candidate["status"], "collecting")
            self.assertEqual(first_candidate["occurrences"], 1)

            second_exit = run_candidates(
                argparse.Namespace(
                    candidate_action="stage",
                    project_root=project_root,
                    assistant="codex",
                    session_file=second_session,
                )
            )
            self.assertEqual(second_exit, 0)
            _, second_candidate = load_candidate(project_root, "workflow-audit")
            self.assertEqual(second_candidate["status"], "ready-for-review")
            self.assertEqual(second_candidate["occurrences"], 2)

            create_exit = run_create_capability(
                argparse.Namespace(
                    capability_id="Workflow Audit",
                    project_root=project_root,
                    from_candidate="workflow-audit",
                )
            )
            self.assertEqual(create_exit, 0)
            self.assertTrue(
                (project_root / ".governed" / "capabilities" / "workflow-audit" / "capability.contract.toml").is_file()
            )
            init_prompt = (
                project_root
                / ".governed"
                / "capabilities"
                / "workflow-audit"
                / "prompts"
                / "initialize-kb.md"
            ).read_text(encoding="utf-8")
            self.assertIn("Candidate facts: `.governed/candidates/workflow-audit/candidate-facts.toml`", init_prompt)
            self.assertIn("Capability: `workflow-audit`", init_prompt)
            created_memory = (
                project_root
                / ".governed"
                / "capabilities"
                / "workflow-audit"
                / "references"
                / "long-term-memory.md"
            ).read_text(encoding="utf-8")
            self.assertIn("Focus this capability on", created_memory)
            _, activated_candidate = load_candidate(project_root, "workflow-audit")
            self.assertEqual(activated_candidate["status"], "activated")

    def test_create_capability_rolls_back_when_generated_contract_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "DemoProject"
            project_root.mkdir(parents=True, exist_ok=True)
            run_init(argparse.Namespace(dest=project_root, project_id="demo-project", project_name="Demo Project"))

            first_session = Path(temp_dir) / "session-one.jsonl"
            second_session = Path(temp_dir) / "session-two.jsonl"
            _write_session(
                first_session,
                "session-one",
                project_root,
                "Create docs/features/Workflow Audit/business.md and capture reusable review workflow.",
            )
            _write_session(
                second_session,
                "session-two",
                project_root,
                "Update docs/features/Workflow Audit/context.md with the same reusable workflow.",
            )

            self.assertEqual(
                run_candidates(
                    argparse.Namespace(
                        candidate_action="stage",
                        project_root=project_root,
                        assistant="codex",
                        session_file=first_session,
                    )
                ),
                0,
            )
            self.assertEqual(
                run_candidates(
                    argparse.Namespace(
                        candidate_action="stage",
                        project_root=project_root,
                        assistant="codex",
                        session_file=second_session,
                    )
                ),
                0,
            )

            candidate_root = project_root / ".governed" / "candidates" / "workflow-audit"
            (candidate_root / "draft-capability.contract.toml").write_text(
                "contract_version = 1\n[capability]\nid = \"workflow-audit\"\n",
                encoding="utf-8",
            )

            create_exit = run_create_capability(
                argparse.Namespace(
                    capability_id="Workflow Audit",
                    project_root=project_root,
                    from_candidate="workflow-audit",
                )
            )

            self.assertEqual(create_exit, 1)
            self.assertFalse((project_root / ".governed" / "capabilities" / "workflow-audit").exists())
            _, candidate = load_candidate(project_root, "workflow-audit")
            self.assertEqual(candidate["status"], "ready-for-review")

    def test_create_capability_uses_suggested_name_when_candidate_id_is_omitted(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "ExampleApp"
            project_root.mkdir(parents=True, exist_ok=True)
            run_init(argparse.Namespace(dest=project_root, project_id="example-app", project_name="ExampleApp"))

            first_session = Path(temp_dir) / "backend-workflow-one.jsonl"
            second_session = Path(temp_dir) / "backend-workflow-two.jsonl"
            _write_session(
                first_session,
                "backend-workflow-one",
                project_root,
                "Capture the reusable backend development workflow and local stack commands.",
            )
            _write_session(
                second_session,
                "backend-workflow-two",
                project_root,
                "Document the durable backend workflow and same local stack commands.",
            )

            self.assertEqual(
                run_candidates(
                    argparse.Namespace(
                        candidate_action="stage",
                        project_root=project_root,
                        assistant="codex",
                        session_file=first_session,
                    )
                ),
                0,
            )
            self.assertEqual(
                run_candidates(
                    argparse.Namespace(
                        candidate_action="stage",
                        project_root=project_root,
                        assistant="codex",
                        session_file=second_session,
                    )
                ),
                0,
            )

            create_exit = run_create_capability(
                argparse.Namespace(
                    capability_id=None,
                    project_root=project_root,
                    from_candidate="backend-workflow",
                )
            )
            self.assertEqual(create_exit, 0)
            self.assertTrue(
                (project_root / ".governed" / "capabilities" / "backend-local-stack-workflow" / "capability.contract.toml").is_file()
            )
            _, activated_candidate = load_candidate(project_root, "backend-workflow")
            self.assertEqual(activated_candidate["status"], "activated")
            self.assertEqual(activated_candidate["proposal"]["capability_id"], "backend-local-stack-workflow")

    def test_auto_create_ready_respects_disabled_policy(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "ExampleApp"
            codex_home = Path(temp_dir) / "codex-home"
            project_root.mkdir(parents=True, exist_ok=True)
            run_init(argparse.Namespace(dest=project_root, project_id="example-app", project_name="ExampleApp"))
            _set_auto_create_policy(project_root, enabled=False, min_occurrences=2)

            first_session = Path(temp_dir) / "backend-workflow-one.jsonl"
            second_session = Path(temp_dir) / "backend-workflow-two.jsonl"
            _write_session(
                first_session,
                "backend-workflow-one",
                project_root,
                "Capture the reusable backend development workflow and local stack commands.",
            )
            _write_session(
                second_session,
                "backend-workflow-two",
                project_root,
                "Document the durable backend workflow and same local stack commands.",
            )
            self.assertEqual(
                run_candidates(
                    argparse.Namespace(candidate_action="stage", project_root=project_root, assistant="codex", session_file=first_session)
                ),
                0,
            )
            self.assertEqual(
                run_candidates(
                    argparse.Namespace(candidate_action="stage", project_root=project_root, assistant="codex", session_file=second_session)
                ),
                0,
            )

            exit_code = run_candidates(
                argparse.Namespace(
                    candidate_action="auto-create-ready",
                    project_root=project_root,
                    assistant="codex",
                    codex_home=codex_home,
                )
            )

            self.assertEqual(exit_code, 0)
            self.assertFalse((project_root / ".governed" / "capabilities" / "backend-local-stack-workflow").exists())
            self.assertFalse((codex_home / "skills" / "govkb-example-app-backend-local-stack-workflow").exists())
            _, candidate = load_candidate(project_root, "backend-workflow")
            self.assertEqual(candidate["status"], "ready-for-review")

    def test_auto_create_ready_creates_capability_and_materializes_codex(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "ExampleApp"
            codex_home = Path(temp_dir) / "codex-home"
            project_root.mkdir(parents=True, exist_ok=True)
            run_init(argparse.Namespace(dest=project_root, project_id="example-app", project_name="ExampleApp"))
            _set_auto_create_policy(project_root, enabled=True, min_occurrences=2)

            first_session = Path(temp_dir) / "backend-workflow-one.jsonl"
            second_session = Path(temp_dir) / "backend-workflow-two.jsonl"
            _write_session(
                first_session,
                "backend-workflow-one",
                project_root,
                "Capture the reusable backend development workflow and local stack commands.",
            )
            _write_session(
                second_session,
                "backend-workflow-two",
                project_root,
                "Document the durable backend workflow and same local stack commands.",
            )
            self.assertEqual(
                run_candidates(
                    argparse.Namespace(candidate_action="stage", project_root=project_root, assistant="codex", session_file=first_session)
                ),
                0,
            )
            self.assertEqual(
                run_candidates(
                    argparse.Namespace(candidate_action="stage", project_root=project_root, assistant="codex", session_file=second_session)
                ),
                0,
            )

            exit_code = run_candidates(
                argparse.Namespace(
                    candidate_action="auto-create-ready",
                    project_root=project_root,
                    assistant="codex",
                    codex_home=codex_home,
                )
            )

            self.assertEqual(exit_code, 0)
            capability_root = project_root / ".governed" / "capabilities" / "backend-local-stack-workflow"
            self.assertTrue((capability_root / "capability.contract.toml").is_file())
            skill_root = codex_home / "skills" / "govkb-example-app-backend-local-stack-workflow"
            self.assertTrue((skill_root / "SKILL.md").is_file())
            self.assertTrue((skill_root / "prompts" / "initialize-kb.md").is_file())
            state = load_install_state(install_state_path(codex_home, "example-app", "codex"))
            self.assertIsNotNone(state)
            self.assertEqual(
                {capability["capability_id"] for capability in state["capabilities"]},
                {"project-knowledge-steward", "backend-local-stack-workflow"},
            )
            _, candidate = load_candidate(project_root, "backend-workflow")
            self.assertEqual(candidate["status"], "activated")
            self.assertEqual(candidate["proposal"]["capability_id"], "backend-local-stack-workflow")


if __name__ == "__main__":
    unittest.main()
