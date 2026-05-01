# Review Diff Prompt

Use this when business or stakeholders return a reviewed document, comments, email notes, or other feedback.

## Outputs

- immutable source copy under `review-rounds/`
- `<label>-changes.md`
- `<label>-reconciliation.md`
- updated `review-rounds/reconciliation-state.json`

## Rules

- Preserve the returned source wording and formatting.
- Do not update canonical `business.md` in the diff step.
- Classify changes as:
  - scope change
  - clarification
  - decision
  - open question
  - non-substantive wording
  - out of scope
- If feedback is mixed across channels, normalize it into one source artifact before diffing.
- Record whether the round is `new`, `diffed`, `classified`, or `reconciled`.

