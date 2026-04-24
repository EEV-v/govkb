# Governed Skill Knowledge Framework

## Summary

Build an MVP for repo-governed AI collaboration knowledge.

The feature lets a project capture reusable lessons from real AI-assisted work, store them in a git-tracked package, review/promote them with governance, and apply them back into local assistant setups.

Codex is the first supported adapter. The project model must stay assistant-agnostic so Claude, Copilot, and other assistants can use the same governed package later.

## Business Problem

Teams repeat the same context and reasoning work across AI sessions.

Useful project knowledge is usually scattered across prompts, local assistant files, chat history, and one-off notes. It is hard to review, share, version, or apply consistently. Local assistant setup also drifts because there is no repo-owned source of truth.

Current problems this MVP addresses:

- reusable lessons from completed work are not captured into a governed project package
- project knowledge is too often tied to one assistant's local format
- routing and memory behavior can depend on hardcoded keyword maps
- adding a new governed capability can require central code changes
- local assistant artifacts can drift from the project team's accepted knowledge
- non-coding work, multilingual sessions, and mixed-language sessions are easy to miss
- auto-learning is risky without confidence, audit, staging, and promotion controls

## Product Goal

Create a generic governed knowledge framework for any project.

The framework should make project knowledge:

- repo-native
- versioned in git
- reviewable
- auditable
- assistant-agnostic
- locally materializable through CLI commands
- capable of controlled self-improvement from real work sessions

## MVP Scope

MVP includes:

- `.governed/` project package format
- governed capability contracts
- project knowledge and capability references stored in repo
- first public CLI surface for init, validate, apply, status, review, promote, and create flows
- Codex adapter as the first live assistant adapter
- semantic session classification for reusable learning
- staged creation of new capability candidates
- conservative auto-apply for high-confidence updates to existing capabilities
- audit reports for learned, staged, rejected, promoted, and applied changes
- migration path for existing local assistant skills/artifacts
- release/revision based local materialization through `govkb apply codex`

MVP does not need full parity across every assistant. It must prove the shared project model and one working adapter.

## Users

- project maintainers who define governed knowledge and approve promoted changes
- engineers/operators who use AI assistants during project work
- reviewers who need to inspect what was learned, staged, rejected, and applied
- future assistant adapter authors who need a stable project package contract

## Core Requirements

### Project Package

1. A project can add a repo-native governed package at:
   - `<project-root>/.governed/`
2. The repo package is the source of truth for project-only governed knowledge.
3. Assistant-local files are derived outputs, not the authoritative model.
4. Project knowledge and references live under the repo package:
   - `<project-root>/.governed/knowledge/...`
   - `<project-root>/.governed/capabilities/.../references/...`
5. Reusable framework source stays outside consuming project repos in the `govkb` package.

### Capability Contracts

1. Governed capabilities are declared with machine-readable contracts:
   - `<project-root>/.governed/capabilities/<capability_id>/capability.contract.toml`
2. Contracts define routing, memory policy, governance rules, and assistant materialization behavior.
3. Framework discovery uses contracts, not hardcoded per-capability keyword maps.
4. A new valid capability can participate in memory review without central scheduler edits.
5. Capability ids, summaries, and candidate facts are based on semantic task meaning and observed outcomes.

### Assistant Adapters

1. Assistant adapter definitions live in the repo package:
   - `<project-root>/.governed/adapters/<assistant>/...`
2. Codex is the first supported adapter.
3. The project model must support future Claude and Copilot adapters without redesign.
4. Adapter materialization must not weaken project-level governance rules.
5. Existing local Codex skill installs remain supported during migration through a controlled legacy path.

### CLI

MVP command surface:

1. `govkb init`
2. `govkb validate`
3. `govkb apply codex [--release <release_id>|--revision <git_sha>]`
4. `govkb status`
5. `govkb review-memory --assistant codex`
6. `govkb promote`
7. `govkb create capability <capability_id>`

CLI requirements:

- `govkb init` scaffolds a valid `.governed/` package
- `govkb validate` checks contracts, package shape, adapter definitions, and release metadata
- `govkb apply codex` applies a git-tracked release or revision into local Codex setup and records the applied revision
- `govkb status` reports local applied state and pending repo changes
- `govkb review-memory --assistant codex` runs the first live memory-review adapter
- `govkb promote` promotes reviewed governed changes into a tracked release
- `govkb create capability` stages a new capability shell with a valid contract

