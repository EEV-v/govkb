### Governed Skill Knowledge Framework - Implementation Plan
Last updated: 2026-04-24

### 0) Existing Code Inventory (REQUIRED FIRST)

| Category | Component | Location | Reuse Strategy |
|----------|-----------|----------|----------------|
| CLI entrypoint | Scheduled Codex memory-review engine | `/home/ev/.codex/bin/codex-memory-review` | Extend as the first live adapter; keep current scheduler/report/state flow |
| Session discovery | index + file-union selector with backfill protection | `/home/ev/.codex/bin/codex-memory-review` | Reuse directly; preserve correctness fixes already landed |
| Signal extraction / prescreen | self-reference filter, generic relevance, explicit skill matching | `/home/ev/.codex/bin/codex-memory-review` | Replace hardcoded routing and hint-first prescreen with AI-first semantic classification while keeping deterministic governance rejection |
| Audit artifacts | report generation, staged patch, applied patch, state/log handling | `/home/ev/.codex/bin/codex-memory-review` | Reuse directly |
| Repo-native documentation ownership | feature and implementation artifacts live in git | `Clearing-docs/docs/features/` | Reuse this ownership pattern for `.governed/` source |
| Existing Codex skill packaging | `SKILL.md`, `references/`, `agents/` layout | `/mnt/c/Users/Ev/.codex/skills/<skill_id>/` | Reuse as the first materialization target, not as project source-of-truth |
| Shared context indirection | `shared-kb.md`, `context-sources.md` patterns | reviewer `references/` files | Reuse to avoid stuffing repo knowledge into the contract itself |
| Scheduler | daily WSL cron entry | user crontab | Reuse unchanged |
| PoC migration inventory | Dry-run classifier for local skills and generated contract candidates | `Clearing-docs/docs/features/Governed Skill Knowledge Framework/poc/skill_inventory_dry_run.py` | Use as the first migration gate and fixture source, not as production code |

**New components (minimal + justified):**
- Shareable `govkb` GitHub repo
  New because the framework/CLI must be reusable across projects instead of living only inside `Clearing-docs`.
- `govkb/src/govkb/core/contracts.py`
  New because contract parsing, validation, merge logic, release resolution, and adapter policy belong in reusable framework source, not in a user-home helper module.
- `govkb/src/govkb/commands/apply.py`
  New because repo changes must be materializable into local assistant setup through `govkb apply codex`.
- `govkb/src/govkb/adapters/codex/memory_review.py`
  New because the first live adapter should be framework-sourced and callable from a thin local shim or direct CLI invocation.
- `govkb/src/govkb/core/learning.py`
  New because reusable project learning needs explicit classification into existing capability updates, new capability candidates, project knowledge, or rejects.
- `<project-root>/.governed/**`
  New in each project because project-governed source of truth must live in the project repo and remain assistant-agnostic.

### 0.5) Pre-flight Checklist

| Prerequisite | Status | Owner |
|--------------|--------|-------|
| Current scheduler is running and producing reports | Yes | Local operator |
| Session discovery correctness fixes are already in place | Yes | Engineering |
| Python runtime supports `tomllib` | Assumed Yes | Engineering |
| Current governed memory-bearing Codex skills are available for pilot migration | Yes | Engineering |
| Repo-governed root `.governed/` can be added to the project repo | Yes | Project owner |
| `codex exec` is available for classifier calls | Yes | Local environment |
| PoC dry-run inventory completed and repeatable | Yes | Engineering |

**Blockers**
- No hard implementation blocker remains.
- One engineering risk must be handled explicitly: migration from local Codex-centric ownership to repo-native governed ownership must not silently change the current behavior of approval-gated capabilities or the current Codex adapter outputs.

**MVP north star**
- Prove that one project can improve its own AI operating knowledge from real team work, store the improvement in git, and redistribute it to another local assistant setup.
- Success is measured first by reusable learning capture and team redistribution, not by exact chatbot cost reduction.
- The capture loop must be transferable beyond coding-only English sessions; it should grow from task meaning, outcomes, and governed evidence packaging.

### 1) Scope & Boundaries

