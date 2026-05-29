# Memory Review Capability Evolution - Business Context

Last updated: 2026-05-28

## Business Purpose

GovKB exists to turn useful AI-assisted project work into governed, repo-native knowledge that can be reviewed, versioned, redistributed, and materialized into assistant-local setups. The current memory-review loop already captures durable memory lessons and stages new capability candidates, but it does not have a first-class way to propose improvements to an existing capability's tool set, scripts, prompts, runbooks, or instructions.

This feature is about making governed skills more operationally useful. A mature governed capability should accumulate reusable assets when repeated work proves that a script, wrapper, checklist, or runbook would save future sessions from rediscovering the same procedure.

## Affected Workflow

The affected workflow is the Codex memory-review adapter and downstream governance review:

1. Discover completed sessions for a governed project.
2. Build a compact evidence package.
3. Classify reusable learning.
4. Apply, stage, reject, or report the result.
5. Promote approved governed changes into repo-owned `.governed/` state.
6. Materialize the accepted package back into local assistant skills.

The proposed change adds a capability-evolution lane alongside existing memory candidates and semantic capability candidates.

## Domain Terms

| Term | Meaning |
|---|---|
| Governed capability | A repo-owned skill package under `.governed/capabilities/<capability-id>/` with contract, instructions, memory, prompts, and optional tools. |
| Memory candidate | A proposed durable bullet for an existing memory target such as `references/long-term-memory.md`. |
| Semantic capability candidate | A proposed new governed capability for repeated or unmatched work that does not fit an existing capability. |
| Capability-evolution proposal | A proposed change to an existing governed capability's assets, such as a script, tool wrapper, prompt, runbook, checklist, or instruction update. |
| Strict validation | GovKB validation mode that checks activation readiness, safety, package shape, memory quality, and tool conventions. |
| Materialization | Applying repo-governed source into assistant-local files such as Codex skills and memory-review tasks. |
| Scheduled review | Cron or automated memory-review execution. It must remain conservative and must not create executable files without review. |

## Product And Process Precedent

- `README.md` lists `govkb review-memory --assistant codex`, governed learning classification, staging, auto-promotion, audit reports, and optional VS Code views as current GovKB scope.
- `docs/governed-skill-knowledge-framework/business.md` defines the MVP goal: reusable lessons should live in git, be reviewable, auditable, assistant-agnostic, and locally materializable.
- `docs/governed-skill-knowledge-framework/business.md` already classifies learning as existing capability expertise, new capability candidates, reusable project knowledge, or rejected content.
- `docs/governed-skill-knowledge-framework/features/governed-skill-quality-gates/business.md` defines optional governed tool locations such as `tools/scripts/`, `tools/fixtures/`, and `tools/README.md`, and says validation must not execute those tools.
- `docs/governed-skill-knowledge-framework/features/vscode-learning-discovery-progress/context.md` establishes that existing skill updates and new capability candidates are separate learning outcomes, and that a zero-candidate result is not the same as zero learning.

## Constraints

- Existing memory-review behavior must remain backward-compatible.
- Scheduled review must not auto-write executable scripts or direct instruction rewrites.
- Proposed tool/script artifacts must be reviewable before application.
- Proposal storage should be repo-owned, not only local `$CODEX_HOME` derived output.
- Strict validation and existing governed tool conventions should remain the safety gate before activation or materialization.
- Raw assistant transcripts, secrets, local credential paths, customer data, and production evidence must not be stored in proposals.

## Assumptions

| ID | Assumption | Risk If Wrong |
|---|---|---|
| A1 | The change belongs in GovKB because the memory-review adapter, classifier schema, candidate flow, strict validation, and CLI live there. | If this is only treated as a Clearing package problem, other projects will keep the same limitation. |
| A2 | The first implementation slice should stage proposals but not apply them automatically. | If users expect fully automatic script generation, the MVP may feel incomplete. |
| A3 | Existing strict validation tool rules are the right baseline for proposed scripts and fixtures. | If proposal safety needs stricter rules, implementation may under-spec approval metadata. |
| A4 | Higher model reasoning can improve proposal quality but cannot solve the missing schema and workflow by itself. | If schema changes are skipped, reviews will continue to lose tool/script opportunities. |

## Resolved Scope Decisions

- Proposal storage uses one project-level inbox at `.governed/review-proposals/<proposal-id>/`.
- New governed capability candidates continue to use `.governed/candidates/<candidate-id>/`.
- Proposal review and application use a dedicated `govkb proposals` command family.
- Memory review always looks for high-confidence capability-evolution opportunities, while cron only stages proposals.
- File generation requires explicit approval metadata before apply.
- The first implementation slice supports `script`, `wrapper`, `prompt`, `runbook`, and `instructions_update`.

## Sources

| Source | Purpose | Access Date |
|---|---|---|
| `README.md` | Current GovKB command and scope summary. | 2026-05-28 |
| `docs/README.md` | Documentation map. | 2026-05-28 |
| `docs/governed-skill-knowledge-framework/business.md` | Product goals, learning capture, audit, and safety rules. | 2026-05-28 |
| `docs/governed-skill-knowledge-framework/implementation-plan.md` | Existing memory-review adapter and learning-flow design. | 2026-05-28 |
| `docs/governed-skill-knowledge-framework/features/governed-skill-quality-gates/business.md` | Governed tool package and strict validation precedent. | 2026-05-28 |
| `docs/governed-skill-knowledge-framework/features/vscode-learning-discovery-progress/context.md` | Learning outcome visibility precedent. | 2026-05-28 |
