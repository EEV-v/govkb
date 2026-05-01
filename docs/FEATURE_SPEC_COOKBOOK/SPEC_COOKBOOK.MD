# GovKB Feature Spec Cookbook

Business-spec convergence workflow for GovKB features before engineering planning starts.

## Goal

Keep one canonical `business.md`, preserve reviewed snapshots and per-round diffs, ground every feature in `business-context.md` and `context.md`, keep open questions and decisions status-driven, produce review materials only when feedback is reconciled, and hand engineering an explicit `spec-handoff.md` only after scope, blockers, decisions, and deferred items are visible.

This cookbook is the pre-implementation companion to `docs/COOKBOOK/COOKBOOK.MD`.

## Canonical Paths

| Item | Path |
|---|---|
| Spec cookbook prompts | `docs/FEATURE_SPEC_COOKBOOK/` |
| Spec cookbook references | `docs/FEATURE_SPEC_COOKBOOK/references/` |
| Engineering cookbook prompts | `docs/COOKBOOK/` |
| Feature folder | `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/` |
| Shared spec knowledge base | `docs/FEATURE_SPEC_COOKBOOK/spec-knowledge-base.md` |

## Phase Timeline

| Phase | Purpose | Primary outputs | Gate |
|---|---|---|---|
| 0.0 | Business Context | `business-context.md` | Business purpose, domain terms, sources, assumptions, and open context gaps are explicit |
| 0.1 | Implementation Context | `context.md` | Existing code/docs/contracts/commands are grounded in GovKB repo evidence |
| 0.2 | Intake | `spec-brief.md` | Canonical `business.md` exists and source artifacts are listed |
| 0.3 | Feedback Normalization | reviewed snapshot or normalized feedback source | Mixed feedback is consolidated into one governable round source before diffing |
| 0.5 | Tracker/Reference Sync | optional `## Tracking` or explicit "not applicable" status | External tracker/linkage assumptions are visible before external review |
| 1 | Questions And Decisions | `open-questions.md`, `decision-log.md` | Unknowns are classified as blocking, deferred, resolved, or assumption |
| 2 | Business Review Pack | `business-review-pack.md`, `business-review-message.md` | Pack is coherent, feedback is reconciled, and tracker/reference status is truthful |
| 2.5 | Final Review Check | reviewer findings | No blocking mismatch exists between canonical/base artifacts and outbound pack/message |
| 3 | Review Reconciliation | `review-rounds/<label>-reviewed.docx.md`, `review-rounds/<label>-changes.md`, `review-rounds/<label>-reconciliation.md`, `review-rounds/reconciliation-state.json` | Incoming feedback is diffed, classified, and explicitly reconciled before canonical update |
| 4 | Knowledge Update | `spec-knowledge-base.md` | Only reusable cross-feature lessons are promoted |
| 5 | Scope Lock | `scope-lock.md` | Blocking questions and open decisions are visible or resolved/deferred |
| 6 | Engineering Handoff | `spec-handoff.md` | Engineering can start with approved scope and explicit deferred items |

## Canonical Artifact Rules

- `business.md` is the canonical working draft.
- `business-context.md` is required before question, decision, or review-pack work.
- `context.md` is required before question, decision, or review-pack work.
- Reviewed `.docx.md` snapshots and normalized feedback sources are immutable inputs.
- `review-rounds/*-changes.md` is a write-once round diff for each round.
- `review-rounds/*-reconciliation.md` records classification and merge intent for each round.
- `review-rounds/reconciliation-state.json` tracks which rounds are `new`, `diffed`, `classified`, or `reconciled`.
- `open-questions.md` and `decision-log.md` are cumulative and status-driven.
- `spec-knowledge-base.md` stores reusable cross-feature lessons only.
- `hours-tracking.md` is optional and local to a feature. Create it only when spec-work hours are previewed, logged, or explicitly left pending.
- External tracker links are optional in GovKB. If no tracker is configured, record `Tracker: Not configured / not applicable` instead of blocking local engineering.

## Standard Feature Folder Additions

