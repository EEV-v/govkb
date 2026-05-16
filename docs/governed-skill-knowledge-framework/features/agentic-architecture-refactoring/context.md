# Agentic Architecture Refactoring - Implementation Context

Last updated: 2026-05-16

## Objective

Refactor GovKB's agentic-app architecture so everyday flows are easier to reason about, safer to rerun, and less likely to drift between CLI state, VS Code state, local Codex materialization, and isolated review worktrees. The feature translates safe structural practices observed in `/Users/vasilevevgeny/code/caveman` into GovKB-specific architecture docs, action registries, lifecycle guards, cleanup flows, and tests.

## Source Artifacts

- `business.md` in this feature folder.
- `README.md`, which identifies GovKB as repo-native governed knowledge tooling and lists current CLI and VS Code scope.
- `docs/README.md`, which identifies feature docs and cookbook prompts.
- `docs/governed-skill-knowledge-framework/features/vscode-guided-daily-workflow-ui/*`, especially the Home/next-action UI plan.
- Caveman repository evidence inspected outside GovKB:
  - `/Users/vasilevevgeny/code/caveman/CLAUDE.md`
  - `/Users/vasilevevgeny/code/caveman/bin/install.js`
  - `/Users/vasilevevgeny/code/caveman/bin/lib/settings.js`
  - `/Users/vasilevevgeny/code/caveman/bin/lib/openclaw.js`
  - `/Users/vasilevevgeny/code/caveman/tests/installer/e2e.dryrun.test.mjs`
- No repo-local `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`, or `.cursorrules` file was found in the GovKB repository root during discovery; active session instructions apply.

## Existing Patterns

| Pattern Type | Existing Example | Location | Reuse? |
|---|---|---|---|
| CLI command boundary | Commands delegate to `src/govkb/commands/*` and core modules. | `src/govkb/cli.py`, `src/govkb/commands/` | Reuse. Keep mutation here. |
| Promotion lifecycle metadata | Sidecar metadata records ready, accepted, applied, rejected, and archived states. | `src/govkb/core/promotion_lifecycle.py` | Extend with idempotent rerun and cleanup semantics. |
| Promotion listing and details | Machine-readable payloads expose worktree paths, digest paths, review, archive, and apply metadata. | `src/govkb/commands/promotions.py` | Reuse as API surface for VS Code. |
| Skill conversion preview/write | Conversion plan is non-mutating until `--write`, validates strict package rules, and removes failed packages. | `src/govkb/core/skill_conversion.py`, `src/govkb/commands/convert.py` | Reuse; improve UX and idempotency around existing converted/governed detection. |
| VS Code Home next-action model | A pure model derives primary actions from status, inventory, run, and promotions. | `vscode-extension/src/homeState.ts` | Reuse, but centralize action metadata. |
| VS Code command orchestration | Extension registers commands and invokes CLI-backed flows. | `vscode-extension/src/extension.ts`, `vscode-extension/src/flows.ts` | Reuse; reduce repeated labels and preconditions. |
| Tree view row models | Rows carry labels, descriptions, commands, context values, and icons. | `vscode-extension/src/views/*.ts`, `vscode-extension/src/views/simpleTree.ts` | Reuse; consume centralized action metadata where useful. |
| Extension manifest | Command ids, titles, icons, menu placement, views, and settings live in one VS Code manifest. | `vscode-extension/package.json` | Keep as VS Code contribution source, but verify against typed action registry. |
| Python temp-dir tests | CLI tests build project roots, Codex homes, and git repos in temporary directories. | `tests/test_promotions.py`, `tests/test_skill_conversion.py` | Reuse for lifecycle and cleanup tests. |
| Extension Node tests | Pure model and package contribution tests run under Node after TypeScript compile. | `vscode-extension/src/test/suite/*.test.ts` | Reuse for action registry and UI state tests. |

## Proposed New Components

