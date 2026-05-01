# Codex Skill Governed Conversion

## Summary

Add a preview-first workflow for converting one existing local Codex skill into a GovKB governed capability package.

This feature depends on `governed-skill-quality-gates`. Conversion must target the strict governed-skill package shape and must not write unsafe content into repo-governed memory.

## Business Problem

Useful Codex skills already exist outside GovKB. Some contain durable project knowledge, prompts, scripts, or memory that should become repo-owned and reviewable. Today there is no guided path to convert one of those skills into `.governed/` without manually copying files and risking unsafe or local-only content.

## Product Goal

Let maintainers safely inspect and convert one local Codex skill into a governed capability package.

Maintainers should be able to:

- preview what would be created before any write
- see what content is copied, transformed, rejected, or left adapter-local
- approve a target capability id and scope
- keep source local skills unchanged
- write a strict-valid governed package when the conversion is acceptable
- materialize the converted package back to Codex through normal GovKB apply

## Dependency

This feature must not start until `governed-skill-quality-gates` defines:

- strict package shape
- strict validation policy
- unsafe content rules
- tool conventions
- activation readiness rules

## MVP Scope

In scope:

- convert one local Codex skill at a time
- source can be a skill directory path or a skill name resolved from a Codex home
- preview mode is the default safe path
- write mode creates a new governed capability package only
- conversion classifies source content before writing
- safe helper scripts and fixtures may be copied into standard governed locations
- source local skill is never mutated

Out of scope:

- bulk conversion
- updating existing governed capability packages
- perfect semantic rewriting of all skill memory
- converting Claude or Copilot artifacts
- running converted scripts
- deleting or disabling source local skills

## Conversion Review Experience

Conversion preview must show:

- source skill path and detected skill name
- proposed capability id and human name
- proposed governed package path
- files to create
- files to copy unchanged
- files to transform
- content rejected with reason
- content requiring manual review
- strict validation issues
- proposed parity level
- next safe action

Preview must write nothing.

## Source Content Classification

Every source item must be classified as one of:

| Class | Meaning | Outcome |
|---|---|---|
| Governed | Durable project knowledge or reusable workflow content | Eligible for governed package |
| Adapter-local | Codex-specific presentation or runtime glue | Keep only under `adapters/codex/` or leave out |
| Tool | Reusable helper script or fixture | Eligible for `tools/` after safety checks |
| Unsafe | Secret, raw transcript, local credential path, or sensitive incident data | Do not copy; report redacted metadata |
| Manual review | Ambiguous or too context-heavy for automatic placement | Report for reviewer decision |

## Parity Levels

The conversion plan must label expected parity:

| Parity | Meaning |
|---|---|
| Exact content copy | Governed output preserves the source content after safety checks |
| Governed semantic parity | Governed output preserves intent but changes structure or wording |
| Adapter-local fallback | Codex-specific behavior remains adapter-local or legacy-only |
| Rejected | Source item is unsafe or not reusable |

Converted packages do not need to be byte-for-byte identical to source skills. Approved differences must be visible in the conversion plan.

## Write Requirements

Write mode must:

1. require an explicit write flag
2. create a new capability package only
3. fail on existing target package unless a later update mode exists
4. write migration metadata
5. copy only safe governed content
6. preserve source local skill unchanged
7. run strict validation before success
8. print rollback guidance

## Migration Metadata

Converted packages must record:

- source adapter: `codex`
- source skill name or path
- conversion timestamp
- conversion status
- parity level
- rejected item count
- whether strict validation passed

## Safety Requirements

Conversion must never copy these into governed memory:

- raw assistant transcripts
- secrets or token-like strings
- local credential-file paths
- local user-home paths
- raw production evidence
- incident-specific identifiers unless already sanitized and approved

Rejected content is reported with path, class, and reason, without copying the unsafe value.

## Acceptance Criteria

1. Maintainer can preview conversion for one local Codex skill without writing files.
2. Preview clearly shows target package, copied content, rejected content, manual-review content, and validation status.
3. Write mode creates a new governed capability package when preview is acceptable.
4. Write mode fails if the target package already exists.
5. Source local skill remains unchanged.
6. Safe long-term memory, prompts, and helper scripts can be preserved in governed locations.
7. Unsafe content is rejected and not copied into repo-governed memory.
8. Converted package passes strict validation before write succeeds.
9. Converted package can be materialized with normal GovKB Codex apply.
10. Rollback path is clear: remove the new governed capability package or revert the repo change.
