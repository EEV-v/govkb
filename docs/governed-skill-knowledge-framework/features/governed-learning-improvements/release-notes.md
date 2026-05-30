# Governed Learning Improvements - Release Notes

Release date: 2026-05-30
Status: Ready

## Summary

GovKB now provides read-only proposal review, doctor, and VS Code health flows that group related staged governed-learning proposals, surface advisory quality warnings, report cron and memory-review freshness, and print actionable next commands for maintainer triage.

## What Changed

- Added `govkb proposals report [project_root] [--json]`.
- Added `govkb proposals review [project_root] [--action ...] [--json]`.
- Added `govkb doctor [project_root] [--codex-home ...] [--json]`.
- Added VS Code `GovKB: Refresh Health` and `GovKB: Review Proposals`.
- Updated VS Code Home and Status to show Doctor state, cron state, memory-review freshness, proposal counts, proposal warnings, and proposal action counts.
- Added proposal grouping, warning, and recommended-action logic.
- Added health/freshness composition for validation, install state, memory-review state/report files, cron, and proposal queue summary.
- Added focused tests and Phase 0-4 feature documentation.

## Why It Matters

- Maintainers can review duplicate or overlapping governed-learning output before applying anything.
- Script and wrapper proposals are easier to inspect for missing draft output, dry-run behavior, and verification evidence.
- VS Code Home and Status now consume stable proposal queue and project health JSON contracts.

## User Impact

| Audience | Impact | Required Action |
|---|---|---|
| GovKB maintainer | Can triage proposal queues and inspect project health with report/review/doctor commands and VS Code health buttons. | Use `govkb proposals review <project-root>`, `govkb doctor <project-root>`, or VS Code Home. |
| Project adopter | Gets clearer proposal groups, cron status, memory-review status, and warnings without mutation. | Review warnings before applying proposals. |
| Assistant user | Future sessions can point to exact proposal show/apply commands. | None. |

## Verification

| Check | Command/Evidence | Result |
|---|---|---|
| Unit/workflow tests | `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -v` | PASS: 196 tests, 33 skipped |
| VS Code extension tests | `cd vscode-extension && npm test` | PASS: 120 tests |
| VS Code package/install | `npm run package`; `code --install-extension .../govkb-0.0.5.vsix --force` | PASS: `govkb-local.govkb@0.0.5` installed |
| CLI smoke | `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli proposals review /home/ev/code/Clearing --action inspect-safety` | PASS |
| CLI doctor | `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli doctor /home/ev/code/Clearing` | PASS |
| PoC parity | `poc-parity-review.md` | Ready for Merge: Yes, Phases 0-1 and 4 |

## Rollback

Revert the VS Code `0.0.5` commit to remove the extension UI changes. Revert commits `69b943e` and `5630082` to remove the Phase 0 proposal report and review commands. Existing staged proposals remain valid because the feature is read-only and does not alter proposal metadata or apply behavior.

## Known Limitations

- VS Code proposal and health UI is read-only; proposal apply remains CLI/manual review only.
- Similarity grouping and script-warning heuristics are advisory and may require tuning.

## Related Artifacts

- Feature folder: `docs/governed-skill-knowledge-framework/features/governed-learning-improvements/`
- Use cases: `use-cases.md`
- Implementation plan: `implementation-plan.md`
- PoC parity review: `poc-parity-review.md`

## Tracking

Tracker item: local GovKB feature folder
Release/commit: `69b943e`, `5630082`, `c208b0c`, `7e4ce99`, plus VS Code `0.0.5`