| Component | Purpose | Notes |
|---|---|---|
| `docs/governed-skill-knowledge-framework/architecture/agentic-state-ownership.md` | Human-maintained source-of-truth and derived-artifact map. | New documentation artifact; no runtime behavior. |
| `vscode-extension/src/actionRegistry.ts` | Typed registry for action ids, labels, icons, command ids, user-facing descriptions, and preconditions. | New extension module; Home and tree views consume it gradually. |
| `vscode-extension/src/stateNarrative.ts` | Small pure helpers for user-facing next-step summaries and "done" states. | Optional if `homeState.ts` grows too large. |
| `src/govkb/core/promotion_cleanup.py` | Side-effect-aware helpers for stale/duplicate promotion cleanup preview and apply. | Only if existing `promotions.py` becomes too large. |
| `src/govkb/commands/promotions.py` cleanup subcommand | CLI entry point for `promotions cleanup --preview` and `--apply`. | Keeps VS Code mutation boundary CLI-backed. |
| `tests/test_agentic_architecture_refactoring_use_cases.py` | Python scenario coverage for promotion cleanup and idempotency. | Use temp dirs and synthetic fixtures. |
| `vscode-extension/src/test/suite/actionRegistry.test.ts` | Tests command metadata, manifest parity, and Home/tree action consistency. | Node test, no VS Code host required. |

## Data Flow

1. Project source state lives under `.governed/**` in the active repository.
2. CLI status, promotions, candidates, and review-memory commands read project source and assistant-local state.
3. `$CODEX_HOME/skills/**` contains materialized Codex skills derived from `.governed/**`.
4. `$CODEX_HOME/memories/govkb/worktrees/<project>/<runId>/` contains isolated promotion review worktrees.
5. `$CODEX_HOME/memories/govkb/promotions/<project>/<runId>.json` contains promotion lifecycle metadata.
6. The VS Code extension reads CLI JSON payloads and derives transient UI state.
7. User actions in VS Code invoke CLI-backed commands or existing extension flow wrappers; the extension does not directly mutate `.governed/**` or `$CODEX_HOME/**`.

## Domain Entities

| Entity | Meaning |
|---|---|
| Governed project | Repository root with `.governed/project.toml` and capabilities. |
| Governed capability | Source package under `.governed/capabilities/<id>/`. |
| Materialized skill | Derived Codex skill under `$CODEX_HOME/skills/govkb-...`. |
| Local source skill | Existing non-governed Codex skill eligible for conversion. |
| Promotion worktree | Isolated git worktree created for reviewing learned memory updates. |
| Promotion metadata | Sidecar JSON lifecycle record for review, apply, archive, and cleanup states. |
| Action registry item | One logical user action with command, icon, label, visibility, and preconditions. |
| Derived UI state | Non-authoritative VS Code model built from CLI JSON and report discovery. |

## Command Map

| Task | Command | Working Dir | Preconditions |
|---|---|---|---|
| Full Python regression | `PYTHONPATH=src python3 -m unittest discover -s tests -v` | Repo root | Python 3.11+ and repo checkout. |
| CLI help | `PYTHONPATH=src python3 -m govkb.cli --help` | Repo root | Python 3.11+ and repo checkout. |
| Show project status | `PYTHONPATH=src python3 -m govkb.cli status <project-root> --codex-home <codex-home> --json` | Repo root | Valid governed project. |
| List promotions | `PYTHONPATH=src python3 -m govkb.cli promotions list <project-root> --codex-home <codex-home> --json` | Repo root | Optional existing promotion worktrees. |
| Show promotion | `PYTHONPATH=src python3 -m govkb.cli promotions show <run-id> --project-root <project-root> --codex-home <codex-home> --json` | Repo root | Existing promotion id or path. |
| Apply accepted promotion | `PYTHONPATH=src python3 -m govkb.cli promotions apply <run-id> --project-root <project-root> --codex-home <codex-home>` | Repo root | Promotion state accepted. |
| Preview skill conversion | `PYTHONPATH=src python3 -m govkb.cli convert skill <skill> --project-root <project-root> --codex-home <codex-home> --json` | Repo root | Source skill exists. |
| Extension tests | `npm test` | `vscode-extension` | Node dependencies installed. |
| Extension host smoke | `npm run test:host` | `vscode-extension` | VS Code test dependencies installed. |

## APIs And CLI Surface

Existing surfaces should stay stable:

- `govkb status ... --json`
- `govkb promotions list ... --json`
- `govkb promotions show ... --json`
- `govkb promotions mark-reviewed ...`
- `govkb promotions apply ...`
- `govkb promotions archive ...`
- `govkb convert skill ... --json`

Potential new CLI surface:

- `govkb promotions cleanup <project-root> --codex-home <path> --preview --json`
- `govkb promotions cleanup <project-root> --codex-home <path> --apply --json`

