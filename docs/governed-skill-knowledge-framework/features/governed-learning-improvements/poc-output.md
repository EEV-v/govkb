# Governed Learning Improvements - PoC Output

Last updated: 2026-05-29

## Summary

Planning PoC confirms that GovKB already has the source surfaces needed for this feature:

- proposal metadata and validation in `src/govkb/core/proposals.py`
- proposal CLI command layer in `src/govkb/commands/proposals.py`
- status JSON in `src/govkb/commands/status.py`
- incremental memory-review selection and proposal staging in `src/govkb/adapters/codex/bin/codex-memory-review`
- VS Code extension metadata and CLI-backed surfaces in `vscode-extension/`
- existing unittest patterns for proposals, memory review, status JSON, and VS Code behavior

## Assertion Results

| Assertion | Result | Evidence | Notes |
|---|---|---|---|
| A-1 | Passed | `stage_proposal`, `load_proposal`, `build_proposals_payload` exist. | Grouping can reuse loaded proposal metadata. |
| A-2 | Passed | Existing safety metadata includes type, safety class, confidence, verification command, outputs, and draft output. | Quality scoring can be read-only. |
| A-3 | Partial | Status JSON exists; memory-review reports and state exist in generated local output. | Need a formal health command and temp fixtures. |
| A-4 | Partial | `reviewAfter` and row filtering points exist. | Need conservative self-noise tests. |
| A-5 | Partial | Capability files and staged proposals expose enough artifact presence. | Need level definitions and tests. |
| A-6 | Partial | VS Code package metadata and install-state revisions exist. | Need doctor command JSON before UI. |
| A-7 | Not Run in this phase | Existing tests were run before this feature package creation. | Run targeted tests when production code changes. |

## Outliers

| Item | Impact | Required Handling |
|---|---|---|
| Clearing's current proposal queue contains overlapping proposal candidates. | Good manual fixture, but not stable enough for tests. | Use synthetic fixtures in tests; use Clearing only for manual verification. |
| Real cron and daemon state are machine-specific. | Health command can be brittle. | Treat unavailable checks as warnings or unknown. |
| Live Codex sessions append rows while an agent is working. | Inventory can select the same session with a newer timestamp. | Skip noise-only tails; preserve user rows. |

## Open Gaps

| Gap | Impact |
|---|---|
| Phase 0 CLI shape is not finalized. | Blocks implementation of proposal report command flags/action. |
| No test fixtures exist yet for grouping, health, maturity, or doctor payload. | Must be created during implementation. |
| VS Code UI scope is not finalized. | Keep UI out of Phase 0. |

## Recommendation

Start with Phase 0: proposal grouping/reporting and advisory quality warnings. It has the clearest inputs, minimal risk, and immediate value for the existing Clearing consumer queue.