- In scope:
  - create the shareable `govkb` framework repo/package with Python CLI, schemas, templates, adapters, and tests
  - add repo-native governed package schema under `.governed/`
  - add governed capability contracts in a parser-friendly machine-readable format
  - add assistant adapter manifests and release manifests under `.governed/`
  - add `govkb apply codex` flow from git-tracked repo source to local setup
  - replace `KEYWORD_SKILL_HINTS`-style hardcoding for governed capabilities in the Codex adapter
  - keep current Codex session discovery, audit artifacts, and scheduler flow
  - enforce monotonic adapter governance
  - shift reusable-learning capture to AI-first semantic classification
  - classify real work sessions into existing capability expertise updates, new capability candidates, project knowledge, or rejects
  - auto-apply existing capability expertise only when confidence and governance allow it
  - stage new capability candidates for explicit review instead of activating them automatically
  - migrate current governed memory-bearing Codex skills as the first live adapter materialization
  - keep legacy fallback for unmigrated local assets during the first increment
  - prove the model on multilingual and non-coding sessions
- Out of scope:
  - overriding the default skill creator
  - bulk migration of all remaining skills
  - runtime prompt composition from adapter-managed prompt files
  - UI for manual staged-memory review
  - fully working Claude and Copilot adapters
  - fully automatic activation of brand-new governed capabilities
  - proving exact token or chatbot cost reduction

### 2) Requirements Mapping

| Use-case | Behavior | Location | New/Modify | Notes |
|----------|----------|----------|------------|-------|
| UC-1 | Shareable framework repo can be cloned and used to scaffold project packages | `govkb/pyproject.toml`, `govkb/src/govkb/**`, `govkb/templates/project/.governed/**` | New | CLI/tooling source lives in the reusable `govkb` repo, not inside each project |
| UC-2 | New governed capability becomes routable without central script edits | `govkb/src/govkb/core/contracts.py`, `govkb/src/govkb/adapters/codex/memory_review.py`, `<project-root>/.governed/capabilities/<capability_id>/capability.contract.toml` | New + Modify | Replace hardcoded governed routing with repo contract loading and AI semantic target selection; hints remain optional accelerators |
| UC-3 | Project-only knowledge stays repo-native and assistant-agnostic | `govkb/src/govkb/core/contracts.py`, `<project-root>/.governed/knowledge/**`, `<project-root>/.governed/adapters/<assistant>/adapter.toml` | New | Project source stays in git; adapters are derived targets |
| UC-4 | `govkb apply codex` updates local assistant setup from git source | `govkb/src/govkb/commands/apply.py`, `<project-root>/.governed/releases/<release_id>.toml` | New | Install/update records local applied revision |
| UC-5 | High-confidence exact lesson auto-applies safely | `govkb/src/govkb/adapters/codex/memory_review.py`, repo governed memory targets | New + Modify | Use resolved contract threshold and sections; keep current sensitivity/duplicate checks |
| UC-6 | Approval-gated or low-confidence lesson stages | `govkb/src/govkb/adapters/codex/memory_review.py`, capability contracts | New + Modify | Explicit-acceptance and threshold policy move into contract resolution |
| UC-7 | File-only session remains discoverable | `govkb/src/govkb/adapters/codex/memory_review.py` | New + Modify | Preserve current union selector and health reporting |
| UC-8 | Invalid contract degrades only the affected capability or adapter | `govkb/src/govkb/core/contracts.py`, `govkb/src/govkb/adapters/codex/memory_review.py` | New + Modify | Add contract validation and report surfacing |
| UC-9 | Maintenance chatter does not become durable memory | `govkb/src/govkb/adapters/codex/memory_review.py` | New + Modify | Keep deterministic governance rejection for self-referential, environment-local, and maintenance-only content before semantic classification |
| UC-10 | Session resolves to the correct governed repo package or skips safely | `govkb/src/govkb/adapters/codex/memory_review.py`, `govkb/src/govkb/core/project.py` | New + Modify | Use session metadata such as cwd/repo path before loading contracts for that session |
| UC-11 | Automated repo-first writes stay isolated from the active developer working tree | `govkb/src/govkb/core/worktree.py`, `govkb/src/govkb/adapters/codex/memory_review.py` | New + Modify | Scheduled auto-apply writes only inside dedicated governed automation worktree/branch; promotion remains explicit |
| UC-12 | Real team work grows an existing governed capability and redistributes it | `govkb/src/govkb/core/learning.py`, `govkb/src/govkb/adapters/codex/memory_review.py`, `<project-root>/.governed/capabilities/**` | New + Modify | Existing capability expertise update is the primary self-improvement loop |
| UC-13 | Repeated unmatched work pattern stages a new governed capability candidate | `govkb/src/govkb/core/learning.py`, `<project-root>/.governed/candidates/**` | New | New capability growth is review-gated in the first increment |
| UC-14 | Durable session can classify without English hint phrases | `govkb/src/govkb/adapters/codex/memory_review.py`, classifier prompt/schema | New + Modify | Semantic evidence package must be sufficient even when contract hints do not match session wording |
| UC-15 | Non-coding or mixed-language session can produce governed output | `govkb/src/govkb/adapters/codex/memory_review.py`, `govkb/src/govkb/core/learning.py`, classifier prompt/schema | New + Modify | Supported session types include docs, QA, review, delivery, ops, and mixed-language work with durable outcomes |

