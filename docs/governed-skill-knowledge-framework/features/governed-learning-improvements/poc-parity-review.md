# Governed Learning Improvements - PoC Parity Review

Last updated: 2026-05-30

## Verdict

Ready for Merge: Yes, Phases 0-1.

Phase 0 covers proposal grouping, advisory quality warnings, and actionable proposal review output. Phase 1 adds read-only `govkb doctor` health output for memory review, cron, install state, repo state, and proposal queue summary. Self-noise filtering, maturity scoring, VS Code freshness, and doctor UI integration remain deferred follow-ups.

## Summary

The implemented Phase 0-1 behavior matches the accepted PoC and plan for proposal queue review and health reporting. GovKB now exposes read-only `govkb proposals report`, `govkb proposals review`, and `govkb doctor` commands, with JSON contracts and text output for maintainers. Tests use synthetic temp project fixtures and do not depend on Clearing, user-home state, raw session transcripts, or credentials.

## Requirement Parity

| Requirement | PoC Assertion | Implementation Evidence | Result | Notes |
|---|---|---|---|---|
| REQ-GLI-01 | A-1 | `src/govkb/core/proposal_report.py`; `test_uc_1_groups_similar_proposals_and_keeps_unrelated_work_separate` | PASS | Similar staged proposals are grouped while unrelated work stays separate. |
| REQ-GLI-02 | A-1 | `build_proposal_review_payload`; `govkb proposals review` | PASS | Review output includes `inspect-safety`, `merge-first`, `reject-duplicate`, and `manual-review` next steps. |
| REQ-GLI-03 | A-2 | Proposal warning fields; `test_uc_2_report_is_read_only_and_surfaces_script_quality_warnings` | PASS | Warnings are advisory and report mode does not mutate proposal files. |
| REQ-GLI-04 | A-3 | `src/govkb/commands/doctor.py`; `tests/test_doctor.py` | PASS | Health output reports cron, latest memory-review report, state advancement, proposal counts, install state, and repo revision. |
| REQ-GLI-05 | A-4 | Not implemented in Phase 0 | DEFERRED | Planned for self-noise filtering phase. |
| REQ-GLI-06 | A-4 | Not implemented in Phase 0 | DEFERRED | Planned with self-noise filtering user-row override. |
| REQ-GLI-07 | A-5 | Not implemented in Phase 0 | DEFERRED | Planned for capability maturity phase. |
| REQ-GLI-08 | A-6 | Not implemented in Phase 0 | DEFERRED | Planned after CLI doctor JSON exists. |
| REQ-GLI-09 | A-7 | `tests.test_proposals`; full suite | PASS | Existing list/show/apply behavior remains covered. |

## Scenario Parity

| Scenario | Test/Verification | Result | Notes |
|---|---|---|---|
| UC-1 | `tests.test_governed_learning_improvements_use_cases` | PASS | Grouping, separation, and merge-first behavior covered. |
| UC-2 | `tests.test_governed_learning_improvements_use_cases` | PASS | Weak verification, script safety warnings, and read-only behavior covered. |
| UC-3 | `tests.test_doctor`; Clearing doctor smoke | PASS | Covers status, install state, memory-review state/report, cron, proposals, and recommendations. |
| UC-4 | Deferred | DEFERRED | Later memory-review filtering phase. |
| UC-5 | Deferred | DEFERRED | Later memory-review filtering phase. |
| UC-6 | Deferred | DEFERRED | Later maturity phase. |
| UC-7 | Deferred | DEFERRED | Later doctor and VS Code phase. |

## Command Evidence

| Command | Working Dir | Result | Evidence |
|---|---|---|---|
| `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest tests.test_governed_learning_improvements_use_cases tests.test_governed_learning_improvements_smoke tests.test_proposals -v` | `/home/ev/code/govkb` | PASS | 12 tests passed. |
| `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -v` | `/home/ev/code/govkb` | PASS | 196 tests passed, 33 skipped scaffold tests. |
| `git diff --check` | `/home/ev/code/govkb` | PASS | No whitespace errors. |
| `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli proposals review --help` | `/home/ev/code/govkb` | PASS | CLI help resolved. |
| `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli proposals review /home/ev/code/Clearing --action inspect-safety` | `/home/ev/code/govkb` | PASS | Clearing consumer queue reported 4 safety-inspection groups. |
| `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest tests.test_doctor tests.test_status_json tests.test_proposals -v` | `/home/ev/code/govkb` | PASS | 14 tests passed. |
| `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli doctor /home/ev/code/Clearing` | `/home/ev/code/govkb` | PASS | Reported cron installed, latest memory-review completed, 30 proposals, 28 groups, and 16 warnings. |

## Deviations

| Deviation | Approved? | Reason | Follow-up |
|---|---|---|---|
| Phase 0 added `govkb proposals review` in addition to the planned `report` command. | Yes | The report JSON is useful for integration, but maintainers also need direct next commands. | Use `review --json` as the VS Code proposal queue contract. |
| Overall feature requirements REQ-GLI-05 through REQ-GLI-08 are not complete. | Yes | The feature is being delivered in bounded phases. | Continue with self-noise, maturity, and VS Code phases. |
| Clearing proposal counts changed between initial and final consumer checks. | Yes | Clearing is a live consumer queue, not an automated fixture. | Keep automated tests on synthetic fixtures. |

## Risks

- Similarity grouping may need tuning after more proposal queues are reviewed.
- Script warning heuristics are advisory and may produce false positives.
- VS Code still shows old UI until it consumes the new proposal review and doctor JSON contracts.

## Required Fixes Before Merge

None for Phase 0.

## Post-merge Follow-ups

- Update VS Code to consume `govkb proposals review --json`.
- Update VS Code to consume `govkb doctor --json`.
- Add conservative self-noise filtering for already processed session tails.
- Add capability maturity scoring after health output stabilizes.
