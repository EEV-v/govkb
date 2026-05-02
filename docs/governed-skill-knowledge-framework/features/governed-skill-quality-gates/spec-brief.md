# Spec Brief — Governed Skill Quality Gates

Last updated: 2026-05-01

## Objective
Define the strict business rules that make a GovKB governed skill package trustworthy before it can be activated, materialized, or used as a migration target.

This is the first implementation slice split out of `governed-skill-contract-and-migration`. It focuses on package standards, validation, lifecycle, data safety, tool conventions, and candidate activation gates. It does not convert existing local skills.

## Source Artifacts
- `business.md`
- `business-context.md`
- `context.md`

## Problem Statement
GovKB can currently validate a governed capability when its TOML contract loads, but syntactic validity is not enough. A project can end up with an active capability that has a vague name, generic memory, invalid commands, local credential-file paths, or unreviewed helper scripts.

This damages trust in governed knowledge because maintainers cannot tell whether a capability is truly reusable, safe, and ready for redistribution.

## Business Value Snapshot
- see whether a governed skill package is structurally complete
- understand why a package is not activation-ready
- prevent weak candidates from becoming active skills
- package helper tools without making them hidden execution risks
- keep existing projects working while stricter rules are introduced

## Scope Snapshot
- strict governed-skill package convention
- strict validation mode and issue reporting
- candidate activation gate based on strict validation
- governed skill lifecycle states
- memory, naming, data, and tooling quality rules
- backward-compatible rollout policy

## Acceptance Snapshot
- Maintainer can run strict validation and see package-quality issues with exact locations.
- A complete domain-specific governed skill package passes strict validation.
- A package with placeholder memory fails strict activation readiness.
- A package with invalid repo-relative command paths fails strict activation readiness.
- A package containing local credential-file paths or token-like strings fails strict activation readiness.
- A package with `tools/scripts/` but no `tools/README.md` is reported.
- Candidate auto-create cannot mark a strict-invalid package active.
- Generic capability ids require explicit justification and approval before activation.

## Review Readiness
- Open questions captured: 0
- Feedback source documents found: 0
- Tracker/reference status: not configured
- Pending feedback reconciliation: No
