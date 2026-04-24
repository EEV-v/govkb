# Governed Skill Knowledge Framework - Fresh Review

Last reviewed: 2026-04-22

## Verdict

**Ready for implementation:** Yes.

The prior blockers are addressed, and the product goal is now explicit: this is not just config migration. The MVP must prove a self-improving project loop where real team work grows governed capability expertise, repeated unmatched patterns stage new capability candidates, and promoted learning can be redistributed through `govkb apply codex`.

Latest PoC rerun:

| Signal | Result |
|--------|--------|
| Run command | `./regenerate-poc-data.sh` |
| Run status | Passed |
| Run time | `2026-04-21T20:46:00Z` |
| Skills scanned | 27 |
| Governed candidates | 9 |
| Legacy keep | 12 |
| Adapter-local | 6 |
| Inventory hash | `cb782540cf1f2812863d4a5bdfd04f1bffcb7288b0b076e7691154830ba9fb67` |

## Resolved Findings

| Priority | Previous Finding | Resolution |
|----------|------------------|------------|
| P1 | CLI command contract mixed executable commands with shorthand wording. | Normalized the first-increment public surface around `govkb init`, `govkb validate`, `govkb apply codex [--release <release_id>|--revision <git_sha>]`, `govkb status`, `govkb review-memory --assistant codex`, `govkb promote`, and `govkb create capability <capability_id>`. |
| P2 | Shareable `govkb` repo was required by use cases and plan but not clearly locked in `business.md`. | Added business target, technical requirement, and acceptance coverage for a separate cloneable/installable `govkb` framework repo/package that scaffolds project `.governed/` packages through `govkb init`. |
| P2 | Phase 0 verified `govkb validate` before schema and contract loader work existed. | Phase 0 now verifies install, help, and `govkb init`; Phase 1 owns meaningful `govkb validate` behavior after contract schema/loader work is implemented. |
| P3 | PoC evidence could be read as full framework proof. | PoC output now states it is a migration inventory gate, not proof of adapter materialization, repo resolution, governed worktree isolation, or live scheduler parity. |

## Implementation Guardrails

| Area | Guardrail |
|------|-----------|
| Product north star | Optimize for reusable learning capture and team redistribution, not framework shape by itself. |
| CLI surface | Do not introduce a separate `govkb update` command in the first increment; use `govkb apply codex` for release/revision materialization. |
| Framework repo | Keep reusable CLI/tooling source in the separate `govkb` repo/package; project repos contain `.governed/` source only. |
| Validation sequencing | Keep `govkb validate` implementation in Phase 1 with contract loader/schema work. |
| Existing skill growth | Allow high-confidence updates to existing governed capability expertise only when contract target, section, threshold, and governance rules all pass. |
| New skill growth | Stage new governed capability candidates from repeated unmatched patterns; do not activate brand-new capabilities automatically in the first increment. |
| PoC usage | Use generated contracts as migration input only, not as final production contracts. |
| Legacy safety | Keep the 12 legacy skills installed and unchanged until contract parity is proven. |
| Scheduled writes | Keep auto-applied repo-first mutations inside the governed automation worktree and require explicit promotion. |
| Cost claim | Treat chatbot cost reduction as an expected later measurement; the MVP proves reusable learning quality and redistribution first. |

## Final Assessment

The architecture is ready to implement as a time-boxed MVP: repo-native `.governed/` source, shareable `govkb` tooling, Codex as first adapter, explicit CLI commands, strict governance, safe legacy fallback, and a visible self-development loop for project AI knowledge.
