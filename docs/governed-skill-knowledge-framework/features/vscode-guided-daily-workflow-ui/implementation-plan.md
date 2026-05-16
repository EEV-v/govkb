# VS Code Guided Daily Workflow UI - Implementation Plan

Last updated: 2026-05-16

## 0. Existing Code Inventory

| Category | Component | Location | Reuse Strategy |
|---|---|---|---|
| Extension manifest | Commands, views, icons, activation events, settings | `vscode-extension/package.json` | Add Home view, Home command, and icon/menu contributions. |
| Extension activation | Command registration, providers, refresh orchestration | `vscode-extension/src/extension.ts` | Register Home provider and feed it existing state refreshes. |
| CLI command builders | GovKB argument arrays | `vscode-extension/src/govkbCli.ts` | Reuse for all Home actions. |
| Flow orchestration | Setup, apply, learning, promotions, candidates, conversion, rename, merge | `vscode-extension/src/flows.ts` | Reuse; Home messages execute existing commands. |
| Settings | Runtime, Codex home, review defaults | `vscode-extension/src/settings.ts` | Reuse for Home refresh and action execution. |
| Status view logic | Skill update and project state summaries | `vscode-extension/src/views/statusView.ts` | Share or mirror state labels in `homeState.ts`. |
| Learning view logic | Next-step rules for learning and promotions | `vscode-extension/src/views/learningView.ts` | Extract reusable rules into `homeState.ts` where practical. |
| Promotion view logic | Group duplicates, detect pending commit, summarize changed files | `vscode-extension/src/views/promotionsView.ts` | Reuse helpers in Home. |
| Local skill discovery | Conversion picker filtering | `vscode-extension/src/localSkills.ts` | Reuse for picker-driven conversion. |
| Promotion review | Reason defaults and validation | `vscode-extension/src/promotionReview.ts` | Reuse for Home accept/reject actions. |
| Reports | Project-scoped report discovery | `vscode-extension/src/reports.ts` | Reuse for latest report and digest links. |
| Tests | Node tests for parser, flow, view, settings, packaging | `vscode-extension/src/test/suite/*.test.ts` | Add `homeState.test.ts`, `homeWebview.test.ts`, and extend packaging/host tests. |
| Python tests | Feature scaffolds and CLI tests | `tests/*.py` | Add skipped feature scaffolds; implement only if CLI behavior changes. |

## 0.5. Pre-flight Checklist

| Prerequisite | Status | Owner |
|---|---|---|
| Existing GovKB extension tests pass | Required before implementation | Engineering |
| No uncommitted unrelated work | Required | Engineering |
| Home scope stays CLI-backed | Required | Engineering |
| Webview CSP and local-resource policy selected | Required before webview implementation | Engineering |
| Product icons mapped to actions | Required before UI polish phase | Engineering |

## 1. Scope And Boundaries

In scope:

- Add a GovKB Home webview view that shows project state, one primary next action, workflow sections, and state-specific buttons.
- Add pure Home model code that derives dashboard state from existing payloads.
- Add webview message handling that delegates to existing commands.
- Tighten Tree View row labels, icon metadata, and context actions.
- Improve picker-driven flows for skill conversion, rename, and merge where existing data allows.
- Add tests for Home model, webview rendering, command routing, and compact native views.

Out of scope:

- New Python CLI mutation commands.
- Automatic Git commit.
- Raw transcript viewing.
- Remote web assets or third-party frontend framework dependency.
- Removing existing tree views.

## 2. Requirements Mapping

| Requirement | Behavior | Location | New/Modify | Notes |
|---|---|---|---|---|
| REQ-VGDW-01 | Derive and render one primary next action. | `homeState.ts`, `homeWebview.ts` | New | Table-driven tests from UC-9. |
| REQ-VGDW-02 | Keep tree views compact. | `views/*.ts`, `simpleTree.ts` | Modify | Add icon support and tighter row sets. |
| REQ-VGDW-03 | Cover setup/apply/learning/promotion/finalize/commit/apply-after-commit states. | `homeState.ts`, `extension.ts` | New/modify | Reuse existing commands. |
| REQ-VGDW-04 | Use icons and clear labels. | `actionIcons.ts`, `package.json`, `simpleTree.ts` | New/modify | Codicon ids only in first slice. |
| REQ-VGDW-05 | Digest-first promotion review. | `homeWebview.ts`, `promotionsView.ts` | New/modify | Open worktree remains secondary. |
| REQ-VGDW-06 | Picker-driven skill management. | `extension.ts`, `localSkills.ts`, `flows.ts` | Modify | Avoid manual entry unless selected. |
| REQ-VGDW-07 | Hide already governed/materialized source skills. | `localSkills.ts` | Modify/test | Existing tests cover main behavior; Home uses same picker. |
| REQ-VGDW-08 | Collapse stale worktrees. | `promotionsView.ts`, `homeState.ts` | Modify/new | Keep only actionable group in Home. |
| REQ-VGDW-09 | Mutate only through CLI. | `extension.ts`, `flows.ts` | Constraint | Tests assert command path. |
| REQ-VGDW-10 | Avoid transcript/local-state leakage. | `homeState.ts`, `homeWebview.ts`, tests | Constraint | Use sanitized fixture payloads only. |

