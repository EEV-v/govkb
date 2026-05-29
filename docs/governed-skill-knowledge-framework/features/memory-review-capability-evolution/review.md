# Memory Review Capability Evolution - Implementation Plan Review

Last updated: 2026-05-28

## Verdict

Ready for Implementation: Yes

## Findings

| Priority | Area | Finding | Evidence | Recommendation |
|---|---|---|---|---|
| P2 | Apply verification | The plan leaves room to either run the proposal verification command automatically or print it for manual execution in the first slice. | `implementation-plan.md` sections 3, 8, and 11. | During implementation, keep automated execution conservative: run strict validation directly, and only run arbitrary proposal verification commands after cwd, timeout, and safety rules are explicit. |
| P2 | Overwrite semantics | The plan correctly warns about overwriting existing output files, but exact replacement metadata is not part of the MVP contract. | `implementation-plan.md` section 6. | Start with refusal to overwrite existing non-identical files. Add reviewed replace semantics later if users need it. |

## Gate Checklist

| Gate | Status | Evidence |
|---|---|---|
| Phase order preserved | PASS | Plan moves from core proposal contracts to apply behavior, command surface, memory-review integration, then docs/parity. |
| Requirements mapped | PASS | `implementation-plan.md` section 2 maps REQ-MRCE-01 through REQ-MRCE-15. |
| PoC assertions carried forward | PASS | Missing CLI, schema, report, storage, and apply contracts from `poc-output.md` are all planned. |
| Tests are target-idiomatic | PASS | Plan uses `unittest`, temp dirs, direct command functions, and existing scheduler import patterns. |
| Commands are executable from stated cwd | PASS | Verification commands use `/home/ev/code/govkb` and `PYTHONPATH=src`. |
| Safety/governance constraints covered | PASS | Plan rejects raw transcripts/secrets, bounds writes to `.governed/capabilities/<capability-id>/`, and keeps cron stage-only. |
| Rollback is explicit | PASS | Each phase has rollback notes and section 10 covers command, adapter, and failed-apply rollback. |

## Required Revisions

None.

## Non-blocking Recommendations

- Add `--json` to `govkb proposals list/show` in the first implementation if VS Code or future automation is expected to consume proposal state soon.
- Keep `proposal.toml` small and stable; put longer review text in `proposal.md` so CLI parsing stays simple.
- Consider a later `govkb proposals approve` helper if manual TOML approval becomes error-prone.

## Residual Risks

- Classifier-generated draft content may be too weak for scripts; the first slice should prefer reviewable proposals and explicit draft output over unattended code generation.
- Proposal apply touches governed package files, so path validation and no-overwrite defaults are the highest-risk implementation details.
- Existing cron installations may need package refresh before they pick up the new adapter behavior; that belongs in implementation closeout or release notes.
