# Governed Skill Contract And Migration - Business Requirements Critical Review

Last updated: 2026-05-01

## Verdict

Business Requirements Ready: No

The draft captures the right problem, but it is not ready for engineering handoff or business review. It mixes business outcomes with implementation design, leaves important policy decisions unresolved, and does not define the migration/review experience tightly enough to prevent another weak governed capability from being created.

## Findings

| Priority | Area | Finding | Evidence | Recommendation |
|---|---|---|---|---|
| P0 | Scope control | The feature combines three large product changes in one scope: strict governed-skill standards, local skill conversion, and Clearing remediation. Without a first-slice boundary, implementation can become a broad platform rewrite. | `business.md` lines 5, 103-131 | Split into explicit MVP scope: strict validation + preview conversion + candidate auto-create gate. Defer actual Clearing cleanup and bulk migration to follow-up work. |
| P0 | Governance | Candidate auto-create is required to stop weak activation, but the draft does not define who can approve activation, what review state is required, or whether auto-create should be disabled by default. | `business.md` lines 107, 127-131 | Add a review-state model: collecting, ready-for-review, strict-valid, approved-for-activation, activated, rejected. Require explicit approval for activation until strict validation has real project history. |
| P1 | Business vs implementation | Many requirements specify implementation paths and CLI flags before the business behavior is settled. That makes the spec look precise while leaving user outcomes underdefined. | `business.md` lines 47-60, 95-101, 113-125 | Keep package locations and CLI names as proposed defaults, but add business outcomes for maintainers: preview, review, approve, apply, rollback, and audit. |
| P1 | Strict validation policy | The draft says strict validation must exist, but it does not define severity, default behavior, compatibility mode, or rollout rules for existing `.governed` projects. | `business.md` lines 103-109, 143-145 | Define validation severities and defaults: errors block conversion writes and candidate activation; warnings report cleanup; default `govkb validate` remains backward-compatible until strict mode is promoted. |
| P1 | Conversion safety | Conversion is required to reject or stage unsafe content, but "stage" is undefined and could accidentally preserve sensitive content in repo artifacts. | `business.md` lines 121-125, 149 | Define unsafe-content handling: never copy secrets/raw transcripts to repo; report rejected item metadata only; optionally write sanitized review notes without the unsafe text. |
| P1 | Existing skill parity | "Equivalent to the governed source" is ambiguous because local Codex skills can include adapter presentation, scripts, prompts, memory, and personal workflow assumptions. | `business.md` line 125 | Define parity levels: exact content copy, governed semantic parity, adapter-local fallback, and rejected content. Require conversion plan to list approved differences. |
| P1 | Tooling contract | Tooling conventions mention scripts and fixtures, but do not define trusted execution, mutating behavior, dependency boundaries, or whether materialized assistant-local tools are executable. | `business.md` lines 93-101 | Add tool classes: docs-only helper, read-only script, mutating script, fixture. Require mutating scripts to be non-default and previewable. |
| P1 | Data classification | The draft rejects secrets and raw transcripts but does not classify project identifiers, account data, incident evidence, proprietary docs, or local credential-file paths consistently. | `business.md` lines 61-62, 90-91, 98 | Add a data classification section with allowed, restricted, and forbidden content. Treat credential paths and exact incident evidence as forbidden in durable memory. |
| P1 | Reviewer workflow | The draft names reviewers but does not define what reviewers inspect or approve. | `business.md` lines 36-41, 120-125 | Add reviewer tasks: inspect conversion plan, validate strict issues, approve capability id/name/scope, approve copied tools, approve migration metadata, approve activation. |
| P2 | Naming rules | The draft says ids must be domain-specific but leaves generic ids conditionally allowed without a decision rule. | `business.md` lines 66-67 | Replace "allowed only when" with objective checks: generic id requires explicit scope statement, at least two non-domain-specific use cases, and reviewer approval. |
| P2 | Memory contract | Memory bullets are described as durable and reusable, but the draft does not distinguish policy, workflow, command, repo map, and authority-rule content. | `business.md` lines 77-91 | Add a short memory taxonomy so validators can detect misplaced command/path/policy content more predictably. |
| P2 | Acceptance criteria | Acceptance criteria are mostly implementation test outcomes and do not state business acceptance for maintainer confidence. | `business.md` lines 141-152 | Add business acceptance: maintainer can identify why a package failed, can safely preview conversion, can approve/reject activation, and can rollback conversion output. |
| P2 | Backward compatibility | The draft does not state what happens to existing projects and local skills when strict validation is introduced. | `business.md` lines 103-109, 133-139 | Add compatibility requirements: no existing materialized skill is deleted; strict failures do not block normal apply unless requested; conversion never mutates source skills. |
| P2 | Clearing example | Clearing is useful as evidence, but the draft risks making a product feature depend on one local workspace state. | `business.md` lines 7, 127-131, 144 | Keep Clearing as acceptance fixture/example, but phrase product behavior generically and make actual Clearing cleanup a separate operational task. |

