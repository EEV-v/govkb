# Codex Skill Governed Conversion - Open Questions

| ID | Question | Status | Owner | Notes |
|---|---|---|---|---|
| Q1 | Should conversion write a Codex-specific `adapters/codex/SKILL.md` by default, or generate `instructions.md` only? | Blocking | Engineering/Product | Impacts materialized skill parity. |
| Q2 | Should rejected unsafe content be represented only in console/JSON output, or also in a redacted conversion report file? | Blocking | Security/Governance | Must not persist unsafe values. |
| Q3 | Should conversion accept source skills outside `--codex-home` when passed as direct paths? | Assumption | Engineering | Current business draft allows direct paths. |
| Q4 | Should update mode for existing governed packages be a later feature? | Resolved | Product | MVP create-only; updates deferred. |
