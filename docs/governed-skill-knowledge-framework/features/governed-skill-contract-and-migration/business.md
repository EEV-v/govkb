# Governed Skill Contract And Migration - Split Overview

## Summary

The original "governed skill contract and migration" draft is now split into smaller feature slices. The combined draft mixed package quality rules, local Codex skill conversion, and Clearing remediation into one feature, which made the scope too broad for a safe implementation handoff.

This parent feature is a split record only. Do not implement directly from the older planning artifacts in this folder.

## Split Features

| Order | Feature | Purpose | Status |
|---|---|---|---|
| 1 | `governed-skill-quality-gates` | Define strict governed-skill package standards, validation policy, lifecycle, data/tool rules, and candidate activation gates. | First implementation slice |
| 2 | `codex-skill-governed-conversion` | Convert one existing local Codex skill into a governed package through preview-first, reviewer-visible migration. | Depends on quality gates |
| 3 | `clearing-governed-skill-remediation` | Use the quality gates to repair Clearing's weak governed capability state. | Operational follow-up |

## Why Split

The critical review found five blocking risks:

- strict validation rollout and backward compatibility were not defined
- candidate auto-create governance was not defined
- conversion safety and parity were ambiguous
- tool/script trust boundaries were underdefined
- Clearing remediation was product evidence, not core GovKB product scope

## Product Direction

GovKB should first make governed skill packages trustworthy. Existing-skill conversion should come after package quality gates exist. Clearing cleanup should use those product capabilities rather than drive them directly.

## Cross-Feature Decisions

1. Strict validation starts as opt-in for normal project validation, but is mandatory for candidate activation and future conversion writes.
2. Existing local skills and materialized skills are not deleted by these features.
3. Unsafe content is never copied into repo-governed memory; reports may include redacted metadata and reasons.
4. GovKB may package helper tools, but validation, conversion, and materialization do not execute project-owned scripts.
5. Clearing remains the proving case, but not part of the first product implementation slice.

## Superseded Artifacts

The following artifacts in this parent folder are historical planning material and must be refreshed or replaced before use:

- `context.md`
- `use-cases.md`
- `requirements-catalog.md`
- `poc-plan.md`
- `poc-output.md`
- `implementation-plan.md`
- `review.md`

The critical review remains useful as the split rationale:

- `business-requirements-critical-review.md`

## Acceptance Criteria

This parent split is complete when:

1. Each child feature has its own `business.md`.
2. The first child feature no longer depends on local Codex skill conversion.
3. The conversion feature explicitly depends on the quality-gates feature.
4. Clearing remediation is recorded as follow-up operational work.
