# Memory Review Capability Evolution - Use Cases

Last updated: 2026-05-28

## Scope

These use cases cover the first engineering slice for a memory-review capability-evolution lane. The slice extends Codex memory review so it can stage reviewable proposals for existing governed capabilities, then adds a manual `govkb proposals` review/apply flow. Existing memory lessons, semantic new-capability candidates, strict validation, and cron safety must remain compatible.

## Actors

| Actor | Goal |
|---|---|
| Maintainer | Review capability-evolution proposals without reading raw assistant transcripts. |
| Engineer | Turn repeated work into reusable governed scripts, wrappers, prompts, runbooks, or instruction updates. |
| Scheduled memory-review cron | Stage useful proposals without writing executable artifacts or rewriting capability instructions. |
| Reviewer | Approve only safe, targeted, auditable proposal application. |
| Future assistant session | Benefit from applied capability improvements through governed package materialization. |

## Background

Given a GovKB project stores governed source under `.governed/`
And existing capability packages live under `.governed/capabilities/<capability-id>/`
And new capability candidates continue to live under `.governed/candidates/<candidate-id>/`
And capability-evolution proposals are staged under `.governed/review-proposals/<proposal-id>/`
And current memory review already supports memory candidates and one semantic new-capability candidate

## Scenarios

### UC-1: No proposal opportunities preserve existing memory-review behavior @smoke

Given a session produces only durable memory lessons or no durable learning
When the maintainer runs `govkb review-memory --assistant codex --project-root <project-root>`
Then existing auto-apply, stage, reject, candidate-staging, report, and progress behavior remains unchanged
And no `.governed/review-proposals/<proposal-id>/` folder is created
And the report shows zero capability-evolution proposals

### UC-2: Memory review stages a script proposal for an existing capability @smoke

Given a classified session contains high-confidence evidence that an existing capability repeatedly needs a reusable read-only script
And the proposed output path is under `.governed/capabilities/<capability-id>/tools/scripts/`
When memory review validates the classifier result
Then it stages a proposal under `.governed/review-proposals/<proposal-id>/`
And the proposal metadata includes target capability, proposal type, output path, purpose, inputs, outputs, safety class, evidence summary, source session, and verification command
And no executable script file is written by the review run

### UC-3: Prompt, runbook, and instruction-update proposals use the same review inbox @regression

Given a classifier result proposes `prompt`, `runbook`, or `instructions_update` improvements for an existing capability
When memory review stages valid proposals
Then each proposal is stored under the project-level `.governed/review-proposals/` inbox
And each proposal points to an approved output path under the target capability package
And proposal type is distinct from memory lessons and new capability candidates

### UC-4: Unsafe or weak proposal rows are rejected @regression

Given a classifier result contains a proposal with a missing target capability, unsupported type, absolute path, parent traversal, sensitive content, raw transcript detail, customer evidence, or missing safety metadata
When proposal validation runs
Then the row is rejected
And no proposal folder or output artifact is created for that row
And the memory-review report records the rejection reason without copying secret-like or transcript-specific text

### UC-5: Scheduled cron remains stage-only @regression

Given scheduled memory review runs in normal apply mode
And a session supports a capability-evolution proposal
When the review completes
Then cron can stage proposal metadata in `.governed/review-proposals/<proposal-id>/`
And cron does not apply proposals, create executable files, rewrite `instructions.md`, or edit `tools/README.md`
And the report explains that maintainer approval is required before file generation

### UC-6: Maintainer can list and inspect staged proposals @regression

Given one or more proposals exist under `.governed/review-proposals/`
When the maintainer runs `govkb proposals list <project-root>`
Then output includes proposal id, status, target capability, type, safety class, proposed output path, source session, and path to the proposal folder
When the maintainer runs `govkb proposals show <proposal-id> --project-root <project-root>`
Then output includes the proposal metadata and sanitized body needed for review
And it does not read or print raw session transcript content

### UC-7: Approved proposal apply writes files only after approval metadata is complete @regression

Given a staged proposal has `status = "approved"`, approver, approved timestamp, target capability, proposal type, approved output paths, safety class, and verification command
When the maintainer runs `govkb proposals apply <proposal-id> --project-root <project-root>`
Then GovKB writes only the approved output paths under `.governed/capabilities/<capability-id>/`
And the proposal status changes to an applied or completed state with apply metadata
And the command runs or prints the configured verification path according to the implementation contract

