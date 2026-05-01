# VS Code Extension UI and Public Distribution - Release Notes

Release date: 2026-04-25
Status: Ready

## Summary

GovKB now has an optional local VS Code extension package and machine-readable CLI output for editor views. The first slice supports WSL/Linux local VSIX validation, one-click setup/apply orchestration through the GovKB CLI, status/candidate/report view contracts, Workspace Trust gating, and dry-run memory review defaults.

## What Changed

- Added `govkb status --json` and `govkb candidates list --json`.
- Added `vscode-extension/` with command palette actions, settings, view providers, workflow orchestration, tests, and local VSIX packaging.
- Added Python and TypeScript tests for JSON CLI contracts, command construction, setup/apply flows, trust gating, settings, report summaries, and packaging exclusions.
- Added cookbook artifacts from PoC through parity review and implementation summaries.

## Why It Matters

- New adopters can use GovKB through a familiar editor surface instead of memorizing CLI flags.
- The extension remains a thin layer over tested GovKB core behavior.
- Views consume durable JSON contracts rather than brittle human CLI text.
- Governance boundaries are explicit: `.governed/` stays source of truth and Codex output stays derived local state.

## User Impact

| Audience | Impact | Required Action |
|---|---|---|
| GovKB maintainer | Can validate and iterate on a local VSIX proof. | Run extension tests and local VSIX package command. |
| Project adopter | Gets a planned one-click setup/apply path in VS Code. | Install local VSIX after maintainer validation. |
| Assistant user | Gets safer memory-review defaults and status visibility. | Use dry-run review path first; do not use Marketplace flow yet. |

## Verification

| Check | Command/Evidence | Result |
|---|---|---|
| Python unit/workflow tests | `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -v` | Passed: 83 tests, 11 scaffold skips. |
| Extension tests | `npm test` from `vscode-extension/` | Passed: 28 Node tests. |
| CLI smoke | `govkb status --json`, `govkb candidates list --json`, `govkb apply codex --preview` on `/tmp/govkb-vscode-smoke.fgQkik/DemoProject` | Passed. |
| VSIX package | `npm_config_cache=/tmp/govkb-npm-cache npx @vscode/vsce package --no-dependencies` | Passed with non-blocking missing repository metadata warning. |
| PoC parity | `poc-parity-review.md` | Ready for Merge: Yes. |

## Rollback

- Revert `vscode-extension/` and README/docs references to remove the editor package.
- Revert additive `--json` flags and JSON payload helpers in `src/govkb/cli.py`, `src/govkb/commands/status.py`, and `src/govkb/commands/candidates.py` if JSON CLI behavior must be backed out.
- Existing human CLI output remains the default and is backward-compatible.

## Known Limitations

- Local VSIX proof only; public Marketplace publishing is not complete.
- WSL/Linux first slice only; macOS, Windows native, and VS Code Web are not validated.
- Marketplace publisher, repository metadata, icon/branding, and final license are deferred.
- npm reported moderate advisories in dev dependencies; review before public distribution.

## Related Artifacts

- Feature folder: `docs/governed-skill-knowledge-framework/features/vscode-extension-public-distribution/`
- Use cases: `use-cases.md`
- Implementation plan: `implementation-plan.md`
- PoC parity review: `poc-parity-review.md`

## Tracking

Tracker item: not configured for this GovKB feature
Release/commit: pending

