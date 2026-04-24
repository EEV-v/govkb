# Governed Skill Knowledge Framework Implementation Summary: Phase 11

Last updated: 2026-04-23

## Scope delivered

Phase 11 added the user-facing one-command install path.

The earlier flow required separate `init`, `validate`, `apply`, and cron setup commands. That is still useful for debugging, but real usage now starts with:

- `govkb install <project-root> --project-id <id> --project-name <name> --cron`

## Behavior added

`govkb install` now handles:

1. scaffold `.governed` when missing
2. validate the governed package
3. apply the Codex adapter with project-scoped materialized skill names
4. optionally add the project-scoped memory-review cron job
5. support `--preview` for a no-write install plan

## Command shape

Preview:

```bash
python3 -m govkb.cli install /home/ev/code/AIApps --project-id aiapps --project-name AIApps --codex-home /home/ev/.codex --cron --preview
```

Apply:

```bash
python3 -m govkb.cli install /home/ev/code/AIApps --project-id aiapps --project-name AIApps --codex-home /home/ev/.codex --cron
```

## Files changed

Implementation:

- `/home/ev/code/Clearing/govkb/src/govkb/commands/install.py`
- `/home/ev/code/Clearing/govkb/src/govkb/cli.py`

Tests:

- `/home/ev/code/Clearing/govkb/tests/test_install.py`

## Verification

Automated tests:

- command:
  - `python3 -m unittest discover -s tests -v`
- result:
  - passed
  - tests run: `17`

AIApps preview:

- command:
  - `python3 -m govkb.cli install /home/ev/code/AIApps --project-id aiapps --project-name AIApps --codex-home /home/ev/.codex --cron --preview`
- result:
  - no files written
  - planned `.governed` scaffold
  - planned project id: `aiapps`
  - planned cron:
    - `15 8 * * * /home/ev/.codex/bin/codex-memory-review --once --project-root /home/ev/code/AIApps >> /home/ev/.codex/memories/govkb/projects/aiapps/codex-memory-review/cron.log 2>&1`

## Decision

Use `govkb install` as the normal onboarding command.

Keep lower-level commands for diagnostics:

- `govkb validate`
- `govkb apply codex`
- `govkb status`
- `govkb review-memory`
- `govkb candidates`
- `govkb promote`