### 2.5) Impact Analysis

| Affected Code | Change Type | Risk | Backward Compatible | Mitigation |
|---------------|-------------|------|---------------------|------------|
| `govkb/src/govkb/adapters/codex/memory_review.py` | core adapter logic | Medium | Yes, with legacy fallback | keep current audit flow and incremental rollout; verify dry-run before live apply |
| `govkb/src/govkb/core/contracts.py` | new reusable helper module | Low | Yes | keep isolated and covered by fixture-based tests |
| `govkb/src/govkb/core/learning.py` | new reusable helper module | Medium | Yes | keep classification conservative; require multiple evidence sessions for new capability candidates |
| `govkb/src/govkb/commands/apply.py` | new installer/update path | Medium | Yes | release manifest validation + preview before apply |
| `<project-root>/.governed/**` | new repo source-of-truth | Medium | Yes | validate manifests/contracts before materialization |
| Local Codex skill dirs | materialized target migration | Medium | Yes | migrate in small batches and compare dry-run outputs against current behavior |
| Shareable `govkb` repo | new framework source | Medium | Yes | package as installable Python CLI; project repos contain only `.governed/` packages |

### 2.6) Migration Eligibility Matrix

Classify existing local skills before migration work starts. The framework should not assume every current local skill becomes a governed capability.

| Track | Qualification | Migration Action | Examples |
|------|---------------|------------------|----------|
| Governed capability now | Skill carries durable project knowledge, routing rules, memory governance, approval policy, or reusable project workflow that should remain valid across assistants | Create repo capability contract under `.governed/capabilities/<capability_id>/`; materialize Codex assets from repo source | project reviewers, bugfix workflow, QA workflow, estimator-like project knowledge keepers |
| Adapter-local only | Skill is assistant-specific runtime glue, formatting/presentation behavior, system utility logic, or tool-wrapper behavior that is not project knowledge | Keep under assistant-local adapter ownership; optionally read governed contracts, but do not make it project source-of-truth | Codex-only wrappers, local style/prompt helpers, thin utility skills |
| Legacy keep until migrated | Skill is still actively used and operationally needed, but contract conversion is not yet ready or parity is not proven | Leave installed and supported as compatibility path; do not block repo-first rollout on full migration | existing local skills awaiting conversion or parity evidence |

Rules:
- New project/domain skills should default to `Governed capability now`.
- Adapter-local skills may not become the only source of project knowledge.
- Legacy keep is transitional only; each retained skill should eventually move to governed or adapter-local ownership.

### 2.7) PoC Results Gate

The migration inventory PoC ran successfully against the current local skill tree.

| Metric | Result |
|--------|--------|
| Total skills scanned | 27 |
| Governed capability now | 9 |
| Legacy keep until migrated | 12 |
| Adapter-local only | 6 |
| Memory-bearing skills | 9 |
| Approval-gated skills | 1 |
| Generated contract candidates | 9 |
| Validation status | Passed |

First-wave governed candidates:
- `clearing-bugfixer`
- `clearing-feature-estimator`
- `clearing-master-reviewer`
- `clearing-qa-on-staging`
- `clearing-review-cashflow-reconciliation`
- `clearing-review-corporate-actions-processing`
- `clearing-review-internal-account-governance`
- `clearing-review-security-master`
- `clearing-review-transaction-lots-reconciliation`