### Session Classification

1. Session triage is AI-first and semantic.
2. Aliases and hints can exist, but only as accelerators.
3. Classification must work without project-specific English keyword rules.
4. Classification must cover:
   - coding
   - docs
   - specs
   - review
   - QA
   - delivery
   - operations
   - other durable project work
5. Classification must support English, Russian, and mixed-language sessions.
6. No-match sessions are skipped with an explicit health signal.

### Learning Capture

The first live adapter must classify completed project work using compact evidence packages:

- user ask
- final outcome
- changed files where available
- successful commands
- relevant failed commands
- repo-relative artifacts
- existing capability and steward memory

Each reusable learning result is classified as one of:

- existing capability expertise update
- new governed capability candidate
- reusable project knowledge outside a capability
- rejected as local, sensitive, duplicate, or non-reusable

Rules:

- existing capability updates may auto-apply only when target capability, section, confidence, and governance rules pass
- approval-gated capabilities must stage changes for review
- new capability creation is staged for explicit review
- one session must not fully auto-create a new governed capability
- self-referential and environment-local sessions must not create durable memory

### Audit And Promotion

1. Memory review keeps auditable outputs:
   - reports
   - staged patches
   - applied patches
   - state tracking
   - dry-run support
   - health signals
2. Automated repo-first memory writes must not dirty an active developer working tree.
3. Scheduled governed mutations must run in an isolated automation branch or worktree.
4. Promotion into a tracked release is explicit.
5. Reports show learned, staged, rejected, promoted, and redistributable changes.

### Migration

Existing local assistant artifacts are classified into:

| Track | Use When | Source Of Truth | Local Outcome |
|------|----------|-----------------|---------------|
| Governed capability now | Artifact contains durable project knowledge, routing policy, memory policy, approval rules, or reusable review/QA/bugfix behavior | Repo contract under `.governed/` | Materialized from repo-governed source |
| Adapter-local only | Artifact is assistant-specific presentation, runtime glue, tool wrapper, or personal workflow logic | Local assistant adapter package | Stays local and may consume governed contracts |
| Legacy keep until migrated | Artifact is still needed, but conversion scope is not ready or parity is not proven | Existing local install until migration is complete | Supported as compatibility path |

## Out Of Scope

- full Claude adapter
- full Copilot adapter
- UI for memory governance
- replacing an existing scheduler
- changing live prompt assembly at assistant runtime
- bulk migration of every old skill/artifact
- fully automatic creation of new governed capabilities
- proving exact AI cost reduction in MVP

MVP proves capture, governance, redistribution, and one working assistant materialization path. Cost reduction can be measured after real team usage.

## Acceptance Criteria

MVP is accepted when:

1. A new project can run `govkb init` and get a valid `.governed/` package.
2. Project-only governed knowledge lives in git and is not stored as a Codex-only overlay.
3. `govkb validate` can validate package shape, capability contracts, adapters, and release metadata.
4. Framework discovers capabilities from repo contracts without hardcoded per-capability keyword maps.
5. A new valid capability contract can participate in memory review without central code edits.
6. The same repo package can define Codex adapter metadata and leave room for Claude/Copilot adapters.
7. `govkb apply codex [--release <release_id>|--revision <git_sha>]` applies a repo-tracked release/revision and records applied state.
8. Project-level governance cannot be weakened by adapter materialization.
9. Codex memory review resolves sessions to the correct repo-governed package or skips them with explicit health signals.
10. Codex memory review still discovers session files when an index is incomplete.
11. Automated repo-first memory writes stay isolated from the active developer working tree.
12. Reports include learned, staged, rejected, promoted, applied, and health outcomes.
13. Existing Codex local skills/artifacts remain usable through controlled migration and legacy fallback.
14. At least one real work session produces a high-confidence reusable lesson that updates an existing capability with report evidence.
15. At least one repeated or unmatched work pattern is staged as a new capability candidate.
16. A promoted governed learning update can be applied by another local setup through `govkb apply codex`.
17. At least one durable session classifies without matching an English hint phrase.
18. At least one non-coding or mixed-language session classifies into governed output without adding a central hint rule.
