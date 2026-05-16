# VS Code Guided Daily Workflow UI - PoC Output

Last updated: 2026-05-16

## Summary

The existing extension architecture can support a guided Home UI without changing core GovKB mutation semantics. Most behavior should be implemented as a TypeScript model and Webview View that orchestrates existing CLI-backed flows.

## Findings

| PoC Question | Evidence | Result |
|---|---|---|
| Can the Home model derive daily workflow state from existing payloads? | `vscode-extension/src/types.ts`, `vscode-extension/src/views/learningView.ts`, `vscode-extension/src/views/promotionsView.ts` | Yes. Current types include status, inventory, progress, report, candidate, and promotion summaries. |
| Can tree views be polished without replacing them? | `vscode-extension/src/views/simpleTree.ts`, `vscode-extension/package.json` | Yes. `SimpleTreeProvider` can add icon fields; package menus already define title and item actions. |
| Can a custom dashboard be added? | `vscode-extension/package.json`, `vscode-extension/src/extension.ts` | Yes. The package already contributes multiple views and activation events; a `WebviewViewProvider` can be registered alongside them. |
| Can mutation remain CLI-backed? | `vscode-extension/src/flows.ts`, `vscode-extension/src/govkbCli.ts` | Yes. Existing flow functions wrap CLI commands and parse outputs. Home can call commands/flows rather than writing files. |
| Can tests run without VS Code host for core behavior? | `vscode-extension/src/test/suite/*.test.ts` | Yes. Existing tests cover pure functions for views, parsers, flows, command builders, settings, and promotion review. |

## Risks Confirmed

- A Webview dashboard adds CSP, message routing, and HTML rendering complexity.
- Tree views remain constrained; they should not be asked to carry the full guided workflow.
- The next-action state machine needs careful tests to avoid stale or misleading UI after finalization and commit.

## PoC Decision

Proceed with implementation planning. Use a TypeScript-first implementation with existing CLI flows as integration points.
