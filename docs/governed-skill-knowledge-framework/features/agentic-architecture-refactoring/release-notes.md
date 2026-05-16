# Agentic Architecture Refactoring - Release Notes

Release date: 2026-05-16
Status: Ready

## Summary

GovKB now has a clearer architecture boundary for agentic state, safer promotion lifecycle reruns, preview-first cleanup for finished promotion worktrees, and a more discoverable VS Code workflow for governed skills and conversions.

## What Changed

- Added an agentic state ownership map for source, derived, generated, disposable, and test-only state.
- Added a typed VS Code action registry and tests that keep public command metadata aligned with `package.json`.
- Made repeated promotion accept, reject, finalize/apply, and archive actions idempotent.
- Added `govkb promotions cleanup` with preview/apply behavior that removes only eligible worktrees and preserves sidecar metadata.
- Improved governed skill display rows and conversion picker filtering.

## Why It Matters

- Users get clearer next actions and fewer stale worktree distractions.
- Maintainers can rerun lifecycle actions without duplicate state or misleading metadata churn.
- Extension mutations remain CLI-backed, previewable, and covered by regression tests.

## User Impact

| Audience | Impact | Required Action |
|---|---|---|
| GovKB maintainer | Easier review of promotion state, cleanup, and governed skill UX. | Review and commit the changed source/docs normally. |
| Project adopter | Safer cleanup and conversion workflows in the VS Code sidebar. | Reinstall or run the updated extension build after merge. |
| Assistant user | Fewer governed/GovKB-generated skills appear as conversion choices. | Use manual entry only for sources not listed. |

## Verification

| Check | Command/Evidence | Result |
|---|---|---|
| Unit/workflow tests | `PYTHONPATH=src /Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest discover -s tests -v` | Passed, 172 tests, 33 skipped. |
| Extension tests | `npm test` from `vscode-extension` | Passed, 115 tests. |
| Extension host smoke | `npm run test:host` from `vscode-extension` | Passed, extension host exited 0. |
| CLI validation | `PYTHONPATH=src /Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m govkb.cli validate /Users/vasilevevgeny/code/govkb` | Passed with one existing non-blocking thin-memory warning. |
| PoC parity | `poc-parity-review.md` | Ready for Merge: Yes. |

## Rollback

Revert the feature branch changes. For local extension testing, reinstall the previous VSIX or rebuild the previous extension revision. Cleanup does not require migration rollback because it preserves sidecar lifecycle metadata and only removes eligible review worktrees after explicit apply.

## Known Limitations

- Tree view command metadata is not fully generated from the registry; parity tests protect the public command ids and manifest contributions.
- Governed skill summaries are derived from current status payload fields; no dedicated summary contract field was added.

## Related Artifacts

- Feature folder: `docs/governed-skill-knowledge-framework/features/agentic-architecture-refactoring/`
- Use cases: `use-cases.md`
- Implementation plan: `implementation-plan.md`
- PoC parity review: `poc-parity-review.md`

## Tracking

Tracker item: local feature folder
Release/commit: pending normal project commit
