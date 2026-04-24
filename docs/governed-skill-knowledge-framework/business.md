# Governed Skill Knowledge Framework

## Tracking
- Azure Epic: not linked
- Azure Feature: not linked
- Monday: not linked

## Request

Turn the current Codex memory-review task into a generic governed knowledge framework.

The product-level goal is bigger than moving skill files around: make any project capable of improving its own AI collaboration quality over time. As the team uses AI on real project work, proven solutions, reusable commands, review patterns, debugging tactics, and domain lessons should be captured into governed project knowledge, shared through git, and applied back into each team member's local assistant setup.

Today the scheduled task at `/home/ev/.codex/bin/codex-memory-review` still contains hardcoded project skill routing such as `KEYWORD_SKILL_HINTS`. It also assumes project-local knowledge can be modeled as a Codex-centric skill overlay.

That is too narrow.

The target model is different:

- project-only knowledge is repo-native and assistant-agnostic
- governed capabilities are declared by contract
- reusable framework tooling lives in a separate shareable `govkb` repo/package
- Codex is the first adapter, not the source-of-truth model
- the same project package must be reusable for other assistants such as Claude or Copilot
- session understanding is AI-first and semantic, not keyword-first
- the framework must work for coding and non-coding project work
- the framework must support English, Russian, and mixed-language sessions
- local assistant setup should be materialized from the git-tracked project package through concrete `govkb` CLI commands such as `govkb apply codex`
- existing governed capabilities can grow in expertise from high-confidence real work sessions
- repeated new work patterns can create governed capability candidates for review and promotion
- new governed capabilities can be created later without modifying central scheduler code

This feature is the design and first implementation foundation for that system. A later phase can override the default skill creator and retrofit the remaining older skills, but the contract and framework need to support that path now.

## Business Problem

- The current memory-review scheduler is coupled to a named Clearing skill list.
- Project-only knowledge is still being modeled through Codex-specific skill packaging instead of a repo-native governed source.
- Global reusable capability memory and project-local knowledge do not have a clean separation.
- Project portability is weak because routing knowledge is embedded in one local script instead of living with the governed project package.
- Local assistant setup can drift because there is no governed git-tracked source-of-truth plus release-aware `govkb apply codex` flow.
- Adding a new governed capability still requires touching framework code, which slows down growth and creates a permanent maintenance hotspot.
- Teams repeatedly pay chatbot context and reasoning cost for problems that were already solved in earlier sessions because reusable project learning is not captured, promoted, and redistributed automatically.
- The current capture model is too dependent on English hints and coding-oriented phrasing, which makes it weak for broader project work and weak outside current projects.
- Candidate naming and routing quality can still mirror prompt wording instead of actual reusable task meaning.

## Goal

Create a governed knowledge framework where:

1. the repo is the source of truth for project-only governed knowledge
2. routing and memory policy come from machine-readable capability contracts plus AI semantic classification, not hardcoded Python maps or English keyword lists
3. project knowledge is not constrained by Codex skill packaging
4. reusable CLI/tooling source lives in a separate shareable `govkb` repo/package
5. Codex, Claude, Copilot, and future assistants can consume the same governed project package through adapters
6. `govkb init` can scaffold a project package and `govkb apply codex` can materialize repo changes into local Codex setup from git-tracked releases
7. existing governed capabilities can automatically gain reusable expertise from high-confidence team work sessions
8. repeated patterns that do not fit an existing capability can be staged as new governed capability candidates
9. classification and capability growth work for coding, docs, QA, review, delivery, ops, and similar project work
10. classification can succeed for English, Russian, and mixed-language sessions without adding per-project language rules
11. promoted learning can be shared back to the team through git so future assistant sessions rediscover less context and reuse more proven project behavior
12. auto-apply behavior stays conservative and auditable

## Technical Requirements

1. Introduce a repo-native governed package root at:
   - `<project-root>/.governed/`
2. Keep reusable framework source outside project repos in a separate shareable `govkb` repo/package that can be cloned, installed, tested, and reused across projects.
3. Introduce machine-readable governed capability contracts at:
   - `<project-root>/.governed/capabilities/<capability_id>/capability.contract.toml`
4. Keep project-only knowledge and references under the repo, not under Codex-specific skill overlays:
   - `<project-root>/.governed/knowledge/...`
   - `<project-root>/.governed/capabilities/.../references/...`
5. Add assistant adapter definitions under the same repo package so the project can target multiple assistants:
   - `<project-root>/.governed/adapters/<assistant>/...`
6. Add governed release/install manifests in git so local setup can be applied from repo revisions:
   - `<project-root>/.governed/releases/<release_id>.toml`
7. Use `govkb` as the CLI/app alias with this first-increment public command surface:
   - `govkb init`
   - `govkb validate`
   - `govkb apply codex [--release <release_id>|--revision <git_sha>]`
   - `govkb status`
   - `govkb review-memory --assistant codex`
   - `govkb promote`
   - `govkb create capability <capability_id>`
8. Remove the requirement for central hardcoded skill routing such as `KEYWORD_SKILL_HINTS`.
9. Session triage for reusable learning must be AI-first and semantic; aliases and hints may exist, but they are optional accelerators and must not be the primary capture mechanism.
10. Session classification must work for coding and non-coding project work, including docs/spec/review/delivery/QA/ops style sessions when durable reusable output exists.
11. Session classification must support English, Russian, and mixed-language sessions without requiring language-specific project hardcoding.
12. Keep current scheduler audit behavior for the first live adapter:
   - reports
   - applied and staged patches
   - state tracking
   - dry-run support
