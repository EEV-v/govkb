# Agentic Architecture Refactoring - Implementation Plan

Last updated: 2026-05-16

## 0. Existing Code Inventory

| Category | Component | Location | Reuse Strategy |
|---|---|---|---|
| CLI parser | Top-level command dispatch and subparser wiring | `src/govkb/cli.py` | Add only minimal promotion cleanup command wiring if required. |
| Promotion command | List, show, mark-reviewed, apply, archive | `src/govkb/commands/promotions.py` | Extend with cleanup preview/apply while preserving existing actions. |
| Promotion lifecycle | Sidecar metadata state helpers | `src/govkb/core/promotion_lifecycle.py` | Add no-op/idempotency helpers or cleanup metadata helpers if needed. |
| Promotion adapter | Auto-promotion and isolated worktree creation | `src/govkb/adapters/codex/promote.py` | Reuse existing worktree layout and metadata paths. |
| Skill conversion | Conversion preview/write, safe copying, strict validation | `src/govkb/core/skill_conversion.py`, `src/govkb/commands/convert.py` | Preserve preview/write semantics; add tests only if filtering or summaries need CLI data. |
| Status payload | Project, validation, capabilities, install state, skill updates | `src/govkb/commands/status.py` | Reuse for UI state and pending-commit detection. |
| Extension manifest | Command ids, titles, icons, views, menu items | `vscode-extension/package.json` | Keep as VS Code contribution file; verify parity with registry. |
| Extension activation | Command registration, state refresh, webview provider | `vscode-extension/src/extension.ts` | Keep command wiring but reduce repeated metadata. |
| Home model | Pure next-action state | `vscode-extension/src/homeState.ts` | Consume action registry definitions and state narratives. |
| Promotion view | Grouping, duplicate hiding, pending-commit detection | `vscode-extension/src/views/promotionsView.ts` | Reuse grouping logic; improve stale/applied/archived labels. |
| Local skills | Discover and filter Codex skills for conversion | `vscode-extension/src/localSkills.ts` | Preserve default exclusion behavior. |
| Python tests | Promotion and conversion temp-dir coverage | `tests/test_promotions.py`, `tests/test_skill_conversion.py` | Extend for cleanup and idempotency. |
| Extension tests | Home, views, packaging, host smoke | `vscode-extension/src/test/suite/*.test.ts` | Add action registry parity and state narrative tests. |

## 0.5. Pre-flight Checklist

| Prerequisite | Status | Owner |
|---|---|---|
| Product decision on cleanup metadata retention | Decided: preserve sidecar metadata and mark cleaned while removing eligible worktrees | Product/engineering |
| Product decision on governed skill summary storage | Decided: derive first-pass UI summaries from existing status payload fields (`name`, `description`, aliases, lifecycle, memory, and migration fields) | Product/engineering |
| Existing Python tests pass before implementation | Verified during Phase 5 full regression | Engineering |
| Existing extension tests pass before implementation | Verified during Phase 5 extension regression | Engineering |
| Current VS Code UI feature changes are either merged or included in branch scope | Included in this feature scope | Engineering |

## 1. Scope And Boundaries

In scope:

- Add a GovKB architecture ownership document.
- Add a typed VS Code action registry and parity tests.
- Make accepted/applied/archived promotion operations visibly idempotent.
- Add promotion cleanup preview/apply for stale or duplicate review artifacts.
- Improve governed skill summaries and conversion action metadata.
- Add Python and TypeScript tests for no-write previews, idempotent reruns, and state consistency.

Out of scope:

- Automatic Git commits.
- Replacing CLI mutation with direct extension writes.
- Rewriting the full extension UI.
- Changing governed package contract semantics without a separate migration.
- Copying Caveman behavior, hooks, or installer design.

## 2. Requirements Mapping

| Requirement | Behavior | Location | New/Modify | Notes |
|---|---|---|---|---|
| REQ-AAR-01 | Document state ownership and mutation owners. | `docs/governed-skill-knowledge-framework/architecture/agentic-state-ownership.md` | New | First phase, no runtime risk. |
| REQ-AAR-02 | Centralize action metadata and verify manifest parity. | `vscode-extension/src/actionRegistry.ts`, tests | New/modify | Do not generate manifest initially. |
| REQ-AAR-03 | Rerunning lifecycle actions reports no-op states. | `src/govkb/commands/promotions.py`, `promotion_lifecycle.py`, extension labels | Modify | Add tests before exposing broader UI. |
| REQ-AAR-04 | Cleanup stale/duplicate worktrees through preview/apply. | `src/govkb/commands/promotions.py`, optional `promotion_cleanup.py` | New/modify | Must be preview-first. |
| REQ-AAR-05 | Preserve CLI mutation boundary. | `vscode-extension/src/extension.ts`, `flows.ts`, tests | Modify/test | Registry marks mutating actions as CLI-backed. |
| REQ-AAR-06 | Hide governed/materialized skills in conversion picker by default. | `localSkills.ts`, `extension.ts`, tests | Modify/test | Existing behavior should become explicit registry/test coverage. |
| REQ-AAR-07 | Show user-facing governed skill summaries. | `capabilitiesView.ts`, optional docs/contract update | Modify | Storage decision needed. |
| REQ-AAR-08 | Add dry-run/no-write/idempotency tests. | Python and TS tests | New/modify | Use temp dirs and synthetic payloads. |
| REQ-AAR-09 | Phase and rollback refactor. | This plan and implementation summaries | Documentation/test | Each phase has rollback. |

