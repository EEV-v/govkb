# Spec Brief — Governed Skill Knowledge Framework

Last updated: 2026-04-22

## Objective

- Replace hardcoded governed-skill routing in `codex-memory-review` with contract-driven capability discovery and governance.
- Prove the self-improving project loop: real team AI sessions produce reusable governed learning, the repo stores it, and teammates receive it through `govkb apply codex`.
- Establish a repo-native governed package under `.governed/` as the project source of truth.
- Make Codex the first adapter/materialization target rather than the project model itself.
- Keep the design ready for Claude and Copilot adapters.

## Source Artifacts

- `business.md`
- `business-context.md`
- `context.md`
- `open-questions.md`
- `decision-log.md`
- `requirements-catalog.md`
- `poc-plan.md`
- `poc-output.md`
- `implementation-plan.md`

## Business Value Snapshot

- New governed capabilities stop depending on central scheduler edits.
- Project-only knowledge stays in git and can be reviewed, released, and updated like the rest of the project source.
- Local assistant setup becomes a governed output instead of a manual local drift surface.
- Existing governed skills can grow in expertise from real completed work.
- Repeated unmatched patterns can become staged new capability candidates instead of scheduler code changes.
- Reusable learning can reduce repeated context explanation and rediscovery after it is promoted and shared with the team.
- The same project package becomes reusable across assistants.

## Scope Snapshot

- In scope now:
  - define a repo-native governed capability contract
  - define assistant adapter and release-manifest structure under `.governed/`
  - make `codex-memory-review` act as the first live adapter against repo-native contracts
	  - allow `govkb apply codex` from git-tracked releases into local setup
	  - classify reusable learning as existing capability update, new capability candidate, project knowledge, or reject
	  - stage new governed capability candidates for explicit review
	  - keep audit/reporting/state behavior
  - preserve strict auto-apply gates
  - support a controlled legacy fallback during migration
  - migrate the current memory-bearing Codex skills as the first adapter-backed set
- Deferred:
  - overriding the default skill creator
  - bulk migration of all remaining skills
  - full Claude and Copilot adapter implementation
	  - runtime prompt composition from adapter-managed prompt fragments
	  - UI for staged-memory review
	  - fully automatic activation of brand-new governed capabilities
	  - proving exact chatbot cost reduction

## Acceptance Snapshot

- A new governed capability with a valid repo contract can be routed without central Python edits.
- Project-only knowledge stays repo-native and assistant-agnostic.
- Adapter materialization cannot weaken project governance.
- `govkb apply codex` can materialize a chosen repo release to local setup.
- The first live adapter still discovers sessions, stages/applies/rejects lessons, and writes auditable artifacts.
- A real work session can update existing governed capability expertise with report evidence.
- Repeated unmatched work can stage a new governed capability candidate without activating it automatically.
- A promoted learning update can be applied by another local setup through `govkb apply codex`.
- Invalid contracts produce health warnings instead of silent corruption.
- The PoC dry run classifies current local skills into governed, legacy, and adapter-local tracks before migration starts.

## Review Readiness

- Open questions captured: 5
- Blocking questions remaining: 0
- Approved decisions captured: 12
- Feedback source documents found: 0
- Tracker sync complete: No, intentionally not started without explicit request
- Pending feedback reconciliation: No
- Ready for engineering handoff: Yes