```text
docs/governed-skill-knowledge-framework/features/<FeatureSlug>/
├── business.md
├── business-context.md
├── context.md
├── spec-brief.md
├── open-questions.md
├── decision-log.md
├── hours-tracking.md
├── business-review-pack.md
├── business-review-message.md
├── scope-lock.md
├── spec-handoff.md
└── review-rounds/
    ├── <label>-reviewed.docx.md
    ├── <label>-changes.md
    ├── <label>-reconciliation.md
    └── reconciliation-state.json
```

## Execution Order

1. Confirm canonical `business.md` exists.
2. Produce or refresh `business-context.md` from local project docs first.
3. Produce or refresh `context.md` from `business-context.md`, `business.md`, current code, tests, and project docs.
4. Produce or refresh `spec-brief.md`.
5. Record tracker/reference status. Do not create external trackers without explicit user confirmation.
6. Produce or refresh `open-questions.md` and `decision-log.md`.
7. Treat the latest unreconciled feedback candidate as a blocker until its paired reconciliation file is classified.
8. Never overwrite `business.md` blindly. Either:
   - mark `Promote source document as canonical: Yes`, or
   - merge changes manually into `business.md` and mark `Canonical business.md updated manually: Yes`.
9. Mark `Round processed: Yes` only after the canonical draft is updated or explicit no-change reconciliation is recorded.
10. Update the shared spec KB only when the round produced a reusable lesson.
11. Generate `business-review-pack.md` and `business-review-message.md` only when feedback is reconciled and tracker/reference status is truthful.
12. Run a fresh final review before sending a pack externally.
13. Generate `scope-lock.md` and `spec-handoff.md` only at explicit checkpoint moments.
14. Switch to `docs/COOKBOOK/COOKBOOK.MD` only after `spec-handoff.md` exists.

## Status Models

Question statuses:

- `Blocking`: must be answered before scope lock.
- `Deferred`: explicitly moved out of the current slice.
- `Resolved`: answered and retained for traceability.
- `Assumption`: accepted unless contradicted by later review.

Decision statuses:

- `Open`: needs explicit outcome before scope lock.
- `Approved`: accepted into current scope.
- `Deferred`: parked for later scope.
- `Rejected`: intentionally not part of current scope.

## Reconciliation State Contract

`review-rounds/reconciliation-state.json` stores one entry per round key under `rounds`.

Each entry should include:

- `sourcePath`
- `sourceName`
- `snapshotPath`
- `changeLogPath`
- `reconciliationPath`
- `status`
- `updatedAt`
- optional `canonicalUpdated`

Allowed `status` values:

- `new`
- `diffed`
- `classified`
- `reconciled`

Markdown reconciliation flags remain the operator-facing control surface; JSON is the machine-readable mirror.

## Refresh Cadence

Always refresh when the source draft or feedback changes:

- `business-context.md`
- `context.md`
- `spec-brief.md`
- `open-questions.md`
- `decision-log.md`

Refresh only when ready to send a new business loop:

- `business-review-pack.md`
- `business-review-message.md`

Run immediately before external send:

- fresh final review using `FINAL_REVIEW_PROMPT.MD`

Refresh when time tracking changes:

- `hours-tracking.md`

Refresh only at explicit checkpoint moments:

- `scope-lock.md`
- `spec-handoff.md`

Update shared knowledge only when reusable lessons exist:

- `spec-knowledge-base.md`

## Feedback Normalization Rule

- If feedback arrives as email notes, meeting bullets, Slack messages, comments, or a non-reviewed file, normalize it into one source artifact before diffing.
- Generic feedback files may support reconciliation, but they are not eligible for wholesale canonical promotion.
- Reviewed return files stay immutable and preserve the wording and formatting received.

## GovKB-Specific Tracker Rule

GovKB does not have a built-in external-tracker requirement. For local repository implementation, tracker sync is not a blocker unless a feature explicitly names an external tracker. If a tracker exists, record links in `business.md`, `spec-brief.md`, `business-review-pack.md`, `scope-lock.md`, and `spec-handoff.md`; otherwise record that tracker linkage is not configured.

## Dry-run Targets

Use these local targets to validate the spec flow:

- `vscode-extension-public-distribution`
- any disposable feature folder under `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/`

Confirm:

- reviewed snapshots remain immutable
- round diff and reconciliation artifacts are useful
- open questions and decisions preserve statuses
- scope lock and handoff do not appear until explicit checkpoint
- shared KB absorbs generic lessons without copying raw feature content
