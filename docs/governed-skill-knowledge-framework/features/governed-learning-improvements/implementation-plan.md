# Governed Learning Improvements - Implementation Plan

Last updated: 2026-05-29

## 0. Existing Code Inventory

| Category | Component | Location | Reuse Strategy |
|---|---|---|---|
| CLI routing | Argparse subcommands | `src/govkb/cli.py` | Extend existing `proposals`; add later `doctor` only after shape decision. |
| Proposal model | Metadata loading, staging, apply validation, safe path checks | `src/govkb/core/proposals.py` | Reuse loaders and safety constants; add report helpers in a focused module if needed. |
| Proposal command | `list`, `show`, `apply` | `src/govkb/commands/proposals.py` | Add Phase 0 report action or option without changing current actions. |
| Status command | Validation, install-state, repo revision, pending local memory | `src/govkb/commands/status.py` | Reuse for health/doctor payload. |
| Memory review | Session discovery, `reviewAfter`, report/state writing, proposal staging | `src/govkb/adapters/codex/bin/codex-memory-review` | Extend only in Phase 2. |
| VS Code extension | CLI-backed Home/status/report views | `vscode-extension/src/` | Consume doctor JSON after CLI exists. |
| Proposal tests | Stage/list/show/apply tests | `tests/test_proposals.py` | Extend or add focused report tests. |
| Memory review tests | Selection/report/state behavior | `tests/test_memory_review.py` | Extend for self-noise. |
| Status tests | JSON payload tests | `tests/test_status_json.py` | Extend or use as pattern. |

## 0.5. Pre-flight Checklist

| Prerequisite | Status | Owner |
|---|---|---|
| Business scope explicit | Done | User/GovKB |
| Feature owner corrected to GovKB | Done | GovKB |
| Clearing treated as consumer fixture | Done | GovKB |
| Phase 0 command shape | Open | GovKB maintainer |
| Health/doctor command split | Open | GovKB maintainer |

## 1. Scope And Boundaries

Phase 0 scope:
- Read-only proposal grouping/reporting.
- Advisory proposal quality warnings.
- Unit tests with synthetic project/proposal fixtures.

Later phases:
- Memory-review health report.
- Self-noise filtering.
- Capability maturity scoring.
- VS Code/GovKB doctor.
- Optional VS Code Home display.

Out of scope:
- Auto-apply.
- External service checks.
- Clearing product changes.
- Raw transcript persistence.

## 2. Requirements Mapping

| Requirement | Behavior | Location | New/Modify | Notes |
|---|---|---|---|---|
| REQ-GLI-01 | Group similar staged proposals | `src/govkb/core/proposal_report.py` or `src/govkb/core/proposals.py` | New or Modify | New helper justified if grouping logic is non-trivial. |
| REQ-GLI-02 | Recommend next action | same as above | New or Modify | Advisory only. |
| REQ-GLI-03 | Quality warnings | same as above | New or Modify | Reuse existing metadata/safety fields. |
| REQ-GLI-04 | Memory-review health | `src/govkb/commands/status.py` or new doctor module | Later | CLI shape open. |
| REQ-GLI-05 | Skip self-generated tails | `src/govkb/adapters/codex/bin/codex-memory-review` | Later Modify | Conservative logic. |
| REQ-GLI-06 | Preserve user rows | `tests/test_memory_review.py` | Later Modify | User-row override. |
| REQ-GLI-07 | Capability maturity | new focused core helper or status extension | Later | Advisory first. |
| REQ-GLI-08 | VS Code freshness | doctor command and optional extension display | Later | CLI-first. |
| REQ-GLI-09 | Backward compatibility | existing tests | Modify tests only as needed | Keep current commands unchanged. |

## 3. Design

Phase 0 proposal report:

- Input: project root.
- Reads: `.governed/review-proposals/<id>/proposal.toml`, optional `draft-output.md`.
- Output: human report and JSON.
- Grouping keys: target capability, proposal type, normalized output filename stem, normalized purpose tokens, and safety class.
- Warnings: duplicate output path, low confidence, weak verification command, script without help/compile wording, mutating script missing dry-run/preview evidence, missing draft output when output is expected.
- Recommendation labels: `apply-one`, `merge-first`, `inspect-safety`, `reject-duplicate`, `manual-review`.
- Side effects: none.

Later design:
- Health report composes existing status payload and memory-review report/state parsing.
- Self-noise filter inspects post-`reviewAfter` rows and skips only no-user tails.
- Maturity scoring inspects artifact presence and pending proposals.
- Doctor compares CLI, extension package, install state, and repo revision.

