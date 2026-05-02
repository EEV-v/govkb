# Scope Lock — Governed Skill Quality Gates

## Readiness
- Ready for engineering handoff: Yes
- Status: ready
- Blocking questions remaining: 0
- Open decisions remaining: 0
- Pending feedback rounds remaining: 0
- Tracker/reference status: not configured

## Locked Scope Snapshot
- strict governed-skill package convention
- strict validation mode and issue reporting
- candidate activation gate based on strict validation
- governed skill lifecycle states
- memory, naming, data, and tooling quality rules
- backward-compatible rollout policy

## Approved Decisions
- Split existing-skill conversion out of the first slice.
- Keep normal `govkb validate` backward-compatible at first.
- Make strict validation mandatory for candidate activation.
- GovKB packages helper tools but does not execute them during validation or materialization.
- Unsafe content is not copied into governed memory.
- Clearing remediation is a follow-up operational feature, not the first product implementation slice.
- Approval state is represented in both candidate metadata and capability metadata.
- First-slice credential path validation blocks home credential roots, common credential files, private keys, and credential/secret/token/service-account path terms.

## Deferred Items
- No deferred decisions are currently logged.

## Unresolved Blockers
- No blocking questions remain.
