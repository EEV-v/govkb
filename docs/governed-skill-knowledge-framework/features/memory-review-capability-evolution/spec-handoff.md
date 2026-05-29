# Spec Handoff — Memory Review Capability Evolution

## Handoff Status
- Ready for engineering cookbook: Yes
- Status: ready
- Blocking questions remaining: 0
- Approved decisions captured: 5
- Deferred decisions captured: 0

## Required Inputs For Engineering
- business.md
- business-context.md
- context.md
- spec-brief.md
- open-questions.md
- decision-log.md
- scope-lock.md

## Approved Decisions
- Stage capability-evolution proposals in `.governed/review-proposals/<proposal-id>/`; keep `.governed/candidates/` for new capability candidates only.
- Add a dedicated `govkb proposals` command family for review proposal UX, starting with `list`, `show`, and `apply`.
- Memory review always looks for high-confidence capability-evolution opportunities, but scheduled cron only stages proposals.
- File generation requires explicit approval metadata: approved status, approver, approved timestamp, target capability, proposal type, output paths, safety class, and verification command.
- First implementation slice supports `script`, `wrapper`, `prompt`, `runbook`, and `instructions_update`; new capability creation remains on the existing candidate flow.

## Deferred / Watch Items
- No deferred decisions are logged.

## Remaining Blockers
- No blocking questions remain.

## Tracker Context
- Tracker references are not populated yet.

## Next Step
- Once this handoff is ready, continue with `docs/COOKBOOK/COOKBOOK.MD` for use cases, PoC, and implementation phases.
