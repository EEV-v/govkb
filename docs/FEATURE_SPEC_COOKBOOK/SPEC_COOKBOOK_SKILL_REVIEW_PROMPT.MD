# Spec Cookbook Workflow Review Prompt

Review the GovKB spec-convergence workflow for whether it can be used reliably without source-project scripts.

## Inputs

- `docs/FEATURE_SPEC_COOKBOOK/SPEC_COOKBOOK.MD`
- `docs/FEATURE_SPEC_COOKBOOK/*_PROMPT.MD`
- `docs/FEATURE_SPEC_COOKBOOK/references/*.md`
- any future GovKB helper scripts, if added

## Review Checks

1. Does the workflow make current stage and next action explicit?
2. Does it preserve durable human-maintained ledgers?
3. Does it prevent accidental canonical `business.md` rewrites?
4. Does it avoid external tracker assumptions when no tracker is configured?
5. Does it clearly separate external review readiness from engineering handoff readiness?
6. Is it lightweight enough for regular GovKB feature work?

## Output

- High/medium/low findings
- Concrete remediation recommendations
- Whether the workflow is ready for routine use

