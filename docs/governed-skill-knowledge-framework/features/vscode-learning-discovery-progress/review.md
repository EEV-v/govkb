# VS Code Learning Discovery and Progress - Implementation Plan Review

Last updated: 2026-05-10

## Verdict

Ready for Implementation: Yes

## Findings

| Priority | Area | Finding | Evidence | Recommendation |
|---|---|---|---|---|
| P3 | Product defaults | The plan proposes changing the extension product default for `reviewMaxSessions` from 1 to 5, but leaves room to keep 1 for packaging validation. This is acceptable for implementation, but tests and package descriptions must be updated consistently if the default changes. | `implementation-plan.md` sections 3 and 11; current `vscode-extension/src/settings.ts`; current `vscode-extension/package.json` | During Phase 2, choose one default and update settings, package metadata, and tests in the same patch. |

## Gate Checklist

| Gate | Status | Evidence |
|---|---|---|
| Phase order preserved | PASS | Plan phases move from contracts, to CLI, to extension integration, to view/workflow behavior, then docs. |
| Requirements mapped | PASS | Section 2 maps REQ-VLDP-01 through REQ-VLDP-12 to concrete files and behavior. |
| PoC assertions carried forward | PASS | CLI help, inventory, classifier failure handling, wrapper forwarding, extension command/view gaps, and raw transcript rejection are covered in sections 3, 7, 8, and 9. |
| Tests are target-idiomatic | PASS | Python plan uses `unittest`, temp dirs, and direct command/helper tests; extension plan uses existing Node test suites and fixtures. |
| Commands are executable from stated cwd | PASS | Section 8 lists working directories and preconditions; Python 3.11+ is explicit. |
| Safety/governance constraints covered | PASS | Sections 1 and 6 keep mutations in CLI-owned paths and block raw transcript exposure. |
| Rollback is explicit | PASS | Each phase includes rollback, and section 10 covers feature-level fallback. |

## Required Revisions

None.

## Non-blocking Recommendations

- Keep `--inventory-json` strictly read-only and add an assertion that report, patch, candidate, state, skill, and memory paths remain untouched.
- For progress JSONL tests, include chunked stdout parsing so the VS Code parser does not assume one event per process chunk.
- In manual VS Code testing, use a disposable project before using Clearing so any apply-mode behavior is observed without touching important local memory.

## Residual Risks

- Long-running classifier sessions can still be slow even with progress events; the first implementation should prioritize accurate visible status over ambitious backfill automation.
- Existing report markdown remains the durable audit artifact, so progress event summaries should be treated as UI state, not a replacement for reports.
- Runtime discovery is better than before, but Python 3.11+ availability must be communicated clearly in VS Code blocker messages.
