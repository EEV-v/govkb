# GovKB KB Quality Implementation Plan

Last updated: 2026-04-24

## Purpose

This plan addresses the current quality gap in governed capability knowledge bases.

The framework already works, but the resulting KB is too shallow and the current capture path still depends too much on lexical hints. The next increment must improve knowledge capture quality without weakening governance, isolation, or auditability.

This increment also removes the main scaling bottleneck:

- hint-first, English-biased, coding-biased session detection
- lexical candidate naming that mirrors prompt wording instead of task meaning

## Scope

In scope:

- clean-start testing only; no backward-compatibility code for older GovKB-generated artifacts
- save candidate knowledge immediately after review without activating it
- shift session capture toward AI-first semantic classification
- extend governed contracts with bootstrap and KB-health metadata
- add a first-class KB bootstrap command
- enrich governed capability memory structure for repo facts
- initialize KB automatically after candidate activation when policy allows
- add thin-KB health signals
- prove the richer KB on AIApps and at least one non-coding or mixed-language path

Out of scope:

- changing the core governed contract ownership model
- changing cron scheduling
- introducing new assistant adapters
- bulk migration of all historical skills
- storing raw or sanitized session transcripts in `.governed`
- full multi-candidate merge UX, as long as candidate artifacts preserve enough distilled knowledge for that later flow
- compatibility logic for previously generated GovKB candidate/capability scaffolds in this test slice

## Target Behavior

### 1. AI-first session triage

When memory review sees a completed session:

- reject immediately only for deterministic governance blockers:
  - self-referential GovKB maintenance
  - secret-like content
  - assistant-runtime-only noise
- otherwise build a compact evidence package and send it to AI classification

Evidence package should include, when available:

- user ask
- final assistant outcome
- changed files
- successful commands
- relevant failed commands
- project/capability contracts
- existing steward/capability memory
- repo-relative artifact paths

AI classification output should be structured, for example:

- durable = true|false
- target = existing capability | steward | candidate
- semantic topic label
- candidate summary
- structured facts with section, confidence, provenance, and optional repo paths

Routing hints remain allowed, but only as a secondary routing signal or tie-breaker.

### 2. Candidate knowledge capture

When memory review sees repeated unmatched work:

- gather session context from local session storage in memory
- run prompt/classifier over that gathered data
- persist repo candidate artifacts immediately
- do not require promotion first

Threshold rule:

- one unmatched durable session may create a `collecting` candidate with distilled facts
- two distinct confirming sessions move the same candidate to `ready-for-review`
- activation and auto-create thresholds remain gated separately

Repo candidate artifacts should contain only distilled governed data, for example:

- candidate metadata
- reusable extracted facts
- source session ids and timestamps
- short rationale and grouping hints

Use a structured fact model, not only markdown. For example:

- `candidate.toml`
- `candidate-facts.toml`
- `draft-capability.contract.toml`
- `draft-instructions.md`

`candidate-facts.toml` should preserve, per fact:

- stable fact text
- target memory section
- confidence
- provenance session ids
- optional repo paths
- optional grouping key

Candidate ids and names should come from semantic topic synthesis, not direct prompt tokenization.

Local-only runtime storage keeps:

- original session files
- sanitized working payloads
- audit logs and reports

No raw or sanitized transcript excerpts should be written into `.governed`.

### 3. Contract-driven bootstrap and health metadata

Add governed contract inputs so bootstrap and validation do not depend on project-specific heuristics.

Possible contract additions:

- `[bootstrap]`
- `profile = "workflow" | "steward" | "reviewer" | "reference"`
- `repo_roots = [...]`
- `authority_paths = [...]`
- `seed_paths = [...]`
- `[kb_health]`
- `requires_verification_commands = true|false`
- `requires_repo_map = true|false`
- `required_sections = [...]`

Rule:

- `init-kb`, thin-KB checks, and candidate-to-capability bootstrap should use these governed fields
- avoid introducing new central hardcoded project logic

