# GovKB - Customer Presentation

Status: Strategic alignment draft
Date: 2026-05-09

## 1. Executive Thesis

GovKB turns AI collaboration knowledge from personal prompts and local assistant files into governed project infrastructure.

The core product is a repo-native knowledge loop: teams define reusable AI capabilities in git, validate and review them like code, materialize them into assistant-specific setups, and improve them from real completed work with audit and promotion controls.

Codex is the first working adapter. The strategic target is broader: the same governed project package should be usable by Codex, Claude, Copilot, and future assistants without redefining project knowledge for each tool.

## 2. Customer Problem

AI pilots often work for individuals but do not reliably scale across teams.

- Engineers repeat the same project context, commands, conventions, and review rules in every new AI session.
- Useful lessons from solved work stay in chat history, local prompt files, or one person's machine.
- Assistant setup drifts because there is no repo-owned source of truth.
- Teams cannot easily review, approve, audit, release, or roll back project-specific AI knowledge.
- Prompt libraries and local skills become assistant-specific, making future assistant changes expensive.
- Auto-learning is risky when it lacks confidence gates, sensitive-data checks, staging, and maintainer approval.

## 3. Strategic Target

GovKB should be positioned as a governed knowledge layer for AI-assisted software and operations work.

It is not just a prompt library. It is not just local assistant configuration. It is a project-owned operating model for how AI tools learn the team's reusable workflows.

The target state:

- Each project owns a `.governed/` package in git.
- Governed capabilities declare their routing, memory targets, verification expectations, and approval rules in machine-readable contracts.
- Assistant adapters project the same governed package into local assistant setups.
- Real completed AI sessions are reviewed for reusable lessons.
- High-confidence safe lessons can update existing governed capability memory when policy allows it.
- Repeated unmatched work can stage a new capability candidate for explicit review.
- Maintainers promote accepted knowledge, and teammates receive it through `govkb apply`.

## 4. How Customers Use It

### Setup

1. A maintainer runs `govkb init` in a project repo.
2. The repo gains a `.governed/` package with project metadata, adapter configuration, and governed capability folders.
3. Existing local assistant skills or workflows can be classified into governed, adapter-local, or legacy tracks.
4. `govkb validate --strict` checks package shape, contracts, unsafe content, path safety, lifecycle state, and memory quality gates.

### Daily Work

1. A teammate runs `govkb apply codex` to materialize the repo-governed package into local Codex skills.
2. Engineers use Codex normally while working on features, bugfixes, reviews, QA, support workflows, docs, or operations.
3. The memory-review adapter inspects completed sessions and maps reusable learning to the correct governed capability or project knowledge area.
4. Unsafe, ambiguous, low-confidence, duplicate, or local-only lessons are rejected or staged instead of silently applied.

### Governance Loop

1. Reports show what was learned, staged, rejected, applied, and why.
2. Maintainers review staged changes and new capability candidates.
3. Accepted changes are committed and promoted like normal project source.
4. Other teammates run `govkb apply codex` and receive the improved assistant behavior.

## 5. What GovKB Delivers

| Customer need | GovKB response |
|---|---|
| Make AI project knowledge durable | Store reusable knowledge in repo-owned `.governed/` files. |
| Avoid assistant lock-in | Keep project knowledge assistant-agnostic and materialize through adapters. |
| Reduce repeated context explanation | Capture stable commands, repo maps, workflow rules, and lessons once, then redistribute. |
| Keep learning safe | Use strict validation, approval gates, confidence thresholds, and sensitive-content rejection. |
| Make changes reviewable | Treat governed AI knowledge as versioned source with diffs, commits, reports, and rollback. |
| Let capabilities grow without central rewrites | Discover governed capabilities from contracts instead of hardcoded routing tables. |
| Support team adoption | Apply a known repo revision into local assistant setup and record install state. |

## 6. Benefits By Stakeholder

| Stakeholder | Benefit |
|---|---|
| CTO / VP Engineering | AI adoption becomes a governed team capability instead of isolated individual prompt craft. |
| Engineering manager | Reusable project practices survive turnover, context switches, and tool changes. |
| Project maintainer | AI knowledge changes can be reviewed, validated, promoted, and rolled back in git. |
| Staff engineer / reviewer | Capabilities can encode stable review, bugfix, QA, and release workflows with explicit gates. |
| Developer / operator | Local assistant setup becomes easier to sync and less dependent on manually remembered context. |
| Security / compliance reviewer | Sensitive or local-only data can be rejected before becoming durable memory. |

