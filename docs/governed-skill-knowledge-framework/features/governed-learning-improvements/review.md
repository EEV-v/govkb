# Governed Learning Improvements - Implementation Plan Review

Last updated: 2026-05-29

## Verdict

Ready for Implementation: Yes, Phase 0 only.

Phase 0 is limited to:
- proposal grouping/reporting
- advisory quality warnings
- tests for duplicate grouping, unrelated proposal separation, and read-only behavior

Do not implement memory-review health, self-noise filtering, maturity scoring, doctor, or VS Code UI until Phase 0 report shape is reviewed.

## Findings

| Priority | Area | Finding | Evidence | Recommendation |
|---|---|---|---|---|
| P1 | CLI contract | Phase 0 command shape is still open. | `business.md` Q1 and `implementation-plan.md` Q1. | Confirm `govkb proposals report <project-root> --json` before code. |
| P2 | Scope | Later phases are valuable but too broad for first implementation. | `implementation-plan.md` phases 1-4. | Ship Phase 0 first and use Clearing consumer queue for manual feedback. |
| P2 | Tests | Test files do not exist yet. | `implementation-plan.md` section 7. | Create use-case and smoke tests before production behavior. |
| P3 | POC | `poc-output.md` is inspectable but not rerunnable via a script. | `poc-plan.md` Rerun Command. | Phase 0 tests should become the rerunnable proof. |

## Gate Checklist

| Gate | Status | Evidence |
|---|---|---|
| Phase order preserved | PASS | Cookbook artifacts exist through plan review. |
| Requirements mapped | PASS | `requirements-catalog.md` and plan section 2. |
| PoC assertions carried forward | PASS | `poc-output.md` and plan section 2. |
| Tests are target-idiomatic | WARN | Planned with `unittest`, but not created yet. |
| Commands are executable from stated cwd | WARN | Existing commands are executable; new report command does not exist yet. |
| Safety/governance constraints covered | PASS | Read-only Phase 0, no raw transcript persistence, no user-home test dependency. |
| Rollback is explicit | PASS | Plan section 10 and per-phase rollback. |

## Required Revisions

- Confirm the Phase 0 CLI command name and flags before editing code.
- Add tests with temp project/proposal fixtures during Phase 0 implementation.

## Non-blocking Recommendations

- Keep the first report text compact and make JSON the primary integration contract.
- Include a manual verification example against Clearing after tests pass, but do not make Clearing a test dependency.
- Keep recommendation labels advisory and avoid auto-reject/apply actions.

## Residual Risks

- Similarity scoring may over-group proposals. Mitigation: show grouping reasons and keep all actions manual.
- Script warning quality may need tuning after real proposal review. Mitigation: warnings are advisory.
- Later health/doctor phases can become platform-specific. Mitigation: unavailable local checks should not fail the command.

