# Governed Skill Knowledge Framework Implementation Summary: Phase 10

Last updated: 2026-04-23

## Scope delivered

Phase 10 added project isolation for governed Codex installs and memory-review runs.

This fixes the multi-project collision risk found before testing AIApps: two governed projects can now both define capabilities such as `project-knowledge-steward` without sharing local skill directories, memory-review state, reports, or candidate staging.

## Behavior added

### Project-scoped Codex skill materialization

`govkb apply codex` now materializes local Codex skills as:

- `govkb-<project-id>-<capability-id>`

Examples:

- `govkb-clearing-project-knowledge-steward`
- `govkb-demo-project-workflow-review`

The repo contract id stays unchanged:

- `project-knowledge-steward`
- `workflow-review`

The local skill directory, `SKILL.md` frontmatter name, metadata, and install state now all record the materialized skill id.

### Multi-project install state

Install state remains per project:

- `$CODEX_HOME/memories/govkb/install-state/<project-id>--codex.json`

Each capability entry now records:

- `capability_id`
- `materialized_skill_id`
- `target_path`
- memory target metadata

### Obsolete managed skill cleanup

When a project is reapplied after the namespacing change, old managed unscoped materialized skills are backed up and removed if their `.govkb-materialized.json` metadata belongs to the same project.

This prevents stale global managed skills from being discovered as unrelated local skills.

### Project-scoped memory-review jobs

`codex-memory-review` now accepts:

- `--project-root <project-root>`

When set, it uses project-specific paths:

- `$CODEX_HOME/memories/govkb/projects/<project-id>/codex-memory-review/state.json`
- `$CODEX_HOME/memories/govkb/projects/<project-id>/codex-memory-review/reports/`
- `$CODEX_HOME/memories/govkb/projects/<project-id>/codex-memory-review/logs/`
- `/tmp/codex-memory-review-<project-id>.lock`

`govkb review-memory --assistant codex --project-root <root>` now passes that project root to the scheduled-task implementation.

The existing local cron entry was migrated from the old global job to a project-scoped Clearing job:

- `/home/ev/.codex/bin/codex-memory-review --once --project-root /home/ev/code/Clearing`

### Project-scoped session selection

When `--project-root` is set, memory review only processes Codex sessions whose session metadata resolves to that governed project root.

This keeps project sessions, reports, state advancement, candidates, and auto-promotion separate.

## Files changed

Implementation:

- `/home/ev/code/Clearing/govkb/src/govkb/adapters/codex/materialize.py`
- `/home/ev/code/Clearing/govkb/src/govkb/commands/apply.py`
- `/home/ev/code/Clearing/govkb/src/govkb/commands/status.py`
- `/home/ev/code/Clearing/govkb/src/govkb/commands/review_memory.py`
- `/home/ev/.codex/bin/codex-memory-review`

Tests:

- `/home/ev/code/Clearing/govkb/tests/test_apply.py`
- `/home/ev/code/Clearing/govkb/tests/test_promote.py`

## Verification

Automated tests:

- command:
  - `python3 -m unittest discover -s tests -v`
- result:
  - passed
  - tests run: `15`

Covered behavior:

- same capability id can be applied from two projects into one Codex home without path collision
- materialized `SKILL.md` frontmatter uses the project-scoped skill name
- install state records `materialized_skill_id`
- promotion still maps local namespaced memory back to repo capability memory

Compile checks:

- `python3 -m py_compile /home/ev/.codex/bin/codex-memory-review`
- `python3 -m py_compile govkb/src/govkb/adapters/codex/materialize.py govkb/src/govkb/commands/apply.py govkb/src/govkb/commands/status.py govkb/src/govkb/commands/review_memory.py`

Live Clearing migration:

- command:
  - `python3 -m govkb.cli apply codex --project-root /home/ev/code/Clearing --codex-home /home/ev/.codex --revision workspace-2026-04-23-project-isolation`
- result:
  - materialized capabilities: `10`
  - old unscoped managed Clearing skill directories removed
  - new local skills use `govkb-clearing-*`

Project-scoped memory-review dry-run:

- command:
  - `python3 -m govkb.cli review-memory --assistant codex --project-root /home/ev/code/Clearing --dry-run --max-sessions 1 --lookback-days 0.25 --codex-timeout 180`
- result:
  - exit code: `0`
  - report path:
    - `/home/ev/.codex/memories/govkb/projects/clearing/codex-memory-review/reports/2026-04-23T111828Z-report.md`

Cron state:

- command:
  - `crontab -l`
- current governed job:
  - `15 8 * * * /home/ev/.codex/bin/codex-memory-review --once --project-root /home/ev/code/Clearing >> /home/ev/.codex/memories/govkb/projects/clearing/codex-memory-review/cron.log 2>&1`

## Decision

The framework is now safe to test on AIApps in the same real Codex home.

Expected AIApps local skill names:

- `govkb-aiapps-project-knowledge-steward`
- future AIApps candidates as `govkb-aiapps-<capability-id>`

Expected AIApps memory-review state:

- `$CODEX_HOME/memories/govkb/projects/aiapps/codex-memory-review/`
