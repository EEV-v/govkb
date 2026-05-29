# Memory Review Capability Evolution

## Summary

Improve GovKB memory review so it can identify and stage durable capability improvements, not only append memory bullets.

The current review flow is useful for preserving domain knowledge, but it does not directly express when a governed capability should gain a reusable script, helper tool, prompt, checklist, runbook, or instruction upgrade. That leaves maintainers with useful lessons but still requires manual interpretation to convert repeated work into better governed skills.

## Business Problem

GovKB governed skills are intended to become reusable operational capabilities. In practice, the scheduled memory review mostly produces append-only `references/long-term-memory.md` updates and occasional new capability candidates.

This is too narrow for mature governed skills. A review may discover that future sessions would benefit from a packaged script, a safer command wrapper, a stronger runbook, or a tool proposal tied to a capability. Today the classifier schema and review report do not provide a first-class place to capture that intent. As a result:

- repeated manual command sequences stay as prose instead of becoming reusable tools
- maintainers cannot easily see which capability should be upgraded
- script/tool opportunities are mixed into memory lessons or lost
- cron remains safe but not very productive for capability evolution
- higher reasoning may improve wording, but it cannot output artifacts that the schema does not support

## Product Goal

Add a capability-evolution lane to GovKB memory review.

The review should continue to preserve safe durable memory, while also staging structured proposals for governed capability improvements such as:

- reusable scripts or CLI wrappers
- prompt or checklist additions
- runbook or tool README additions
- instruction updates
- capability-bound tool candidates
- new capability candidates when no existing capability owns the workflow

The default scheduled review must remain conservative. It should stage proposals for maintainer review rather than automatically writing executable code.

## Users

- Project maintainers who review GovKB learning output.
- Engineers who want governed skills to accumulate practical tools, not just prose.
- Future assistant sessions that rely on governed capabilities for repeatable workflows.
- Reviewers who need a clear distinction between domain memory and proposed executable/helper artifacts.

## MVP Scope

In scope:

- Extend the memory-review classifier contract to emit structured capability-evolution proposals.
- Add report sections for proposed scripts, tools, prompts, runbooks, and instruction changes.
- Persist staged proposals under repo-owned `.governed/` paths instead of local Codex memory paths.
- Keep scheduled cron reviews non-mutating for executable artifacts.
- Provide a manual apply or generation path that can turn an approved proposal into repo files.
- Support higher-reasoning manual review runs for capability-evolution extraction.
- Preserve existing append-only memory behavior and safety gates.

Out of scope:

- Auto-writing executable scripts from cron.
- Auto-approving or activating new governed capabilities without maintainer review.
- Refactoring all existing Clearing capability memories.
- Designing a full workflow-builder UI.
- Changing external tracker behavior.
- Storing raw assistant transcripts, private session details, secrets, or customer evidence in proposals.

## Desired Workflow

1. Scheduled memory review runs as it does today.
2. The classifier emits both memory candidates and capability-evolution proposals when supported by session evidence.
3. Memory candidates follow the existing auto-apply, stage, reject, and promotion rules.
4. Capability-evolution proposals are staged under `.governed/review-proposals/<proposal-id>/` as one project-level review inbox with:
   - target capability
   - proposal type
   - proposed repo-relative path
   - purpose
   - inputs and outputs
   - safety constraints
   - evidence summary
   - suggested verification command
   - reason the proposal should not be auto-applied by cron
5. Maintainers review the proposals.
6. A manual `govkb proposals apply <proposal-id>` command can generate or apply an approved proposal, then run validation and tests.

## Approved Decisions

- Stage capability-evolution proposals in a project-level queue at `.governed/review-proposals/<proposal-id>/`.
- Keep `.governed/candidates/<candidate-id>/` for new governed capability candidates only; do not overload it for improvements to existing capabilities.
- Apply proposals through a dedicated `govkb proposals` command family, starting with `list`, `show`, and `apply`.
- Let memory review always look for high-confidence capability-evolution opportunities; no separate discovery flag is required.
- Keep cron safe by staging proposals only. Cron must not create executable files, rewrite instructions, or apply proposals.
- Require explicit approval metadata before any proposal can generate files: `status = "approved"`, approver, approved timestamp, target capability, approved proposal type, approved output paths, safety class, and verification command.
- First implementation slice supports `script`, `wrapper`, `prompt`, `runbook`, and `instructions_update` proposals. New capability creation continues through the existing candidate flow.

## Proposal Types

The MVP should support at least:

| Type | Example |
|---|---|
| `script` | Add `tools/scripts/query_reconciliation_logs.py` for a capability-owned read-only log query workflow. |
| `wrapper` | Add a safer command wrapper around a repeated DB or API investigation command. |
| `prompt` | Add a reusable prompt for review or initialization work. |
| `runbook` | Add `tools/README.md` or `docs/runbook.md` for repeated operator steps. |
| `instructions_update` | Strengthen `instructions.md` when memory alone is not enough. |

New capability creation stays on the existing `.governed/candidates/<candidate-id>/` path and is not part of the first proposal-apply slice.

## Safety Rules

- Cron must not create executable scripts or modify capability instructions directly.
- Generated executable proposals must default to reviewed/manual application.
- Staged proposal metadata must live under `.governed/review-proposals/<proposal-id>/`.
- Approved output paths must be under `.governed/capabilities/<capability-id>/`.
- Script proposals must declare read-only versus mutating behavior.
- Mutating script proposals must require `--dry-run`, `--preview`, or an equivalent explicit confirmation pattern.
- Proposals must not contain secrets, local credential paths, raw transcript text, customer identifiers, or production evidence.
- Existing strict validation rules for governed tools should apply before activation or materialization.

## Acceptance Criteria

- Memory review reports include a distinct capability-evolution section when proposals exist.
- The classifier schema can represent proposed tools/scripts/prompts/runbooks independently from memory lessons.
- A run with no proposal opportunities behaves like the current memory review.
- A run with proposal opportunities stages reviewable artifacts without writing executable code.
- Existing `govkb validate --strict` behavior remains compatible.
- Existing Clearing and AIApps review cron jobs continue to run.
- Maintainers can tell exactly which proposal came from which review and source session.

## Tracker

Tracker: Not configured / not applicable.

## Resolved Questions

- No blocking business questions remain for this slice.