### 4. KB bootstrap command

Add:

- `govkb init-kb <project-root> --capability <id>`
- `govkb init-kb <project-root> --all`

Behavior:

- read capability contract, instructions, and current memory
- inspect only repo files relevant to the capability
- append durable initial entries
- run `govkb validate`
- report files used as evidence

### 5. Richer memory sections

Keep current memory sections, but require support for durable repo-fact capture such as:

- `Stable Workflows`
- `Commands And Verification`
- `Repo Conventions`
- `Code And Docs Map`
- `Authority Rules`

Design rule:

- use repo-relative paths only
- prefer short bullets
- keep entries operational, not narrative

### 6. Multilingual and non-coding support

Classifier prompts and evidence handling must work for:

- English
- Russian
- mixed-language sessions
- coding work
- docs/spec/review/delivery/QA/ops work

Design rules:

- do not require code diffs for a session to be durable
- allow durable facts to originate from commands, artifacts, review output, or delivery outcomes
- do not require English hint phrases to reach classification

### 7. Candidate activation bootstrap

When `govkb create capability --from-candidate <candidate-id>` succeeds:

- create the capability scaffold
- generate the initialize prompt
- immediately run the same KB bootstrap pipeline in-process unless `--no-init-kb` is passed
- if bootstrap cannot prove durable facts, leave the capability valid but warn that KB stayed minimal

The bootstrap source should prefer distilled candidate knowledge first, then repo inspection.

Clean-start rule:

- this increment may assume regenerated candidate artifacts and regenerated test capabilities
- no migration adapter is required for older candidate formats

### 8. Thin-KB detection

Add thin-KB checks to validation/status.

Thin means one or more of:

- only scaffold headings and no real entries
- no verification command for a workflow capability
- no repo-fact entry for a capability that claims stable workflow scope
- only one broad summary line after activation from repeated evidence

Output:

- warning, not hard failure
- clear list of affected capabilities
- suggested next command:
  - `govkb init-kb --capability <id>`

## Required Code Changes

### CLI

- add `govkb/src/govkb/commands/init_kb.py`
- register `init-kb` in:
  - [cli.py](/home/ev/code/Clearing/govkb/src/govkb/cli.py)

### Core helpers

- extend:
  - `govkb/src/govkb/core/contracts.py`
  - [init_prompt.py](/home/ev/code/Clearing/govkb/src/govkb/core/init_prompt.py)
- add helper module for repo-fact extraction, for example:
  - `govkb/src/govkb/core/kb_bootstrap.py`

Responsibilities:

- read contract-driven bootstrap metadata
- pick files to inspect from capability scope and candidate knowledge
- consume distilled candidate knowledge when present
- derive reusable repo-fact bullets
- map bullets to memory sections
- reject local-only or one-off findings

### Candidate flow

- update:
  - `govkb/src/govkb/core/candidates.py`
  - [create_capability.py](/home/ev/code/Clearing/govkb/src/govkb/commands/create_capability.py)

Responsibilities:

- stage candidate knowledge immediately from in-memory prompt/classifier output
- stop writing transcript-like user/assistant excerpts into repo candidate files
- persist only provenance, extracted reusable facts, and grouping metadata
- synthesize candidate ids and names from semantic task meaning rather than prompt wording
- trigger initial KB bootstrap after candidate activation
- carry candidate knowledge into bootstrap
- allow opt-out for debugging

Suggested repo candidate shape:

- `candidate.toml`
- `candidate-facts.toml`
- `draft-capability.contract.toml`
- `draft-instructions.md`

If a human-readable digest is kept, it must be summary-level only and must not contain transcript-like excerpts.

### Validation and status

- update:
  - `govkb/src/govkb/commands/validate.py`
  - `govkb/src/govkb/commands/status.py`

Responsibilities:

- use contract-driven KB-health expectations
- detect thin KB
- expose warnings and suggested remediation

