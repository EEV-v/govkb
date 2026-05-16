# VS Code Guided Daily Workflow UI - PoC Plan

Last updated: 2026-05-16

## Goal

Prove that the feature can be implemented using current extension data contracts and VS Code primitives without adding a new Python mutation path.

## Evidence To Collect

| Evidence | Method | Expected Result |
|---|---|---|
| Extension data contracts are enough for Home state. | Inspect `types.ts`, `flows.ts`, `learningView.ts`, and `promotionsView.ts`. | Status, learning, reports, candidates, and promotions cover the state machine. |
| Tree Views can support icons and inline actions. | Inspect `simpleTree.ts` and package command/menu contributions. | `TreeRow` can grow icon metadata; menus already use `view/item/context`. |
| Webview can be added as a sidebar view. | Inspect package contribution structure and extension activation pattern. | Add `govkb.home` with a `WebviewViewProvider`. |
| Existing tests can cover the model. | Inspect extension test suite. | Add pure Node tests without extension host for most behavior. |
| Governance boundary remains intact. | Inspect `flows.ts`. | Home commands can delegate to existing flow functions. |

## PoC Constraints

- No raw user session data.
- No new CLI mutation commands.
- No dependency on external web assets.
- No implementation code in this PoC package.

## Regeneration

The PoC is inspection-based for this feature start. If implementation starts, evidence should be updated by running:

```bash
cd /Users/vasilevevgeny/code/govkb/vscode-extension
npm test
```

and:

```bash
cd /Users/vasilevevgeny/code/govkb
PYTHONPATH=src <python3.11+> -m unittest discover -s tests -v
```