### UC-8: Mutating script proposals require preview or dry-run behavior @regression

Given an approved `script` or `wrapper` proposal declares mutating behavior
When `govkb proposals apply` validates the proposal
Then apply is blocked unless the proposal declares a `--dry-run`, `--preview`, or equivalent explicit confirmation pattern
And the rejection points to proposal metadata rather than executing the proposed script

### UC-9: New capability candidates stay on the existing candidate flow @regression

Given a session reveals reusable unmatched work that does not belong to an existing capability
When memory review classifies the session
Then new capability creation continues through `.governed/candidates/<candidate-id>/` and `govkb candidates`
And no capability-evolution proposal is staged for a missing target capability

## Scenario Outlines

### UC-10: Supported proposal types are accepted when paths and safety metadata are valid @regression

Given a proposal has type <proposal_type>
And the output path is under the target capability package
When proposal validation runs
Then the proposal is <expected>

Examples:

| proposal_type | expected |
|---|---|
| `script` | accepted |
| `wrapper` | accepted |
| `prompt` | accepted |
| `runbook` | accepted |
| `instructions_update` | accepted |
| `new_capability` | rejected for this lane |

## Negative And Governance Cases

- Proposal staging must not store raw assistant transcripts, local credential paths, secrets, customer identifiers, or production evidence.
- Proposal apply must not write outside `.governed/capabilities/<capability-id>/`.
- Proposal validation must not execute proposed scripts.
- Dry-run memory review must not stage proposal folders.
- Existing `govkb validate --strict` behavior must remain compatible.
- Existing Clearing and AIApps memory-review cron jobs must continue to run when no proposals are emitted.

## Traceability

| Requirement | Scenario(s) | Coverage |
|---|---|---|
| Extend memory-review classifier contract to emit structured capability-evolution proposals | UC-1, UC-2, UC-3, UC-10 | Covered |
| Add report sections for proposed scripts, tools, prompts, runbooks, and instruction changes | UC-1, UC-2, UC-4, UC-5 | Covered |
| Persist staged proposals under `.governed/review-proposals/<proposal-id>/` | UC-2, UC-3, UC-5, UC-6 | Covered |
| Keep scheduled cron non-mutating for executable artifacts | UC-5 | Covered |
| Provide manual apply path for approved proposals | UC-6, UC-7, UC-8 | Covered |
| Support higher-reasoning manual review runs without a separate proposal flag | UC-2, UC-3 | Covered through existing `--codex-reasoning` memory-review option |
| Preserve existing append-only memory behavior and safety gates | UC-1, UC-4, UC-9 | Covered |
| New capability creation remains existing candidate flow | UC-9, UC-10 | Covered |

## Test Notes

| Scenario | Suggested Test Module | Notes |
|---|---|---|
| UC-1 | `tests/test_memory_review_capability_evolution_smoke.py` | Assert empty proposal array preserves current report/state behavior. |
| UC-2 | `tests/test_memory_review_capability_evolution_smoke.py` | Use synthetic classifier output and temp governed project. |
| UC-3 | `tests/test_memory_review_capability_evolution_use_cases.py` | Parameterize supported non-script proposal types. |
| UC-4 | `tests/test_memory_review_capability_evolution_use_cases.py` | Cover unsafe paths, missing target, sensitive text, and raw transcript indicators. |
| UC-5 | `tests/test_memory_review_capability_evolution_use_cases.py` | Assert cron/apply review mode stages only proposal metadata. |
| UC-6 | `tests/test_proposals.py` | Direct command-function tests for list/show output and JSON payloads if added. |
| UC-7 | `tests/test_proposals.py` | Temp project apply with approved metadata and bounded output paths. |
| UC-8 | `tests/test_proposals.py` | Mutating script metadata without dry-run/preview is blocked before write. |
| UC-9 | `tests/test_memory_review.py` | Existing semantic candidate tests remain candidate-flow tests. |
| UC-10 | `tests/test_memory_review_capability_evolution_use_cases.py` | Table-driven proposal type validation. |