Implementation rule:
- Use generated PoC contracts as migration input only, not final production contracts.
- `clearing-feature-estimator` must preserve `requires_explicit_acceptance = true`.
- Keep the 12 legacy skills installed and unchanged until contract parity is proven.
- Keep `.system/*` and `ev-style-writer` adapter-local.

### 3) Domain & Data Design

**Repo-governed contract format**
- Files:
  - shareable framework repo: `govkb/`
  - `.governed/project.toml`
  - `.governed/capabilities/<capability_id>/capability.contract.toml`
  - `.governed/adapters/<assistant>/adapter.toml`
  - `.governed/releases/<release_id>.toml`
- Reason: Python can parse TOML via `tomllib` with no new dependency

**Storage**
- Reusable framework source: shareable `govkb` GitHub repo
- Canonical project source: `<project-root>/.governed/`
- Capability contracts: `<project-root>/.governed/capabilities/<capability_id>/capability.contract.toml`
- Project-only knowledge: `<project-root>/.governed/knowledge/**`
- Assistant adapters: `<project-root>/.governed/adapters/<assistant>/adapter.toml`
- Release manifests: `<project-root>/.governed/releases/<release_id>.toml`
- Governed automation workspace: local dedicated git branch/worktree for scheduled repo-first mutations
- Local assistant files remain materialized outputs, not project source-of-truth

**Merge rules**
- Match active capability by exact `capability.id`
- Merge project capability contract with active assistant adapter rules
- `routing.aliases`, `routing.hints`, `routing.negative_hints`: union + dedupe
- `memory.auto_apply_min_confidence`: `max(project, adapter floor)`
- `memory.requires_explicit_acceptance`: `project OR adapter hardening`
- `memory.targets`: project-defined source targets; adapter may add projection targets but may not redefine project source ownership

**Validation**
- required: package manifest, `contract_version`, `capability.id`, `capability.governed`, `memory.enabled` when governed, and at least one valid source target when memory is enabled
- reject target paths containing parent traversal or absolute paths
- warn on unknown contract version
- treat malformed contract as capability-specific warning, not process-wide failure
- refuse scheduled auto-apply if the governed automation workspace cannot be resolved safely; downgrade to stage + health warning instead

### 4) Integration Points

| Type | Details |
|------|---------|
| Scheduler | Keep existing daily cron schedule at `08:15` Istanbul time; no schedule change in this phase |
| CLI | Add installable `govkb` commands from the shareable framework repo; Codex adapter remains the first scheduled operator interface |
| Contract registry | Capability contracts and adapter manifests loaded from `<repo-root>/.governed/` |
| Classifier | Continue using `codex exec --ephemeral --skip-git-repo-check --output-schema` in the Codex adapter, but pass a compact semantic evidence package plus candidate capability metadata; aliases and hints are optional accelerators, not the primary engine |
| Reports | Continue writing timestamped report, applied patch, staged patch, and logs under `$CODEX_HOME/memories/codex-memory-review/` |

### 5) Application Logic

**Flow**
Repo-governed release selected -> `govkb apply codex` materializes local Codex setup -> scheduler trigger -> acquire lock -> load state -> discover eligible sessions -> resolve session repo root/package -> load repo capability contracts + Codex adapter manifest -> validate and merge registry -> derive repo-governed memory targets -> sanitize session -> deterministic governance prescreen -> build compact semantic evidence package -> call classifier -> classify learning as existing capability update / new capability candidate / project knowledge / reject -> local validate candidate -> apply/stage/reject against repo source in governed automation workspace -> write report/patches/logs -> explicit promotion -> teammate runs `govkb apply codex` -> team receives improved assistant behavior

**Detailed behavior**
1. Session repo resolution
   - Resolve repo root from session metadata such as cwd, repo path markers, or known repo ancestry
   - Require exactly one governed repo package match before loading contracts for that session
   - Skip unmatched sessions with an explicit health warning; do not borrow another repo package opportunistically
2. Repo contract loading
   - Scan `<repo-root>/.governed/project.toml`
   - Scan `<repo-root>/.governed/capabilities/*/capability.contract.toml`
   - Build governed capability registry for valid contracts only
3. Adapter loading
   - Load `<repo-root>/.governed/adapters/codex/adapter.toml` for the first live adapter
   - Reject adapter projections whose target paths escape allowed local roots
