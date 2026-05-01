# Review Pack Prompt

Use this when the canonical draft is ready to send back to business or stakeholders.

## Outputs

- `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/business-review-pack.md`
- `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/business-review-message.md`

## Rules

- Keep wording business-facing and concise.
- Group asks into:
  - scope to confirm
  - blockers to answer
  - decisions to approve or defer
- Keep tracker/reference readiness separate from feedback reconciliation readiness.
- If tracker linkage is required but incomplete, say the pack is not ready to send externally.
- If feedback reconciliation is still pending, do not refresh the outgoing pack yet.
- Include concrete asks, not only counts.
- If the pack is for internal engineering handoff rather than external send, mark it as such.
- After generating the pack and message for external send, run the fresh final-review check from `FINAL_REVIEW_PROMPT.MD`.

