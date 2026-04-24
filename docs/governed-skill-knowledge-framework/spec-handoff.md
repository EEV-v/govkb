# Spec Handoff — Governed Skill Knowledge Framework

## Handoff Status
- Ready for engineering cookbook: Yes
- Status: ready
- Blocking questions remaining: 0
- Approved decisions captured: 12
- Deferred decisions captured: 6

## Required Inputs For Engineering
- business.md
- business-context.md
- context.md
- spec-brief.md
- open-questions.md
- decision-log.md
- scope-lock.md
- requirements-catalog.md
- poc-plan.md
- poc-output.md
- use-cases.md
- implementation-plan.md

## Approved Decisions
- The governed framework is contract-driven and capability-agnostic.
- The canonical project-governed source lives under `<project-root>/.governed/`.
- Governed capabilities declare `capability.contract.toml`.
- Assistant adapters are repo-defined materialization targets and may tighten governance but may not weaken it.
- Governed release/install manifests drive local setup through `govkb apply codex` from git-tracked revisions.
- `.governed/` stays the repo package folder and `govkb` is the CLI/app alias.
- The first increment proves the self-improving loop: existing governed capabilities can gain expertise from real work, new capability candidates are staged from repeated unmatched patterns, and promoted learning can be redistributed to another local setup.
- Brand-new governed capability activation is review-gated in the first increment; automatic staging is allowed, automatic activation is not.
- The first increment extends `codex-memory-review` as the first live adapter instead of replacing it.
- The first increment migrates the current governed memory-bearing Codex skills and keeps a legacy fallback path for unmigrated local assets.
- Invalid contracts and adapter conflicts surface as run-health warnings instead of silently falling through.
- Skill creator override, broad retrofit work, and fully working non-Codex adapters remain explicit follow-up phases.

## Deferred / Watch Items
- Default skill creator override.
- Bulk retrofit of remaining skills.
- Runtime prompt assembly from project-local adapter fragments.
- Interactive staged-memory review tooling.
- Fully working Claude and Copilot adapters.
- Exact chatbot cost-reduction measurement.

## Remaining Blockers
- No blocking questions remain.

## Tracker Context
- Azure Epic: not linked
- Azure Feature: not linked
- Monday: not linked

## Next Step
- Engineering can review and execute `implementation-plan.md`.
- After the Codex-first adapter lands, a follow-up feature can override the skill creator and add Claude/Copilot adapter materialization on top of the same repo package.
