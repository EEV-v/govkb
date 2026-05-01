# Review Diff Workflow Review Prompt

Review the feedback diff and reconciliation workflow for GovKB specs.

## Inputs

- `docs/FEATURE_SPEC_COOKBOOK/REVIEW_DIFF_PROMPT.MD`
- `docs/FEATURE_SPEC_COOKBOOK/RECONCILIATION_PROMPT.MD`
- a sample feature `review-rounds/` folder when available

## Review Checks

1. Are reviewed and normalized feedback inputs preserved as immutable sources?
2. Does the diff classify substantive changes clearly?
3. Does reconciliation prevent blind canonical `business.md` overwrites?
4. Does `reconciliation-state.json` mirror the markdown control surface?
5. Are generic feedback files kept distinct from reviewed snapshots?

## Output

- Findings
- Recommended prompt updates
- Readiness recommendation

