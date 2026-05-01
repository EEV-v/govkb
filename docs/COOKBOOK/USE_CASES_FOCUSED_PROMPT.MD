ROLE
Senior product engineer writing focused BDD use cases for a GovKB feature.

GOAL
Create `use-cases.md` with high-signal scenarios that can drive PoC assertions, implementation planning, and Python test scaffolds.

DOCUMENT CHAIN
- Inputs:
  - `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/business.md`
  - `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/context.md`
- Output:
  - `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/use-cases.md`
- Next:
  - `POC_PROMPT.MD`

INPUT
- FeatureSlug: <kebab-case folder name>
- FeatureName: <human-readable title>
- FeatureType: <CLI | Adapter | KnowledgeModel | Automation | VSCodeExtension | DocsWorkflow>

OUTPUT FORMAT

```markdown
# <FeatureName> - Use Cases

Last updated: <YYYY-MM-DD>

## Scope

## Actors

| Actor | Goal |
|---|---|

## Background

Given <shared starting condition>
And <shared repository/package state>

## Scenarios

### UC-1: <scenario title> @smoke

Given <precondition>
When <action>
Then <expected result>
And <observable evidence>

### UC-2: <scenario title> @regression

...

## Scenario Outlines

### UC-N: <outline title> @regression

Given <precondition with <placeholder>>
When <action>
Then <expected result>

Examples:

| placeholder | expected |
|---|---|
| value | result |

## Negative And Governance Cases

## Traceability

| Requirement | Scenario(s) | Coverage |
|---|---|---|

## Test Notes

| Scenario | Suggested Test Module | Notes |
|---|---|---|
```

SCENARIO RULES
- Produce 5-9 scenarios total unless the feature is genuinely smaller.
- Include exactly one or two `@smoke` scenarios.
- Cover the happy path, validation errors, idempotency or re-run behavior, governance/security boundaries, and rollback or failure handling.
- For CLI features, include command output and filesystem side effects.
- For adapter or memory-review features, include report/state behavior and raw-transcript leakage prevention.
- For docs workflow features, include artifact location, traceability, and review gate behavior.
- Keep steps implementation-neutral but testable.

TRACEABILITY RULES
- Every scenario must map to one or more requirements from `business.md`.
- If a business requirement is not testable, list it with the reason.
- Preserve business wording for user-visible outcomes.

TEST SCAFFOLD NOTES
- Use `tests/test_<feature_slug>_use_cases.py` for scenario coverage.
- Use `tests/test_<feature_slug>_smoke.py` for one or two smoke/happy-path flows.
- Use `tests/<feature_slug>_test_helper.py` for feature-specific helper API.
- Do not reference non-existent fixtures or third-party test frameworks.

END
