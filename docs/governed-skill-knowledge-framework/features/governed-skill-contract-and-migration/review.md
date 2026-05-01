# Governed Skill Contract And Migration - Implementation Plan Review

Last updated: 2026-05-01

Status note: Superseded by `business-requirements-critical-review.md`. Do not use this implementation-plan review as an implementation gate until the business requirements blockers are resolved or explicitly deferred.

## Verdict

Ready for Implementation: No

Reason: business requirements review found blocking scope, governance, validation-policy, conversion-safety, and approval-lifecycle gaps.

## Findings

| Priority | Area | Finding | Evidence | Recommendation |
|---|---|---|---|---|
| P2 | Severity policy | The plan leaves open whether strict validation is default or opt-in. This is acceptable for implementation start but must be decided before changing candidate auto-create behavior in existing projects. | `implementation-plan.md` Open Questions | Implement strict validation as opt-in first, then gate conversion writes and candidate auto-create explicitly through strict checks. |
| P2 | Migration metadata | The plan prefers `[migration]` initially but still lists the metadata location as open. | `implementation-plan.md` Design and Open Questions | Use existing `[migration]` parser support for Phase 1-3. Revisit separate metadata only after conversion works. |
| P3 | Clearing cleanup | The feature defines a remediation path but does not execute Clearing cleanup. | `business.md` Clearing Remediation Use Case | Track Clearing cleanup as a follow-up after validation can prove the weak package is invalid. |

## Gate Checklist

| Gate | Status | Evidence |
|---|---|---|
| Phase order preserved | PASS | Feature has business, context, use cases, PoC, plan, and review |
| Requirements mapped | PASS | `requirements-catalog.md` maps requirements to scenarios |
| PoC assertions carried forward | PASS | `implementation-plan.md` carries baseline gaps into phases |
| Tests are target-idiomatic | PASS | Plan uses `unittest`, temp dirs, and command-function tests |
| Commands are executable from stated cwd | PASS | Commands use `/home/ev/code/govkb` and existing GovKB CLI conventions |
| Safety/governance constraints covered | PASS | Plan rejects secrets, raw transcripts, local paths, and source skill mutation |
| Rollback is explicit | PASS | Each implementation phase has rollback notes |

## Required Revisions

None before implementation.

## Non-blocking Recommendations

- Add rule ids to strict validation issues from the first implementation phase.
- Keep JSON output stable enough for the VS Code extension, but do not block core validation on UI work.
- Add a small CLI smoke test for `govkb convert skill --help`.

## Residual Risks

- Freeform existing skills may require manual cleanup after conversion.
- Strict validation can produce false positives on legitimate local operational scripts until tool conventions are tuned.
- Candidate auto-create behavior should remain conservative until existing project packages are cleaned up.
