# Codex Skill Governed Conversion - PoC Output

## Summary

Baseline evidence supports adding a new conversion command rather than modifying materialization. GovKB already knows how to materialize governed packages into Codex skills and how to parse migration metadata. The missing behavior is source-skill resolution, safe classification, preview/write orchestration, and strict validation gating.

## Assertion Results

| Assertion | Result | Evidence | Notes |
|---|---|---|---|
| A1: No conversion command exists today | Passed | `govkb.cli --help` before implementation had no `convert`; `src/govkb/cli.py` had no convert parser. | New command is additive. |
| A2: Materialization can wrap governed instructions | Passed | `src/govkb/adapters/codex/materialize.py` uses `_render_wrapped_skill`; `tests/test_apply.py` covers materialized `SKILL.md`. | Conversion should always write `instructions.md`. |
| A3: Migration metadata is already loaded | Passed | `CapabilityContract` includes migration fields; `test_apply_uses_migration_fallback_when_repo_files_are_missing` passes. | Conversion can reuse `[migration]` with extra fields. |
| A4: Strict validation can gate converted packages | Passed | Quality-gates implementation added `validate_governed_skill_package`; targeted tests pass. | Conversion should not reimplement strict package rules. |

## Outliers

- System `/usr/bin/python3` lacks `tomllib`; bundled Python 3.12 is used for verification.
- Full repository discovery still has unrelated baseline failures outside conversion and strict validation.

## Open Gaps

- No conversion planner/writer exists yet.
- No conversion command tests exist yet.
- No conversion report writer exists yet.

## Recommendation

Proceed with a focused implementation:

1. Add `src/govkb/core/skill_conversion.py`.
2. Add `src/govkb/commands/convert.py`.
3. Add `govkb convert skill`.
4. Add `tests/test_skill_conversion.py`.
5. Reuse strict validation and existing Codex apply behavior.

