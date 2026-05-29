# Spec Brief — Memory Review Capability Evolution

Last updated: 2026-05-28

## Objective
Improve GovKB memory review so it can identify and stage durable capability improvements, not only append memory bullets.

The current review flow is useful for preserving domain knowledge, but it does not directly express when a governed capability should gain a reusable script, helper tool, prompt, checklist, runbook, or instruction upgrade. That leaves maintainers with useful lessons but still requires manual interpretation to convert repeated work into better governed skills.

## Source Artifacts
- `business.md`
- `business-context.md`
- `context.md`

## Problem Statement
GovKB governed skills are intended to become reusable operational capabilities. In practice, the scheduled memory review mostly produces append-only `references/long-term-memory.md` updates and occasional new capability candidates.

This is too narrow for mature governed skills. A review may discover that future sessions would benefit from a packaged script, a safer command wrapper, a stronger runbook, or a tool proposal tied to a capability. Today the classifier schema and review report do not provide a first-class place to capture that intent. As a result:

- repeated manual command sequences stay as prose instead of becoming reusable tools
- maintainers cannot easily see which capability should be upgraded
- script/tool opportunities are mixed into memory lessons or lost
- cron remains safe but not very productive for capability evolution
- higher reasoning may improve wording, but it cannot output artifacts that the schema does not support

## Business Value Snapshot
- reusable scripts or CLI wrappers
- prompt or checklist additions
- runbook or tool README additions
- instruction updates
- capability-bound tool candidates
- new capability candidates when no existing capability owns the workflow

## Scope Snapshot
- Extend the memory-review classifier contract to emit structured capability-evolution proposals.
- Add report sections for proposed scripts, tools, prompts, runbooks, and instruction changes.
- Persist staged proposals under repo-owned `.governed/` paths instead of local Codex memory paths.
- Keep scheduled cron reviews non-mutating for executable artifacts.
- Provide a manual apply or generation path that can turn an approved proposal into repo files.
- Support higher-reasoning manual review runs for capability-evolution extraction.
- Preserve existing append-only memory behavior and safety gates.

## Acceptance Snapshot
- Memory review reports include a distinct capability-evolution section when proposals exist.
- The classifier schema can represent proposed tools/scripts/prompts/runbooks independently from memory lessons.
- A run with no proposal opportunities behaves like the current memory review.
- A run with proposal opportunities stages reviewable artifacts without writing executable code.
- Existing `govkb validate --strict` behavior remains compatible.
- Existing Clearing and AIApps review cron jobs continue to run.
- Maintainers can tell exactly which proposal came from which review and source session.

## Review Readiness
- Open questions captured: 0
- Feedback source documents found: 0
- Tracker/reference status: not configured
- Pending feedback reconciliation: No
