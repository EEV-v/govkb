# Reconciliation Prompt

Use this after the review diff exists.

## Outputs

- updated `<label>-reconciliation.md`
- optional manual update to canonical `business.md`
- updated `review-rounds/reconciliation-state.json`
- refreshed `open-questions.md` and `decision-log.md`

## Rules

- Only modify canonical `business.md` after reconciliation explicitly records merge intent.
- Valid canonical update signals:
  - `Promote source document as canonical: Yes`
  - `Canonical business.md updated manually: Yes`
  - `No canonical changes required: Yes`
- Mark `Round processed: Yes` only after canonical handling is complete.
- Refresh question and decision ledgers after reconciliation.
- Refresh `business-review-pack.md` only when tracker/reference status is truthful and no feedback round remains pending.

