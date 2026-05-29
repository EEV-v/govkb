# Scope Lock — Memory Review Capability Evolution

## Readiness
- Ready for engineering handoff: Yes
- Status: ready
- Blocking questions remaining: 0
- Open decisions remaining: 0
- Pending feedback rounds remaining: 0
- Tracker/reference status: not configured

## Locked Scope Snapshot
- Extend the memory-review classifier contract to emit structured capability-evolution proposals.
- Add report sections for proposed scripts, tools, prompts, runbooks, and instruction changes.
- Persist staged proposals under repo-owned `.governed/` paths instead of local Codex memory paths.
- Keep scheduled cron reviews non-mutating for executable artifacts.
- Provide a manual apply or generation path that can turn an approved proposal into repo files.
- Support higher-reasoning manual review runs for capability-evolution extraction.
- Preserve existing append-only memory behavior and safety gates.

## Approved Decisions
- Stage capability-evolution proposals in `.governed/review-proposals/<proposal-id>/`; keep `.governed/candidates/` for new capability candidates only.
- Add a dedicated `govkb proposals` command family for review proposal UX, starting with `list`, `show`, and `apply`.
- Memory review always looks for high-confidence capability-evolution opportunities, but scheduled cron only stages proposals.
- File generation requires explicit approval metadata: approved status, approver, approved timestamp, target capability, proposal type, output paths, safety class, and verification command.
- First implementation slice supports `script`, `wrapper`, `prompt`, `runbook`, and `instructions_update`; new capability creation remains on the existing candidate flow.

## Deferred Items
- No deferred decisions are currently logged.

## Unresolved Blockers
- No blocking questions remain.
