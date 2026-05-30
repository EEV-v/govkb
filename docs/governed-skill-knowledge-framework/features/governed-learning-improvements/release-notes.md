# Governed Learning Improvements - Release Notes

Release date: 2026-05-30
Status: Ready

## Summary

GovKB now provides a read-only proposal review flow that groups related staged governed-learning proposals, surfaces advisory quality warnings, and prints actionable next commands for maintainer triage.

## What Changed

- Added `govkb proposals report [project_root] [--json]`.
- Added `govkb proposals review [project_root] [--action ...] [--json]`.
- Added proposal grouping, warning, and recommended-action logic.
- Added focused tests and Phase 0 feature documentation.

## Why It Matters

- Maintainers can review duplicate or overlapping governed-learning output before applying anything.
- Script and wrapper proposals are easier to inspect for missing draft output, dry-run behavior, and verification evidence.
- VS Code has a stable JSON contract to consume for the proposal queue in a later UI phase.

## User Impact

| Audience | Impact | Required Action |
|---|---|---|
| GovKB maintainer | Can triage proposal queues with report/review commands. | Use `govkb proposals review <project-root>`. |
| Project adopter | Gets clearer proposal groups and warnings without mutation. | Review warnings before applying proposals. |
| Assistant user | Future sessions can point to exact proposal show/apply commands. | None. |

## Verification

| Check | Command/Evidence | Result |
|---|---|---|
| Unit/workflow tests | `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -v` | PASS: 194 tests, 33 skipped |
| CLI smoke | `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli proposals review /home/ev/code/Clearing --action inspect-safety` | PASS |
| PoC parity | `poc-parity-review.md` | Ready for Merge: Yes, Phase 0 only |

## Rollback

Revert commits `69b943e` and `5630082`. Existing staged proposals remain valid because Phase 0 is read-only and does not alter proposal metadata or apply behavior.

## Known Limitations

- Health, cron, installed revision, and VS Code freshness are not implemented in Phase 0.
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
