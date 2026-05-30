# Governed Learning Improvements - Stakeholder Presentation

Status: Ready
Date: 2026-05-30

## 1. Executive Summary

GovKB now has a read-only proposal review and doctor layer for governed learning output. Maintainers can group related staged proposals, see quality warnings, check cron and memory-review freshness, and get concrete next commands without applying or mutating any proposal files.

## 2. Problem

- Staged learning proposals can overlap and compete for similar governed artifacts.
- Script and wrapper proposals need visible safety and verification review before approval.
- The old queue shape was too flat for maintainers and VS Code integration.

## 3. Delivered Scope

| Area | Delivered |
|---|---|
| Product behavior | Proposal groups, advisory warnings, next review actions, and project health/freshness diagnostics. |
| CLI/API behavior | `govkb proposals report`, `govkb proposals review`, and `govkb doctor` with JSON and text output. |
| Documentation | Feature artifacts through Phase 8 parity and release closeout. |
| Tests | Synthetic `unittest` fixtures for grouping, read-only behavior, warnings, filters, and existing proposal regressions. |

## 4. Workflow

```text
flat staged proposal queue plus manual cron/status checks -> GovKB review and doctor output -> safer maintainer triage before apply
```

## 5. Use Case Coverage

| Scenario | Status | Evidence |
|---|---|---|
| UC-1 Proposal Queue Groups Similar Work | Delivered | `tests/test_governed_learning_improvements_use_cases.py` |
| UC-2 Proposal Quality Warnings Are Advisory | Delivered | `tests/test_governed_learning_improvements_use_cases.py` |
| UC-3 Memory Review Health Is Visible In One Report | Delivered | `tests/test_doctor.py` |
| UC-4 Self-Generated Session Tails Are Skipped | Deferred | Planned later phase |
| UC-5 User Decisions After A Processed Marker Are Still Reviewed | Deferred | Planned later phase |
| UC-6 Capability Maturity Score Explains Next Investment | Deferred | Planned later phase |
| UC-7 VS Code Freshness Check Identifies Stale Layers | Deferred | Planned after doctor JSON |

## 6. Verification

| Check | Evidence | Result |
|---|---|---|
| Test suite | `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -v` | PASS: 196 tests, 33 skipped |
| CLI smoke/dry-run | `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli proposals review /home/ev/code/Clearing --action inspect-safety` | PASS |
| CLI doctor | `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli doctor /home/ev/code/Clearing` | PASS |
| PoC parity | `poc-parity-review.md` | Ready for Merge: Yes, Phases 0-1 |

## 7. Rollout And Rollback

Rollout:

- Use `govkb proposals report <project-root> --json` for machine-readable grouping.
- Use `govkb proposals review <project-root> --action <action>` for maintainer triage.
- Use `govkb doctor <project-root> --json` for project health and VS Code integration.

Rollback:

- Revert the doctor commit to remove Phase 1, or revert commits `69b943e` and `5630082` to remove the Phase 0 proposal report and review commands.

## 8. Decisions Or Follow-ups

| Item | Owner | Needed By |
|---|---|---|
| Wire VS Code to `govkb proposals review --json` and `govkb doctor --json` | GovKB maintainer | Next UI phase |
| Review Clearing safety groups manually | Clearing maintainer | Before applying script/wrapper proposals |
