# Agentic Architecture Refactoring - Implementation Summary Phase 3

## Completed

- Added promotion cleanup preview/apply behavior for non-actionable isolated promotion worktrees.
- Preserved sidecar lifecycle metadata by marking cleaned promotions with cleanup details instead of deleting metadata.
- Added CLI wiring for `govkb promotions cleanup`.
- Added VS Code command wiring for preview-first cleanup with an explicit confirmation before apply.
- Added regression coverage for no-write preview, contained apply, metadata preservation, hidden cleaned worktrees, and idempotent reruns.

## Files Changed

- `src/govkb/core/promotion_lifecycle.py`
- `src/govkb/commands/promotions.py`
- `src/govkb/cli.py`
- `vscode-extension/package.json`
- `vscode-extension/src/extension.ts`
- `vscode-extension/src/flows.ts`
- `vscode-extension/src/govkbCli.ts`
- `vscode-extension/src/jsonParsers.ts`
- `vscode-extension/src/types.ts`
- `tests/test_agentic_architecture_refactoring_use_cases.py`
- `vscode-extension/src/test/suite/flows.test.ts`
- `vscode-extension/src/test/suite/govkbCli.test.ts`
- `vscode-extension/src/test/suite/jsonParsers.test.ts`
- `vscode-extension/src/test/suite/packaging.test.ts`

## Verification

- `PYTHONPATH=src /Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_agentic_architecture_refactoring_use_cases -v`
- `PYTHONPATH=src /Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_promotions -v`
- `PYTHONPATH=src /Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m govkb.cli promotions cleanup --help`
- `npm test` from `vscode-extension`
- `git diff --check`

## Deviations From Plan

- Cleanup was implemented before the full VS Code action registry because stale worktree cleanup was the active operational blocker. The CLI mutation boundary remains intact; VS Code now exposes a guarded preview/apply cleanup action and the registry work remains the next refactoring phase.

## Next Phase

Phase 4 - Governed Skill Summary And Conversion UX.
