# Governed Skill Knowledge Framework Implementation Summary: Phase 2

Last updated: 2026-04-22

## Scope delivered

Phase 2 turned `govkb apply codex` into a real local materialization flow.

Delivered surfaces:

- `/home/ev/code/Clearing/govkb/src/govkb/adapters/codex/materialize.py`
- `/home/ev/code/Clearing/govkb/src/govkb/core/install_state.py`
- `/home/ev/code/Clearing/govkb/src/govkb/commands/apply.py`
- `/home/ev/code/Clearing/govkb/src/govkb/commands/status.py`
- `/home/ev/code/Clearing/govkb/src/govkb/commands/create_capability.py`

## Behavior now implemented

- `govkb apply codex --preview`
  - validates the governed bundle
  - resolves release/revision
  - builds the local Codex install plan
  - reports planned skill targets and install-state path
  - does not write local skills or install state
- `govkb apply codex`
  - materializes governed capabilities into a local Codex home
  - copies repo capability `references/` and optional `agents/`
  - builds local `SKILL.md` from:
    - repo `adapters/codex/SKILL.md`, or
    - repo `SKILL.md`, or
    - repo `instructions.md`, or
    - migration fallback local Codex skill, or
    - generated governed fallback text
  - writes `.govkb-materialized.json` for each derived skill
  - records local install state only after materialization succeeds
  - backs up replaced local skills under `$CODEX_HOME/memories/govkb/backups/...`
- `govkb status --codex-home ...`
  - reports applied release, revision, timestamp, and capability count from local install state
- `govkb create capability`
  - now scaffolds `instructions.md` in addition to the contract and memory file

## Migration-safe behavior

This slice also added legacy Codex migration fallback support through optional contract fields:

- `[migration].source_adapter`
- `[migration].source_path`
- `[migration].status`

When a governed capability does not yet carry full repo-native source files, `govkb apply codex` can reuse missing `SKILL.md`, `references/`, or `agents/` content from the existing local Codex skill path while still treating the repo contract as authoritative.

## Routing foundation added

To reduce the later scheduler cutover, the package now also contains contract-derived helper logic in:

- `/home/ev/code/Clearing/govkb/src/govkb/adapters/codex/memory_review.py`

Implemented helpers:

- governed memory-target discovery from repo contracts
- session project-root resolution from session metadata
- alias/hint/negative-hint based signal extraction
- prompt-target narrowing

The live scheduled script cutover is now covered by `implementation-summary-phase-3.md`.

## Verification completed

Automated:

- `python3 -m unittest discover -s tests -v`

Manual CLI rehearsal with temp Codex home:

1. `python3 -m govkb.cli init`
2. `python3 -m govkb.cli create capability`
3. `python3 -m govkb.cli apply codex --preview`
4. `python3 -m govkb.cli apply codex`
5. `python3 -m govkb.cli status --codex-home ...`

Result: passed

## Deferred to next slice

- full contract-driven governed routing in the live daily task
- governed automation worktree / promotion flow
- multi-session new capability candidate staging in the live adapter
