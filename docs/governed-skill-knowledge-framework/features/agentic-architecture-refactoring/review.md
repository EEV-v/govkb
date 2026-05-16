# Agentic Architecture Refactoring - Implementation Plan Review

Last updated: 2026-05-16

## Verdict

Ready for Implementation: Yes

This approval covers Phase 0 through Phase 3. Cleanup apply is now unblocked by policy: it must remove eligible worktrees, preserve sidecar lifecycle metadata, and mark the metadata as cleaned.

## Findings

| Priority | Area | Finding | Evidence | Recommendation |
|---|---|---|---|---|
| P2 | Scope | The feature spans docs, extension refactoring, promotion lifecycle, cleanup, and governed skill summaries. This is workable only if phases stay independently mergeable. | `implementation-plan.md` phases 0 through 5. | Keep phase PRs small. Do not start cleanup apply until action registry and lifecycle no-op tests are stable. |
| P2 | Cleanup safety | The cleanup policy is now decided, but implementation must keep deletion scoped to computed worktree roots and preserve audit metadata. | `context.md` Storage and Security sections, `implementation-plan.md` Promotion Cleanup. | Add preview no-write, scoped apply, idempotent rerun, and metadata-preservation tests before exposing the UI action. |
| P3 | Action registry | The plan intentionally avoids manifest generation in the first slice. Manual parity can still drift if tests are incomplete. | `implementation-plan.md` Phase 1. | Make registry/package parity tests strict for public commands and require explicit internal exemptions. |

## Gate Checklist

| Gate | Status | Evidence |
|---|---|---|
| Phase order preserved | PASS | `implementation-plan.md` starts with docs and registry before cleanup mutation. |
| Requirements mapped | PASS | `requirements-catalog.md` maps REQ-AAR-01 through REQ-AAR-09. |
| PoC assertions carried forward | PASS | `implementation-plan.md` addresses ownership map, action registry, lifecycle state, cleanup gap, and tests. |
| Tests are target-idiomatic | PASS | Existing anchors were verified in `tests/test_promotions.py`, `tests/test_skill_conversion.py`, `vscode-extension/src/test/suite/homeState.test.ts`, `vscode-extension/src/test/suite/views.test.ts`, and `vscode-extension/src/test/suite/localSkills.test.ts`; new test modules are explicitly planned. |
| Commands are executable from stated cwd | PASS | `context.md` command map was checked against `src/govkb/cli.py`; existing promotion detail/apply actions use `<run-id> --project-root <project-root>`. |
| Safety/governance constraints covered | PASS | CLI mutation boundary, no raw transcripts, preview no-write, and root containment are explicit. |
| Rollback is explicit | PASS | Each implementation phase includes rollback. |

## Required Revisions

None before Phase 0 through Phase 3.

Phase 3 apply mode must follow the resolved cleanup policy: preserve sidecar metadata, add a cleanup marker, and hide cleaned records from the default actionable promotion list.

## Non-blocking Recommendations

- Add a short "do not copy from Caveman" note in the architecture ownership doc so future maintainers understand the external repo was used for patterns only.
- Prefer registry parity tests over package generation initially; generation can be a later cleanup if drift remains a problem.
- Keep the first cleanup UI action as "Preview cleanup" rather than "Clean now" to match the no-surprises product direction.

## Residual Risks

- The broad feature can become a catch-all refactor if unrelated UI polish gets added. Keep acceptance tied to REQ-AAR items.
- VS Code manifest contribution constraints may prevent full registry centralization without build tooling. Tests should document intentional duplication.
- Cleanup commands can damage user trust if path containment, metadata preservation, and preview behavior are not heavily tested.
