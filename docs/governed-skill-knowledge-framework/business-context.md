# Business Context — Governed Skill Knowledge Framework

Last updated: 2026-04-22

## Business Purpose

- Remove the central maintenance bottleneck from governed capability growth.
- Make project AI collaboration self-improving: real team work should feed reusable lessons back into governed project knowledge.
- Keep project-only knowledge in the git repo that owns it instead of in Codex-specific overlays.
- Let the scheduler learn from new governed capabilities by contract instead of by bespoke Python edits.
- Make the knowledge framework portable so the same operating model can be reused in other projects and across assistants.
- Make local assistant setup a materialized output from repo-tracked governed releases so learned improvements can be shared across the team.

## Affected Operational Workflow

1. The project stores governed knowledge, capability definitions, adapters, and release manifests under `.governed/`.
2. `govkb apply codex` materializes a chosen repo revision into local Codex setup for the first live adapter.
3. The team continues normal project work with AI assistance.
4. The scheduled Codex memory-review adapter scans completed sessions.
5. The framework resolves repo capabilities plus adapter materialization rules.
6. High-confidence reusable lessons update existing governed capability expertise only when governance allows it.
7. Repeated unmatched patterns are staged as new governed capability candidates with evidence.
8. Ambiguous, approval-gated, low-confidence, sensitive, duplicate, or local-only lessons are staged or rejected.
9. Reports and patches remain the audit trail for what was learned, applied, staged, rejected, promoted, or skipped.
10. Promoted repo updates are redistributed when another teammate runs `govkb apply codex`.

## Domain Terms

| Term | Meaning in this feature | Current precedent |
|---|---|---|
| Governed capability | A governed unit of reusable behavior and knowledge that can be materialized for one or more assistants | Replaces the narrower project-only “Codex skill overlay” concept |
| Capability contract | Machine-readable declaration of routing, governance, and memory targets for a governed capability | New repo-native contract |
| Project governed package | The git-tracked project source of truth under `.governed/` | New concept requested in-thread |
| Assistant adapter | Materialization layer that projects repo-native governed content into a local assistant-specific setup | Codex is the first live adapter; Claude/Copilot are future targets |
| Global reusable memory | Durable reusable lessons shared across projects or user-level capability libraries | Current memory-bearing Codex skills are the nearest precedent |
| Project-only governed knowledge | Durable lessons that only make sense inside one repo or project | New canonical location is under `<project-root>/.governed/knowledge/...` |
| Governed release manifest | Git-tracked install/update description for a repo revision or release | New concept for `govkb apply codex` |
| Memory review adapter | The first live adapter that scans assistant sessions and proposes governed knowledge updates | Current Codex scheduler at `/home/ev/.codex/bin/codex-memory-review` |
| Capability expertise update | A reusable lesson added to an existing governed capability from completed project work | Current memory-bearing skill updates are the nearest precedent |
| New capability candidate | A staged proposal for a new governed capability based on repeated unmatched project work | Future skill creator override will automate scaffolding later |

## Relevant Product / Process Precedent

- Codex skills already exist as directories with `SKILL.md`, optional `references/`, optional `agents/`, and in some cases durable memory files.
- Memory-bearing skills already treat the memory file as a maintained knowledge base rather than a transcript dump.
- Some reviewer skills already separate stable context from mutable memory via files such as:
  - `references/long-term-memory.md`
  - `references/context-sources.md`
  - `references/shared-kb.md`
- The current scheduler already has the right high-level operating model:
  - session discovery
  - sanitization
  - classification
  - local validation
  - apply/stage/reject
  - auditable reports
- The main gap is ownership: routing and governance are still partly encoded in the scheduler instead of living with the governed repo package.

## Source-Backed Constraints And Business Rules

- Project-only governed knowledge must stay in the git repo rather than polluting assistant-local installs.
- The framework must remain conservative; missing a lesson is cheaper than writing noisy memory.
- Explicit-acceptance capabilities cannot lose that protection just because an assistant adapter exists.
- Session discovery must continue to use both the session index and real session files so the framework does not silently miss eligible chats.
- The framework needs to support future dynamic governed capability creation, which means the scheduler cannot require hardcoded knowledge of skill ids or Codex-only overlay paths.
- Existing governed skills can grow from high-confidence real work; new governed skills must be staged for review before activation.
- The scheduled task already runs daily and has established audit artifacts; the first live adapter should keep that operating model intact.
- The whole project-governed source should live in git and be materializable into local Codex setup by `govkb apply codex`.
- The first increment should prove reusable learning capture and redistribution, not exact chatbot cost reduction.

## Implementation Findings That Shape Scope

- The current script discovers memory-bearing Codex skills from the filesystem, but routing is still partially hardcoded through `KEYWORD_SKILL_HINTS`.
- Existing project docs do not expose a repo-native governed package; project-only knowledge is still being pulled toward assistant-local packaging.
- Existing Codex skill package layout is strong enough to serve as the first adapter target, but it should not be the project source of truth.
- Current reports, staged patches, applied patches, and state tracking are already useful and should be preserved rather than replaced.
- Recent fixes already improved the scheduler in important ways:
  - session discovery uses the union of index plus real session files
  - self-referential maintenance sessions are screened out
  - environment-local lessons are rejected
  - discovery health is reported
- Those fixes are a good foundation for the first Codex adapter; this feature should not rewrite the pipeline from scratch.
- The strongest product value is team-level compounding knowledge: once one person solves a project-specific problem with AI, the reusable part can become governed repo knowledge for everyone.

## Assumptions

- The first increment should focus on the repo-native governed package, Codex adapter materialization, and `govkb apply codex`, not on full runtime prompt composition for every assistant.
- A contract format with a built-in Python parser is preferable so the first adapter does not gain a new runtime dependency just to load contracts.
- Codex is the first live adapter; Claude and Copilot can remain contract-defined targets until later phases.
- Cost reduction is expected to come from fewer rediscovered commands, less repeated context explanation, and better routing, but the MVP measures capture/reuse first.

## Open Questions Created By Context

- No blocking business-context questions remain. Implementation choices are locked in the decision log for this first increment.

## Sources

- `Clearing-docs/docs/features/Governed Skill Knowledge Framework/business.md` — accessed 2026-04-21
- `/home/ev/.codex/bin/codex-memory-review` — accessed 2026-04-21
- `/home/ev/.codex/session_index.jsonl` and `/home/ev/.codex/sessions/*` behavior observed during scheduler review on 2026-04-21
- Skill package layout reviewed on 2026-04-21 under:
  - `/mnt/c/Users/Ev/.codex/skills/clearing-master-reviewer`
  - `/mnt/c/Users/Ev/.codex/skills/clearing-review-corporate-actions-processing`
  - `/mnt/c/Users/Ev/.codex/skills/clearing-review-internal-account-governance`
  - `/mnt/c/Users/Ev/.codex/skills/clearing-bugfixer`
- Existing durable-memory file locations reviewed on 2026-04-21 under `/mnt/c/Users/Ev/.codex/skills/*/references/*memory*.md`
- Additional product-direction constraints provided in-thread on 2026-04-21:
  - project-only KB should not be constrained by Codex skills
  - the whole flow should be reusable for Claude and Copilot
  - the project-governed source should live in git and be applied or updated into local setup per governed release/install prompt
