### Governed Skill Knowledge Framework — Implementation Context
Last updated: 2026-04-22

### Existing Patterns
| Pattern Type | Existing Example | Location | Reuse? |
|--------------|------------------|----------|--------|
| Scheduled Codex session review with audit artifacts | `codex-memory-review` scans sessions, classifies lessons, and writes reports/state | `/home/ev/.codex/bin/codex-memory-review` | Yes, this remains the first live adapter |
| Session discovery from index plus real files | `load_sessions(...)` merges `session_index.jsonl` with session files under `~/.codex/sessions` | `/home/ev/.codex/bin/codex-memory-review` | Yes |
| Repo-native feature documentation | feature and implementation artifacts live in git | `Clearing-docs/docs/features/` | Yes, same ownership model should apply to governed project knowledge |
| Existing Codex skill packaging | `SKILL.md`, `references/`, `agents/` layout | `/mnt/c/Users/Ev/.codex/skills/<skill_id>/` | Yes, but only as a Codex adapter target |
| Shared context indirection | reviewer skills use `shared-kb.md` and `context-sources.md` instead of copying repo context into `SKILL.md` | reviewer `references/` files | Yes |
| Strict auto-apply validation | local Python validation gates `auto_apply`, `stage`, `reject` after model classification | `/home/ev/.codex/bin/codex-memory-review` | Yes |
| Scheduled execution | WSL cron invokes the review task daily at `08:15` Istanbul time | user crontab / scheduler setup | Yes |

### Current Control Flow
`WSL cron -> codex-memory-review -> discover sessions -> sanitize session -> infer likely skills -> call codex exec classifier -> local validation -> update memory / stage patch / write report -> advance state`

### Target Control Flow
`git-tracked .governed package -> govkb apply codex -> materialize local assistant setup -> WSL cron -> codex memory-review adapter -> discover sessions -> resolve session repo package -> load repo capability contracts + codex adapter rules -> sanitize session -> infer likely capabilities -> call codex exec classifier with contract-derived targets -> local validation -> update existing capability expertise, stage new capability candidate, or reject -> write repo-governed changes in governed automation worktree -> write health-rich report -> explicit promotion -> teammate runs govkb apply codex -> team receives improved assistant behavior`

| Step | System | Input | Output | Trigger |
|------|--------|-------|--------|---------|
| 1 | Repo package | `.governed/` source in git | governed project source of truth | repo change / release |
| 2 | `govkb apply codex` | repo package + Codex target + release | materialized local setup + installed-state record | install/update prompt |
| 3 | Scheduler | daily cron or manual invocation | one Codex adapter review run | `08:15` daily or ad hoc |
| 4 | Session selector | session index + session files + state | eligible session list | each run |
| 5 | Repo resolver | session metadata such as cwd / repo path | matched repo-governed package or explicit skip reason | each eligible session |
| 6 | Contract resolver | repo capability contracts + Codex adapter manifest | resolved governed capability registry for the adapter | each resolved repo |
| 7 | Signal extractor | session transcript | explicit capabilities, routing hints, generic relevance, self-reference flags | each eligible session |
| 8 | Classifier | sanitized session + candidate governed capability targets | proposed memory candidates and unmatched reusable patterns | per eligible session |
| 9 | Local validator | proposal + resolved contract + current repo-governed memory text | apply/stage/reject decision | per candidate |
| 10 | Capability candidate detector | repeated unmatched patterns + evidence sessions | staged new governed capability candidate | per run |
| 11 | Audit writer | run results | report, applied patch, staged patch, logs, state | end of run |
| 12 | Promotion/apply loop | governed automation worktree + release manifest | team-redistributable project knowledge update | explicit promotion and `govkb apply codex` |

### Domain Entities

#### ProjectGovernedManifest
Source of truth: repo-native governed package manifest.

Location:
- `<project-root>/.governed/project.toml`

| Field | Type | Example |
|------|------|---------|
| `schema_version` | `int` | `1` |
| `project.id` | `string` | `"clearing"` |
| `project.name` | `string` | `"Clearing"` |
| `release.current` | `string` | `"2026.04.21"` |
| `adapters.enabled` | `list[string]` | `["codex", "claude", "copilot"]` |

#### CapabilityContract
Source of truth: repo-native governed capability definition.

Location:
- `<project-root>/.governed/capabilities/<capability_id>/capability.contract.toml`

