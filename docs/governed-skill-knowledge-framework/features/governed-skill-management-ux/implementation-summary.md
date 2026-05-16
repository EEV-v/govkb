# Governed Skill Management UX Implementation Summary

## Completed

- Added `src/govkb/core/capability_management.py` for detailed capability listing, transactional rename, and transactional merge.
- Added `govkb capabilities list`, `govkb capabilities rename`, and `govkb capabilities merge`.
- Extended status JSON capability rows with package paths, instruction paths, memory targets, aliases, lifecycle state, and migration state.
- Added VS Code commands for Refresh Governed Skills, Open Governed Skill, Convert One Existing Skill To Governed, Rename Governed Skill, and Merge Governed Skills.
- Conversion now uses a one-skill picker from `CODEX_HOME/skills` with a manual path fallback, so users do not need to remember exact skill ids.
- The conversion picker hides `.system` skills, materialized governed outputs, and source skills already represented by the active project's governed capabilities or aliases.
- Conversion now repairs safe path references before strict validation: moved `scripts/` files point to `tools/scripts/`, copied reference files point to governed package paths, and absolute target-project paths become repo-relative paths.
- Conversion preview copies referenced repo files into the temporary validation project, so strict validation can prove that repo-relative references are real before writing a package.
- Conversion fallback memory now uses an existing target-project entry point such as `README.md` or `AGENTS.md`; preview no longer invents `README.md`, keeping preview and write strict validation aligned.
- Restored the Governed Skills view in the activity panel and added title/context actions.
- Added focused Python and extension tests for the new management workflows.

## Verification

- `PYTHONPATH=src /Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_capability_management tests.test_skill_conversion tests.test_status_json -v` passed.
- `PYTHONPATH=src /Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_skill_conversion -v` passed with 10 tests.
- `/Users/vasilevevgeny/code/govkb/scripts/govkb-dev convert skill /Users/vasilevevgeny/.codex/skills/comparative-grade-screening --project-root /Users/vasilevevgeny/code/Etna/Clearing --codex-home /Users/vasilevevgeny/.codex --capability-id comparative-grade-screening --write --json` returned `strictStatus: passed` and kept the package.
- `/Users/vasilevevgeny/code/govkb/scripts/govkb-dev validate /Users/vasilevevgeny/code/Etna/Clearing --strict` passed after cleaning a generic `review.md` memory reference in the existing Clearing feature cookbook.
- `npm test` from `vscode-extension` passed with 97 tests.
- Real Clearing picker discovery now returns only `comparative-grade-screening`, `govkb-feature-cookbook`, and `govkb-feature-spec-cookbook` after active-project filtering.
