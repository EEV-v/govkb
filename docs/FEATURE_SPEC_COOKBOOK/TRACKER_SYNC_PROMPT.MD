# Tracker / Reference Sync Prompt

Use this before an external business review is sent or before scope lock.

GovKB has no mandatory external tracker linkage. This phase records whether an external tracker exists and whether local artifacts reflect it honestly.

## Goal

Ensure tracker/reference status is explicit:

- external tracker configured and links recorded, or
- tracker not configured / not applicable for local implementation, or
- tracker needed but unresolved

## Outputs

Update the `## Tracking` or readiness section in these files when present:

- `business.md`
- `spec-brief.md`
- `business-review-pack.md`
- `scope-lock.md`
- `spec-handoff.md`

## Rules

- Do not create or wire external trackers without explicit user confirmation.
- Do not treat missing tracker links as a local-engineering blocker unless the feature explicitly requires external/public tracking.
- Public Marketplace work may need a tracker later; local VSIX or internal proof work may proceed with `Tracker: Not configured`.
- If multiple tracker candidates exist, require explicit ids or links before marking tracker status resolved.
- Keep tracker readiness separate from feedback reconciliation readiness.
