# VS Code Guided Daily Workflow UI - Implementation Plan Review

Last updated: 2026-05-16

## Verdict

Ready for Implementation: Yes

## Findings

| Priority | Area | Finding | Evidence | Recommendation |
|---|---|---|---|---|
| P2 | Webview scope | The plan adds a Webview View, which is the right primitive for a polished dashboard but introduces CSP and message-routing complexity beyond the current tree-only extension. | `implementation-plan.md` Phase 1, `context.md` Proposed New Components | Keep Phase 0 as a pure model first, then implement webview rendering with small HTML and tested command ids. |
| P2 | Shared state logic | Existing next-action behavior already lives in `learningView.ts` and `promotionsView.ts`; duplicating it in Home could create divergent UI states. | `context.md` Existing Patterns, `implementation-plan.md` Design | Extract shared pure helpers or add cross-view tests that assert equivalent states. |
| P3 | Git handoff | Commit-required behavior is advisory; the plan does not integrate with VS Code Git APIs. | `implementation-plan.md` Open Questions | Keep advisory commit guidance in the first slice and revisit Git integration only after Home state is stable. |

## Gate Checklist

| Gate | Status | Evidence |
|---|---|---|
| Phase order preserved | PASS | Phase 0 model before Webview and command routing. |
| Requirements mapped | PASS | `requirements-catalog.md` and `implementation-plan.md` section 2. |
| PoC assertions carried forward | PASS | `poc-output.md` maps current contracts to plan components. |
| Tests are target-idiomatic | PASS | Node tests for TypeScript behavior; Python unittest scaffolds only. |
| Commands are executable from stated cwd | PASS | `implementation-plan.md` section 8. |
| Safety/governance constraints covered | PASS | CLI mutation boundary and transcript avoidance are explicit. |
| Rollback is explicit | PASS | Phase rollback and overall rollback are additive. |

## Required Revisions

None.

## Non-blocking Recommendations

- Add `homeState.test.ts` before any rendering work.
- Use VS Code theme variables and codicons before introducing custom CSS complexity.
- Keep report and digest inline display summary-only in the first slice.

## Residual Risks

- The Home dashboard can still become noisy if every section shows all actions at once; manual QA confirmed the primary next action is visible first in the normal Clearing side bar, but secondary-section density should be watched after real daily use.
- Webview tests cannot fully replace manual visual inspection inside VS Code; the current-state Clearing smoke is complete, while stale, ready-for-review, accepted, and pending-commit state checks remain useful follow-ups.