Cleanup is project-scoped, so it may follow the existing `promotions list <project-root>` positional project-root shape. Existing per-promotion actions must keep the current parser contract: promotion id or path first, with `--project-root` as an option.

Potential internal extension API:

- `actionRegistry.ts` exports immutable action definitions.
- Home and tree rows reference action ids rather than duplicating user-facing labels.

## Storage

| Store | Authority | Notes |
|---|---|---|
| `.governed/**` | Source of truth | Project-owned governed package source. |
| `.governed/reports/**` | Repo audit artifact | Generated reports can be committed when useful. |
| `$CODEX_HOME/skills/**` | Derived local output | Rebuilt by apply; not source. |
| `$CODEX_HOME/memories/govkb/promotions/**` | Lifecycle sidecar | Records review/apply/archive/cleanup states and is retained as compact audit metadata after cleanup. |
| `$CODEX_HOME/memories/govkb/worktrees/**` | Review artifact | Disposable after finalize/archive/cleanup. |
| VS Code workspace state | UI convenience | Stores selected project root and transient preferences only. |
| Test temp dirs | Disposable | Required for regression tests touching filesystem state. |

## Security And Governance

- No raw assistant session transcripts should be written to new docs or test fixtures.
- Cleanup commands must not delete outside the computed promotions root.
- Preview mode must not mutate project roots, Codex homes, worktrees, or lifecycle metadata.
- VS Code must call CLI commands for mutation and should present destructive cleanup as explicit preview/apply.
- Path handling should resolve and compare roots before removing worktrees or metadata.
- Cleanup apply must delete only eligible promotion worktrees and, when needed, safe generated promotion report copies. It must not delete sidecar lifecycle metadata. Instead, it marks metadata with a `cleanup` block containing `cleanedAt`, `removedPaths`, and `reason`.

## Tests

| Area | Existing Pattern | Proposed Coverage |
|---|---|---|
| Promotion lifecycle | `tests/test_promotions.py` | Idempotent accept/finalize/archive and cleanup preview/apply. |
| Skill conversion | `tests/test_skill_conversion.py` | Already governed/materialized exclusion and failed-write cleanup remain covered. |
| Extension action state | `vscode-extension/src/test/suite/homeState.test.ts` | Action registry parity and next-action labels. |
| Extension packaging | `vscode-extension/src/test/suite/packaging.test.ts` | Manifest command/icon parity with registry. |
| Tree view summaries | `vscode-extension/src/test/suite/views.test.ts` | Stale/duplicate compaction and icon metadata. |

## Observability

- CLI JSON payloads should report state, next safe action, affected files, and whether an operation was a no-op.
- VS Code output channel should include the exact CLI command and exit code.
- Home UI should show concise next-step state and link to detailed output for troubleshooting.

## Open Questions

| # | Question | Blocking? | Owner |
|---|---|---|---|
| 1 | Should cleanup remove sidecar lifecycle metadata for archived/applied promotions, or keep metadata while deleting worktrees? Decision: keep sidecar metadata and mark it cleaned; remove only eligible worktrees and safe generated report copies. | No | Product/engineering |
| 2 | Should `actionRegistry.ts` be source of truth for `package.json` command titles, or should tests only verify parity with the manifest? | No | Engineering |
| 3 | Should human-facing governed skill summaries live in `capability.contract.toml`, a new `README.md`, or be derived from existing `name` and `description` fields? | Yes for REQ-AAR-07 | Product/engineering |

## Assumptions

| # | Assumption | Risk If Wrong |
|---|---|---|
| 1 | Existing CLI JSON payloads are acceptable as the primary extension data contract. | Refactor may need broader command changes. |
| 2 | Users prefer explicit preview/apply cleanup over automatic deletion. | Cleanup UX may remain too manual. |
| 3 | Manifest parity tests are enough to prevent most action-label drift. | Some view-specific labels may still diverge. |

## Traceability

| Context Section | business.md Source |
|---|---|
| Existing Patterns | Business Goals, Requirements REQ-AAR-01 through REQ-AAR-08 |
| Proposed New Components | Requirements REQ-AAR-01 through REQ-AAR-08 |
| Data Flow | Constraints |
| Security And Governance | Non-Goals, Constraints |
| Tests | REQ-AAR-08 |