| Field | Type | Example |
|------|------|---------|
| `contract_version` | `int` | `1` |
| `capability.id` | `string` | `"clearing-master-reviewer"` |
| `capability.governed` | `bool` | `true` |
| `routing.aliases` | `list[string]` | `["master reviewer"]` |
| `routing.hints` | `list[string]` | `["review", "severity:"]` |
| `routing.negative_hints` | `list[string]` | `["codex-memory-review"]` |
| `memory.targets.<name>.path` | `string` | `"references/long-term-memory.md"` |
| `memory.targets.<name>.sections` | `list[string]` | `["Repository Best Practices"]` |

#### AssistantAdapterManifest
Source of truth: repo-native adapter definition that materializes capability and knowledge content into a local assistant-specific setup.

Location:
- `<project-root>/.governed/adapters/<assistant>/adapter.toml`

| Field | Type | Example |
|------|------|---------|
| `adapter.id` | `string` | `"codex"` |
| `adapter.materialization.targets` | `list[string]` | `["skills", "memory-review"]` |
| `adapter.governance.min_confidence_floor` | `float` | `0.85` |
| `adapter.routing.aliases` | `list[string]` | `["$clearing-master-reviewer"]` |
| `adapter.local_state_key` | `string` | `"clearing/codex"` |

#### ReleaseManifest
Source of truth: git-tracked governed release manifest.

Location:
- `<project-root>/.governed/releases/<release_id>.toml`

| Field | Type | Example |
|------|------|---------|
| `release.id` | `string` | `"2026.04.21"` |
| `release.git_revision` | `string` | `"abc1234"` |
| `release.adapters` | `list[string]` | `["codex"]` |
| `release.notes` | `string` | `"initial codex adapter rollout"` |

#### LocalInstallState
Source of truth: local `govkb` installer state outside the repo.

| Field | Type | Example |
|------|------|---------|
| `project_id` | `string` | `"clearing"` |
| `assistant` | `string` | `"codex"` |
| `applied_release_id` | `string` | `"2026.04.21"` |
| `applied_git_revision` | `string` | `"abc1234"` |
| `applied_at` | `string` | `"2026-04-21T18:10:00Z"` |

#### RepoResolution
Source of truth: session metadata matched to the correct governed repo package before contract loading.

| Field | Type | Example |
|------|------|---------|
| `session_id` | `string` | `"session-skill-001"` |
| `session_cwd` | `string` | `"/home/ev/code/Clearing/ETNAClearingService"` |
| `repo_root` | `string` | `"/home/ev/code/Clearing"` |
| `governed_root` | `string` | `"/home/ev/code/Clearing/.governed"` |
| `status` | `enum` | `"matched"` |

#### GovernedAutomationWorkspace
Source of truth: dedicated automation branch/worktree where scheduled repo-first mutations land without touching the active developer working tree.

| Field | Type | Example |
|------|------|---------|
| `project_id` | `string` | `"clearing"` |
| `assistant` | `string` | `"codex"` |
| `workspace_root` | `string` | `"/home/ev/.codex/governed-worktrees/clearing-codex"` |
| `git_branch` | `string` | `"governed/codex-auto"` |
| `promotion_state` | `string` | `"awaiting-explicit-release-promotion"` |

#### SessionMemoryCandidate
Source of truth: `codex exec` structured classifier output plus local validation.

| Field | Type | Example |
|------|------|---------|
| `target_capability` | `string` | `"clearing-master-reviewer"` |
| `memory_section` | `string` | `"Repository Best Practices"` |
| `lesson` | `string` | `"Keep repo-wide review rules in the project-governed source, not only in local skill outputs."` |
| `bucket` | `enum` | `"auto_apply"` |
| `confidence` | `float` | `0.91` |

#### GovernedLearningCandidate
Source of truth: reusable learning extracted from completed team work and classified into the self-development loop.

| Field | Type | Example |
|------|------|---------|
| `source_session_id` | `string` | `"session-fix-001"` |
| `learning_type` | `enum` | `"existing_capability_update"` |
| `target_capability` | `string` | `"clearing-bugfixer"` |
| `reuse_scope` | `enum` | `"project"` |
| `lesson` | `string` | `"Use the production replay fixture before patching reconciliation importer behavior."` |
| `confidence` | `float` | `0.93` |
| `decision` | `enum` | `"apply"` |

#### NewCapabilityCandidate
Source of truth: staged proposal for a governed capability when repeated completed work does not fit an existing valid contract.

| Field | Type | Example |
|------|------|---------|
| `candidate_id` | `string` | `"clearing-review-tax-lots"` |
| `evidence_sessions` | `list[string]` | `["session-tax-001", "session-tax-002"]` |
| `suggested_routing_hints` | `list[string]` | `["tax lot", "wash sale", "cost basis"]` |
| `suggested_memory_targets` | `list[string]` | `["references/long-term-memory.md"]` |
| `decision` | `enum` | `"stage_for_review"` |

