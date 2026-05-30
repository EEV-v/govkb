# Governed Learning Improvements - PoC Plan

Last updated: 2026-05-29

## Mode

`fixture-validation`

## Evidence Strategy

Use current GovKB source, existing tests, and synthetic/temp fixtures. Clearing's real proposal queue can be used for manual validation, but automated tests should not depend on `/home/ev/code/Clearing` or `/home/ev/.codex`.

## Assertions

| Assertion | Method | Command/File | Expected Result |
|---|---|---|---|
| A-1 | Inspect current proposal model and sample staged proposals. | `src/govkb/core/proposals.py`, `tests/test_proposals.py` | Existing metadata supports grouping by target, type, purpose, and output path. |
| A-2 | Inspect safety metadata. | `proposal.toml` fixtures and `stage_proposal` validation | Quality warnings can be derived without mutating files. |
| A-3 | Inspect status/report sources. | `src/govkb/commands/status.py`, memory-review report/state fixtures | Health report can combine status JSON, reports, state, and proposal counts. |
| A-4 | Inspect memory-review row selection. | `src/govkb/adapters/codex/bin/codex-memory-review` | Self-noise can be filtered after `reviewAfter` with user-row override. |
| A-5 | Inspect governed capability tree. | `.governed/capabilities/<id>/` fixtures | Maturity levels are derivable from file presence and staged proposals. |
| A-6 | Inspect extension and install metadata. | `vscode-extension/package.json`, status JSON | Doctor output can compare extension, CLI, repo, and install state. |
| A-7 | Run existing tests. | `python3 -m unittest tests.test_proposals tests.test_memory_review tests.test_status_json -v` | Existing command behavior remains stable. |

## Data And Fixtures

Planned fixtures:
- temp project root with `.governed/review-proposals/` entries for duplicate DVCA and unrelated proposals
- temp governed capabilities with memory/runbook/script/test evidence
- temp Codex home with memory-review `state.json` and synthetic report files
- synthetic session JSONL rows for assistant/tool noise and user-decision tails
- mocked VS Code package metadata and status JSON

## Rerun Command

Initial planning evidence does not create a dedicated rerun script. Phase 0 should add test fixtures and use:

```bash
cd /home/ev/code/govkb
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest tests.test_proposals tests.test_memory_review tests.test_status_json -v
```

Final implementation verification should use:

```bash
cd /home/ev/code/govkb
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## Risks And Blockers

| Risk | Status | Handling |
|---|---|---|
| Proposal grouping over-merges unrelated work. | Open | Keep report advisory; show reasons and never mutate. |
| Self-noise filter skips useful content. | Open | Only skip tails with no user-authored rows. |
| Health report depends on machine-specific cron/systemctl behavior. | Open | Report unavailable checks without failing. |
| VS Code freshness needs UI design. | Open | Build CLI doctor JSON first; UI second. |