## Missing Business Requirements

| Gap | Why It Matters | Suggested Requirement |
|---|---|---|
| Review state lifecycle | Prevents automatic activation of weak packages | GovKB must expose a governed skill lifecycle from draft/conversion through review, approval, activation, and rollback. |
| Conversion preview UX | Current draft says "conversion plan" but not what users need to decide | Preview must show target id, scope, files to create, files copied, files rejected, validation issues, and next safe action. |
| Rollback behavior | Conversion writes repo files and materialization writes local outputs | Every conversion write must have a clear rollback path: delete new capability folder or revert changed files; local materialization remains derived. |
| Compatibility mode | Existing governed projects may fail strict validation initially | Strict validation must be opt-in for normal validation at first, but mandatory for conversion write and candidate activation. |
| Approval boundary | Prevents tools/scripts from becoming hidden executable risk | Copying scripts into `tools/scripts/` requires reviewer-visible safety metadata and must not imply automatic execution. |
| Auditability | Maintainers need to know why a conversion or activation happened | Conversion and activation should leave an auditable summary without raw unsafe content. |
| Migration classification | Existing skills are not all governed skill candidates | Converter must classify content as governed, adapter-local, unsafe/rejected, or manual-review-needed. |

## Required Open Questions

| ID | Question | Blocking? | Recommended Owner |
|---|---|---|---|
| Q1 | Should strict validation be opt-in for `govkb validate` initially, while mandatory for conversion write and candidate activation? | Yes | Engineering/Product |
| Q2 | What lifecycle states must a governed skill have before activation? | Yes | Product |
| Q3 | Does `govkb convert skill --write` create only new capability packages in the MVP, or can it update existing packages? | Yes | Engineering |
| Q4 | Should unsafe converted content be reported only, or should sanitized review notes be written into the feature package? | Yes | Security/Governance |
| Q5 | What is the minimum reviewer approval required before scripts under `tools/scripts/` are considered governed? | Yes | Security/Governance |
| Q6 | Is Clearing remediation part of the product MVP, or a follow-up validation fixture and operational cleanup task? | Yes | Product |
| Q7 | What exact parity level is required between a converted local skill and the governed materialized skill? | Yes | Product/Engineering |
| Q8 | Should bulk conversion remain explicitly out of scope for the first release? | No | Product |

## Required Decisions

| ID | Decision | Status | Recommendation |
|---|---|---|---|
| D1 | Strict validation rollout policy | Open | Start opt-in for general validation; mandatory for conversion write and candidate activation. |
| D2 | Governed skill lifecycle states | Open | Add draft, strict-valid, approved, active, rejected, deprecated. |
| D3 | Conversion write overwrite policy | Open | MVP should create new packages only; updates require later explicit mode. |
| D4 | Unsafe content handling | Open | Never persist unsafe content; persist only redacted metadata and reason. |
| D5 | Tools execution policy | Open | GovKB may package tools but must not execute them during conversion or validation. |
| D6 | Clearing remediation scope | Open | Use Clearing as validation evidence; perform cleanup as separate task after validator exists. |

## Suggested Business.md Revisions

1. Add a `## MVP Scope` section that explicitly limits first release to strict validation, conversion preview/write for one skill, candidate activation gate, and documentation.
2. Add a `## Governance Lifecycle` section for governed skill states and approval points.
3. Add a `## Data Classification` section that separates allowed durable knowledge, restricted metadata, and forbidden content.
4. Add a `## Conversion Review Experience` section describing the conversion plan in business terms.
5. Add a `## Backward Compatibility And Rollout` section for existing packages and local skills.
6. Move low-level path conventions into a `Proposed Package Convention` subsection or reference artifact, while keeping user outcomes in the main requirements.
7. Rework Clearing remediation as evidence and follow-up acceptance, not part of the core product scope.
8. Replace broad acceptance criteria with scenario-like criteria that prove maintainer confidence and safety.

## Readiness Recommendation

Do not proceed to implementation yet. First revise `business.md`, then generate `open-questions.md` and `decision-log.md` from this review. After blocking questions are resolved or explicitly deferred, rerun the spec workflow and only then refresh implementation planning.
