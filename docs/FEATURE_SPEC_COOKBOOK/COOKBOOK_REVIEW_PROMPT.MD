# Spec Cookbook Review Prompt

Review the GovKB feature spec cookbook for daily usability and handoff safety.

## Inputs

- `docs/FEATURE_SPEC_COOKBOOK/SPEC_COOKBOOK.MD`
- operational prompts under `docs/FEATURE_SPEC_COOKBOOK/`
- references under `docs/FEATURE_SPEC_COOKBOOK/references/`
- recent feature folders under `docs/governed-skill-knowledge-framework/features/`

## Review Focus

- phase order and gates are clear
- `business-context.md` and `context.md` are required before analysis
- reviewed snapshots remain immutable
- question and decision ledgers preserve statuses
- tracker/reference status is truthful without assuming external systems
- business review pack readiness is not confused with engineering handoff readiness
- scope lock and handoff are produced only at explicit checkpoints
- the handoff into `docs/COOKBOOK/COOKBOOK.MD` is concrete

## Output

- findings ordered by severity
- recommended prompt or cookbook updates
- residual risks

