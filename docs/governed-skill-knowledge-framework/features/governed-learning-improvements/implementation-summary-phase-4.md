# Governed Learning Improvements - Implementation Summary Phase 4

Date: 2026-05-30

## Completed

- Added VS Code command builders for `govkb doctor --json` and `govkb proposals review --json`.
- Added strict extension-side parsers and types for Doctor and proposal-review payloads.
- Added `GovKB: Refresh Health` and `GovKB: Review Proposals` commands.
- Updated Home to show Doctor state, cron state, latest memory-review report state, proposal counts, warning counts, and proposal action counts.
- Updated Status to include read-only Doctor, proposal queue, cron, and recommendation rows.
- Bumped the local VSIX package to `0.0.5`.

## Files Changed

- `vscode-extension/src/govkbCli.ts`
- `vscode-extension/src/jsonParsers.ts`
- `vscode-extension/src/types.ts`
- `vscode-extension/src/actionRegistry.ts`
- `vscode-extension/src/homeState.ts`
- `vscode-extension/src/extension.ts`
- `vscode-extension/src/views/statusView.ts`
- `vscode-extension/src/test/suite/*.test.ts`
- `vscode-extension/package.json`
- `vscode-extension/package-lock.json`
- `vscode-extension/README.md`
- `vscode-extension/CHANGELOG.md`

## Verification

```bash
cd /home/ev/code/govkb/vscode-extension
npm run compile
npm test
npm run package
code --install-extension /home/ev/code/govkb/vscode-extension/govkb-0.0.5.vsix --force
```

Result:

- TypeScript compile passed.
- Extension test suite passed: 120 tests.
- VSIX package built: `vscode-extension/govkb-0.0.5.vsix`.
- VS Code reports installed extension: `govkb-local.govkb@0.0.5`.

```bash
cd /home/ev/code/govkb
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest tests.test_doctor tests.test_proposals tests.test_governed_learning_improvements_use_cases tests.test_governed_learning_improvements_smoke -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli doctor /home/ev/code/Clearing --json
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli proposals review /home/ev/code/Clearing --action inspect-safety
git diff --check
```

Result:

- Focused Python CLI tests passed: 14 tests.
- Full Python suite passed: 196 tests, 33 skipped scaffold tests.
- Clearing Doctor smoke reported state `attention`, cron `installed`, latest memory-review `completed`, 30 proposals, 16 warnings, and action counts of 4 `inspect-safety`, 2 `merge-first`, and 22 `manual-review`.
- Clearing proposal review smoke listed 4 `inspect-safety` groups.
- Diff whitespace check passed.

## Deviations From Plan

- Phase 4 stayed read-only. The extension prints proposal inspect commands and refreshes status, but it does not apply proposals from the UI.
- The existing Home webview and Status tree were extended instead of adding a dedicated proposal tree. This keeps the user flow simple and avoids another navigation surface.

## Next Phase

- Continue with self-noise filtering for session tails after the UI confirms the new health/proposal surfaces.
