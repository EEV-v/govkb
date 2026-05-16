# VS Code Guided Daily Workflow UI - Implementation Context

Last updated: 2026-05-16

## Objective

Create a guided GovKB extension experience that turns the existing setup, apply, learning, promotion, report, candidate, and governed skill commands into a clear everyday workflow. The first implementation should add a Home surface and tighten existing native views without weakening the CLI-first governance boundary.

## Source Artifacts

- `docs/governed-skill-knowledge-framework/features/vscode-guided-daily-workflow-ui/business.md` defines the stakeholder need.
- `README.md` describes GovKB as repo-native governed knowledge tooling and lists current CLI and VS Code extension scope.
- `docs/README.md` maps feature delivery documentation roots.
- `docs/governed-skill-knowledge-framework/features/vscode-extension-public-distribution/**` documents the initial extension delivery model.
- `docs/governed-skill-knowledge-framework/features/vscode-learning-discovery-progress/**` documents the current learning inventory and progress UX.
- `docs/governed-skill-knowledge-framework/features/governed-skill-management-ux/**` documents the current capability management UX.
- No repo-local instruction file was found during this feature start; active session and cookbook instructions apply.

## Existing Patterns

| Pattern Type | Existing Example | Location | Reuse? |
|---|---|---|---|
| Extension command contribution | Commands, titles, icons, activation events, and views | `vscode-extension/package.json` | Reuse and add commands/view contributions. |
| Tree provider | Generic row-to-TreeItem adapter | `vscode-extension/src/views/simpleTree.ts` | Extend to support icons where tree rows remain useful. |
| Status rows | Compact status and action summaries | `vscode-extension/src/views/statusView.ts` | Reuse logic for Home project summary. |
| Learning rows | Next-step learning and promotion summary | `vscode-extension/src/views/learningView.ts` | Reuse as the source of daily-flow state rules. |
| Promotion lifecycle rows | Grouped promotions and finalized detection | `vscode-extension/src/views/promotionsView.ts` | Reuse grouping and pending-commit logic. |
| CLI orchestration | Flow functions wrap CLI commands and parse JSON | `vscode-extension/src/flows.ts` | Reuse; Home must call flows rather than shell directly. |
| Runtime and settings | Resolved settings and runtime discovery | `vscode-extension/src/settings.ts`, `vscode-extension/src/runtimeDiscovery.ts` | Reuse for dashboard commands. |
| JSON parsing | Defensive payload validators | `vscode-extension/src/jsonParsers.ts` | Reuse for Home input validation. |
| Progress parsing | JSONL learning progress reducer | `vscode-extension/src/learningProgress.ts` | Reuse for Home progress state. |
| Capability management CLI | List, rename, merge, conversion | `src/govkb/commands/capabilities.py`, `src/govkb/core/capability_management.py`, `src/govkb/core/skill_conversion.py` | Reuse as mutation backend. |
| Extension tests | Node test suite for commands, parsers, flows, views | `vscode-extension/src/test/suite/*.test.ts` | Add Home model/provider tests. |
| Python tests | Direct function tests with temp dirs | `tests/*.py` | Add scaffolds only unless CLI contracts change. |

## Proposed New Components

| Component | Purpose | Notes |
|---|---|---|
| `vscode-extension/src/homeState.ts` | Derive one next action and dashboard sections from status, learning inventory, reports, candidates, and promotions. | Pure TypeScript model, heavily tested. |
| `vscode-extension/src/homeWebview.ts` | Render GovKB Home as a Webview View and receive command messages. | Must keep CSP tight and use VS Code theme variables. |
| `vscode-extension/src/views/actionIcons.ts` | Centralize `ThemeIcon` or codicon ids for repeated GovKB actions. | Shared by Tree rows and Home message metadata. |
| `govkb.home` view contribution | First-class Home surface in the GovKB activity container. | Should appear before Status. |
| `tests/test_vscode_guided_daily_workflow_ui_*.py` | Cookbook scaffolds for traceable use cases. | Skipped until implementation needs Python CLI changes. |

## Data Flow

