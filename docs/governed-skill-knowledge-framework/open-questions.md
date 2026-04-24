# Open Questions — Governed Skill Knowledge Framework

Last updated: 2026-04-21

| ID | Question | Status | Blocking | Owner | Source | Notes |
|---|---|---|---|---|---|---|
| Q1 | Where should the project-governed source of truth live? | Resolved | No | Engineering | business.md, context.md | Resolved on 2026-04-21: project-only governed source lives in git under `<project-root>/.governed/`, not under `.codex/skills/`. |
| Q2 | Can an assistant adapter relax project governance, for example by lowering confidence thresholds or disabling explicit acceptance? | Resolved | No | Engineering | business.md, context.md | Resolved on 2026-04-21: no. Adapter merge is monotonic; project governance can only tighten downstream, never weaken upstream. |
| Q3 | Should the first increment wait for full migration of every existing local skill install before the framework is usable? | Resolved | No | Engineering | business.md, context.md | Resolved on 2026-04-21: no. Phase 1 uses Codex as the first live adapter and keeps legacy fallback for unmigrated local assets. |
| Q4 | Does the first increment need fully working Claude and Copilot adapters? | Resolved | No | Engineering | business.md, business-context.md | Resolved on 2026-04-21: no. The repo package and adapter contract must be ready for those assistants, but Codex is the first live adapter. |
| Q5 | Is `governed` the final app/CLI name? | Resolved | No | Engineering | user decision | Resolved on 2026-04-21: folder stays `.governed`, contracts use governed language, and CLI/app alias is `govkb`. |