### Memory review

Update the Codex memory-review path conservatively:

- replace hint-first prescreen with:
  - deterministic reject for obvious governance blockers
  - AI-first classification for almost all meaningful sessions
- save candidate knowledge before promotion or activation when repeated unmatched work is detected
- allow capability memory sections that store repo-map facts
- improve routing so semantic task meaning and repo evidence choose the target capability
- keep routing hints only as optional accelerators or tie-breakers
- do not store absolute local paths or assistant-runtime details

Likely files:

- [codex-memory-review](/home/ev/code/Clearing/govkb/src/govkb/adapters/codex/bin/codex-memory-review)
- `govkb/src/govkb/adapters/codex/memory_review.py`

## Governance Rules

Do not weaken any of these:

- no secrets in memory
- no raw or sanitized session transcripts in `.governed`
- no assistant-runtime artifacts as durable project memory
- no absolute local paths unless contract-owned and intentionally governed
- no auto-apply below the active confidence threshold
- explicit-acceptance capabilities remain gated

## Acceptance Criteria

This increment is complete when all are true:

1. candidate knowledge is saved before promotion or activation
2. repo candidate artifacts contain no transcript-like excerpts
3. first unmatched durable session creates a collecting candidate and second confirming session advances it to ready-for-review
4. `govkb init-kb` works for one capability and `--all`
5. durable session capture does not depend on English hint phrases
6. bootstrap and thin-KB checks are driven by governed contract metadata
7. activating a capability from candidate knowledge leaves it with non-trivial memory when durable facts exist
8. AIApps story/backend/auth capability memory includes stable repo-relative facts
9. at least one non-coding or mixed-language scenario classifies correctly without custom hint additions
10. thin KB is surfaced by validation or status
11. second-home reapply receives the richer KB unchanged

## Implementation Order

### Phase A. AI-first session classification

- minimize deterministic prescreen
- build compact evidence package from session outcome and artifacts
- shift routing and candidate synthesis to AI semantic output

### Phase B. Candidate storage boundary

- stop persisting transcript-like candidate evidence in repo
- persist distilled structured candidate knowledge plus provenance only
- keep full gathered session context local-only

### Phase C. Contract metadata

- extend contract schema for bootstrap and KB-health metadata
- wire validation for the new governed fields
- keep this contract-driven, not project-hardcoded

### Phase D. Bootstrap command

- add CLI command
- reuse current initialize prompt rendering
- support dry-run first if needed

### Phase E. Repo-fact extraction

- derive stable facts from repo files
- add memory-section mapping
- validate against governance filters

### Phase F. Candidate activation hook

- auto-run bootstrap after capability creation from candidate
- preserve deterministic output where evidence is thin

### Phase G. Thin-KB health checks

- warn in validate/status
- make warning text actionable

### Phase H. Real-life proof

- reset AIApps governed artifacts and local Codex materialization for a clean-start run
- verify candidate knowledge is saved immediately after repeated unmatched sessions
- bootstrap AIApps capabilities
- rerun review/promote flow
- verify richer KB in second Codex home
- add one multilingual or non-coding scenario and verify semantic capture without hint tuning

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| AI-first classification becomes too permissive | KB becomes noisy | keep deterministic governance rejection and confidence thresholds |
| Bootstrap writes low-value noise | KB becomes cluttered | keep conservative evidence threshold and repo-file scoping |
| Candidate repo artifacts become chat-like again | contributors get noisy repo state | persist distilled knowledge only; keep transcripts local-only |
| Bootstrap stores local-only facts | portability degrades | allow only repo-relative facts and governed paths |
| Candidate activation becomes too magical | debugging gets harder | support `--no-init-kb` and clear output |
| Thin-KB warning is noisy | users ignore it | warn only on clear scaffold-thin patterns |
| English or coding assumptions leak back in | product stops generalizing | add multilingual and non-coding regression tests |
