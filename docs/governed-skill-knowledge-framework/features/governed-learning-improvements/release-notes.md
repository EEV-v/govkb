# Governed Learning Improvements - Release Notes

Release date: 2026-05-30
Status: Ready

## Summary

GovKB now provides read-only proposal review and doctor flows that group related staged governed-learning proposals, surface advisory quality warnings, report cron and memory-review freshness, and print actionable next commands for maintainer triage.

## What Changed

- Added `govkb proposals report [project_root] [--json]`.
- Added `govkb proposals review [project_root] [--action ...] [--json]`.
- Added `govkb doctor [project_root] [--codex-home ...] [--json]`.
- Added proposal grouping, warning, and recommended-action logic.
- Added health/freshness composition for validation, install state, memory-review state/report files, cron, and proposal queue summary.
- Added focused tests and Phase 0 feature documentation.

## Why It Matters

- Maintainers can review duplicate or overlapping governed-learning output before applying anything.
- Script and wrapper proposals are easier to inspect for missing draft output, dry-run behavior, and verification evidence.
- VS Code has stable JSON contracts to consume for proposal queue and project health in a later UI phase.

## User Impact

| Audience | Impact | Required Action |
|---|---|---|
| GovKB maintainer | Can triage proposal queues and inspect project health with report/review/doctor commands. | Use `govkb proposals review <project-root>` and `govkb doctor <project-root>`. |
| Project adopter | Gets clearer proposal groups, cron status, memory-review status, and warnings without mutation. | Review warnings before applying proposals. |
| Assistant user | Future sessions can point to exact proposal show/apply commands. | None. |

## Verification

| Check | Command/Evidence | Result |
|---|---|---|
| Unit/workflow tests | `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -v` | PASS: 196 tests, 33 skipped |
| CLI smoke | `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli proposals review /home/ev/code/Clearing --action inspect-safety` | PASS |
| CLI doctor | `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli doctor /home/ev/code/Clearing` | PASS |
| PoC parity | `poc-parity-review.md` | Ready for Merge: Yes, Phases 0-1 |

## Rollback

Revert commits `69b943e` and `5630082`. Existing staged proposals remain valid because Phase 0 is read-only and does not alter proposal metadata or apply behavior.

## Known Limitations

- VS Code freshness UI is not implemented yet, but `govkb doctor --json` now provides the backend contract.
- Similarity grouping and script-warning heuristics are advisory and may require tuning.
- VS Code still needs a separate UI integration pass.

## Related Artifacts

- Feature folder: `docs/governed-skill-knowledge-framework/features/governed-learning-improvements/`
- Use cases: `use-cases.md`
- Implementation plan: `implementation-plan.md`
- PoC parity review: `poc-parity-review.md`

## Tracking

Tracker item: local GovKB feature folder
Release/commit: `69b943e` plus `5630082`
