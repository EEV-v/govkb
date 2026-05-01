# VS Code Extension UI and Public Distribution - Implementation Plan Review

Last updated: 2026-04-25

## Verdict

Ready for Implementation: Yes

## Findings

No blocking findings.

| Priority | Area | Finding | Evidence | Recommendation |
|---|---|---|---|---|
| P3 | JSON CLI tests | The plan calls for status JSON tests and candidates JSON tests, but final test names can be tightened during implementation. | `implementation-plan.md` sections 7 and 9 | Include explicit tests for default text output, JSON success output, and JSON error output with the same exit code as text mode. |
| P3 | Extension packaging | VSIX packaging depends on Node/npm dependencies and provisional package metadata that do not exist yet. | `implementation-plan.md` sections 0.5, 8, and Phase 4 | Keep packaging in Phase 4 after `npm install`, compile, tests, `.vscodeignore`, and provisional metadata are present. |

## Gate Checklist

| Gate | Status | Evidence |
|---|---|---|
| Phase order preserved | PASS | Plan starts with JSON CLI contracts, then extension scaffold, workflows, views, and packaging. |
| Requirements mapped | PASS | `implementation-plan.md` section 2 maps REQ-VSCODE-01 through REQ-VSCODE-15. |
| PoC assertions carried forward | PASS | PoC gaps for missing `--json`, extension scaffold, report parser, and VSIX exclusions are explicit in phases and tests. |
| Tests are target-idiomatic | PASS | Python tests follow existing `unittest` temp-dir patterns; extension tests are isolated under `vscode-extension/src/test/suite/`. |
| Commands are executable from stated cwd | PASS | Verification table includes `/home/ev/code/govkb` and `/home/ev/code/govkb/vscode-extension` working directories and preconditions. |
| Safety/governance constraints covered | PASS | Plan preserves `.governed/` as source of truth, `$CODEX_HOME` as derived output, Workspace Trust gating, and no raw transcript persistence. |
| Rollback is explicit | PASS | Each implementation phase has a rollback section and section 10 covers feature-level rollback. |

## Required Revisions

None.

## Non-blocking Recommendations

- In Phase 0, prefer small payload-builder functions that Python tests can call directly, plus command tests that verify stdout JSON.
- In Phase 1, keep non-VS Code API logic in testable modules so most extension tests can run without a full extension host.
- Keep local VSIX metadata clearly provisional until publisher, icon, and public branding decisions are made.

## Residual Risks

- Node/npm dependency installation may require network access during implementation.
- Report markdown structure may evolve; parser tests should use sanitized fixtures and fail closed rather than guessing from raw report text.
- Marketplace-ready packaging remains deferred until product branding and publisher decisions are made.

