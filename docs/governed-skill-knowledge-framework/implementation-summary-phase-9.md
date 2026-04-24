# Governed Skill Knowledge Framework Implementation Summary: Phase 9

Last updated: 2026-04-23

## Scope delivered

Phase 9 added the first self-developing project loop for new capability growth.

The framework now supports projects that start with no specialized governed skills or only a few skills:

- `govkb init` creates a default `project-knowledge-steward`
- unmatched durable sessions can stage new capability candidates under `.governed/candidates/`
- candidates include evidence, draft contract, draft instructions, and starter memory
- reviewed candidates can be activated with `govkb create capability <id> --from-candidate <candidate-id>`
- `govkb review-memory --assistant codex` runs the same Codex memory-review path as the scheduled task
- the scheduled Codex memory-review task reports candidate stage requests and runs candidate staging after successful non-dry-run reviews

## Behavior added

### Cold-start steward

New project templates now include:

- `.governed/capabilities/project-knowledge-steward/capability.contract.toml`
- `.governed/capabilities/project-knowledge-steward/instructions.md`
- `.governed/capabilities/project-knowledge-steward/references/long-term-memory.md`

This gives every governed project a safe broad knowledge keeper before specialized capabilities exist.

### Candidate staging

New command:

- `govkb candidates stage --project-root <root> --assistant codex --session-file <session.jsonl>`

It creates or updates:

- `.governed/candidates/<candidate-id>/candidate.toml`
- `.governed/candidates/<candidate-id>/evidence.md`
- `.governed/candidates/<candidate-id>/draft-capability.contract.toml`
- `.governed/candidates/<candidate-id>/draft-instructions.md`
- `.governed/candidates/<candidate-id>/references/long-term-memory.md`

Status rules:

- first evidence session: `collecting`
- second unique evidence session: `ready-for-review`
- after activation: `activated`

### Candidate activation

New activation path:

- `govkb create capability <capability-id> --from-candidate <candidate-id>`

This copies the draft candidate package into `.governed/capabilities/<capability-id>/` and marks the candidate as activated.

### Scheduler integration

`/home/ev/.codex/bin/codex-memory-review` now detects durable sessions that do not match a specialized governed capability.

For those sessions, the report includes:

- `Capability candidates` count
- `Capability Candidate Stage Requests` section

During non-dry-run apply, the scheduler calls:

- `python3 -m govkb.cli candidates stage ...`

Candidate staging is skipped during dry-run.

## Files changed

Implementation:

- `/home/ev/code/Clearing/govkb/src/govkb/core/ids.py`
- `/home/ev/code/Clearing/govkb/src/govkb/core/candidates.py`
- `/home/ev/code/Clearing/govkb/src/govkb/commands/candidates.py`
- `/home/ev/code/Clearing/govkb/src/govkb/commands/create_capability.py`
- `/home/ev/code/Clearing/govkb/src/govkb/commands/init.py`
- `/home/ev/code/Clearing/govkb/src/govkb/commands/review_memory.py`
- `/home/ev/code/Clearing/govkb/src/govkb/cli.py`
- `/home/ev/code/Clearing/govkb/pyproject.toml`
- `/home/ev/.codex/bin/codex-memory-review`

Templates and live Clearing package:

- `/home/ev/code/Clearing/govkb/src/govkb/templates/project/.governed/capabilities/project-knowledge-steward/`
- `/home/ev/code/Clearing/.governed/capabilities/project-knowledge-steward/`
- `/home/ev/code/Clearing/.governed/releases/2026.04.23.toml`

Tests:

- `/home/ev/code/Clearing/govkb/tests/test_candidates.py`
- `/home/ev/code/Clearing/govkb/tests/test_init.py`
- `/home/ev/code/Clearing/govkb/tests/test_apply.py`

## Verification

Automated tests:

- command:
  - `python3 -m unittest discover -s tests -v`
- result:
  - passed
  - tests run: `14`

Package validation:

- command:
  - `python3 -m govkb.cli validate /home/ev/code/Clearing`
- result:
  - passed
  - capabilities loaded: `10`

Compile checks:

- `python3 -m py_compile /home/ev/.codex/bin/codex-memory-review`
- `python3 -m py_compile govkb/src/govkb/core/candidates.py govkb/src/govkb/commands/candidates.py govkb/src/govkb/commands/create_capability.py govkb/src/govkb/cli.py`

Live apply:

- command:
  - `python3 -m govkb.cli apply codex --project-root /home/ev/code/Clearing --codex-home /home/ev/.codex`
- result:
  - materialized capabilities: `10`
  - applied revision: `workspace-2026-04-23-self-developing-candidates`
  - new local skill: `/home/ev/.codex/skills/project-knowledge-steward`

Scheduler dry-run:

- command:
  - `/home/ev/.codex/bin/codex-memory-review --dry-run --once --max-sessions 1 --lookback-days 0.25 --codex-timeout 180`
- result:
  - exit code: `0`
  - discovered memory targets: `10`
  - latest report: `/home/ev/.codex/memories/codex-memory-review/reports/2026-04-23T105015Z-report.md`

CLI wrapper dry-run:

- command:
  - `python3 -m govkb.cli review-memory --assistant codex --project-root /home/ev/code/Clearing --dry-run --max-sessions 1 --lookback-days 0.25 --codex-timeout 180`
- result:
  - exit code: `0`
  - discovered memory targets: `10`
  - latest report: `/home/ev/.codex/memories/codex-memory-review/reports/2026-04-23T105214Z-report.md`

## Current state

Clearing has no staged capability candidates yet:

- command:
  - `python3 -m govkb.cli candidates list /home/ev/code/Clearing`
- result:
  - `No candidates found.`

That is expected because this phase installed the mechanism; candidates appear after eligible future non-dry-run memory-review sessions.

## Decision

The MVP now covers both growth paths:

- existing governed capabilities can gain expertise through safe memory updates and auto-promote
- repeated unmatched project work can stage new governed capability candidates for review

The next useful slice is tightening the candidate detector quality:

1. improve candidate naming and grouping beyond simple feature-path and keyword extraction
2. add a candidate review command or digest that shows ready-for-review candidates clearly
3. add a manual reject/archive path so stale candidates do not accumulate