4. Release apply
   - Resolve selected release manifest or git revision
   - Materialize local Codex assets from repo-governed source
   - Record local install state with applied revision
5. Target resolution
   - Repo capability contracts are authoritative for project-only knowledge
   - Legacy fallback remains only for unmigrated local Codex assets
6. Session routing
   - Explicit capability mention uses `capability.id` plus resolved aliases
   - AI semantic classification over compact evidence packages is the primary routing path
   - Resolved hints and aliases are optional accelerators or tie-breakers, not the gating mechanism
   - Negative hints may suppress obvious false positives, but must not become the primary exclusion engine
   - Durable capture must not depend on English hint phrases or coding-only wording
7. Evidence packaging
   - Build a compact evidence package from the session before classifier execution
   - Include the user ask, final outcome, changed files where available, successful commands, relevant failed commands, repo-relative artifact paths, and current steward/capability memory excerpts
   - Keep the package assistant-agnostic and language-agnostic so the same model works for coding, docs, review, QA, delivery, and ops sessions
   - Keep evidence compact enough for the existing scheduler runtime targets
8. Candidate validation
   - Resolved contract supplies allowed sections and resolved threshold
   - Current sensitive-content, duplicate, self-referential, and environment-local guards stay in place
   - Apply only when exact target + valid section + clean content + reusable lesson + confidence >= resolved threshold + governance allows it
   - Project-only writes land in repo-governed targets first inside the governed automation worktree; local adapter outputs are refreshed by `govkb apply codex`
9. Self-development classification
   - Existing capability expertise update: one completed project session can apply or stage when an exact governed capability and allowed target are resolved
   - New capability candidate: require repeated unmatched project work across at least two evidence sessions before staging a suggested contract
   - Reusable project knowledge outside a capability: stage under `.governed/knowledge/**` for review
   - Reject local, sensitive, duplicate, speculative, or maintenance-only lessons
10. Mutation safety
   - Scheduled auto-apply writes are allowed only in the dedicated governed automation branch/worktree for that repo + assistant
   - The active developer working tree must remain untouched by scheduled automation
   - Promotion from the governed automation worktree into a tracked release or developer branch remains an explicit step outside the scheduled run
11. Team redistribution
   - Promoted learning updates are tied to a release or git revision
   - Another local setup can run `govkb apply codex` and receive the updated capability expertise
   - Reports expose whether a learning update is local-only, staged, promoted, or redistributable

### 5.5) Data Consistency

**Transactions**
- File-based writes stay atomic through temp file + replace where already used
- Repo-governed memory mutation, report patch generation, and state advancement must preserve current ordering
- `govkb apply codex` must write local install state only after local materialization succeeds

**Invariants**
- Every contract-backed governed capability resolves to one canonical `capability.id`
- An assistant adapter may not weaken project governance
- A project-governed source target may not escape `.governed/`
- A scheduled session must resolve to at most one governed repo package before contract loading
- A processed session id is not re-applied on later runs unless explicitly backfilled outside the normal state path
- The success watermark never moves backwards
- Local install state must identify the repo revision or release that was applied
- Scheduled automation must not dirty the active developer working tree
- Active new governed capability contracts are never created from a single session without explicit review
- Existing capability updates and new capability candidates must record evidence session ids

**Idempotency**
| Operation | Key | On Duplicate |
|-----------|-----|--------------|
| Load capability contract | `capability.id + contract path` | latest valid contract for that owner path replaces prior load in same run |
| Resolve adapter rules | `assistant + repo root` | recompute resolved view deterministically |
| Apply governed release | `project + assistant + git revision` | skip or preview as already applied |
| Process session | session id | skip if already in processed state |
| Apply memory lesson | target file + normalized lesson | reject as duplicate |
| Stage new capability candidate | normalized candidate id + evidence session ids | merge evidence into existing staged candidate |
| Write report bundle | run timestamp | unique timestamped filenames |

### 5.6) Performance

