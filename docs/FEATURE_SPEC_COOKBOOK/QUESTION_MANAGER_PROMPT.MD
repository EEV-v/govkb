# Question Manager Prompt

Use this after intake and after every reviewed or normalized feedback round.

## Outputs

- `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/open-questions.md`
- `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/decision-log.md`

## Rules

- Preserve statuses, owners, notes, and stable ids already set by humans.
- Treat existing files as durable ledgers; append or update entries instead of deleting unresolved rows because the current sources are narrower.
- New questions default to `Blocking` unless they are clearly deferred or safe as an assumption.
- Question statuses are `Blocking`, `Deferred`, `Resolved`, or `Assumption`.
- New decisions default to `Open`.
- Decision statuses are `Open`, `Approved`, `Deferred`, or `Rejected`.
- Keep questions and decisions separate.
- Convert resolved questions into decision-log entries when the answer materially locks scope.
- For GovKB public-distribution features, separate first-slice implementation decisions from later Marketplace/public-launch decisions.

