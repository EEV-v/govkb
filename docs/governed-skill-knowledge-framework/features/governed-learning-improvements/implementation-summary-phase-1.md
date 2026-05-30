# Governed Learning Improvements - Phase 1 Implementation Summary

Date: 2026-05-30

## Scope Implemented

Phase 1 adds a read-only project health command:

- `govkb doctor [project_root]`
- `govkb doctor [project_root] --json`
- `govkb doctor [project_root] --codex-home <path>`

The command composes existing GovKB data instead of running classification or mutating project files:

- validation status from `build_status_payload`
- repo revision and governed dirty state
- Codex install-state revision and materialized capabilities
- pending local skill update state
- proposal queue counts and review actions
- memory-review state path, last run timestamp, last successful advancement timestamp, and processed session count
- latest memory-review report path, run id, status, summary counts, and discovery/backlog counts
- project-scoped cron presence, stale cron detection, script path, and cron log path
- concrete next commands for missing cron, missing memory-review report, proposal safety groups, and merge groups

## Consumer Check

The command was run against Clearing as a consumer project:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli doctor /home/ev/code/Clearing
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli doctor /home/ev/code/Clearing --json
```

Observed result:

- State: `attention`
- Cron: `installed`
- Memory review latest run: `completed`
- Memory review processed sessions: 46
- Selected before max-session limit in latest report: 44
- Proposals: 30
- Proposal groups: 28
- Proposal warnings: 16
- Proposal actions: 4 `inspect-safety`, 2 `merge-first`, 22 `manual-review`
- Installed revision matched repo revision: `d7ae41a7d6ac5b25dbd186401ccf23e386c67688`

## Verification

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest tests.test_doctor tests.test_status_json tests.test_proposals -v
git diff --check
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli doctor --help
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli doctor /home/ev/code/Clearing
```

Result:

- Focused tests passed: 14 tests.
- Full suite passed: 196 tests, 33 skipped scaffold tests.
- Diff whitespace check passed.
- CLI help and Clearing consumer doctor commands resolved.

## Deferred

Phase 1 does not implement self-noise filtering, capability maturity scoring, or VS Code UI changes. VS Code should consume `govkb proposals review --json` and `govkb doctor --json` in the next UI slice.
