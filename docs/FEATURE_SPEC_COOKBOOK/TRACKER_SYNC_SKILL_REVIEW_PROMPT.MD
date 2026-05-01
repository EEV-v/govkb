# Tracker / Reference Sync Review Prompt

Review the tracker/reference sync phase for GovKB feature specs.

## Inputs

- `docs/FEATURE_SPEC_COOKBOOK/TRACKER_SYNC_PROMPT.MD`
- feature artifacts that include tracking or readiness sections

## Review Checks

1. Does the workflow avoid assuming a specific external tracker?
2. Does it avoid creating or wiring trackers without explicit user confirmation?
3. Does it distinguish local-engineering readiness from external/public review readiness?
4. Does ambiguous tracker linkage stop only tracker-dependent actions?
5. Is the recorded tracker/reference status truthful and visible?

## Output

- Findings
- Recommended wording or process changes
- Whether tracker/reference status is safe for the current feature stage