### Upstream Dependencies
| Source | Owner | Delivery | Format | Failure Mode | Handling |
|--------|-------|----------|--------|--------------|----------|
| Repo-governed package | Project repo owner | git-tracked files | TOML + Markdown + templates | invalid or missing manifest | exclude affected capability/adapter and warn |
| Session index | Codex local runtime | local file | JSONL | session missing from index | fall back to session file discovery |
| Session files | Codex local runtime | local files | JSONL | malformed or partial rows | skip bad rows, preserve run health |
| Session repo metadata | Codex local runtime | session JSONL metadata | cwd / repo path fields | missing or unmappable repo path | skip session with health warning |
| Local Codex materialization | Governed installer | local filesystem | generated skill files / config | stale local setup vs repo release | governed update required |
| `codex exec` classifier | Codex CLI | subprocess | JSON schema response | classifier failure or invalid JSON | fail session, keep run report, do not advance session state |

### Services
| Service | Owner | SLA | Retry |
|---------|-------|-----|-------|
| `govkb apply codex` | Local operator / framework owner | Local Codex setup must be syncable from repo release | rerun after fixing repo or local state |
| `codex-memory-review` adapter | Local operator / framework owner | Daily run available and auditable | next scheduled run or manual rerun |
| Repo capability registry | Project owner | Contracts must be parseable on each run | fixed on next run after contract repair |
| `codex exec` classifier | Codex CLI | best-effort local dependency for candidate extraction | rerun session next scheduled/manual pass |

### Surfaces
**Existing to consume:**
| Surface | Purpose |
|---------|---------|
| `/home/ev/.codex/bin/codex-memory-review` | current scheduled operator entrypoint |
| `codex exec --ephemeral --skip-git-repo-check --output-schema ...` | structured classification step |

**New/modified internal surfaces:**
| Surface | Required change |
|---------|-----------------|
| `.governed/project.toml` | repo-native governed package manifest |
| `capability.contract.toml` | repo-native governed capability contract |
| `adapter.toml` | repo-native assistant adapter definition |
| release manifest | repo-native `govkb apply codex` descriptor |
| Codex adapter loader | resolve repo contracts instead of hardcoded skill map |

### Storage
| Location | Format | Retention |
|----------|--------|-----------|
| `<project-root>/.governed/project.toml` | TOML | repo history |
| `<project-root>/.governed/capabilities/<capability_id>/capability.contract.toml` | TOML | repo history |
| `<project-root>/.governed/knowledge/**` | Markdown | repo history |
| `<project-root>/.governed/adapters/<assistant>/adapter.toml` | TOML | repo history |
| `<project-root>/.governed/releases/<release_id>.toml` | TOML | repo history |
| `$CODEX_HOME/memories/codex-memory-review/reports/*` | Markdown/Patch | audit history |
| `$CODEX_HOME/memories/codex-memory-review/state.json` | JSON | current run state |
| local `govkb` install state | JSON | current local state |

### Business Rules
| Rule | Logic | Error Handling |
|------|-------|----------------|
| Repo is canonical for project knowledge | Project-only governed knowledge must live under `.governed/` in git | reject writes that target adapter-local derived files as source of truth |
| No central skill allowlist | The framework must not require hardcoded project skill ids or keyword tables for governed capabilities | fail build/review if new capability requires central routing edit |
| Contract-first governance | A governed capability participates in memory review only through a valid repo contract | invalid contract excludes that capability and raises run-health warning |
| Adapter cannot weaken policy | Assistant adapter may add routing/context/projection and tighten policy, but cannot lower confidence threshold or disable explicit acceptance | merged policy uses stricter result |
| Local setup is derived | Assistant-local materialization is an output of `govkb apply codex`, not the project source of truth | `govkb apply codex` may overwrite stale local artifacts after preview/confirmation |
| Session-to-repo routing is explicit | Each scheduled session must resolve to one governed repo package from session metadata before contract loading | unmatched session is skipped with report health warning |
| Auto-apply stays conservative | apply only on exact capability, valid section, clean sensitivity check, reusable lesson, and confidence >= resolved threshold | otherwise stage or reject |
| Active developer working tree stays clean | Scheduled repo-first mutations must land only in the governed automation worktree/branch | if isolated workspace is unavailable, stage only and warn instead of mutating the active repo |
| Self-referential sessions are not durable memory | maintenance/report/debug sessions about the framework itself must not create long-term skill memory | reject before classification when possible |
| Discovery completeness | eligible Codex session files inside the review window must not be missed because the session index is incomplete | file-only sessions are counted and processed |
| Release-aware local sync | Local setup must be traceable to a repo release or git revision | missing or stale install state raises governed update warning |
| Existing capability expertise may grow automatically | High-confidence reusable lessons from completed project work may update an existing governed capability when the resolved contract permits the target and section | otherwise stage or reject with report reason |
| New capability growth is review-gated | Repeated unmatched project patterns may create staged capability candidates, but active contracts are not auto-created in the first increment | candidate remains staged until explicitly promoted, edited, or rejected |
| Team redistribution is the value loop | Promoted learning must be materializable by another local setup through `govkb apply codex` | stale install state reports drift until applied |