13. Preserve strict memory governance:
   - auto-apply only for high-confidence reusable lessons
   - approval-gated capabilities must still stage when explicit acceptance is required
   - self-referential and environment-local sessions must not generate durable memory
14. Project-only governed knowledge mutations must target the repo package first; local assistant artifacts are derived outputs.
15. The scheduled adapter must resolve each session to the correct repo-governed package from session metadata such as repo path or working directory; no-match sessions must be skipped with an explicit health signal.
16. Automated repo-first memory writes must not dirty an active developer working tree; the first implementation must isolate scheduled governed mutations inside a dedicated governed automation branch or worktree, with explicit promotion into a tracked release.
17. The Codex adapter must continue discovering real session files even if `session_index.jsonl` is incomplete.
18. The first implementation must preserve existing local Codex skill installs as supported legacy materializations during migration; repo-governed packages become authoritative without breaking current workflows.
19. The first implementation must be ready to add Claude and Copilot adapters without redefining the project knowledge model.
20. The migration model must classify existing local skills into explicit tracks:
   - governed capability now, when the skill carries durable project knowledge or governance that should survive across assistants
   - adapter-local only, when the skill is assistant-specific or tool-wrapper behavior and should not become project source-of-truth
   - legacy keep until migrated, when the skill remains operationally needed but is not yet converted
21. The first live adapter must identify reusable learning from completed project work by using AI semantic classification over compact evidence packages, including:
   - user ask
   - final outcome
   - changed files where available
   - successful commands
   - relevant failed commands
   - repo-relative artifacts
   - existing capability and steward memory
22. The first live adapter must classify reusable learning from completed project work as:
   - existing capability expertise update
   - new governed capability candidate
   - reusable project knowledge outside a capability
   - reject as local, sensitive, duplicate, or non-reusable
23. Existing governed capability expertise updates may auto-apply only when the target capability, section, confidence, and governance rules are all satisfied.
24. New governed capability creation must be staged for explicit review in the first implementation; it must not be fully auto-created from one session.
25. Candidate ids, summaries, and facts must be derived from semantic task meaning and observed outcomes rather than raw prompt tokenization.
26. Reports must make the self-improvement loop visible by showing learned, staged, rejected, promoted, and redistributable changes.

## Migration Eligibility

Use this matrix to decide how current local skills move into the repo-first model.

| Track | Use When | Source Of Truth | Local Codex Outcome |
|------|----------|-----------------|---------------------|
| Governed capability now | The skill contains durable project knowledge, routing hints, memory policy, approval rules, or reusable review/QA/bugfix behavior that should work across assistants | Repo contract under `.governed/` | Materialized from repo-governed source |
| Adapter-local only | The skill is Codex-specific presentation, runtime glue, tool-wrapper behavior, or personal workflow logic that does not represent project knowledge | Local assistant adapter package | Stays local and may consume governed contracts where relevant |
| Legacy keep until migrated | The skill is still needed in production use, but conversion scope is not ready or parity is not proven yet | Existing local install until migration is complete | Remains supported as a compatibility path during transition |

## Non-Goals

- overriding the default skill creator in this first delivery
- bulk retrofitting every existing skill, including non-governed or system skills
- changing live prompt assembly for `SKILL.md` at runtime
- replacing the current cron schedule with a different scheduler
- introducing a UI for memory governance in this phase
- shipping fully working Claude and Copilot adapters in the first increment
- fully automatic new governed capability creation without explicit review
- proving exact chatbot cost reduction in the first increment; the first increment proves reusable learning capture and redistribution, then cost reduction can be measured later

## Acceptance Intent

This request should be considered satisfied when all of the following are true:

1. Project-only governed knowledge lives in the git repo and is not modeled as a Codex-only overlay.
2. The reusable `govkb` framework repo/package can be cloned, installed, and used through `govkb init` to scaffold a project `.governed/` package without copying framework source into the project repo.
3. The framework can discover governed capabilities from repo contracts without a hardcoded per-capability keyword map.
4. A new governed capability with a valid repo contract can participate in memory review without central script edits.
5. The same repo package can define assistant adapters for Codex and future targets such as Claude or Copilot without redefining project knowledge.
6. `govkb apply codex [--release <release_id>|--revision <git_sha>]` can apply a repo-tracked release or revision to local Codex setup and record the applied revision.
7. Project-local governance rules cannot be weakened by adapter-specific materialization.
8. Scheduled session routing can resolve the correct repo-governed package or skip no-match sessions with an explicit health signal.
9. Automated repo-first memory writes stay isolated from the active developer working tree until they are explicitly promoted into a tracked release.
10. The first live adapter still produces auditable reports, staged patches, applied patches, and health signals.
11. The first implementation keeps existing Codex skill installs working through a controlled migration and legacy fallback path while repo-governed packages become the authoritative source.
12. The framework is documented well enough that a later task can override the skill creator and scaffold compliant governed capabilities and adapters automatically.
13. Existing local skills can be classified consistently into governed, adapter-local, or legacy migration tracks without redesigning the framework.
14. At least one real work session can produce a high-confidence reusable lesson that updates an existing governed capability in the repo-governed automation worktree, with report evidence and no active working-tree mutation.
15. At least one repeated or unmatched work pattern can be staged as a new governed capability candidate instead of requiring a central scheduler code edit.
16. A promoted governed learning update can be applied by another local setup through `govkb apply codex`, proving the team-sharing loop from captured lesson to redistributed assistant behavior.
17. At least one durable session must reach classification without matching an English hint phrase, proving semantic capture is not gated by project-specific wording.
18. At least one non-coding or mixed-language project session must classify into governed output without adding a new central hint rule.
