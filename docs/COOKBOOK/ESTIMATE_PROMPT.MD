ROLE
Principal engineer producing a compact feature estimate for GovKB.

GOAL
Create or revise `estimates.md` from `business.md`, `context.md`, and `implementation-plan.md`.

DOCUMENT CHAIN
- Inputs:
  - `business.md`
  - `context.md`
  - `implementation-plan.md`
  - optional `review.md`
- Output:
  - `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/estimates.md`

INPUT
- FeatureSlug: <kebab-case folder name>
- FeatureName: <human-readable title>
- EstimateMode: <first-pass | revise>

OUTPUT FORMAT

```markdown
# <FeatureName> - Estimate

Last updated: <YYYY-MM-DD>

## Summary

| Area | Estimate | Confidence | Notes |
|---|---:|---|---|

## Assumptions

## Phase Estimate

| Phase | Work | Estimate | Risk |
|---|---|---:|---|

## Test And Verification Estimate

## Review And Release Estimate

## Risks That Can Move The Estimate

## Exclusions
```

RULES
- Estimate only the accepted scope.
- Mention the implementation phases from `implementation-plan.md`.
- Include test and documentation effort.
- Use ranges when uncertainty is real.
- Do not invent external tracker IDs or delivery dates.

END
