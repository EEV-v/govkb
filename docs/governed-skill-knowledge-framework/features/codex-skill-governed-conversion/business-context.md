# Codex Skill Governed Conversion - Business Context

Last updated: 2026-05-01

## Business Purpose

GovKB already supports repo-governed capability packages and Codex materialization. Useful local Codex skills can still live outside the repo package, which makes their project knowledge harder to review, version, share, or apply consistently.

This feature gives maintainers a preview-first path to convert one existing local Codex skill into a governed package after quality gates exist. The goal is controlled migration of valuable local skills without copying unsafe content or changing the source local skill.

## Affected Workflow

1. A maintainer identifies one local Codex skill by name or direct directory path.
2. GovKB resolves and classifies the skill contents.
3. Preview shows target capability id, files to write, copied/transformed/rejected content, parity level, and strict-validation outcome.
4. Write mode creates one new governed package only when the preview is acceptable.
5. Normal `govkb apply codex` materializes the converted package back into Codex.

## Domain Terms

| Term | Meaning |
|---|---|
| Local Codex skill | A skill under a Codex home, usually with `SKILL.md`, `references/`, `prompts/`, `agents/`, or helper assets. |
| Governed package | Repo-owned capability package under `.governed/capabilities/<capability-id>/`. |
| Conversion preview | Non-mutating conversion plan and safety report. |
| Conversion write | Explicit creation of a new governed capability package. |
| Adapter-local content | Codex-specific presentation or runtime glue that should not become assistant-agnostic governed memory. |
| Parity level | Reviewer-visible explanation of how closely governed output matches the source skill. |

## Product And Process Precedent

- `governed-skill-quality-gates` is the required predecessor because conversion writes must target strict-valid packages.
- `src/govkb/adapters/codex/materialize.py` already supports materializing from `adapters/codex/SKILL.md`, root `SKILL.md`, `instructions.md`, or migration fallback.
- `src/govkb/core/contracts.py` already supports `[migration]` fields for source adapter, source path, and migration status.
- The parent split record keeps bulk migration and Clearing remediation out of the conversion MVP.

## Source-Backed Constraints

- Preview must write nothing.
- Source local skills must remain unchanged.
- Write mode creates new packages only and fails on existing targets.
- Unsafe values, raw transcripts, credential paths, secrets, and local user-home paths must not be copied into governed memory.
- Helper scripts can be copied only as reviewed package artifacts; conversion must not execute them.
- Converted output must pass strict validation before write success.

## Assumptions

- Direct source paths outside `--codex-home` are allowed when explicitly provided.
- The first implementation can use standard-library parsing for simple `SKILL.md` frontmatter unless tests prove a parser dependency is necessary.
- Conversion should always create canonical `instructions.md`, with `adapters/codex/SKILL.md` only for Codex-specific parity.
- Preview reports rejected content via console/JSON only; write mode records a redacted package report.

## Open Context Gaps

- Exact conversion-plan JSON shape is an engineering design detail.
- Exact redacted report filename can be decided in implementation planning; `docs/conversion-report.md` is the preferred default.
- Bulk conversion remains out of scope until one-skill conversion is proven.

## Sources

- `docs/governed-skill-knowledge-framework/features/codex-skill-governed-conversion/business.md` on 2026-05-01
- `docs/governed-skill-knowledge-framework/features/governed-skill-quality-gates/spec-handoff.md` on 2026-05-01
- `src/govkb/adapters/codex/materialize.py` on 2026-05-01
- `src/govkb/core/contracts.py` on 2026-05-01
- `docs/governed-skill-knowledge-framework/features/governed-skill-contract-and-migration/context.md` on 2026-05-01