| Query/Operation | Frequency | Est. Rows | Index |
|-----------------|-----------|-----------|-------|
| Load repo capability contracts | per run | 10-50 capabilities | filesystem directory scan |
| Load adapter manifests | per run | 1-5 adapters | filesystem directory scan |
| `govkb apply codex` manifest resolution | per install/update | 1 release | filesystem read |
| Session selection | per run | 0-25 recent sessions | existing index/file discovery |
| Evidence package build + target narrowing | per selected session | 10-50 capabilities | in-memory contract registry + compact session summary |
| Classifier call | per eligible session | 1 prompt | N/A |

Targets:
- normal daily run: `< 5 minutes`
- stretched daily run: `< 10 minutes`
- `govkb apply codex` for one assistant target: `< 5 minutes`
- multilingual and non-coding evidence packaging must stay within the same daily run targets

### 6) UI (if applicable)

No UI scope.

### 7) Notifications

| Status | Subject | Recipients | Timing |
|--------|---------|------------|--------|
| Processed | run report + log entry | local operator | end of run |
| Inconsistencies | run report health warning | local operator | end of run |
| Skipped | run report entry | local operator | end of run |
| Error | run log + report entry | local operator | immediate during run |

### 8) Observability

**Metrics**
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
- local installs updated from promoted learning
- classifier failures

**Reprocessing procedure**
- fix contract or adapter issue
- run `govkb apply codex --preview`
- run Codex adapter dry-run
- verify health report and target resolution
- run live once
- confirm state and report bundle

### 9) Test Strategy

| Level | Target | Focus |
|-------|--------|-------|
| Unit | contract loader / validator / merge helper | parse, merge, path safety, governance precedence |
| Integration | `govkb apply codex --preview` + Codex adapter dry-run with fixtures | materialization, session selection, semantic evidence packaging, apply/stage/reject behavior |
| Integration | learning classifier fixtures | existing capability updates, new capability candidate staging, semantic naming, reject reasons |
| End-to-end | one real local `govkb apply codex` plus one real Codex adapter run | local setup sync, audit artifacts, state advancement, scheduler compatibility |
| End-to-end | promoted learning applied by a second local setup fixture | team redistribution proof |
| End-to-end | multilingual and non-coding fixture sessions | semantic capture without project-specific English hint dependence |

**Data Consistency Tests**
- invalid capability contract does not break valid capabilities
- invalid adapter manifest does not corrupt project source behavior
- adapter cannot lower threshold or disable explicit acceptance
- duplicate lesson does not re-append
- file-only session processed without watermark rollback
- local install state records applied repo revision only after successful apply
- new capability candidate is staged, not activated, when evidence is repeated but unreviewed
- promoted existing capability expertise appears in materialized Codex output after `govkb apply codex`
- English hint mismatch does not block classification when semantic evidence is sufficient
- mixed-language or non-coding durable session can produce governed output without central rule edits

### 10) Risks & Dependencies

| Risk/Dependency | Impact | Mitigation/Fallback |
|-----------------|--------|---------------------|
| Contract migration misses a routing phrase | capability gets fewer candidates than before | compare dry-run outputs before live rollout; keep legacy fallback temporarily |
| Too many contract files drift over time | routing quality degrades | add contract lint step in follow-up phase |
| Repo-governed package becomes mixed with assistant-specific noise | project model loses portability | keep assistant-specific rules in adapter manifests only |
| `tomllib` unavailable in runtime | parser plan breaks | switch to JSON contract in fallback branch if runtime disproves assumption |
| Classifier prompt grows with too many contracts | runtime cost increases | keep deterministic rejection first, build compact evidence packages, and pass only likely capabilities plus steward memory |
| Local install drift across assistants | confusing support state | record governed local install state per project + assistant + revision |
| Session metadata lacks stable repo path | wrong package could be selected or session skipped | use explicit repo resolution rules and surface unmatched sessions in health report |
| Governed automation worktree diverges from tracked release | repo-first updates become hard to promote | require explicit promotion flow and report drift before release apply |
| Self-improvement produces noisy memory | long-term skill quality degrades | require reusable lesson checks, duplicate detection, confidence threshold, and report visibility |
| New capability candidates proliferate | repo gets cluttered | require repeated evidence sessions and keep candidates staged until explicit review |
| Hint-first or English-biased capture remains in the live path | framework fails outside current coding-heavy projects | make AI semantic classification the primary routing path; prove with multilingual and non-coding end-to-end cases before calling MVP done |

### 11) Phased Delivery