## 3. Design

### Home Model

`homeState.ts` should expose a pure function:

```ts
buildHomeModel(input: HomeModelInput): HomeModel
```

The model should include:

- project badges
- primary action
- secondary actions
- workflow sections
- promotion cards
- governed skill actions
- latest report action
- blockers and warnings

The model should not depend on VS Code APIs. This keeps state selection testable in Node.

### Home Webview

`homeWebview.ts` should implement a `WebviewViewProvider` that:

- renders local HTML/CSS with VS Code theme variables
- uses nonced script content
- listens for command messages
- posts refresh and action messages to `extension.ts`
- shows a minimal loading/error state when no model is available

### Tree View Polish

Extend `TreeRow` with optional icon metadata:

```ts
icon?: string
```

`SimpleTreeProvider` maps the string to `new vscode.ThemeIcon(icon)`. Existing rows remain valid.

### Command Routing

Home actions should be logical ids such as `refresh`, `setup`, `apply`, `discover`, `reviewDryRun`, `reviewApply`, `openDigest`, `acceptPromotion`, `rejectPromotion`, `finalizePromotion`, `openOutput`, `convertSkill`, `renameSkill`, `mergeSkill`, and `openReport`.

`extension.ts` maps those ids to existing registered commands or flow helpers.

## 4. Integration Points

| Integration | Contract |
|---|---|
| `package.json` | Add `govkb.home` view and `govkb.openHome` command. |
| `extension.ts` | Register provider, refresh model, handle webview messages, and update Home after existing refreshes. |
| `types.ts` | Add Home model and TreeRow icon types. |
| `simpleTree.ts` | Render ThemeIcon when row icon is present. |
| `learningView.ts` and `promotionsView.ts` | Share next-action and promotion grouping logic with Home or keep behavior aligned by tests. |
| `localSkills.ts` | Continue filtering governed/materialized skills for conversion picker. |
| `flows.ts` | No direct webview mutation; all mutating actions use existing flows. |

## 5. Application Logic

1. On activation, create `HomeModelState` from the latest known status, inventory, run, reports, candidates, and promotions.
2. On startup refresh, update Home after status/reports/promotions/candidates/inventory refreshes.
3. When Home sends an action message, run the same command path as current tree actions.
4. During long-running review, push progress updates to Home through the model.
5. After each mutating action, refresh relevant data and re-render Home.
6. If a command fails, show blocker state in Home and offer Open Output.

## 6. Data Consistency And Safety

- Home state is derived and disposable.
- CLI output remains the durable source of truth.
- Project and assistant-local file writes stay in Python CLI commands.
- Webview HTML must not embed raw transcript text.
- Worktree paths may appear in tooltips or secondary actions, not as the primary happy path.
- Duplicate/finalized promotions should be collapsed based on existing promotion grouping and commit-state logic.

## 7. Testing Strategy

| Test Type | Location | Coverage |
|---|---|---|
| Home model unit tests | `vscode-extension/src/test/suite/homeState.test.ts` | Primary action table, badges, sections, promotion grouping. |
| Home webview tests | `vscode-extension/src/test/suite/homeWebview.test.ts` | HTML contains expected buttons, no raw path flood, command ids are present. |
| Tree view tests | `vscode-extension/src/test/suite/views.test.ts` | Icon metadata, compact labels, finalized/duplicate behavior. |
| Flow tests | `vscode-extension/src/test/suite/flows.test.ts` | Home action routing reuses CLI flows. |
| Packaging tests | `vscode-extension/src/test/suite/packaging.test.ts` | New view, command, activation event. |
| Extension host smoke | `vscode-extension/src/test/host/suite/index.ts` | New command registered. |
| Python scaffold tests | `tests/test_vscode_guided_daily_workflow_ui_use_cases.py`, `tests/test_vscode_guided_daily_workflow_ui_smoke.py` | Skipped BDD traceability until CLI work is needed. |

## 8. Verification Commands

| Command | Working Dir | Purpose | Preconditions |
|---|---|---|---|
| `npm test` | `vscode-extension` | Compile and run extension Node tests. | Node dependencies installed. |
| `npm run compile` | `vscode-extension` | TypeScript compile only. | Node dependencies installed. |
| `PYTHONPATH=src <python3.11+> -m unittest discover -s tests -v` | repo root | Full Python regression suite. | Python satisfies `requires-python >=3.11`. |
| `git diff --check` | repo root | Whitespace safety. | None. |