## 3. Design

### Architecture Ownership Map

Create `docs/governed-skill-knowledge-framework/architecture/agentic-state-ownership.md` with tables for:

- authoritative stores
- derived stores
- generated audit/report stores
- disposable review stores
- mutation owners
- cleanup policy
- test isolation policy

This mirrors the useful Caveman "what owns what" practice but uses GovKB domain entities.

### Action Registry

Create `vscode-extension/src/actionRegistry.ts` with a small stable model:

```ts
export type GovkbActionId = "setup" | "apply" | "discoverLearning" | "...";

export interface GovkbActionDefinition {
  id: GovkbActionId;
  command: string;
  label: string;
  description: string;
  icon: string;
  mutates: "none" | "project" | "codexHome" | "promotionMetadata" | "promotionWorktree";
  cliBacked: boolean;
}
```

The registry should not replace all command registration in one pass. First it should support:

- Home primary and secondary actions.
- Tree row command metadata for promotions, capabilities, candidates, and reports where labels overlap.
- Packaging tests that verify every registry command has a manifest contribution or is intentionally internal.

### Promotion Cleanup

Add cleanup planning helpers that:

1. Resolve the project id and promotions root using existing promotion helpers.
2. Build a list of promotion worktrees and metadata.
3. Classify artifacts as current, actionable, duplicate, applied, archived, missing metadata, or stale.
4. In preview mode, return JSON and text output with no writes.
5. In apply mode, remove only eligible worktrees under the computed root, optionally remove safe generated report copies whose only purpose was worktree review, and preserve sidecar lifecycle metadata.
6. Mark preserved metadata with a `cleanup` block containing `cleanedAt`, `removedPaths`, and `reason`, and set a terminal state such as `cleaned` so the default promotions list can hide it.

Safety rules:

- Never delete outside `$CODEX_HOME/memories/govkb/worktrees/<project>/`.
- Never delete ready or accepted promotions unless explicitly targeted and confirmed by command flags.
- Never touch `.governed/**` in cleanup.
- Never delete `$CODEX_HOME/memories/govkb/promotions/<project>/<run-id>.json`; preserved metadata is the audit record that explains why the worktree disappeared.

### State Narrative

Create pure helpers if needed:

- `promotionNextAction(promotion, status)`
- `skillUpdateNarrative(status)`
- `cleanupNarrative(payload)`

These helpers keep user-facing next-step wording out of command handlers.

### Governed Skill Summaries

First slice should use existing capability fields:

- `name`
- `description`
- `aliases`
- `lifecycleState`
- `migrationStatus`

If that is insufficient, add a follow-up decision to store an optional `README.md` or `summary` field in the capability contract.

## 4. Integration Points

| Integration | Contract |
|---|---|
| `src/govkb/cli.py` | Add cleanup subcommand only after core helper tests pass. |
| `src/govkb/commands/promotions.py` | Add cleanup JSON/text entry point. Existing list/show/apply/archive behavior remains stable. |
| `src/govkb/core/promotion_lifecycle.py` | Add idempotent state helpers only if command code would otherwise duplicate logic. |
| `vscode-extension/src/actionRegistry.ts` | New source for extension action metadata. |
| `vscode-extension/src/homeState.ts` | Consume registry actions and keep state selection pure. |
| `vscode-extension/src/views/*.ts` | Use registry metadata where it reduces duplicate labels/icons. |
| `vscode-extension/package.json` | Continue declaring VS Code commands and menus; tests enforce parity. |
| `docs/governed-skill-knowledge-framework/architecture/` | New docs folder for cross-feature architecture ownership. |

## 5. Application Logic

1. Build ownership map as documentation before runtime changes.
2. Add action registry with no behavior change, then update Home and selected tree views to consume it.
3. Add registry/package parity tests and update existing Home/view tests.
4. Add promotion cleanup planner with pure classification tests.
5. Add CLI cleanup preview and apply commands.
6. Add VS Code action for cleanup preview/open output only after CLI tests pass.
7. Improve promotion and skill summaries using state narrative helpers.
8. Add implementation summaries per phase.

