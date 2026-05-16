# VS Code Learning Discovery and Progress - Implementation Summary Phase 5

## Completed

- Added an explicit Learning next-step row so users see the immediate action before reading lifecycle state.
- Changed ready promotion rows into a visible sequence: open the learning review, then accept reviewed updates or reject the review.
- Kept accepted promotion apply as the primary action and described that it copies `.governed` changes without committing.
- Restored visible Candidates and Reports views in the GovKB activity container.
- Added `GovKB: Open Candidate Draft` so staged candidates open their draft instructions directly from the UI.
- Updated candidate rows to say that staged candidates need triage before promotion.

## Files Changed

- `vscode-extension/package.json`
- `vscode-extension/src/extension.ts`
- `vscode-extension/src/views/candidatesView.ts`
- `vscode-extension/src/views/learningView.ts`
- `vscode-extension/src/views/promotionsView.ts`
- `vscode-extension/src/test/host/suite/index.ts`
- `vscode-extension/src/test/suite/packaging.test.ts`
- `vscode-extension/src/test/suite/views.test.ts`

## Verification

- `npm test` in `/Users/vasilevevgeny/code/govkb/vscode-extension`
- `npm run test:host` in `/Users/vasilevevgeny/code/govkb/vscode-extension`