#### Phase 0: Shareable GovKB Framework Scaffold
- Create the reusable `govkb` repo/package structure with `pyproject.toml`, `src/govkb`, command modules, core modules, adapter folders, schemas, templates, examples, and tests
- Add command registration for: `init`, `validate`, `apply`, `status`, `review-memory`, `promote`, `create capability`
- Implement `govkb init` enough to scaffold a template project `.governed/` package
- Verify: `pipx install` or editable install exposes `govkb`; `govkb --help` succeeds; `govkb init` creates the expected template files
- Rollback: keep the framework repo unpublished/uninstalled; no project repo or local skill install changes are required

#### Phase 1: Contract Foundations
- Add `.governed/` package schema in the repo
- Add reusable contract loader and validator in `govkb/src/govkb/core/contracts.py`
- Define capability, adapter, release, and path-safety rules
- Verify: `govkb validate` passes against the template project, fixture contracts load, invalid contracts degrade safely, and repo resolution rules are documented
- Rollback: remove `.governed/` scaffold and contract loader references; keep current Codex-only routing untouched

#### Phase 2: Governed Apply For Codex
- Add `govkb/src/govkb/commands/apply.py`
- Materialize repo-governed source into local Codex setup
- Record local install state per project + assistant + revision
- Verify: preview/apply writes local install state only after successful materialization and can resolve governed automation workspace
- Rollback: disable `govkb apply codex` entrypoint and continue using current local Codex installs without repo-driven sync

#### Phase 3: Codex Adapter Integration
- Add `govkb/src/govkb/adapters/codex/memory_review.py`
- Add `govkb/src/govkb/core/learning.py` for self-development classification
- Replace hardcoded governed routing with AI-first semantic classification backed by repo contracts
- Classify reusable session outcomes as existing capability updates, new capability candidates, project knowledge, or rejects
- Preserve current session discovery, health reporting, and audit behavior
- Verify: dry-run output matches current behavior for migrated capabilities where semantics overlap, repo resolution works, unmatched sessions warn cleanly, multilingual/non-coding fixtures classify, and learning decisions are visible in reports
- Rollback: point the scheduled task back to the legacy local adapter path and preserve generated audit artifacts

#### Phase 4: Codex Materialization Migration
- Classify candidate local skills using the migration eligibility matrix before converting anything
- Use the PoC inventory as the first migration gate
- Materialize selected current memory-bearing Codex skills from repo-governed capability definitions
- Keep legacy fallback only for unmigrated local assets
- Validate that current approval-gated behavior survives migration
- Verify: migrated skills retain approval gates, legacy fallback still works, active developer working tree stays untouched during scheduled runs
- Rollback: restore affected migrated skills from legacy local installs and stop governed projection for those capabilities

#### Phase 5: Release And Multi-Adapter Hardening
- Add repo release manifests and update prompts
- Verify promoted learning can be applied by a second local setup through `govkb apply codex`
- Validate repo package against future `claude` and `copilot` adapter manifests
- Add health reporting for adapter conflicts and invalid local targets
- Verify: governed automation workspace can be promoted intentionally, release drift is reported, future adapter manifests validate without changing project source
- Rollback: pin Codex to the last known-good governed release and disable future-adapter validation gates until repaired

### 12) Definition of Done

- [ ] Governed routing no longer depends on a hardcoded per-skill map
- [ ] Shareable `govkb` repo/package can be cloned, installed, and used to scaffold a project `.governed/` package
- [ ] Project-only governed knowledge lives in git under `.governed/`
- [ ] `govkb apply codex` can materialize a repo release into local Codex setup
- [ ] Adapter governance cannot weaken project policy
- [ ] Invalid contracts surface as health warnings
- [ ] Codex adapter still writes reports, patches, logs, and state correctly
- [ ] One live `govkb apply codex` plus one live Codex adapter run succeed after dry-run verification
- [ ] One real work session updates an existing governed capability or stages it with a clear governance reason
- [ ] One repeated unmatched pattern stages a new governed capability candidate without activating it automatically
- [ ] One promoted learning update can be applied by another local setup through `govkb apply codex`
- [ ] PoC inventory continues to pass and the first-wave migration set matches the reviewed candidate list
- [ ] At least one durable session classifies without matching an English hint phrase
- [ ] At least one non-coding or mixed-language session produces governed output without adding a new central hint rule
