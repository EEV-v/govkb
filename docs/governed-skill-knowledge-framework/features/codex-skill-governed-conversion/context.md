# Codex Skill Governed Conversion - Implementation Context

Last updated: 2026-05-01

## Existing Code Surface

| Area | Current Location | Observed Behavior |
|---|---|---|
| CLI parser | `src/govkb/cli.py` | No `convert` command exists yet. |
| Capability package model | `src/govkb/core/contracts.py` | Loads governed capability contracts and existing `[migration]` fields. |
| Materialization source selection | `src/govkb/adapters/codex/materialize.py` | Prefers `adapters/codex/SKILL.md`, then root `SKILL.md`, then `instructions.md`, then migration fallback. |
| Capability creation pattern | `src/govkb/commands/create_capability.py` | Creates contract, `instructions.md`, `references/long-term-memory.md`, and `prompts/initialize-kb.md`. |
| Migration fallback tests | `tests/test_apply.py` | Existing behavior proves local Codex skill fallback can remain available during migration. |
| Prior parent planning | `governed-skill-contract-and-migration/context.md` | Names likely new modules: `src/govkb/core/skill_conversion.py`, `src/govkb/commands/convert.py`, and `tests/test_skill_conversion.py`. |

## Current Gaps Against The Spec

- No conversion planner or source resolver exists.
- No `govkb convert skill` CLI command exists.
- No conversion preview/write command tests exist.
- No source item classification model exists for governed, adapter-local, tool, unsafe, or manual-review items.
- No redacted conversion report writer exists.
- No strict-validation integration exists yet; this feature depends on `governed-skill-quality-gates`.

## Engineering Implications

- Implement after quality gates define strict package validation and lifecycle/approval metadata.
- Add a conversion core module that can parse a local Codex skill directory without mutating it.
- Add `govkb convert skill <skill-or-path> --project-root <root> [--codex-home <home>] [--capability-id <id>] [--preview | --write] [--json]`.
- Default behavior should be preview/non-mutating.
- Write mode should fail if target capability package already exists.
- Always write canonical `instructions.md`.
- Write `adapters/codex/SKILL.md` only when the plan records a Codex-specific parity reason.
- Use existing `[migration]` support initially unless implementation planning finds a stronger reason for a separate metadata file.
- Create redacted conversion report metadata on write without unsafe values.

## Recommended Test Focus

- preview writes no files
- source skill name resolves from `--codex-home`
- direct source path outside `--codex-home` works when explicitly provided
- write creates exactly one new governed package
- rerun write fails on existing target
- source local skill is unchanged
- safe memory/prompts/scripts/fixtures are copied or transformed into standard locations
- unsafe content is rejected and omitted from governed files
- redacted conversion report contains only metadata and reasons
- converted package passes strict validation before success
- materialized Codex output uses `adapters/codex/SKILL.md` when present, otherwise wraps `instructions.md`

## Dependency Boundary

This spec is ready for engineering planning, but implementation should follow the quality-gates implementation because conversion write success depends on strict validation behavior. The engineering plan should treat strict validation as an upstream interface and should not reimplement quality-gate rules inside conversion logic.

## Verification Baseline

Run from the repo root after implementation:

```bash
PYTHONPATH=src python3 -m govkb.cli convert skill <skill-or-path> --project-root <temp-project> --codex-home <temp-codex-home> --preview
PYTHONPATH=src python3 -m govkb.cli convert skill <skill-or-path> --project-root <temp-project> --codex-home <temp-codex-home> --write
python3 -m unittest tests.test_skill_conversion -v
python3 -m unittest tests.test_apply -v
```

## Sources

- `src/govkb/cli.py`
- `src/govkb/core/contracts.py`
- `src/govkb/adapters/codex/materialize.py`
- `src/govkb/commands/create_capability.py`
- `tests/test_apply.py`
- `docs/governed-skill-knowledge-framework/features/governed-skill-contract-and-migration/context.md`
