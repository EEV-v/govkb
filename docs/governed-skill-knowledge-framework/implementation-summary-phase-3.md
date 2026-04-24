# Governed Skill Knowledge Framework Implementation Summary: Phase 3

Last updated: 2026-04-22

## Scope delivered

Phase 3 connected the existing scheduled Codex memory-review runtime to governed install-state routing.

Live runtime changed:

- `/home/ev/.codex/bin/codex-memory-review`

Framework support already added in the package:

- `/home/ev/code/Clearing/govkb/src/govkb/adapters/codex/memory_review.py`

## Runtime behavior now implemented

The scheduled runtime now:

- reads governed install-state files from:
  - `$CODEX_HOME/memories/govkb/install-state/*.json`
- overlays governed routing metadata on top of the existing local skill scan
- scopes governed capabilities by session project root from session `cwd`
- keeps legacy local skill discovery for unmigrated skills
- uses contract-derived:
  - aliases
  - hints
  - negative hints
  - explicit-acceptance requirement
  - memory target path/sections
- updates in-memory target state without dropping governed routing metadata after auto-apply

## Migration safety

This cutover is intentionally hybrid:

- legacy local skills still work
- governed capabilities from `govkb apply codex` override legacy routing only for the matching materialized capability id
- sessions outside a governed repo package continue using legacy behavior

That means the hardcoded `KEYWORD_SKILL_HINTS` path is no longer the only routing source for governed capabilities, but it still remains as fallback for legacy local skills until migration is complete.

## Verification completed

Before applying the live edit:

- rehearsed the full rewrite against a temp copy of the script
- validated syntax with `python3 -m py_compile`
- validated startup with `--help`
- validated governed install-state discovery against a synthetic temp `CODEX_HOME`

After applying the live edit:

- reran syntax validation on the real script
- reran governed install-state discovery against the real script using a synthetic temp `CODEX_HOME`

Result: passed

## Deferred to later work

- move more of the live runtime into reusable `govkb` package code instead of maintaining a patched local script
- repo-worktree mutation and promotion flow for scheduled governed writes
- staged new capability candidate generation in the live adapter
- second-local-setup proof using a real project `.governed` package and real applied release
