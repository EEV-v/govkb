# Scope Lock — Governed Skill Knowledge Framework

## Readiness
- Ready for engineering handoff: Yes
- Status: ready
- Blocking questions remaining: 0
- Open decisions remaining: 0
- Pending feedback rounds remaining: 0
- Monday linked: No
- Azure Feature linked: No

## Locked Scope Snapshot
- `.governed/` becomes the canonical project-governed source in git.
- `codex-memory-review` remains the first live execution adapter and gains contract-driven routing and governance from the repo package.
- Project knowledge is repo-native and assistant-agnostic; Codex/Claude/Copilot are adapter targets rather than the project model.
- Governed release/install manifests drive local `govkb apply codex` flows from git-tracked revisions.
- The first increment must demonstrate self-improving project knowledge: existing capability expertise update, staged new capability candidate, and team redistribution through `govkb apply codex`.
- Current Codex reporting, staged-patch behavior, applied-patch behavior, and state tracking remain in place.
- The first increment migrates the currently governed memory-bearing Codex skills and keeps legacy fallback for the rest.

## Approved Decisions
- The framework must be capability-agnostic and must not depend on a hardcoded skill map.
- The canonical project-governed source lives under `<project-root>/.governed/`.
- Governed capabilities declare `capability.contract.toml`.
- Assistant adapters are repo-defined materialization targets and may not weaken project governance.
- Governed release/install manifests drive local setup through `govkb apply codex`.
- Existing governed capability expertise may grow automatically when confidence and governance allow it.
- New governed capability candidates are staged for explicit review before activation.
- The Codex scheduler is extended as the first adapter, not replaced.
- Invalid contracts surface as health warnings and degrade only the affected capability or adapter.
- Skill creator override, broader retrofits, and non-Codex live adapters are deferred.

## Deferred Items
- Override the default skill creator to scaffold compliant governed skills.
- Bulk retrofit remaining non-governed or currently unmigrated skills.
- Merge repo-local prompt text into live assistant execution flow.
- Build a UI or interactive queue for staged-memory review.
- Ship fully working Claude and Copilot adapters.
- Prove exact token or chatbot cost reduction.

## Unresolved Blockers
- No unresolved blockers remain at scope-lock time.
