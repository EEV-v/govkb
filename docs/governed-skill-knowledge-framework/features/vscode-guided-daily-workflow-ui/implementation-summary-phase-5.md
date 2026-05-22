# VS Code Guided Daily Workflow UI - Implementation Summary Phase 5

Date: 2026-05-17

## Scope

This phase tightened the Home everyday flow wording after user review. The primary action now carries explicit `reason` and `consequence` text so the user can see why GovKB recommends the action and what clicking it will do before running it.

## Changes

- `vscode-extension/src/homeState.ts` adds reason/consequence metadata for primary states including setup, apply, promotion review, finalization, commit handoff, learning review, and discovery.
- `vscode-extension/src/homeWebview.ts` renders the primary explanation directly below the primary action.
- `vscode-extension/src/actionRegistry.ts` renames the Home-facing bounded preview action from "Dry run" to "Preview review" while preserving the existing command.
- `vscode-extension/src/test/suite/homeState.test.ts` verifies stale apply explanation and that the primary learning review label does not expose dry-run wording.
- `vscode-extension/src/test/suite/homeWebview.test.ts` verifies explanation rendering and stale apply reason/consequence text.

## Verification

- `npm test` from `vscode-extension`: passed, 116 tests.

## Notes

The underlying CLI mutation boundary did not change. The primary learning preview still delegates to `govkb.reviewLearningDryRun`; only the everyday Home label changed.
