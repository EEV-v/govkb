# Agentic Architecture Refactoring - PoC Output

## Summary

The PoC confirms that GovKB already has many reusable building blocks: promotion lifecycle metadata, CLI JSON payloads, temp-dir Python tests, pure VS Code Home state tests, and conversion preview/write flows. The gaps are architectural cohesion and operational clarity: no consolidated state ownership map, no central VS Code action registry, no promotion cleanup command, and insufficient explicit tests for idempotent reruns and no-write cleanup previews.

## Assertion Results

| Assertion | Result | Evidence | Notes |
|---|---|---|---|
| Current GovKB has no consolidated agentic state ownership map. | Passed | `README.md`, `docs/README.md`, feature docs list product scope but not a source/derived/disposable state map. | New architecture doc is justified. |
| Current VS Code action metadata is spread across multiple files. | Passed | `vscode-extension/src/homeState.ts`, `vscode-extension/src/extension.ts`, `vscode-extension/package.json`. | Refactor should start with a registry and parity tests. |
| Current promotion lifecycle already has sidecar state that can be extended. | Passed | `src/govkb/core/promotion_lifecycle.py` defines ready, accepted, applied, rejected, and archived metadata helpers. | Build on this instead of replacing it. |
| Current promotion cleanup command is absent. | Passed | `src/govkb/commands/promotions.py` dispatches list, show, mark-reviewed, apply, and archive. | Cleanup is additive CLI surface. |
| Current tests have reusable dry-run/temp-dir patterns. | Passed | `tests/test_promotions.py`, `tests/test_skill_conversion.py`, `vscode-extension/src/test/suite/homeState.test.ts`. | Implementation can stay idiomatic. |
| Caveman patterns are safely reusable only as architecture practices. | Passed | Caveman source-of-truth docs, provider registry, JSONC settings helper, idempotent marker-block helper, and dry-run tests were inspected. | Do not copy Caveman user-facing behavior or installer. |

## Outliers

- Caveman is not a VS Code extension, so UI layout patterns do not transfer directly.
- Caveman uses cross-agent installer and hook behavior that is outside this GovKB feature's scope.
- GovKB has a Python CLI plus TypeScript extension split; the action registry must respect VS Code manifest constraints instead of copying a Node installer matrix.

## Open Gaps

- Cleanup policy for lifecycle metadata after worktree deletion is resolved in the implementation plan: preserve sidecar metadata, add a cleanup marker, and remove eligible worktrees from the actionable list.
- Human-facing governed skill summary storage is undecided.
- Whether to generate `package.json` command contributions from the action registry or only test parity remains undecided.

## Recommendation

Proceed with a phased implementation. Start with documentation and typed action-registry tests, then add idempotent promotion lifecycle cleanup, then refine governed skill summaries and conversion UX. Keep all mutation CLI-backed and require preview/no-write tests before exposing cleanup in VS Code.
