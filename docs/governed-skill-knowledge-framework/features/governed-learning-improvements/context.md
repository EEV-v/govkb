# Governed Learning Improvements - Implementation Context

Last updated: 2026-05-29

## Objective

Build GovKB-owned improvements to proposal review, memory-review health, self-noise filtering, script proposal quality, capability maturity visibility, and VS Code freshness checks. Clearing remains a consumer and verification fixture.

## Source Artifacts

| Source | Evidence |
|--------|----------|
| `README.md` | GovKB current scope includes `review-memory`, governed learning classification, proposal review flow, and optional VS Code proof. |
| `docs/README.md` | Product docs and feature folders live under `docs/governed-skill-knowledge-framework/`. |
| `docs/COOKBOOK/COOKBOOK.MD` | Feature artifacts belong under `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/`. |
| `src/govkb/cli.py` | Existing argparse subcommands include `status`, `review-memory`, `proposals`, `promote`, and `promotions`. |
| `src/govkb/core/proposals.py` | Proposal storage, metadata validation, safety checks, and apply flow already exist. |
| `src/govkb/commands/proposals.py` | Current public proposal commands are `list`, `show`, and `apply`. |
| `src/govkb/commands/status.py` | Existing status JSON includes validation, install state, repo revision, and local memory update state. |
| `src/govkb/adapters/codex/bin/codex-memory-review` | Memory-review selection, `reviewAfter`, report/state writing, proposal staging, and auto-promotion live here. |
| `vscode-extension/` | The extension delegates mutations to GovKB CLI and displays derived state. |
| `tests/test_proposals.py`, `tests/test_memory_review.py`, `tests/test_status_json.py` | Closest current test patterns. |

No repo-local instruction file was found in `/home/ev/code/govkb`; active session and cookbook instructions apply.

## Existing Patterns

| Pattern Type | Existing Example | Location | Reuse? |
|---|---|---|---|
| CLI command routing | Argparse subcommands with command handler functions | `src/govkb/cli.py` | Extend |
| Proposal storage | `.governed/review-proposals/<id>/proposal.toml` | `src/govkb/core/proposals.py` | Extend |
| Proposal commands | `govkb proposals list/show/apply` | `src/govkb/commands/proposals.py` | Extend |
| Status JSON | Machine-readable validation, install, repo, memory state | `src/govkb/commands/status.py` | Extend or consume |
| Memory review state | `reviewAfter`, processed session map, report writing | `src/govkb/adapters/codex/bin/codex-memory-review` | Extend |
| Tests | `unittest.TestCase`, temp dirs, direct command calls | `tests/` | Reuse |
| VS Code state | CLI-backed derived Home/status surfaces | `vscode-extension/src/` | Extend after CLI JSON exists |

## Proposed New Components

| Component | Purpose | Notes |
|---|---|---|
| Proposal review report | Group related staged proposals and emit quality warnings. | Prefer extending `govkb proposals` first. |
| Memory-review health report | Summarize cron, latest reports/state, backlog, proposal count, and install/repo revision. | CLI shape still open. |
| Self-noise detector | Skip review tails with only assistant/tool/report noise after `reviewAfter`. | Must preserve user-authored rows. |
| Capability maturity report | Derive L1-L5 maturity from governed artifacts and pending proposals. | Advisory first. |
| VS Code/GovKB doctor payload | Identify stale extension, CLI, repo, or installed materialization layer. | CLI-first, UI second. |

## Data Flow

`Codex sessions -> govkb review-memory -> local review reports/state -> local memory and staged proposals -> governed promotion/proposal review -> project .governed package -> govkb install/apply -> VS Code/Home status`

The new feature adds read-only inspection and advisory scoring around that flow. It does not replace existing apply or promotion gates.

## Domain Entities

### Proposal

Source of truth: `.governed/review-proposals/<proposal-id>/proposal.toml`

| Field | Type | Constraints | Example |
|---|---|---|---|
| id | string | normalized identifier | `qa-dvca-aggregate-payout-e2e-runbook` |
| status | enum | staged, approved, applied | `staged` |
| target_capability | string | existing capability id | `clearing-qa-on-staging` |
| proposal_type | enum | script, wrapper, prompt, runbook, instructions_update | `runbook` |
| safety_class | enum | read_only, mutating_with_dry_run, docs_only, prompt_only, instructions_only | `docs_only` |
| output_paths | list | must stay under target capability root | `.governed/capabilities/.../runbooks/...md` |
| verification_command | string | required | `n/a docs-only` |
| confidence | number | 0 to 1 | `0.86` |

### Memory Review Run

Source of truth: `$CODEX_HOME/memories/govkb/projects/<project>/codex-memory-review/reports/*-report.md` and `state.json`.

