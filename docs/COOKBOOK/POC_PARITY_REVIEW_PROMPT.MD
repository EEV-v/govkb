ROLE
Principal reviewer checking that implemented GovKB behavior matches the PoC and accepted plan.

GOAL
Create `poc-parity-review.md` as the merge gate between implementation and release artifacts.

DOCUMENT CHAIN
- Inputs:
  - `requirements-catalog.md`
  - `poc-plan.md`
  - `poc-output.md`
  - `implementation-plan.md`
  - `review.md`
  - implementation summaries
  - test results and refreshed PoC outputs
- Output:
  - `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/poc-parity-review.md`
- Next:
  - PR, release notes, stakeholder presentation, sign-off

INPUT
- FeatureSlug: <kebab-case folder name>
- FeatureName: <human-readable title>

REVIEW TASKS
1. Compare every PoC assertion with implemented behavior.
2. Compare every requirement with tests or documented manual verification.
3. Confirm accepted deviations are explicitly recorded.
4. Confirm test commands ran from the stated working directory.
5. Confirm no raw transcript content, user secrets, or local assistant state were committed.
6. Confirm new tests use GovKB's actual `unittest` patterns.

OUTPUT FORMAT

```markdown
# <FeatureName> - PoC Parity Review

Last updated: <YYYY-MM-DD>

## Verdict

Ready for Merge: <Yes | No>

## Summary

## Requirement Parity

| Requirement | PoC Assertion | Implementation Evidence | Result | Notes |
|---|---|---|---|---|

## Scenario Parity

| Scenario | Test/Verification | Result | Notes |
|---|---|---|---|

## Command Evidence

| Command | Working Dir | Result | Evidence |
|---|---|---|---|

## Deviations

| Deviation | Approved? | Reason | Follow-up |
|---|---|---|---|

## Risks

## Required Fixes Before Merge

## Post-merge Follow-ups
```

PASS RULES
- `Ready for Merge: Yes` requires all blocking requirements to be passed or explicitly approved as non-blocking.
- Failed tests, missing final verification, or unapproved PoC deviation means `Ready for Merge: No`.
- Stale commands or source-project references mean `Ready for Merge: No`.

END
