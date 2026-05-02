# Spec Handoff — Codex Skill Governed Conversion

## Handoff Status
- Ready for engineering cookbook: Yes
- Status: ready
- Blocking questions remaining: 0
- Approved decisions captured: 8
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
- Conversion depends on governed skill quality gates.
- MVP converts one skill at a time.
- MVP write mode creates new packages only.
- Source local skills are never mutated.
- Conversion does not execute helper scripts.
- Conversion always writes canonical `instructions.md`; it writes `adapters/codex/SKILL.md` only when Codex-specific presentation or exact local-skill parity requires it.
- Preview rejected-content reporting is console/JSON only; write mode also records a redacted conversion report in the governed package.
- Direct source skill paths outside `--codex-home` are allowed when explicitly passed.

## Deferred / Watch Items
- No deferred decisions are logged.

## Remaining Blockers
- No blocking questions remain.

## Tracker Context
- Tracker references are not populated yet.

## Next Step
- Once this handoff is ready, continue with `docs/COOKBOOK/COOKBOOK.MD` for use cases, PoC, and implementation phases.
