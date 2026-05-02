# Scope Lock — Codex Skill Governed Conversion

## Readiness
- Ready for engineering handoff: Yes
- Status: ready
- Blocking questions remaining: 0
- Open decisions remaining: 0
- Pending feedback rounds remaining: 0
- Tracker/reference status: not configured

## Locked Scope Snapshot
- convert one local Codex skill at a time
- source can be a skill directory path or a skill name resolved from a Codex home
- preview mode is the default safe path
- write mode creates a new governed capability package only
- conversion classifies source content before writing
- safe helper scripts and fixtures may be copied into standard governed locations
- source local skill is never mutated

## Approved Decisions
- Conversion depends on governed skill quality gates.
- MVP converts one skill at a time.
- MVP write mode creates new packages only.
- Source local skills are never mutated.
- Conversion does not execute helper scripts.
- Conversion always writes canonical `instructions.md`; it writes `adapters/codex/SKILL.md` only when Codex-specific presentation or exact local-skill parity requires it.
- Preview rejected-content reporting is console/JSON only; write mode also records a redacted conversion report in the governed package.
- Direct source skill paths outside `--codex-home` are allowed when explicitly passed.

## Deferred Items
- No deferred decisions are currently logged.

## Unresolved Blockers
- No blocking questions remain.