## 7. Operating Model

```text
Project repo
  -> .governed package
  -> capability contracts and governed memory
  -> govkb validate
  -> govkb apply codex
  -> local Codex skills
  -> normal AI-assisted work
  -> memory review reports
  -> staged or applied governed updates
  -> maintainer promotion
  -> teammates apply the promoted revision
```

The important distinction is source ownership:

- `.governed/` is the project source of truth.
- Codex skills are derived outputs.
- Future Claude or Copilot adapters should consume the same governed project source.

## 8. Example Customer Story

A Clearing team has several repeatable AI-assisted workflows: feature planning, bugfix documentation, Level 3 support comment writing, and Monday-to-Azure matching.

Before GovKB, these workflows live as local assistant skills and personal process knowledge. They help one operator, but they are difficult to audit, share, or safely improve.

With GovKB:

- The team initializes a local `.governed/` package for the Clearing workspace.
- Feature, bugfix, and Level 3 workflows become strict-validated governed capabilities.
- `govkb apply codex` materializes them into local Codex skills.
- Remediation reports prove the governed package is clean.
- New workflows can be converted or redesigned without copying credential paths, scripts, or unsafe local assumptions into durable project memory.

The result is a concrete customer-facing proof: real project workflows move from local assistant behavior into repo-governed, auditable, reusable AI operating knowledge.

## 9. Guardrails

GovKB should be sold with conservative governance as a feature, not a limitation.

- New capabilities are staged for review before activation.
- Invalid or unsafe capabilities fail strict validation.
- Assistant adapters cannot weaken project governance.
- Automation promotes accepted learning into an isolated git worktree branch, not the active developer checkout.
- Raw transcripts, secrets, credential paths, and production-only data do not belong in governed memory.
- Missing a lesson is preferable to writing noisy or unsafe long-term memory.

## 10. Current Proof Points

The GovKB repo already contains the first working pieces of the target model:

- `govkb init` scaffolds a project `.governed/` package.
- `govkb validate --strict` enforces governed package and capability quality gates.
- `govkb apply codex` materializes governed content into local Codex skills and records applied revision state.
- `govkb promote --auto` creates reviewable isolated git worktree branches for safe memory promotion.
- `govkb promotions list/show/mark-reviewed/archive` makes isolated automated promotion reviews discoverable and records GovKB lifecycle decisions without taking over Git history.
- Local skill conversion supports strict-governed migration from Codex skills into repo-owned packages.
- Remediation reporting checks governed packages and writes auditable reports only when the target `.governed` root is owned by the selected git repo.
- A real Clearing governance repo has governed feature, bugfix, and Level 3 capabilities materialized into Codex from `.governed`.

## 11. What Is Not The Promise Yet

GovKB should not be presented as fully complete enterprise AI governance.

Current positioning should be:

- First adapter: Codex.
- Future adapter direction: Claude and Copilot.
- Current strength: repo-governed project knowledge, strict validation, controlled materialization, migration, and auditable improvement loop.
- Deferred: full UI for staged-memory review, full non-Codex adapter implementations, automatic activation of brand-new capabilities, and exact cost-reduction measurement.

## 12. Customer Demo Flow

1. Show a project with no governed package.
2. Run `govkb init`.
3. Show `.governed/project.toml` and one capability contract.
4. Run `govkb validate --strict`.
5. Run `govkb apply codex`.
6. Show the generated local Codex skill.
7. Run a remediation or memory-review dry run.
8. Show the report: clean, staged, rejected, or recommended actions.
9. Run `govkb promote --auto` and `govkb promotions list/show/mark-reviewed` to demonstrate isolated review branches and lifecycle state.
10. Commit the governed package and explain that teammates can apply the same revision.

See `docs/governed-skill-knowledge-framework/examples/` for deeper team-learning, rejection, Clearing, candidate, and isolated-review stories.

## 13. Positioning Statement

GovKB gives engineering teams a governed knowledge layer for AI collaboration.

It lets a project own its reusable AI workflows in git, validate them, audit how they change, materialize them into local assistant tools, and safely improve them from real work. The result is less repeated context, less local assistant drift, more reviewable AI behavior, and a path to portable project knowledge across assistants.

## 14. Customer-Ready Message

If your team is using AI assistants seriously, the problem is no longer only prompting. The problem is governance, reuse, and portability of the project knowledge those assistants need.

GovKB makes that knowledge a repo-owned asset. The assistant becomes a materialization target; the project remains the authority.
