# Memory Review Capability Evolution - PoC Parity Review

Last updated: 2026-05-28

## Verdict

Ready for Merge: Yes

## Summary

The implementation matches the accepted PoC and plan. GovKB now has a first-slice capability-evolution lane with proposal storage, public proposal review/apply commands, memory-review schema/report/progress integration, and focused `unittest` coverage.

Cron and dry-run behavior remain conservative: memory review can report proposals in dry-run without writing proposal folders, and normal staging writes review metadata under `.governed/review-proposals/<proposal-id>/` rather than final executable artifacts.

## Requirement Parity

| Requirement | PoC Assertion | Implementation Evidence | Result | Notes |
|---|---|---|---|---|
| REQ-MRCE-01 | A2, A3 | `schema_text()` now requires `capability_evolution_proposals`; memory-review report has proposal sections. | Passed | Existing strict schema test passes. |
| REQ-MRCE-02 | A2, A3, A8 | Empty proposal arrays are handled and report zero proposals. | Passed | Covered by `test_uc_1_no_proposal_opportunities_preserve_report_behavior`. |
| REQ-MRCE-03 | A1, A7 | `stage_proposal()` writes `.governed/review-proposals/<proposal-id>/`. | Passed | Covered by `test_stage_proposal_writes_reviewable_metadata`. |
| REQ-MRCE-04 | A4 | `govkb candidates` remains unchanged; proposal work is in `govkb proposals` and `core/proposals.py`. | Passed | Candidate regression tests passed. |
| REQ-MRCE-05 | A1, A4 | Added `govkb proposals list`, `show`, and `apply`. | Passed | `govkb proposals --help` shows only public actions. |
| REQ-MRCE-06 | A6 | Prompt now always asks for `capability_evolution_proposals`; no extra discovery flag was added. | Passed | Manual higher-reasoning still uses existing `--codex-reasoning`. |
| REQ-MRCE-07 | A2, A3 | Dry-run reports proposal rows without creating `.governed/review-proposals`. | Passed | Covered by `test_uc_5_dry_run_reports_proposals_without_staging_files`. |
| REQ-MRCE-08 | A5, A7 | `apply_proposal()` requires approved status plus approver and approved timestamp. | Passed | Covered by `test_apply_requires_approval_and_writes_bounded_output`. |
| REQ-MRCE-09 | A5, A7 | Output paths are normalized and constrained under the target capability root. | Passed | Unsafe parent traversal is rejected. |
| REQ-MRCE-10 | A7 | Supported types are `script`, `wrapper`, `prompt`, `runbook`, `instructions_update`. | Passed | Covered by UC-10 type validation test. |
| REQ-MRCE-11 | A5, A7 | Mutating script/wrapper proposals require dry-run or preview behavior. | Passed | Covered by `test_mutating_script_requires_dry_run_or_preview`. |
| REQ-MRCE-12 | A5, A7 | Proposal text validation rejects token-like, credential-path, raw-transcript, and private-evidence indicators. | Passed | Sensitive evidence test added. |
| REQ-MRCE-13 | A3 | Report summary and sections include proposal counts and rows. | Passed | Covered by report use-case tests. |
| REQ-MRCE-14 | A5 | Proposal apply runs strict validation on the target capability after writes and rolls back on failure. | Passed | Strict validation tests and proposal apply tests passed. |
| REQ-MRCE-15 | A3, A7 | Proposal metadata stores source run id, source session id, and sanitized evidence summary. | Passed | Raw transcript storage is not used. |

## Scenario Parity

| Scenario | Test/Verification | Result | Notes |
|---|---|---|---|
| UC-1 | `tests/test_memory_review_capability_evolution_use_cases.py` | Passed | Report zero-proposal behavior covered. |
| UC-2 | `tests/test_memory_review_capability_evolution_smoke.py`; `tests/test_proposals.py` | Passed | Valid script proposal stages metadata only. |
| UC-3 | `test_uc_10_supported_proposal_types_validate` | Passed | Supported non-script proposal types validated. |
| UC-4 | `test_invalid_proposal_paths_and_sensitive_content_are_rejected` | Passed | Unsafe path and sensitive evidence covered. |
| UC-5 | `test_uc_5_dry_run_reports_proposals_without_staging_files` | Passed | Dry-run remains non-mutating for proposal folders. |
| UC-6 | `test_proposals_list_and_show_support_text_and_json` | Passed | Text and JSON list/show covered. |
| UC-7 | `test_apply_requires_approval_and_writes_bounded_output` | Passed | Approval-gated apply covered. |
| UC-8 | `test_mutating_script_requires_dry_run_or_preview` | Passed | Mutating script safety covered. |
| UC-9 | Existing candidate regression tests | Passed | Candidate flow remains separate. |
| UC-10 | `test_uc_10_supported_proposal_types_validate` | Passed | Supported and unsupported type behavior covered. |

## Command Evidence

| Command | Working Dir | Result | Evidence |
|---|---|---|---|
| `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest tests.test_proposals -v` | `/home/ev/code/govkb` | Passed | 6 tests OK. |
| `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest tests.test_memory_review_capability_evolution_smoke tests.test_memory_review_capability_evolution_use_cases -v` | `/home/ev/code/govkb` | Passed | 4 tests OK. |
| `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest tests.test_memory_review tests.test_review_memory_command tests.test_candidates tests.test_candidates_json tests.test_governed_skill_quality_gates_use_cases tests.test_validate -v` | `/home/ev/code/govkb` | Passed | 64 tests OK. |
| `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli proposals --help` | `/home/ev/code/govkb` | Passed | Shows `list`, `show`, and `apply`. |
| `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli proposals list --json .` | `/home/ev/code/govkb` | Passed | Emits schema version 1 and empty proposal list for this repo. |
| `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -v` | `/home/ev/code/govkb` | Passed | 185 tests OK, 33 skipped scaffold tests. |
| `git diff --check` | `/home/ev/code/govkb` | Passed | No whitespace errors. |

## Deviations

| Deviation | Approved? | Reason | Follow-up |
|---|---|---|---|
| Strict validation runs on the target capability after proposal apply, not the whole project. | Yes | Avoid unrelated strict findings blocking a bounded proposal apply. | Consider project-wide strict validation as an optional later flag. |
| Staging is an internal core operation instead of a public `govkb proposals stage` command. | Yes | Public UX remains simple: `list`, `show`, `apply`; memory review stages through core code in a subprocess. | Add public staging only if maintainers need manual imports. |
| Apply does not run arbitrary verification commands from metadata. | Yes | Keeps first slice conservative; strict validation is run directly. | Add safe verification execution later with cwd, timeout, and command allowlist rules. |

## Risks

- Classifier-generated `draft_output` may need maintainer editing before approval for non-trivial scripts.
- Existing installed cron copies need `govkb install --cron` or equivalent refresh before they pick up the updated memory-review script.
- Future VS Code proposal views should consume `govkb proposals list/show --json` rather than parsing text output.

## Required Fixes Before Merge

None.

## Post-merge Follow-ups

- Add `govkb proposals approve` if direct TOML approval is too manual.
- Add safe verification-command execution with explicit cwd, timeout, and allowlist behavior.
- Surface proposal counts in the VS Code Learning view after the CLI contract settles.
