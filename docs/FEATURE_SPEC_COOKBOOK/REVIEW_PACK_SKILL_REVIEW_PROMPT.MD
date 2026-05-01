# Review Pack Workflow Review Prompt

Review the business review-pack workflow for outbound communication quality.

## Inputs

- `docs/FEATURE_SPEC_COOKBOOK/REVIEW_PACK_PROMPT.MD`
- `docs/FEATURE_SPEC_COOKBOOK/FINAL_REVIEW_PROMPT.MD`
- generated `business-review-pack.md` and `business-review-message.md`
- base artifacts: `business.md`, `business-context.md`, `context.md`, `spec-brief.md`, `open-questions.md`, `decision-log.md`

## Review Checks

1. Does the pack accurately reflect canonical scope?
2. Does it represent question and decision ledger status correctly?
3. Does it avoid claiming external-send readiness when tracker/reference or feedback gates are unresolved?
4. Are asks concrete and stakeholder-usable?
5. Does the message summarize the pack without dropping a blocker?

## Output

- Findings
- Send recommendation
- Required fixes before external send

