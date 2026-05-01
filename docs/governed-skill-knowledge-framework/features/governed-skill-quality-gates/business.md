# Governed Skill Quality Gates

## Summary

Define the strict business rules that make a GovKB governed skill package trustworthy before it can be activated, materialized, or used as a migration target.

This is the first implementation slice split out of `governed-skill-contract-and-migration`. It focuses on package standards, validation, lifecycle, data safety, tool conventions, and candidate activation gates. It does not convert existing local skills.

## Business Problem

GovKB can currently validate a governed capability when its TOML contract loads, but syntactic validity is not enough. A project can end up with an active capability that has a vague name, generic memory, invalid commands, local credential-file paths, or unreviewed helper scripts.

This damages trust in governed knowledge because maintainers cannot tell whether a capability is truly reusable, safe, and ready for redistribution.

## Product Goal

Give maintainers a clear governed-skill quality gate.

Maintainers should be able to:

- see whether a governed skill package is structurally complete
- understand why a package is not activation-ready
- prevent weak candidates from becoming active skills
- package helper tools without making them hidden execution risks
- keep existing projects working while stricter rules are introduced

## Users

- Maintainers who own `.governed/` packages.
- Reviewers who approve candidate activation.
- Engineers who consume materialized assistant-local skills.
- Future conversion workflows that need a trusted package target.

## MVP Scope

In scope:

- strict governed-skill package convention
- strict validation mode and issue reporting
- candidate activation gate based on strict validation
- governed skill lifecycle states
- memory, naming, data, and tooling quality rules
- backward-compatible rollout policy

Out of scope:

- converting existing local Codex skills
- bulk migration
- direct cleanup of Clearing's current `.governed` package
- Claude or Copilot adapter work
- executing package-owned scripts

## Governed Skill Lifecycle

GovKB must distinguish these states:

| State | Meaning | Allowed Outcome |
|---|---|---|
| Draft | Capability package exists but has not passed strict review | Can be edited and validated |
| Strict-valid | Package passes strict quality checks | Can be considered for approval |
| Approved | Reviewer has accepted id, scope, memory, tools, and safety posture | Can be activated |
| Active | Capability can participate in routing, memory review, and materialization | Can be used by adapters |
| Rejected | Candidate or package is not acceptable in current form | Cannot activate |
| Deprecated | Capability remains for compatibility but should not receive new routing or learning | Existing users can migrate away |

Candidate auto-create may create draft packages or reviewable candidates, but it must not mark a package active unless the package is strict-valid and approved.

## Governed Skill Package Requirements

A governed skill is represented by one capability package:

```text
<project-root>/.governed/capabilities/<capability-id>/
```

Required package files:

- `capability.contract.toml`
- `instructions.md`
- `references/long-term-memory.md` when memory is enabled
- `prompts/initialize-kb.md`

Standard optional locations:

- `adapters/<assistant>/` for assistant-specific presentation files
- `docs/` for capability-owned runbooks and review notes
- `tools/scripts/` for governed helper scripts
- `tools/fixtures/` for sanitized fixtures
- `tools/README.md` for tool purpose, safety, and usage

All package references to project artifacts must use repo-relative paths unless the value is explicitly documented as user-provided runtime input.

## Naming And Routing Requirements

Capability ids must be lower kebab-case and must describe the durable domain or workflow.

Good ids:

- `corporate-actions-alert-cleanup`
- `fix-dropcopy-ingest-resilience`
- `golden-security-master-review`
- `backend-local-stack-workflow`

Weak generic ids such as `local-stack-workflow`, `workflow-review`, or `project-workflow` require all of the following:

- an explicit scope statement explaining why the capability is intentionally generic
- at least two use cases that are not tied to one domain feature
- reviewer approval before activation

Routing aliases and hints must help discover the domain. They must not be padded with generic words like "local", "workflow", "governed", or "reusable" unless those words are genuinely part of the domain.

## Memory Requirements

`references/long-term-memory.md` must use the sections declared in the contract.

Default memory taxonomy:

