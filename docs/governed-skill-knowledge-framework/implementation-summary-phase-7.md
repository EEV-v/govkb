# Governed Skill Knowledge Framework Implementation Summary: Phase 7

Last updated: 2026-04-23

## Scope delivered

Phase 7 changed the promotion model from manual-only to guarded auto-promotion.

The product decision is:

- `govkb promote` remains available for manual/admin recovery
- the scheduled memory-review task now auto-promotes safe governed memory changes after successful non-dry-run auto-apply
- auto-promotion is restricted to append-only bullet additions inside configured memory sections
- any existing-line edit, deletion, heading change, or non-target section change is rejected and reported

This avoids depending on daily human `govkb promote` usage while still preventing the scheduler from rewriting arbitrary repo files.

## New implementation

Added real promotion logic:

- `/home/ev/code/Clearing/govkb/src/govkb/adapters/codex/promote.py`
- `/home/ev/code/Clearing/govkb/src/govkb/commands/promote.py`

Updated CLI:

- `/home/ev/code/Clearing/govkb/src/govkb/cli.py`

New command behavior:

- `govkb promote <project-root> --assistant codex --codex-home <path>`
- `govkb promote <project-root> --assistant codex --codex-home <path> --preview`
- `govkb promote <project-root> --assistant codex --codex-home <path> --auto`

Promotion reads:

- local install state under `$CODEX_HOME/memories/govkb/install-state/<project>--codex.json`
- local materialized memory files under `$CODEX_HOME/skills/<capability>/references/...`
- repo source memory files under `.governed/capabilities/<capability>/references/...`

Promotion writes:

- repo source memory files only when the local change is append-only and section-safe
- promotion audit reports under `.governed/reports/promotions/`

## Scheduler integration

Updated live scheduled runtime:

- `/home/ev/.codex/bin/codex-memory-review`

New behavior:

- after a successful non-dry-run memory-review run, if governed targets received auto-applied memory updates, the script calls:
  - `python3 -m govkb.cli promote <project-root> --assistant codex --codex-home <CODEX_HOME> --auto`
- promotion runs only for governed project targets that actually received auto-applied local memory changes
- staged or explicit-acceptance-gated candidates are not written locally and therefore are not auto-promoted
- promotion can be disabled with:
  - `--no-auto-promote`

## Guardrails

Auto-promotion accepts only:

- same markdown preamble
- same section headings and order
- no changes in non-target sections
- no edits or deletions of existing lines in target sections
- inserted non-empty lines must be markdown bullets beginning with `- `

Rejected changes:

- return non-zero from `govkb promote`
- write a promotion report with the rejection reason
- make the scheduler return non-zero when auto-promote fails after an apply

## Verification

Automated tests:

- command:
  - `python3 -m unittest discover -s tests -v`
- result:
  - passed
  - tests run: `12`

Covered cases:

- append-only local memory addition is promoted into repo source
- non-append local memory change is rejected and repo source stays unchanged
- existing materialization and validation tests still pass

Runtime checks:

- `python3 -m py_compile /home/ev/.codex/bin/codex-memory-review`
- `python3 /home/ev/.codex/bin/codex-memory-review --help`
- `python3 -m govkb.cli promote /home/ev/code/Clearing --codex-home /home/ev/.codex --preview`

Current live promote preview result:

- promoted: `0`
- rejected: `0`
- reason: no local governed memory changes currently need promotion

## Resulting loop

The intended daily loop is now:

`real work session -> scheduled memory review -> safe local auto-apply -> guarded auto-promote into .governed -> repo has team-shareable learning`

Manual review is still required for staged candidates, including estimator-style explicit-acceptance memory.

## Next decision

The next useful slice should be one of:

1. Add git hygiene around auto-promote: status checks, dirty-file reporting, and optional branch/worktree mode.
2. Add a report digest that tells the user what was auto-promoted since the last run.
3. Add new-capability candidate staging for repeated unmatched work.

The highest leverage next step is git hygiene plus a digest, because auto-promotion will now dirty `.governed` files by design and that needs to be visible instead of surprising.
