# VS Code Extension UI and Public Distribution - Implementation Summary Phase 5

## Completed

- Added a first-class VS Code `Promotions` view for isolated automated promotion worktrees.
- Added extension commands for `govkb promote --auto` and `govkb promotions list/show/mark-reviewed/archive`.
- Added promotion lifecycle parsing, tree rows, command builders, and flow tests.
- Updated extension documentation to explain that promotion lifecycle decisions are sidecar GovKB state and do not replace normal Git commit, merge, push, or cleanup flows.
- Added read-only startup refresh for the remembered project root so users do not need to re-run setup/apply just to see GovKB state after reopening the same workspace.
- Added optional read-only monitoring interval and a `Skill updates` status row comparing current project Git state to the applied Codex install state.
- Extended CLI status JSON with a single authoritative `skillUpdates` object that also reports safe/rejected pending local memory promotions.
- Added a strict-ready customer-demo fixture under `docs/governed-skill-knowledge-framework/examples/strict-ready-demo-project`.
- Added extension-host smoke tests with `@vscode/test-electron` to validate activation and command registration inside VS Code.
- Added default GovKB runtime discovery for GUI-launched VS Code sessions that do not inherit shell PATH.
- Updated the local `scripts/govkb-dev` launcher to select Python 3.11 or newer.
- Ensured `govkb review-memory` runs Python adapters with the active GovKB interpreter and the extension passes a bounded classifier timeout by default.

## Existing UX Now Covered

- One-click setup per selected workspace folder.
- One-click apply per selected workspace folder.
- Status, capabilities, candidates, memory-review reports, and promotions views.
- Startup auto-refresh and optional periodic monitoring for read-only surfaces.
- Skill update visibility: current, not applied, apply available, learned updates, local `.governed` changes, or unknown comparison state.
- Memory-review dry-run and apply commands with streamed output.
- Promotion review affordances: auto promote, refresh, open digest, show details, accept, reject, and archive.

## Still Needed

- Manual VS Code walkthrough after reinstall on the target workstation.

## Files Changed

- `vscode-extension/package.json`
- `vscode-extension/src/types.ts`
- `vscode-extension/src/govkbCli.ts`
- `vscode-extension/src/jsonParsers.ts`
- `vscode-extension/src/flows.ts`
- `vscode-extension/src/extension.ts`
- `vscode-extension/src/workspaceProject.ts`
- `vscode-extension/src/runtimeDiscovery.ts`
- `vscode-extension/src/views/promotionsView.ts`
- `vscode-extension/src/test/fixtures/promotions.sample.json`
- `vscode-extension/src/test/suite/govkbCli.test.ts`
- `vscode-extension/src/test/suite/flows.test.ts`
- `vscode-extension/src/test/suite/jsonParsers.test.ts`
- `vscode-extension/src/test/suite/views.test.ts`
- `vscode-extension/src/test/suite/workspaceProject.test.ts`
- `vscode-extension/src/test/suite/runtimeDiscovery.test.ts`
- `vscode-extension/src/test/host/runTest.ts`
- `vscode-extension/src/test/host/suite/index.ts`
- `vscode-extension/README.md`
- `vscode-extension/MANUAL.md`
- `src/govkb/commands/status.py`
- `src/govkb/commands/review_memory.py`
- `tests/test_status_json.py`
- `tests/test_review_memory_command.py`
- `tests/test_strict_ready_demo_fixture.py`
- `scripts/govkb-dev`
- `docs/governed-skill-knowledge-framework/examples/strict-ready-demo-project/README.md`

## Verification

- `npm test`
- `npm run test:host`
- `python3 -m unittest tests.test_status_json tests.test_strict_ready_demo_fixture -v`