## 6. Data Consistency And Safety

- Preview commands must not write files, lifecycle metadata, or reports.
- Cleanup apply must use resolved paths and root containment checks.
- Idempotent actions should return success with an explanatory no-op state when the desired state already exists.
- Extension actions marked as mutating must map to CLI-backed commands or existing flow wrappers.
- Tests must use temporary project roots and Codex homes.
- No raw transcript text may appear in fixtures or docs.

## 7. Testing Strategy

| Test Type | Location | Coverage |
|---|---|---|
| Ownership doc smoke | `tests/test_agentic_architecture_refactoring_smoke.py` | Required stores and mutation owners documented. |
| Promotion cleanup unit/workflow | `tests/test_agentic_architecture_refactoring_use_cases.py` | Preview no-write, apply scoped removal, idempotent rerun. |
| Promotion lifecycle regression | `tests/test_promotions.py` | Reapply accepted/applied promotion no-op semantics. |
| Action registry unit | `vscode-extension/src/test/suite/actionRegistry.test.ts` | Action ids, command ids, icons, mutation flags. |
| Manifest parity | `vscode-extension/src/test/suite/packaging.test.ts` | Registry commands have manifest entries or explicit internal exemption. |
| Home state regression | `vscode-extension/src/test/suite/homeState.test.ts` | Primary action states remain correct after registry refactor. |
| View summary regression | `vscode-extension/src/test/suite/views.test.ts` | Promotion and governed skill summaries stay readable. |

## 8. Verification Commands

| Command | Working Dir | Purpose | Preconditions |
|---|---|---|---|
| `git diff --check` | Repo root | Whitespace safety. | None. |
| `PYTHONPATH=src python3 -m unittest discover -s tests -v` | Repo root | Full Python regression. | Python 3.11+. |
| `npm test` | `vscode-extension` | TypeScript compile and Node tests. | Node dependencies installed. |
| `npm run test:host` | `vscode-extension` | Extension host smoke if manifest/view behavior changed. | VS Code test runtime available. |
| `PYTHONPATH=src python3 -m govkb.cli promotions cleanup <project-root> --codex-home <tmp-home> --preview --json` | Repo root | Manual cleanup preview validation after implementation. | Disposable project fixture. |

## 9. Implementation Phases

### Phase 0 - Shape And Contracts

Scope:

- Add architecture ownership documentation.
- Add skipped or active smoke tests for the documentation.
- Add implementation summary for the docs-only phase.

Files:

- `docs/governed-skill-knowledge-framework/architecture/agentic-state-ownership.md`
- `tests/test_agentic_architecture_refactoring_smoke.py`
- `docs/governed-skill-knowledge-framework/features/agentic-architecture-refactoring/implementation-summary-phase-0.md`

Verify:

- `PYTHONPATH=src python3 -m unittest tests.test_agentic_architecture_refactoring_smoke -v`

Rollback:

- Remove the new architecture doc, smoke test, and implementation summary.

### Phase 1 - Action Registry And Extension Parity

Scope:

- Add typed action registry.
- Refactor Home primary and secondary action construction to use registry metadata.
- Add registry/manifest parity tests.
- Keep existing command ids and VS Code contributions stable.

Files:

- `vscode-extension/src/actionRegistry.ts`
- `vscode-extension/src/homeState.ts`
- `vscode-extension/src/views/*.ts` only where labels are currently duplicated.
- `vscode-extension/src/test/suite/actionRegistry.test.ts`
- `vscode-extension/src/test/suite/homeState.test.ts`
- `vscode-extension/src/test/suite/packaging.test.ts`

Verify:

- `npm test`

Rollback:

- Revert registry file and restore direct action construction from previous tests.

### Phase 2 - Promotion Lifecycle Idempotency

Scope:

- Add explicit no-op handling for already accepted, rejected, archived, or applied promotions.
- Ensure repeated finalize/apply reports clear text/JSON and does not hang the extension progress state.
- Add tests using temporary project roots and Codex homes.

Files:

- `src/govkb/commands/promotions.py`
- `src/govkb/core/promotion_lifecycle.py` if helper extraction is warranted.
- `tests/test_promotions.py`
- `vscode-extension/src/views/promotionsView.ts`
- `vscode-extension/src/homeState.ts`

Verify:

- `PYTHONPATH=src python3 -m unittest tests.test_promotions -v`
- `npm test`

Rollback:

- Revert no-op behavior and related UI labels/tests.

### Phase 3 - Promotion Cleanup Preview And Apply

