# Combined Review Feedback

Historical/adoption review notes for the GovKB feature spec cookbook.

## Prioritized Feedback Themes

1. Make workflow state explicit.
- Separate tracker/reference readiness from feedback reconciliation.
- Tell the operator the current stage and next action directly.

2. Preserve durable human-maintained ledgers.
- `open-questions.md` and `decision-log.md` should not shrink just because a later source is narrower.
- Stable ids, statuses, owners, and notes should survive repeated runs.

3. Keep review rounds safe.
- Reviewed snapshots stay immutable.
- Existing round packages should be reused, not regenerated blindly.
- Only reviewed snapshots may be promoted wholesale into canonical `business.md`.

4. Reduce misleading output.
- Do not label all blockers as tracker blockers.
- Do not regenerate review-pack, scope-lock, or handoff artifacts while feedback reconciliation is still pending.

5. Make tracker/reference status truthful.
- Ambiguity must stop tracker-dependent actions.
- Local artifacts should not claim external readiness before linkage is resolved.
- Missing external tracker linkage is not automatically a local-engineering blocker in GovKB.

## Changes Applied In GovKB Adoption

- Spec workflow now requires `business-context.md` and `context.md` before spec analysis.
- Tracker sync was generalized to tracker/reference status.
- GovKB feature path is `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/`.
- Scope lock and handoff can be produced for a named slice while public-launch scope remains deferred.
- Shared KB was rewritten around GovKB product, CLI, extension, and public-distribution patterns.

## Remaining Intentional Boundaries

- Canonical merge is still supervised. The workflow does not auto-merge reviewed content line-by-line into `business.md`.
- Review-pack files should not be regenerated while feedback is pending.
- Generic feedback files can inform reconciliation, but they are not eligible for direct canonical promotion.
- External tracker creation or wiring remains explicit-confirmation work.