## 9. Implementation Phases

### Phase 0 - Shape And Contracts

Status: Complete on 2026-05-16.

Scope:

- Add Home model types and pure next-action derivation.
- Add skipped Python scaffold tests from use cases.

Files:

- `vscode-extension/src/homeState.ts`
- `vscode-extension/src/test/suite/homeState.test.ts`
- `vscode-extension/src/types.ts`
- `tests/test_vscode_guided_daily_workflow_ui_use_cases.py`
- `tests/test_vscode_guided_daily_workflow_ui_smoke.py`
- `tests/vscode_guided_daily_workflow_ui_test_helper.py`

Verify:

- `npm test`
- `PYTHONPATH=src <python3.11+> -m unittest discover -s tests -p 'test_vscode_guided_daily_workflow_ui*.py' -v`

Rollback:

- Remove new model and scaffold files.

### Phase 1 - Home Webview

Status: Complete on 2026-05-16 for the first Home dashboard slice. Manual QA against the Clearing workspace verified the Home view contribution and moved the primary next action above the status badges so it remains visible in the normal side bar pane.

Scope:

- Add `WebviewViewProvider`.
- Add `govkb.home` contribution and `govkb.openHome`.
- Render dashboard from `HomeModel`.

Files:

- `vscode-extension/package.json`
- `vscode-extension/src/homeWebview.ts`
- `vscode-extension/src/extension.ts`
- `vscode-extension/src/test/suite/homeWebview.test.ts`
- `vscode-extension/src/test/suite/packaging.test.ts`

Verify:

- `npm test`

Rollback:

- Remove view contribution, provider registration, and Home webview files.

### Phase 2 - Command Routing And Progress

Status: Complete on 2026-05-16 for CLI-backed Home action routing and refresh integration. Home actions route to existing commands and the Home model refreshes through existing status, learning, reports, candidates, and promotion refresh paths. Explicit in-webview failure cards remain for a later slice.

Scope:

- Route Home messages to existing commands.
- Update Home model during refresh and learning review progress.
- Surface failures with Open Output.

Files:

- `vscode-extension/src/extension.ts`
- `vscode-extension/src/flows.ts`
- `vscode-extension/src/test/suite/flows.test.ts`
- `vscode-extension/src/test/suite/homeState.test.ts`

Verify:

- `npm test`

Rollback:

- Disable Home message handling and leave tree commands intact.

### Phase 3 - Native View Polish

Status: Complete on 2026-05-16 for row-level VS Code ThemeIcon support and compact icon metadata.

Scope:

- Add TreeRow icon metadata.
- Tighten labels and tooltips.
- Ensure finalized/duplicate promotions remain hidden from current work.

Files:

- `vscode-extension/src/types.ts`
- `vscode-extension/src/views/simpleTree.ts`
- `vscode-extension/src/views/*.ts`
- `vscode-extension/src/test/suite/views.test.ts`

Verify:

- `npm test`

Rollback:

- Remove icon metadata and revert view row changes.

### Phase 4 - Skill Management Picker Refinement

Status: Complete on 2026-05-16 by reusing the existing picker-driven conversion, rename, and merge flows from Home. Existing local skill discovery filters materialized governed skills and project-governed source skills before showing the conversion picker; manual entry remains an explicit fallback.

Scope:

- Ensure Home and Governed Skills use picker-driven convert/rename/merge.
- Keep manual skill entry as explicit fallback only.
- Show strict validation previews and package removal failures clearly.

Files:

- `vscode-extension/src/extension.ts`
- `vscode-extension/src/localSkills.ts`
- `vscode-extension/src/flows.ts`
- `vscode-extension/src/test/suite/localSkills.test.ts`
- `vscode-extension/src/test/suite/flows.test.ts`

Verify:

- `npm test`

Rollback:

- Keep CLI commands and remove picker refinements.

## 10. Rollback Plan

The feature is additive. If Home causes issues, remove the `govkb.home` view contribution and provider registration while retaining existing tree views and commands. If icon polish causes confusing labels, revert only `views/*.ts` and `simpleTree.ts`. Python CLI behavior is not changed in the planned first implementation, so rollback should not affect governed packages.

## 11. Open Questions

- Should GovKB Home be the first view in the activity container or an explicit separate view after Status?
- Should the dashboard include a Git handoff button, or only text that commit is required?
- Should Home render report/digest markdown inline or show summaries with open-file actions only in the first slice?

## 12. Ready Checklist

- [x] Requirements are mapped to use cases.
- [x] Existing code inventory is path-based.
- [x] Implementation phases preserve CLI mutation boundary.
- [x] Tests are identified by module.
- [x] Rollback is explicit.
- [x] Plan review approved.