## 4. Integration Points

| Integration | Boundary |
|---|---|
| `.governed/review-proposals` | Read-only in report mode. |
| `govkb proposals apply` | Remains approval-gated and unchanged. |
| `$CODEX_HOME/memories/govkb` | Later health report reads generated state/reports only. |
| VS Code extension | Later phase consumes CLI JSON only. |

## 5. Application Logic

Phase 0:
1. Load project proposals using existing proposal functions.
2. Normalize metadata into report items.
3. Compute similarity groups.
4. Compute warnings per item and per group.
5. Emit text or JSON from `govkb proposals report`.
6. Keep list/show/apply behavior unchanged.

## 6. Data Consistency And Safety

- Phase 0 is read-only.
- No source files under `.governed` are changed.
- Tests use temporary project roots.
- Report output excludes raw transcript content.
- Proposal safety checks remain authoritative in apply/stage paths.

## 7. Testing Strategy

| Test Type | Location | Coverage |
|---|---|---|
| Unit | `tests/test_governed_learning_improvements_use_cases.py` | Proposal grouping, warnings, no mutation. |
| Smoke | `tests/test_governed_learning_improvements_smoke.py` | One proposal report flow. |
| Regression | `tests/test_proposals.py` | Existing list/show/apply stays stable. |
| Later | `tests/test_memory_review.py` | Self-noise skip and user-row override. |

## 8. Verification Commands

| Command | Working Dir | Purpose | Preconditions |
|---|---|---|---|
| `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest tests.test_governed_learning_improvements_use_cases tests.test_governed_learning_improvements_smoke -v` | `/home/ev/code/govkb` | Feature tests | Test scaffolds exist |
| `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest tests.test_proposals -v` | `/home/ev/code/govkb` | Proposal regression | None |
| `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli proposals report <temp-or-consumer-project> --json` | `/home/ev/code/govkb` | CLI report preview | Command implemented |
| `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -v` | `/home/ev/code/govkb` | Full verification | Production code changed |

## 9. Implementation Phases

### Phase 0 - Proposal Report And Quality Warnings

Scope:
- Add proposal report core behavior.
- Add CLI surface.
- Add tests.

Files:
- `src/govkb/core/proposal_report.py` if grouping logic is separated.
- `src/govkb/commands/proposals.py`
- `src/govkb/cli.py`
- `tests/test_governed_learning_improvements_use_cases.py`
- `tests/test_governed_learning_improvements_smoke.py`

Verify:
- Feature tests.
- `tests.test_proposals`.
- CLI report command against a temp fixture and optionally Clearing consumer.

Rollback:
- Revert new report module/tests and remove report CLI action.

### Phase 1 - Memory-Review Health

Scope:
- Add read-only health payload from status, report files, state, and proposal queue.

Verify:
- Temp Codex home fixtures.
- Status tests.

Rollback:
- Remove health command/action and tests.

### Phase 2 - Self-Noise Filtering

Scope:
- Add conservative no-user-tail skip behavior in memory review.

Verify:
- `tests/test_memory_review.py`.
- Inventory dry-run with synthetic session fixtures.

Rollback:
- Revert selection filter changes.

### Phase 3 - Capability Maturity

Scope:
- Add advisory maturity scoring from governed artifacts and pending proposals.

Verify:
- Temp capability tree fixtures.

Rollback:
- Remove maturity helper/payload.

### Phase 4 - VS Code/GovKB Doctor

Scope:
- Add CLI doctor JSON.
- Optionally display freshness in VS Code Home after CLI stabilizes.

Verify:
- Python doctor tests.
- `cd vscode-extension && npm test` if UI changes.

Rollback:
- Remove doctor action/UI display.

## 10. Rollback Plan

Each phase is additive and can be reverted independently. No data migrations or persistent state schema changes are required in Phase 0. Existing staged proposals remain valid if the report command is removed.

## 11. Open Questions

| # | Question | Blocking? |
|---|---|---|
| Q1 | Confirm Phase 0 command shape: `govkb proposals report`. | Yes for code |
| Q2 | Confirm whether health and doctor are one command or two. | Later |
| Q3 | Confirm whether maturity appears in status or a dedicated report. | Later |

## 12. Ready Checklist

- [x] Business scope explicit.
- [x] Existing code inventory complete.
- [x] Phase 0 bounded and read-only.
- [x] Verification and rollback documented.
- [ ] Phase 0 CLI shape confirmed.
- [ ] Test scaffolds created.

