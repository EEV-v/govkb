# Governed Skill Management UX Implementation Plan

## Scope

Implement governed skill management as a CLI-backed feature with VS Code affordances. Reuse existing conversion logic and add a new capability management core for list, rename, and merge.

## Plan

1. Add a core capability management module that can produce detailed capability summaries, rename capabilities transactionally, and merge capabilities transactionally.
2. Expose `govkb capabilities list`, `govkb capabilities rename`, and `govkb capabilities merge`.
3. Extend status JSON capability summaries with paths, aliases, memory targets, lifecycle state, and migration state.
4. Add VS Code command builders and flows for conversion, rename, and merge.
5. Restore the missing Governed Skills view and add actions for refresh, open, convert, rename, and merge.
6. Repair conversion previews so copied skill-owned files and moved helper scripts are referenced through their governed package paths, while project-local absolute paths become repo-relative paths.
7. Add Python and TypeScript tests for CLI behavior, view rows, command builders, flow command sequencing, and strict conversion repair.

## Verification

- `PYTHONPATH=src <python3.11+> -m unittest tests.test_capability_management tests.test_skill_conversion tests.test_status_json -v`
- `npm test` from `vscode-extension`
- `PYTHONPATH=src <python3.11+> -m govkb.cli capabilities --help`
- `govkb convert skill <path> --project-root <project> --json` for a skill with copied references and scripts