### Security
| Entity/Field | Classification | Handling |
|--------------|----------------|----------|
| session content | local operational data | sanitize and redact before classifier call |
| repo-governed contract files | project configuration | validate paths; no shell expansion or parent traversal |
| repo-governed memory files | durable project knowledge | write through staged diff or controlled append/merge |
| staged capability candidates | proposed project knowledge structure | require explicit review before becoming active governed contracts |
| governed automation workspace | local automation state | isolate scheduled writes from active developer worktree; require explicit promotion for release adoption |
| local adapter materialization | local derived setup | regenerate from `govkb apply codex`; do not treat as canonical project source |

### Volume & Scale
| Metric | Typical | Peak | Implication |
|--------|---------|------|-------------|
| eligible sessions per daily run | `0-10` | `25` | contract resolution cost must stay small |
| governed capabilities | `10-20` | `50` | registry load should remain cheap |
| assistant adapters per repo | `1-3` | `5` | validation should stay linear |
| memory targets per capability | `1-3` | `5` | prompt target narrowing remains valuable |
| new capability candidates per week | `0-2` | `5` | candidate creation must be conservative and review-gated |

### Schedules
| Job | Schedule | Timezone | Grace |
|-----|----------|----------|-------|
| `codex-memory-review --once` | daily at `08:15` | `Europe/Istanbul` | manual rerun any time |
| `govkb apply codex` | on demand per release/update prompt | local operator timezone | manual confirmation/apply path |

### Service Levels
| Service Level | Target |
|---------------|--------|
| Repo source-of-truth | `100%` of project-only governed knowledge stored in git under `.governed/` |
| Discovery completeness | `100%` of session files in the review window discovered even if absent from `session_index.jsonl` |
| Scheduled freshness | one successful scheduled run every 24 hours under normal operation |
| Runtime target | normal daily run completes in `< 5 minutes`; stretched daily run in `< 10 minutes` |
| Report availability | report, patch files, and logs written in the same run that produced decisions |
| Contract safety | invalid contract degrades that capability or adapter only; it must not corrupt or stop unrelated processing |
| `govkb apply codex` | install or update of one repo release to local Codex setup completes in `< 5 minutes` under normal operation |
| Self-improvement proof | first increment demonstrates at least one existing governed capability expertise update from real work and one staged new capability candidate from repeated unmatched work |

### Observability
Metrics, logs, alerts:
- run duration
- eligible sessions selected
- file-only sessions detected
- governed contracts loaded
- adapters loaded
- releases applied
- invalid contracts
- install drift warnings
- applied, staged, rejected counts
- existing capability expertise updates
- new capability candidates staged
- promoted learning updates
- teammate/local installs updated from promoted learning
- classifier failures

Suggested log events:
- `contract_loaded`
- `contract_invalid`
- `adapter_loaded`
- `adapter_invalid`
- `governed_release_applied`
- `governed_release_drift_detected`
- `session_prescreen_skipped`
- `memory_candidate_applied`
- `memory_candidate_staged`
- `capability_expertise_updated`
- `new_capability_candidate_staged`
- `learning_update_promoted`

Suggested alerts / warnings:
- no successful scheduled run in 48 hours
- invalid contract count > 0
- classifier failure count > 0
- local install state drift vs selected release

### Assumptions
| # | Assumption | Risk if Wrong |
|---|------------|---------------|
| 1 | `tomllib` is available in the runtime Python used by the scheduler, so TOML can be parsed without a new dependency. | A different format or dependency would be required |
| 2 | The repo-governed root can be standardized as `<project-root>/.governed/`. | If a different root is required, discovery and apply paths change |
| 3 | Current governed memory-bearing Codex skills are a sufficient pilot materialization set for the first increment. | Value lands later than expected if the pilot set is too narrow |
