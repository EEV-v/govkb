# VS Code Learning Discovery and Progress - Implementation Summary Phase 4

## Completed

- Added a governed promotion lifecycle apply step: `govkb promotions apply <promotion> --project-root <root> --codex-home <home>`.
- Apply requires an accepted promotion by default, copies reviewed `.governed` changes from the isolated worktree into the active project, and leaves the active project uncommitted for normal Git review.
- Recorded applied promotions in sidecar lifecycle metadata with applied files and timestamp.
- Stopped repeat auto-promote from creating equivalent isolated worktrees when the same local memory additions already have a non-archived isolated promotion.
- Updated the VS Code Promotions view to show accepted promotions as ready to apply, applied promotions as pending commit, and compact equivalent duplicate worktree rows.
- Added the `GovKB: Apply Accepted Promotion To Project` command and context action for accepted promotion rows.
- Made the accepted promotion apply action the primary Learning and Promotions row action, added a confirmation prompt before mutating the active project, and removed the worktree opener from inline actions so normal clicking no longer opens a new VS Code window.

## Files Changed

- `src/govkb/commands/promotions.py`
- `src/govkb/core/promotion_lifecycle.py`
- `src/govkb/adapters/codex/promote.py`
- `src/govkb/cli.py`
- `tests/test_promotions.py`
- `tests/test_promote.py`
- `vscode-extension/src/govkbCli.ts`
- `vscode-extension/src/flows.ts`
- `vscode-extension/src/extension.ts`
- `vscode-extension/src/types.ts`
- `vscode-extension/src/views/promotionsView.ts`
- `vscode-extension/src/views/learningView.ts`
- `vscode-extension/package.json`
- `vscode-extension/src/test/suite/govkbCli.test.ts`
- `vscode-extension/src/test/suite/flows.test.ts`
- `vscode-extension/src/test/suite/views.test.ts`
- `vscode-extension/src/test/suite/packaging.test.ts`
- `vscode-extension/src/test/host/suite/index.ts`

## Verification

- `PYTHONPATH=src /Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_promotions tests.test_promote`
- `PYTHONPATH=src /Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest discover -s tests`
- `npm test` in `/Users/vasilevevgeny/code/govkb/vscode-extension`
- `npm run test:host` in `/Users/vasilevevgeny/code/govkb/vscode-extension`
- `scripts/govkb-dev validate /Users/vasilevevgeny/code/Etna/Clearing --strict --json`
- `scripts/govkb-dev promote /Users/vasilevevgeny/code/Etna/Clearing --codex-home /Users/vasilevevgeny/.codex --auto`

## Real Clearing Result

- Clearing strict validation returned no errors or warnings.
- Repeat auto-promote did not create another duplicate worktree; it reported an existing equivalent isolated promotion.
- Existing duplicate worktrees remain on disk for auditability; the UI now compacts equivalent rows rather than presenting every duplicate as a separate required decision.

## Deviations From Earlier UX

- Accepting a promotion still only records the review decision.
- Applying a promotion is now a separate explicit action and does not commit. This preserves the project Git flow while giving users a one-step way to move reviewed worktree changes back into the active project.

## Next Phase

- Add optional cleanup/archive affordances for superseded duplicate promotion worktrees after users confirm the lifecycle wording and UI behavior.