Scope:

- Add cleanup planner and CLI subcommand.
- Support JSON/text preview with no writes.
- Support apply for eligible stale/duplicate/applied/archived artifacts after policy decision.
- Add VS Code action only after CLI behavior is stable.

Files:

- `src/govkb/core/promotion_cleanup.py` if added.
- `src/govkb/commands/promotions.py`
- `src/govkb/cli.py`
- `tests/test_agentic_architecture_refactoring_use_cases.py`
- `vscode-extension/package.json`
- `vscode-extension/src/actionRegistry.ts`
- `vscode-extension/src/extension.ts`
- `vscode-extension/src/views/promotionsView.ts`

Verify:

- `PYTHONPATH=src python3 -m unittest tests.test_agentic_architecture_refactoring_use_cases -v`
- `PYTHONPATH=src python3 -m unittest discover -s tests -v`
- `npm test`
- `npm run test:host` if new VS Code command contribution is added.

Rollback:

- Remove cleanup command wiring, helper, tests, and extension action contribution.

### Phase 4 - Governed Skill Summary And Conversion UX

Scope:

- Improve governed skill view summaries using existing capability payload fields first.
- Strengthen conversion picker tests for already governed/materialized exclusion and manual fallback.
- Decide whether a dedicated summary artifact is needed after evaluating existing fields.

Files:

- `vscode-extension/src/views/capabilitiesView.ts`
- `vscode-extension/src/extension.ts`
- `vscode-extension/src/localSkills.ts`
- `vscode-extension/src/test/suite/views.test.ts`
- `vscode-extension/src/test/suite/localSkills.test.ts` if new test module is useful.

Verify:

- `npm test`

Rollback:

- Revert UI summary and picker changes; no CLI data migration expected.

### Phase 5 - Docs, Rollout, And Manual QA

Scope:

- Update feature implementation summaries.
- Run full regression.
- Package VSIX if extension behavior changed.
- Manually QA on a disposable or known-safe governed project.

Files:

- Feature implementation summaries.
- Optional release notes/sign-off artifacts if requested.

Verify:

- `git diff --check`
- `PYTHONPATH=src python3 -m unittest discover -s tests -v`
- `npm test`
- `npm run test:host`
- Manual VS Code Extension Development Host QA against a governed project.

Rollback:

- Reinstall previous VSIX or revert feature branch.

## 10. Rollback Plan

- Docs-only phase: delete new docs and tests.
- Extension registry phase: revert registry consumption and restore existing Home/view action construction.
- CLI lifecycle phase: revert `promotions.py` and lifecycle helper changes; sidecar metadata schema remains compatible because no new required fields should be introduced.
- Cleanup phase: remove cleanup command and helper; no source project files are changed by cleanup tests.
- UI summary phase: revert view label changes; no project data migration.

## 11. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| 1 | Should cleanup preserve metadata after deleting a stale worktree? Decision: yes. Preserve sidecar metadata, add cleanup details, and hide cleaned records from the default actionable list. | Product/engineering | Resolved |
| 2 | Should registry drive manifest generation or stay test-verified against `package.json`? Decision: keep `package.json` as the VS Code contribution source and enforce parity with registry tests. Full tree-view metadata consolidation is non-blocking follow-up. | Engineering | Resolved |
| 3 | Should governed skill summaries be contract fields, README files, or derived UI summaries? Decision: derive summaries from existing status payload fields until a concrete data gap requires a new persisted contract field. | Product/engineering | Resolved |

## 13. Phase 5 Completion Status

Phase 5 completed the merge gate without adding new runtime contracts. The remaining user-facing blockers are covered by implemented behavior and tests:

- Tree view command metadata consolidation is not required for this merge because public command ids now have registry parity coverage, Home actions consume the registry, and the current tree views keep existing command ids. Broader tree metadata generation can remain a later refactor.
- Governed skill summaries do not need a persisted contract field in this slice. The VS Code capability view now displays `name`, `description`, `id`, aliases, lifecycle state, memory targets, and migration status from the existing status payload.
- Promotion cleanup remains preview-first, root-contained, and metadata-preserving.
- Repeated promotion accept, reject, apply/finalize, and archive actions return no-op success when already done.
- Conversion selection hides already governed and GovKB-generated skills by default while preserving manual entry.

Final verification is recorded in `implementation-summary-phase-5.md` and `poc-parity-review.md`.

## 12. Ready Checklist

- Requirements mapped to use cases.
- PoC assertions identify current gaps and reusable code.
- Plan keeps mutation in CLI-backed commands.
- Tests use temp dirs and synthetic payloads.
- Cleanup has preview-first semantics.
- Each phase has rollback.
- Open questions are scoped to the phase that needs them.
