# Agentic Architecture Refactoring - PoC Parity Review

Last updated: 2026-05-16

## Verdict

Ready for Merge: Yes

## Summary

The implementation closes the PoC gaps without replacing GovKB's CLI-owned mutation boundary. GovKB now has a state ownership map, a typed VS Code action registry with manifest parity tests, idempotent promotion lifecycle behavior, preview-first promotion cleanup, improved governed skill summaries, conversion picker filtering for already governed or GovKB-generated skills, and regression coverage for no-write and isolated-state behavior.

## Requirement Parity

| Requirement | PoC Assertion | Implementation Evidence | Result | Notes |
|---|---|---|---|---|
| REQ-AAR-01 | Existing docs lacked one consolidated ownership map. | `docs/governed-skill-knowledge-framework/architecture/agentic-state-ownership.md`; `tests/test_agentic_architecture_refactoring_smoke.py`. | PASS | The doc names authoritative, derived, generated, disposable, and test-only stores. |
| REQ-AAR-02 | Action labels and ids were spread across extension files. | `vscode-extension/src/actionRegistry.ts`, `vscode-extension/src/homeState.ts`, `vscode-extension/src/test/suite/actionRegistry.test.ts`, `vscode-extension/src/test/suite/packaging.test.ts`. | PASS | `package.json` remains the VS Code contribution source; tests enforce parity. |
| REQ-AAR-03 | Lifecycle states existed but rerun semantics needed explicit no-op reporting. | `src/govkb/commands/promotions.py`, `tests/test_promotions.py`. | PASS | Accept, reject, apply/finalize, and archive reruns return no-op success and do not rewrite metadata. |
| REQ-AAR-04 | Cleanup command was absent. | `govkb promotions cleanup`, `src/govkb/commands/promotions.py`, `src/govkb/core/promotion_lifecycle.py`, `tests/test_agentic_architecture_refactoring_use_cases.py`. | PASS | Cleanup is preview-first, root-contained, metadata-preserving, and idempotent. |
| REQ-AAR-05 | Extension flows already used CLI wrappers and the registry had to preserve that boundary. | `vscode-extension/src/actionRegistry.ts`, `vscode-extension/src/flows.ts`, `vscode-extension/src/govkbCli.ts`, `vscode-extension/src/test/suite/actionRegistry.test.ts`. | PASS | Mutating action registry entries are required to be CLI-backed. |
| REQ-AAR-06 | Conversion picker needed discoverable selection and default exclusions. | `vscode-extension/src/localSkills.ts`, `vscode-extension/src/extension.ts`, `vscode-extension/src/test/suite/localSkills.test.ts`, Clearing helper QA. | PASS | Already governed and GovKB-generated skills are hidden by default; manual entry remains available. |
| REQ-AAR-07 | Summary placement needed a UI/storage decision. | `vscode-extension/src/views/capabilitiesView.ts`, `vscode-extension/src/test/suite/views.test.ts`. | PASS | Existing status payload fields are sufficient; no new persisted contract field is required. |
| REQ-AAR-08 | New dry-run/no-write/idempotency/local-isolation tests were required. | Python temp-dir tests plus extension fake-runner and parser tests. | PASS | Coverage includes preview no-write, scoped cleanup, metadata preservation, idempotent reruns, and local skill filtering. |
| REQ-AAR-09 | Implementation had to remain phased and reversible. | Phase summaries 0 through 5 and implementation plan rollback sections. | PASS | No phase changes `.governed/**` semantics without a migration. |

## Scenario Parity

