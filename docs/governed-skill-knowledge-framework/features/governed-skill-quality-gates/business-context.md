# Governed Skill Quality Gates - Business Context

Last updated: 2026-05-01

## Business Purpose

GovKB is the repo-native source of truth for reusable AI collaboration knowledge. The current product can load syntactically valid governed capability contracts and materialize Codex skills, but syntactic validity does not prove that a capability is trustworthy, safe, reviewable, or activation-ready.

This feature creates the first strict quality gate for governed skill packages. It protects maintainers from weak active capabilities with vague ids, placeholder memory, local-only paths, unsafe credential references, or unreviewed helper scripts.

## Affected Workflow

The affected workflow starts when a project maintainer creates, reviews, auto-creates, or materializes a governed capability:

1. A capability package exists under `.governed/capabilities/<capability-id>/`.
2. GovKB validates the project package.
3. Candidate auto-create may turn ready candidates into capabilities.
4. `govkb apply codex` materializes derived assistant-local output.
5. Future conversion work may write governed packages from existing local Codex skills.

Strict quality gates should fit into that flow without breaking existing normal validation or materialization during rollout.

## Domain Terms

| Term | Meaning |
|---|---|
| Governed package | Repo-owned `.governed/` project package that is the source of truth for project AI knowledge. |
| Governed capability | One capability contract plus instructions, memory, prompts, and optional adapter/tool assets under `.governed/capabilities/<capability-id>/`. |
| Strict validation | Additional package-quality validation beyond TOML/schema loading. |
| Candidate | A staged possible governed capability under `.governed/candidates/`, usually produced from repeated unmatched work. |
| Activation | Promotion of a candidate/package into active capability use for routing, learning, and materialization. |
| Materialization | Derived assistant-local output, currently Codex skills, generated from repo-governed source. |

## Product And Process Precedent

- `README.md` lists `govkb validate`, `govkb create capability`, `govkb apply codex`, and candidate flows as current product surface.
- `docs/governed-skill-knowledge-framework/business.md` defines `.governed/` as the source of truth and assistant-local files as derived outputs.
- Existing MVP requirements require controlled self-improvement, staged new capability candidates, audit reports, and controlled migration of existing local assistant artifacts.
- `docs/governed-skill-knowledge-framework/mvp-plus-test-plan.md` already treats candidate quality, fact quality, no transcript excerpts, and redistribution as validation goals.
- The parent split record in `governed-skill-contract-and-migration` established that quality gates must precede Codex skill conversion and Clearing remediation.

## Source-Backed Constraints

- Normal `govkb validate` should remain backward-compatible at first because existing projects may not pass strict rules immediately.
- Strict validation must be mandatory before candidate activation and future conversion writes.
- Existing local skills and materialized skills must not be deleted by this feature.
- GovKB may package helper tools, but validation, conversion, and materialization must not execute package-owned scripts.
- Unsafe content must not be copied into governed memory; rejected or unsafe findings may be reported with redacted metadata and reasons.

## Assumptions

- First implementation supports Codex materialization only; Claude and Copilot adapter work remains out of scope.
- Strict validation can be introduced as an opt-in flag or explicitly named command path for normal validation.
- Candidate approval state should be stored before activation, and active capability lifecycle/approval state should remain visible after activation.
- Credential path detection can start with deterministic path/content indicators rather than a full secret-scanning engine.

## Open Context Gaps

- The exact TOML field names for lifecycle and approval metadata are an engineering design choice for implementation planning.
- Deprecated capability routing behavior is deferred because the first slice only needs to prevent weak new activation.
- The timeline for promoting strict validation to default normal validation is deferred until real project cleanup data exists.

## Sources

- `README.md` on 2026-05-01
- `docs/governed-skill-knowledge-framework/business.md` on 2026-05-01
- `docs/governed-skill-knowledge-framework/implementation-plan.md` on 2026-05-01
- `docs/governed-skill-knowledge-framework/mvp-plus-test-plan.md` on 2026-05-01
- `docs/governed-skill-knowledge-framework/features/governed-skill-contract-and-migration/business.md` on 2026-05-01
