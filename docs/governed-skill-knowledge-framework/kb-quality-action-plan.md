# GovKB KB Quality Action Plan

Last updated: 2026-04-24

## Problem

GovKB now proves the governed loop mechanics:

- repo-native `.governed` source
- project-scoped Codex materialization
- memory-review reports and promotion
- candidate creation and activation
- multi-project isolation

But the quality model is still too narrow for a reusable product.

Observed gaps:

- newly scaffolded capabilities start with almost empty KB
- KB initialization prompt files are generated, but the KB bootstrap is not executed as part of normal flow
- useful session-derived knowledge is captured too late; we wait for activation instead of saving reusable candidate knowledge immediately
- capability activation from a candidate does not convert candidate evidence into first useful memory
- memory review favors short operational lessons and under-captures repo facts such as code locations, docs locations, scripts, and authoritative entrypoints
- current candidate artifacts are still too close to session content; repo-governed source should store distilled knowledge, not transcript-like evidence
- broad project steward memory is absorbing knowledge that should move into narrower capabilities sooner
- session prescreen and routing are still too hint-driven
- the current capture path is too English-biased and too coding-biased
- candidate naming can still mirror prompt wording instead of semantic task meaning

Testing constraint for this slice:

- do not add backward-compatibility code for older GovKB-generated candidate or capability scaffolds
- treat this increment as a clean-start test path
- regenerate governed test artifacts instead of carrying forward old candidate artifact formats

## Goal

Close the KB quality gap and move GovKB toward the intended product model:

- AI-first semantic capture instead of hint-first routing
- coding and non-coding task support under one governed model
- English, Russian, and mixed-language support
- project growth driven by observed reusable behavior, not by central phrase lists

Success means:

1. new governed capabilities are created with a meaningful initial KB
2. candidate knowledge is saved immediately after review without waiting for promotion
3. existing capabilities can accumulate stable repo facts, not only short lesson bullets
4. broad steward memory stays lean because repeated specialized knowledge moves into dedicated capabilities
5. a second local setup receives the richer KB and benefits from it without rediscovery
6. durable sessions no longer depend on English hint phrases to reach classification
7. candidate names and facts are derived from semantic task meaning, changed artifacts, commands, and outcomes
8. the same framework can classify coding, docs, review, delivery, QA, ops, and similar work

## Workstreams

### 1. Capability bootstrap

- add a first-class KB bootstrap command
- make it runnable for one capability or all capabilities
- use repo facts plus candidate knowledge to populate initial memory

### 2. Candidate knowledge capture boundary

- save reusable knowledge at candidate stage as soon as cron sees one unmatched durable session
- keep gathered session payload local-only under runtime and audit storage
- persist to repo only distilled candidate artifacts:
  - candidate metadata
  - reusable extracted facts
  - source session ids and timestamps
  - short rationale
- do not store raw or sanitized transcript excerpts in `.governed`
- first unmatched durable session creates a `collecting` candidate
- second distinct confirming session moves the same candidate to `ready-for-review`
- activation and redistribution still stay gated

### 3. Richer memory model

- keep concise lessons
- also capture durable repo-relative facts:
  - code locations
  - docs locations
  - scripts and entrypoints
  - verification commands
  - authority rules when docs and code disagree

### 4. Contract-driven bootstrap and health rules

- extend the governed contract so bootstrap and thin-KB checks do not rely on ad hoc project heuristics
- declare capability profile and bootstrap hints in the contract, for example:
  - workflow vs steward vs reviewer profile
  - relevant repo roots/files
  - authority sources
  - required KB coverage such as repo-map or verification facts
- use those governed inputs in both `init-kb` and validation/status warnings

### 5. AI-first semantic session classification

- keep deterministic prescreen only for obvious rejection cases:
  - self-referential GovKB maintenance
  - secrets
  - local runtime noise
- send almost all remaining meaningful sessions to AI classification
- use AI to decide:
  - durable or not durable
  - existing capability vs steward vs candidate
  - candidate semantic label
  - reusable structured facts
- keep routing hints only as optional accelerators or tie-breakers

### 6. Multilingual and non-coding support

- design prompts and evidence packaging so the classifier works on English, Russian, and mixed-language sessions
- do not assume code changes are the only durable evidence
- support evidence from:
  - changed files
  - docs reviewed or updated
  - commands executed
  - validation results
  - deployment or delivery outcomes
  - ticket or artifact updates
  - review findings

### 7. Candidate activation quality

- when a candidate becomes a capability, do not leave it nearly empty
- generate and validate initial memory from:
  - candidate knowledge
  - contract scope
  - direct repo inspection

### 8. Candidate grouping and merge decisions

- keep capture conservative, but do not force early capability activation
- support later decisions such as:
  - merge candidate knowledge into an existing capability
  - group several candidate clusters into one new capability
  - reject or archive low-value candidates
- design candidate artifacts so these later decisions do not need transcript recovery
- store candidate knowledge in a structured fact model, not only markdown summary text

### 9. Thin-KB health checks

- detect capabilities that are still scaffold-only or nearly empty
- surface that in `govkb validate` and `govkb status`
- keep the warning actionable

### 10. Real-life proof

- reset AIApps governed artifacts and local materialization to clean-start state
- rerun AIApps validation with richer KB
- prove the richer KB is applied to a second clean Codex home
- run a follow-up AIApps task and confirm reuse
- prove at least one non-coding or mixed-language scenario is captured correctly without new hint rules

## Delivery Order

1. lock clean-start boundary and drop backward-compatibility work from scope
2. move candidate storage to distilled structured knowledge only
3. replace hint-first prescreen with AI-first semantic classification plus minimal deterministic rejection
4. redesign candidate naming and fact extraction around semantic task meaning and observed outcomes
5. extend governed contracts with bootstrap and KB-health metadata
6. implement `govkb init-kb`
7. extend memory sections and insertion logic
8. hook candidate activation into KB bootstrap
9. add thin-KB validation/status warnings
10. rerun AIApps and clean-start project tests
11. verify second-home redistribution
12. verify multilingual or non-coding reuse behavior

## Exit Criteria

This slice is done when all are true:

- reusable candidate knowledge is saved before promotion
- first durable unmatched session creates a collecting candidate and second confirming session advances it
- repo candidate artifacts contain no raw or sanitized transcript excerpts
- durable sessions no longer depend on English hint phrases to reach classification
- routing hints are optional accelerators, not the primary capture mechanism
- `govkb init-kb` exists and works for one capability and for all capabilities
- bootstrap and thin-KB behavior are driven by governed contract metadata, not project-specific hardcoding
- at least one AIApps capability stores code/docs/scripts/verification knowledge in durable memory
- candidate-created capabilities no longer remain scaffold-thin after activation
- at least one non-coding or mixed-language scenario produces durable classified output without custom hint additions
- `govkb validate` or `govkb status` warns on thin KB
- second-home AIApps reapply shows the richer KB and a follow-up session reuses it

## Out Of Scope

- redesigning the whole governed contract model
- adding Claude or Copilot adapters
- replacing memory-review classifier with a different runtime
- auto-promoting every staged lesson without governance
- storing raw or sanitized session transcripts in repo-governed source
