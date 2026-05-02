# Codex Skill Governed Conversion - PoC Plan

## Mode

baseline-vs-candidate

## Evidence Strategy

Use repository source and existing tests to prove the baseline:

- no conversion command exists yet
- Codex materialization can already consume governed `instructions.md`
- existing `[migration]` metadata is parsed and materialization can use a local Codex skill fallback
- strict validation is now available for package write gating

## Assertions

| Assertion | Method | Command/File | Expected Result |
|---|---|---|---|
| A1: No conversion command exists today | CLI help/source search | Working dir: `/Users/vasilevevgeny/code/govkb`; `/Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m govkb.cli --help`; `rg -n "convert" src/govkb tests` | CLI has no `convert` command before implementation. |
| A2: Materialization can wrap governed instructions | Existing tests/source | `src/govkb/adapters/codex/materialize.py`, `tests/test_apply.py` | `_render_wrapped_skill` and apply tests prove `instructions.md` can become local Codex `SKILL.md`. |
| A3: Migration metadata is already loaded | Existing tests/source | `src/govkb/core/contracts.py`, `tests/test_apply.py::test_apply_uses_migration_fallback_when_repo_files_are_missing` | Existing `[migration]` fields are parsed and used by Codex materialization. |
| A4: Strict validation can gate converted packages | Existing feature implementation | `src/govkb/core/governed_skill.py`, `tests/test_governed_skill_quality_gates_*` | Conversion write can reuse strict validation instead of duplicating rules. |

## Data And Fixtures

Use synthetic local Codex skill directories in temp dirs:

- `SKILL.md` with simple frontmatter/body
- safe `references/long-term-memory.md`
- safe `prompts/release-check.md`
- safe `tools/scripts/check.sh`
- unsafe `references/unsafe.md` with synthetic token-like and credential-path content

No raw assistant transcripts, real `$CODEX_HOME`, source user home state, or external services are required.

## Rerun Command

Working dir: `/Users/vasilevevgeny/code/govkb`

```bash
docs/governed-skill-knowledge-framework/features/codex-skill-governed-conversion/regenerate-poc-data.sh
```

## Risks And Blockers

- Full test discovery has unrelated baseline failures in install/memory-review tests.
- The MVP uses direct command metadata and does not add a separate approval UI.
- Preview validation can only validate a rendered temp package approximation; write validation remains authoritative.

