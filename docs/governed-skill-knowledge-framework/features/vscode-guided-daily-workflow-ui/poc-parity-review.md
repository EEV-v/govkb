# VS Code Guided Daily Workflow UI - PoC Parity Review

Last updated: 2026-05-16

## Verdict

Ready for Merge: Yes

## Summary

The implementation matches the accepted PoC direction: the extension now has a first-class Home view, derives one primary next action from existing GovKB state, keeps mutating operations routed through existing CLI-backed commands, collapses duplicate promotion review worktrees in the native view layer, and exposes picker-driven governed skill management from the guided workflow. Manual QA against the real Clearing workspace found and fixed two first-use issues: the Home contribution needed to be registered as a webview view, and the primary next action needed to appear above the status badge grid so it is visible in the normal side bar height. The implementation remains additive and preserves existing tree views.

## Requirement Parity

| Requirement | PoC Assertion | Implementation Evidence | Result | Notes |
|---|---|---|---|---|
| REQ-VGDW-01 | A single primary action must be derived from current state. | `vscode-extension/src/homeState.ts`; `vscode-extension/src/test/suite/homeState.test.ts`. | PASS | Tests cover setup, apply, review digest, finalize, commit, dry-run, and apply-after-dry-run states. |
| REQ-VGDW-02 | Native tree views remain compact. | `vscode-extension/src/views/*.ts`; `vscode-extension/src/views/simpleTree.ts`; `vscode-extension/src/test/suite/views.test.ts`. | PASS | Rows now carry ThemeIcon metadata and clearer next-step labels. |
| REQ-VGDW-03 | Setup, apply, learning, promotion, finalize, commit, and apply-after-commit states are represented. | `homeState.ts`, `learningView.ts`, `promotionsView.ts`, and view tests. | PASS | Home and native views share promotion helper behavior. |
| REQ-VGDW-04 | UI uses icons and clear labels. | Home inline SVG icons, manifest command icons, and TreeRow ThemeIcons. | PASS | No remote web assets or third-party UI package added. |
| REQ-VGDW-05 | Promotion review is digest-first. | Home primary action and promotion rows open the digest; worktree open remains secondary. | PASS | Finalize is available only after acceptance. |
| REQ-VGDW-06 | Skill management is picker-driven. | Home actions call existing conversion, rename, and merge commands; conversion picker has explicit manual fallback. | PASS | Manual entry remains available but is not the default path. |
| REQ-VGDW-07 | Already governed/materialized skills are hidden from conversion picker. | `vscode-extension/src/localSkills.ts`; `vscode-extension/src/test/suite/localSkills.test.ts`. | PASS | Existing governed source skills and materialized GovKB skills are filtered. |
| REQ-VGDW-08 | Stale or duplicate worktrees are collapsed. | `promotionGroups` and promotion view tests. | PASS | Equivalent review worktrees show as hidden duplicates instead of separate primary actions. |
| REQ-VGDW-09 | Mutations go through CLI-backed commands. | `extension.ts` Home action dispatch executes contributed commands only. | PASS | No direct repository mutation was added to the webview. |
| REQ-VGDW-10 | Raw transcript and local assistant state stay out of UI fixtures. | Tests use synthetic status, inventory, report, and promotion payloads. | PASS | Feature docs contain summarized requirements, not raw transcripts. |

## Scenario Parity

| Scenario | Test/Verification | Result | Notes |
|---|---|---|---|
| UC-1 First-open guided Home | `homeState.test.ts`, `homeWebview.test.ts`, packaging tests. | PASS | Home renders setup when no status is loaded. |
| UC-2 Setup/apply guidance | `homeState.test.ts`. | PASS | Stale materialized skills guide to one-click apply. |
| UC-3 Learning review from daily flow | `homeState.test.ts`, `learningView` tests. | PASS | Productive dry runs guide to apply; inventory guides to dry run. |
| UC-4 Promotion review/finalize | `homeState.test.ts`, `views.test.ts`. | PASS | Ready, accepted, and applied states have distinct next steps. |
| UC-5 Applied changes need commit | `homeState.test.ts`, `views.test.ts`. | PASS | Commit prompt appears only when active governed paths overlap the applied promotion. |
| UC-6 Picker-driven skill management | `localSkills.test.ts`, `homeWebview.test.ts`. | PASS | Home exposes convert, rename, and merge without requiring typed skill names by default. |
| UC-7 Compact native tree views | `views.test.ts`. | PASS | Icon metadata and concise labels are covered. |
| UC-8 Governance boundary | `homeWebview.test.ts`, command routing review. | PASS | Webview emits action messages that route to commands. |
| UC-9 Primary action by state | `homeState.test.ts`. | PASS | Table-style state cases are covered. |
| Manual Clearing Home smoke | VS Code Extension Development Host opened on `/Users/vasilevevgeny/code/Etna/Clearing` with the local GovKB extension. | PASS | Home rendered current Clearing state, surfaced `Review next learning batch` as the first visible action, and showed candidates/promotions/reports without mutating the project. |
| Manual Clearing conversion picker smoke | Clicked `Convert one skill` in the Clearing dev host and dismissed the picker without selection. | PASS | Picker showed only non-governed local skills and manual fallback; existing governed Clearing skills and already converted materialized skills were absent. |

## Command Evidence

| Command | Working Dir | Result | Evidence |
|---|---|---|---|
| `git diff --check` | `/Users/vasilevevgeny/code/govkb` | PASS | No whitespace errors. |
| `npm test` | `/Users/vasilevevgeny/code/govkb/vscode-extension` | PASS | 107 extension tests passed. |
| `npm run test:host` | `/Users/vasilevevgeny/code/govkb/vscode-extension` | PASS | Extension host exited with code 0. |
| `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src /Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest discover -s tests -v` | `/Users/vasilevevgeny/code/govkb` | PASS | 164 Python tests passed, 33 skipped scaffold tests. |
| VS Code Extension Development Host manual QA | `/Users/vasilevevgeny/code/govkb` | PASS | Isolated dev host launched on Clearing with `--extensionDevelopmentPath`; CDP inspection confirmed Home webview content and conversion picker filtering. |

## Deviations

| Deviation | Approved? | Reason | Follow-up |
|---|---|---|---|
| In-webview failure cards are deferred. | Yes | Existing command progress and output handling already report failures; first slice focuses on next-action clarity and command routing. | Add inline failure cards if users still need fewer trips to Output. |
| Git commit automation is not implemented. | Yes | Finalization intentionally applies changes without committing so the project keeps normal Git review semantics. | Consider a Git API affordance only after Home state proves stable. |
| Python use-case tests remain skipped scaffolds. | Yes | This slice changes the VS Code extension, not Python CLI semantics. | Convert selected scaffolds to executable integration tests if CLI behavior changes. |

## Risks

The main residual risk is secondary-section density inside the Home webview. The primary action is now visible at the top of the normal side bar pane, but the secondary workflow sections still expose several controls because the feature intentionally keeps setup, learning, promotion, reports, and skill management discoverable in one place.

## Required Fixes Before Merge

None.

## Post-merge Follow-ups

- Manually inspect stale, ready-for-review, accepted, and applied-pending-commit fixture states inside VS Code after the first Clearing current-state smoke.
- Consider inline failure summaries in the Home webview after the first real user pass.
- Consider a dedicated Git handoff action if normal VS Code Source Control is still too indirect after finalization.