| Section | Business Meaning |
|---|---|
| Working Agreement | How future work in this capability should be approached |
| Stable Workflows | Repeatable workflow steps or review gates |
| Commands And Verification | Commands, working directories, prerequisites, and expected evidence |
| Code And Docs Map | Durable repo-relative source, test, docs, and artifact locations |
| Authority Rules | Which governed source wins when references conflict |

Memory bullets must be durable, reusable, action-oriented, and future-facing.

Memory must not keep:

- TODO/scaffold placeholders after activation
- one-off task status
- incident ids or exact timestamps
- raw assistant transcript text
- secrets, tokens, passwords, or credential-file paths
- local user-home paths
- environment trivia that only applies to one machine

Commands in memory must include enough context to run safely, including working directory when needed. Repo paths in memory must exist unless clearly marked as planned.

## Data Classification

Allowed in governed memory:

- reusable workflow rules
- repo-relative paths to source, tests, docs, and sanitized fixtures
- non-secret command examples
- high-level operational lessons without incident identifiers

Restricted to reviewed docs or redacted reports:

- sensitive but non-secret operational context
- project identifiers that are useful but not necessary in memory
- sanitized examples that are clearly synthetic or redacted

Forbidden in governed memory:

- secrets or token-like strings
- local credential-file paths
- raw assistant transcripts
- raw production evidence
- account identifiers, customer identifiers, exact incident timestamps, or ticket-specific state unless explicitly approved for a sanitized artifact

## Tooling Requirements

GovKB may package helper tools with a governed skill, but it must not execute those tools during validation, candidate activation, conversion, or materialization.

Tool classes:

| Class | Location | Rules |
|---|---|---|
| Docs-only helper | `docs/` or `tools/README.md` | Describes workflow without executable behavior |
| Read-only script | `tools/scripts/` | Must document inputs and avoid mutation |
| Mutating script | `tools/scripts/` | Must support `--dry-run` or `--preview` and must not run by default |
| Fixture | `tools/fixtures/` | Must be sanitized and safe to commit |

If `tools/scripts/` or `tools/fixtures/` exists, `tools/README.md` is required.

## Strict Validation Policy

GovKB must provide strict validation with structured issues.

Issue severities:

- `error`: blocks activation and future conversion writes
- `warning`: does not block existing project operation, but indicates cleanup is needed
- `info`: advisory context for reviewers

Rollout policy:

- normal `govkb validate` remains backward-compatible at first
- strict validation is opt-in for normal project checks
- strict validation is mandatory before candidate activation
- strict validation is mandatory before any future existing-skill conversion write
- strict failures do not delete or disable existing materialized local skills

Validation output must identify location, severity, rule id, and message.

## Candidate Activation Requirements

Candidate auto-create must not silently create active governed skills.

Before activation:

1. candidate has enough repeated evidence or explicit maintainer request
2. package id and scope are reviewer-visible
3. generated package passes strict validation
4. reviewer approves activation
5. activation is auditable

If validation fails, the candidate remains reviewable and the report lists exact reasons.

## Backward Compatibility

Existing governed packages and materialized local skills remain usable.

Strict validation may report warnings or errors for existing packages, but normal apply/materialization remains available unless a maintainer explicitly opts into strict enforcement for that operation.

## Acceptance Criteria

1. Maintainer can run strict validation and see package-quality issues with exact locations.
2. A complete domain-specific governed skill package passes strict validation.
3. A package with placeholder memory fails strict activation readiness.
4. A package with invalid repo-relative command paths fails strict activation readiness.
5. A package containing local credential-file paths or token-like strings fails strict activation readiness.
6. A package with `tools/scripts/` but no `tools/README.md` is reported.
7. Candidate auto-create cannot mark a strict-invalid package active.
8. Generic capability ids require explicit justification and approval before activation.
9. Existing projects can still use normal validation and materialization during rollout.
10. Clearing's current weak `local-stack-workflow` shape can be flagged by strict validation without making Clearing cleanup part of this feature.
