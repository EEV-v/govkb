# Project Knowledge Steward

## Project Working Agreement









- Keep durable project knowledge in `.governed` so it can be reviewed, versioned, and shared with the team.

## Stable Workflows

- Use feature folders under `docs/governed-skill-knowledge-framework/features/` for durable GovKB feature planning, implementation evidence, review, release notes, and sign-off.
- Keep reusable GovKB lifecycle operation in the `curator` capability instead of expanding the broad project steward.

## Commands And Verification










- Use `npm --prefix vscode-extension run test` for the `test` workflow in `vscode-extension/package.json`.

## Repo Conventions

- Keep governed package definitions under `.governed/capabilities/`; materialized skills under the local Codex home are generated artifacts, not the durable source of truth.
- Keep VS Code extension source under `vscode-extension/src/` and compiled output under `vscode-extension/out/`.

## Code And Docs Map










- Setup and reference notes for this capability start in `README.md`.
- Project docs for this capability live under `docs/`.
- Relevant source code for this capability lives under `src/`.
- Automated tests for this capability live under `tests/`.
- Setup and reference notes for this capability start in `docs/governed-skill-knowledge-framework/features/README.md`.
- Setup and reference notes for this capability start in `docs/README.md`.
- Setup and reference notes for this capability start in `docs/scripts/feature_spec/README.md`.
- Setup and reference notes for this capability start in `vscode-extension/README.md`.
- Python project metadata for this capability is defined in `pyproject.toml`.
- Node workspace for this capability is rooted at `vscode-extension/` with scripts in `vscode-extension/package.json`.

## Authority Rules

- Capability contract files define routing, memory targets, lifecycle state, and quality requirements for governed capabilities.
- Capability instruction files define the active skill instructions materialized into Codex.
- Capability long-term memory files are the durable memory source for governed capabilities.

## Candidate Skill Signals









- Track repeated specialized work as a candidate governed capability instead of expanding this broad steward indefinitely.