| Field | Type | Constraints | Example |
|---|---|---|---|
| run_id | string | UTC timestamp key | `2026-05-29T100647Z` |
| selected sessions | list | project-scoped and state-filtered | 5 |
| review_after | timestamp | optional stale per-session marker | `2026-05-28T12:16:58.254Z` |
| applied/staged/rejected | counts | report summary | applied 13, staged 4, rejected 8 |
| stagedProposals | count | successful staged proposal rows | 5 |
| status | enum | completed, failed | `completed` |

### Capability Maturity

Derived from `.governed/capabilities/<id>/` files and staged proposal metadata.

| Level | Meaning | Evidence |
|---|---|---|
| L1 | Memory only | `references/long-term-memory.md` |
| L2 | Runbook present | `runbooks/*.md` or approved runbook proposal |
| L3 | Verification included | runbook has explicit command/checklist |
| L4 | Reusable script/helper | `scripts/*` or script proposal |
| L5 | Tested script plus reporting integration | tests and health/report surface |

## Command Map

| Task | Command | Working Dir | Preconditions |
|---|---|---|---|
| Run full tests | `python3 -m unittest discover -s tests -v` | `/home/ev/code/govkb` | Python available |
| CLI help | `PYTHONPATH=src python3 -m govkb.cli --help` | `/home/ev/code/govkb` | Source checkout |
| Proposal list fixture | `PYTHONPATH=src python3 -m govkb.cli proposals list /home/ev/code/Clearing --json` | `/home/ev/code/govkb` | Clearing consumer checkout exists |
| Status fixture | `PYTHONPATH=src python3 -m govkb.cli status /home/ev/code/Clearing --codex-home /home/ev/.codex --json` | `/home/ev/code/govkb` | Local Codex home exists |
| Inventory fixture | `CODEX_HOME=/home/ev/.codex PYTHONPATH=src python3 -m govkb.cli review-memory --assistant codex --project-root /home/ev/code/Clearing --inventory-json --lookback-days 1 --max-sessions 5` | `/home/ev/code/govkb` | Local Codex state exists |

Tests should prefer synthetic temp projects over `/home/ev/code/Clearing`.

## APIs And CLI Surface

Current public surfaces:
- `govkb proposals list/show/apply`
- `govkb status --json`
- `govkb review-memory --inventory-json`
- VS Code extension status/report views backed by CLI output

Candidate surfaces:
- `govkb proposals report <project-root> --json`
- `govkb doctor <project-root> --codex-home <path> --json`
- optional additive status JSON fields for maturity and freshness

## Storage

| Store | Authority | Notes |
|---|---|---|
| Project `.governed/**` | Source of truth | Proposal report reads staged proposals; apply remains approval-gated. |
| `$CODEX_HOME/memories/govkb/**` | Derived local output | Health report may summarize but must not treat as repo source of truth. |
| VS Code extension state | Derived UI state | Must not become an authoritative writer. |
| Feature docs | Planning artifacts | This folder is GovKB-owned. |

## Security And Governance

- Do not copy raw session transcripts into repo artifacts.
- Use synthetic JSONL/session fixtures in tests.
- Use disposable `CODEX_HOME` directories in tests.
- Proposal report commands are read-only.
- Existing proposal safety validation remains in `src/govkb/core/proposals.py`.
- Mutating script proposals still require dry-run or preview behavior.

## Tests

| Area | Existing Pattern |
|---|---|
| Proposal command/core behavior | `tests/test_proposals.py` |
| Memory review selection/reporting | `tests/test_memory_review.py` |
| Capability evolution | `tests/test_memory_review_capability_evolution_use_cases.py` |
| Status JSON | `tests/test_status_json.py` |
| VS Code extension behavior | `vscode-extension/src/test/suite/` and Python use-case docs tests |

## Observability

Reports should expose machine-readable counts:
- proposal count, group count, warning count
- health status, latest run id, latest run status
- maturity level distribution
- stale layer count

## Open Questions

| # | Question | Blocking? | Owner |
|---|---|---|
| Q1 | Final Phase 0 CLI shape for proposal report. | Yes | GovKB maintainer |
| Q2 | Final health/doctor command split. | Yes for later phases | GovKB maintainer |
| Q3 | Whether maturity appears in `status --json` or a separate report. | No | GovKB maintainer |

## Assumptions

| # | Assumption | Risk If Wrong |
|---|---|---|
| A1 | Phase 0 should start with proposal grouping/reporting. | Health or VS Code needs may remain open until later phases. |
| A2 | Clearing can be used for manual verification but not as a test dependency. | Tests would be brittle if they depend on local Clearing state. |
| A3 | Proposal report should be advisory only. | Maintainers may still need manual decisions for merge/reject/apply. |

## Traceability

| Context Section | business.md Source |
|---|---|
| Proposal grouping | G1, AC1 |
| Health reporting | G2, AC2 |
| Self-noise filtering | G3, AC3 |
| Script quality gates | G4, AC4 |
| Maturity scoring | G5, AC5 |
| VS Code freshness | G6, AC6 |