| Scenario | Test/Verification | Result | Notes |
|---|---|---|---|
| UC-1 | `tests/test_agentic_architecture_refactoring_smoke.py` | PASS | Ownership map exists and names key stores and mutation owners. |
| UC-2 | `vscode-extension/src/test/suite/actionRegistry.test.ts`, `packaging.test.ts` | PASS | Registry command ids are unique and contributed in `package.json`. |
| UC-3 | `tests/test_promotions.py` | PASS | Repeated review/apply/archive actions return no-op success. |
| UC-4 | `tests/test_agentic_architecture_refactoring_use_cases.py` | PASS | Cleanup preview lists eligible items without writing files or metadata. |
| UC-5 | `tests/test_agentic_architecture_refactoring_use_cases.py` | PASS | Cleanup apply removes only eligible worktrees and preserves sidecar metadata. |
| UC-6 | `vscode-extension/src/test/suite/localSkills.test.ts`, Clearing helper QA | PASS | Picker hides governed and generated packages while keeping manual fallback. |
| UC-7 | `vscode-extension/src/test/suite/views.test.ts` | PASS | Governed skill rows show human-readable names, descriptions, aliases, memory targets, and lifecycle metadata. |
| UC-8 | `vscode-extension/src/test/suite/actionRegistry.test.ts`, `flows.test.ts`, Python temp-dir tests | PASS | Mutating VS Code actions remain CLI-backed and tests avoid real user state. |
| UC-9 | `vscode-extension/src/test/suite/homeState.test.ts` | PASS | Home primary actions still map project and promotion state to the intended next action. |

## Command Evidence

| Command | Working Dir | Result | Evidence |
|---|---|---|---|
| `PYTHONPATH=src /Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest discover -s tests -v` | `/Users/vasilevevgeny/code/govkb` | PASS | 172 tests passed, 33 skipped. |
| `npm test` | `/Users/vasilevevgeny/code/govkb/vscode-extension` | PASS | 115 tests passed. |
| `npm run test:host` | `/Users/vasilevevgeny/code/govkb/vscode-extension` | PASS | Extension host exited with code 0. |
| `PYTHONPATH=src /Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m govkb.cli validate /Users/vasilevevgeny/code/govkb` | `/Users/vasilevevgeny/code/govkb` | PASS | Validation passed with one existing non-blocking `project-knowledge-steward` thin-memory warning. |
| `PYTHONPATH=src /Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m govkb.cli status /Users/vasilevevgeny/code/Etna/Clearing --codex-home /Users/vasilevevgeny/.codex --json` | `/Users/vasilevevgeny/code/govkb` | PASS | Clearing status valid; 6 capabilities; one pending local memory item. |
| `PYTHONPATH=src /Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m govkb.cli promotions cleanup /Users/vasilevevgeny/code/Etna/Clearing --codex-home /Users/vasilevevgeny/.codex --preview --json` | `/Users/vasilevevgeny/code/govkb` | PASS | Empty preview: no eligible, skipped, removed, or errored items. |
| Compiled Node helper for `discoverLocalSkills` and `governedSkillNamesForConversion` | `/Users/vasilevevgeny/code/govkb` | PASS | Clearing selectable skills count was 0; governed/generated examples were hidden. |

## Deviations

| Deviation | Approved? | Reason | Follow-up |
|---|---|---|---|
| Full tree-view command metadata consolidation is deferred. | Yes | Registry parity and Home registry consumption cover the drift risk for this slice, while broad tree refactoring is not needed for the user-visible blockers. | Consider moving remaining tree row labels/icons to registry if drift appears again. |
| No new persisted governed skill summary contract was added. | Yes | Existing capability status fields provide enough human-readable summary data and avoid a needless migration. | Add a contract field only when a concrete summary data gap appears. |
| Adjacent conversion/merge prompt safety changes are present in dirty core files. | Yes | They align with governed conversion and merge safety, but do not introduce new storage semantics. | Keep covered by existing capability management, conversion, and validation tests. |

## Risks

- Some VS Code command contribution metadata still lives in `package.json` because VS Code requires manifest contributions. Parity tests now guard this duplication.
- Cleanup should stay preview-first in UI; future targeted cleanup of actionable reviews should require explicit confirmation and separate tests.
- The repository has an unrelated untracked `.governed/capabilities/prompt-engineering-kb/` directory that was intentionally not modified.

## Required Fixes Before Merge

None.

## Post-merge Follow-ups

- Consider registry-backed helpers for more tree row commands if command label drift returns.
- Consider a persisted governed skill summary field only if the existing status payload cannot support a future UI need.
- Decide separately whether the unrelated untracked `prompt-engineering-kb` governed package should be committed, ignored, or removed.
