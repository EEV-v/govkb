# Governed Learning Improvements - Business Requirements

Last updated: 2026-05-29

## Summary

Improve the GovKB governed-learning loop so project usage turns into useful governed capabilities, reusable runbooks, and safe helper scripts instead of only accumulating memory bullets.

Clearing is the first consumer and integration fixture for this feature. The implementation owner is GovKB, and durable feature artifacts live in the GovKB repository under `docs/governed-skill-knowledge-framework/features/governed-learning-improvements/`.

The latest GovKB fixes made memory review incremental for existing sessions and prevented invalid proposal drafts from blocking state advancement. This feature starts the next improvement set: proposal queue cleanup, health reporting, self-noise filtering, stronger script proposal quality gates, capability maturity scoring, and VS Code freshness checks.

## Problem

Governed learning works, but the operator experience still has gaps:

- Staged proposals can overlap, such as multiple DVCA and split QA runbooks in a consumer project.
- Cron health requires manual inspection of crontab, daemon state, logs, reports, and state files.
- Live Codex sessions can append assistant/tool noise after the processed marker, creating low-value review tails.
- Script proposals have baseline safety checks, but reviewers need clearer quality scoring and verification expectations.
- Skill maturity is not visible; it is hard to tell which capabilities have memory only versus runbooks, scripts, tests, and report integration.
- VS Code can show old UI or stale installed state without a direct doctor command.

## Goals

| ID | Goal | Business Value |
|----|------|----------------|
| G1 | Group and score similar staged proposals before apply. | Maintainers spend less time reviewing duplicates and avoid applying conflicting runbooks. |
| G2 | Provide one memory-review health report for a project. | Operators can tell whether cron and governed learning are working without hand-assembling evidence. |
| G3 | Reduce self-generated memory-review noise. | Review batches focus on user decisions and durable lessons. |
| G4 | Raise quality gates for script and wrapper proposals. | Executable governed additions stay reviewable, dry-run capable, and audit-friendly. |
| G5 | Surface capability maturity. | Maintainers can decide whether a capability needs memory, runbook, script, test, or reporting investment. |
| G6 | Add an explicit VS Code/GovKB freshness check. | Stale extension or materialized-skill state is visible and actionable. |

## In Scope

- GovKB CLI/read-only reporting commands for proposal review, memory-review health, and VS Code freshness checks.
- GovKB memory-review filtering improvements for already processed live-session tails.
- Proposal metadata and report output that score quality without applying proposals automatically.
- GovKB tests using synthetic fixtures and disposable temp directories.
- Clearing governed state as a consumer fixture or manual verification target, not as the implementation owner.
- Optional VS Code UI display of stable CLI JSON fields after the CLI surface exists.

## Out of Scope

- Auto-applying runbook or script proposals without maintainer approval.
- Changing Clearing business behavior, Clearing service code, or Clearing UI product workflows.
- Querying production or staging systems for this feature.
- Storing raw transcripts, credentials, customer data, or live environment secrets in repo artifacts.
- Replacing the existing GovKB proposal flow with a separate workflow engine.

## Acceptance Criteria

| ID | Acceptance Criteria |
|----|---------------------|
| AC1 | A maintainer can run one GovKB command and see duplicate/similar proposal groups, quality warnings, and recommended next actions. |
| AC2 | A maintainer can run one GovKB command and see memory-review health: cron presence, latest run/report, state advancement, selected sessions, failures/deferred rows, proposal count, installed revision, and repo revision. |
| AC3 | Memory review avoids classifying obvious self-generated review/report/tool-output tails unless there is a user decision or durable content after the processed marker. |
| AC4 | Script/wrapper proposals expose dry-run or preview behavior, help/compile verification, mutation class, and audit/log expectations before approval. |
| AC5 | Each governed capability can be scored into maturity levels: memory-only, memory plus runbook, runbook plus verification, reusable scripts, tested scripts plus reporting integration. |
| AC6 | A VS Code/GovKB doctor command reports extension package version, configured CLI path, CLI revision, installed materialization revision, repo revision, and stale state. |
| AC7 | Existing commands remain backward compatible: `govkb proposals list/show/apply`, `govkb status`, and `govkb review-memory` continue to work. |

## Stakeholders

| Role | Need |
|------|------|
| GovKB maintainer | Keep learning automation useful, safe, explainable, and testable. |
| Project maintainer | Review useful governed updates without duplicate proposal churn. |
| Feature engineer | Start project work with fresher, more actionable governed capabilities. |
| VS Code user | Know whether the visible GovKB UI reflects current installed state. |
| Clearing consumer | Benefit from better proposal review and health checks without owning the GovKB feature code. |

## Constraints

- Proposal application remains manual and approval-gated.
- Reports must not persist raw session transcript content.
- Mutating script proposals must include dry-run or preview behavior.
- The implementation belongs in `/home/ev/code/govkb`.
- Clearing is a consumer/integration target only.

## Open Questions

| # | Question | Blocking? | Owner |
|---|----------|-----------|-------|
| Q1 | Should proposal dedupe be `govkb proposals report`, `govkb proposals list --report-json`, or a separate `govkb doctor proposals` action? | Yes for Phase 0 CLI shape | GovKB maintainer |
| Q2 | Should memory-review health live under `govkb review-memory --health-json`, `govkb status --json`, or a new `govkb doctor` command? | Yes for Phase 1 CLI shape | GovKB maintainer |
| Q3 | How much VS Code freshness checking should be CLI-only versus shown in the extension Home surface? | No | GovKB maintainer |
| Q4 | Should maturity scoring be advisory only or should low maturity block release/apply flows? | No | GovKB maintainer |