1. Extension selects the active GovKB project root through the existing project selection helper.
2. Extension refreshes status, learning inventory, promotions, reports, and candidates through existing CLI-backed flows.
3. `homeState.ts` converts those payloads into a deterministic dashboard model with a primary next action.
4. `homeWebview.ts` renders the model and sends command messages back to the extension host.
5. The extension host executes existing commands such as `govkb.discoverLearning`, `govkb.reviewLearningDryRun`, `govkb.finalizeAcceptedPromotion`, or `govkb.convertSkillToGoverned`.
6. Mutating operations continue to run through CLI flows and refresh derived dashboard state after completion.

## Domain Entities

- Project status payload from `govkb status --json`.
- Learning inventory payload from `govkb review-memory --inventory-json`.
- Learning progress state from `review-memory --progress-jsonl`.
- Promotion summary from `govkb promotions list --json`.
- Candidate summary from `govkb candidates list --json`.
- Report summary from local project-scoped report discovery.
- Dashboard action, section, badge, and command message.

## Command Map

| Task | Command | Working Dir | Preconditions |
|---|---|---|---|
| Run extension unit tests | `npm test` | `vscode-extension` | Node dependencies installed. |
| Compile extension | `npm run compile` | `vscode-extension` | Node dependencies installed. |
| Run Python tests | `PYTHONPATH=src <python3.11+> -m unittest discover -s tests -v` | repo root | Python satisfies `requires-python >=3.11`. |
| Show CLI help | `PYTHONPATH=src <python3.11+> -m govkb.cli --help` | repo root | Python satisfies `requires-python >=3.11`. |
| Validate target project | `PYTHONPATH=src <python3.11+> -m govkb.cli validate <project-root>` | repo root | Target has `.governed`. |
| Preview Codex apply | `PYTHONPATH=src <python3.11+> -m govkb.cli apply codex --project-root <project-root> --codex-home <temp-codex-home> --preview` | repo root | Target has `.governed`. |

## APIs And CLI Surface

No new CLI mutation surface is required for the first Home implementation. The extension should reuse existing commands and flows. New TypeScript commands may be added for Home-specific actions such as opening the Home view or refreshing all dashboard data.

## Storage

The Home model is transient extension state. It may cache the latest loaded payloads in memory only. Durable state remains in `.governed/**`, `$CODEX_HOME/memories/govkb/**`, generated reports, and existing install-state files controlled by the CLI.

## Security And Governance

- The Home webview must not expose raw session transcript text.
- The webview must not use remote scripts, inline unsafe code without nonce controls, or arbitrary file access.
- The extension must not write `.governed/**` or `$CODEX_HOME/**` directly.
- Report and digest links must come from validated project-scoped paths.
- Tests must use synthetic fixtures and temporary roots.

## Tests

- TypeScript tests should cover model derivation, command routing, duplicate/finalized promotion display, icon metadata, and HTML snapshot sanity.
- Existing extension host tests should include the new Home command/view contribution.
- Python unittest scaffolds trace the feature use cases but can remain skipped until a CLI contract changes.
- Full verification remains `PYTHONPATH=src <python3.11+> -m unittest discover -s tests -v` and `npm test`.

## Observability

- Existing output channel remains the detailed log.
- Home should show compact operation progress and provide an "Open output" action.
- Long-running commands should continue to use `withProgress`.
- Dashboard refresh failures should produce visible blockers with concise details.

## Open Questions

| # | Question | Blocking? | Owner |
|---|---|---|---|
| 1 | Should GovKB Home replace the Status tree as the first view, or be added above it? | No | Engineering |
| 2 | Should Home use only VS Code native codicons, or include a small custom icon set? | No | Engineering |
| 3 | Should commit detection remain advisory, or should the UI offer a Git extension handoff button? | No | Engineering |

## Assumptions

| # | Assumption | Risk If Wrong |
|---|---|---|
| 1 | A Webview View is acceptable for richer workflow UX. | If not, Tree View polish will be the main path and layout will remain constrained. |
| 2 | Existing CLI flows provide enough data for Home without new Python commands. | If not, a later phase must add read-only JSON contracts. |
| 3 | The user wants guided flow over command density. | If wrong, Home may hide useful advanced actions; keep Tree Views available. |

## Traceability

| Context Section | business.md Source |
|---|---|
| Objective | Stakeholder Need, Success Criteria |
| Existing Patterns | Constraints |
| Proposed New Components | Success Criteria |
| Data Flow | Success Criteria, Constraints |
| Security And Governance | Constraints, Non-Goals |
| Tests | Success Criteria, Constraints |
