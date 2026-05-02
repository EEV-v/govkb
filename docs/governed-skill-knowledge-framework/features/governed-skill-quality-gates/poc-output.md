# Governed Skill Quality Gates - PoC Output

## Summary

Baseline evidence confirms the feature is a real behavior change, not a documentation-only update. GovKB has base package validation and candidate activation today, but no opt-in strict validation mode and no mandatory strict gate before auto-created candidates become active.

## Assertion Results

| Assertion | Result | Evidence | Notes |
|---|---|---|---|
| A1: CLI has no strict validation flag today | Passed | `/Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m govkb.cli --help` lists `validate`; `rg -n -e "--strict\|strict validation\|strict" src/govkb tests` finds no strict validation implementation. | The feature docs now contain strict references, so source-only search is the relevant proof. |
| A2: base validation rejects configured unsafe relative paths | Passed | `/Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_validate -v` ran 2 tests and passed. | Existing contract parser already handles memory target parent traversal. |
| A3: candidate auto-create currently activates and materializes ready candidates | Passed | `/Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_candidates.CandidateCommandTests.test_auto_create_ready_creates_capability_and_materializes_codex -v` ran 1 test and passed. | This proves the strict activation gate is currently absent. |
| A4: strict scanner needs a new core surface | Passed | Source inventory: `src/govkb/core/contracts.py`, `src/govkb/commands/validate.py`, `src/govkb/commands/candidates.py`, `src/govkb/core/kb_bootstrap.py`. | Reusing `kb_bootstrap` placeholder patterns is useful, but strict rules should not be mixed into TOML parsing. |

## Outliers

- An initial `rg "--strict|strict validation|strict"` command failed because the pattern started with `--`; the rerun used `rg -n -e`.
- Full test discovery is not a clean baseline in this environment because unrelated memory-review and install-cron tests fail. Targeted baseline tests for this feature pass.

## Open Gaps

- No strict validation data model exists yet.
- No `govkb validate --strict` CLI output exists yet.
- No lifecycle or approval metadata is parsed from capability contracts.
- Candidate metadata has activation status but no review approval block.

## Recommendation

Proceed with a narrow implementation slice:

1. Add strict issue/result models and package scanning under `src/govkb/core/`.
2. Add `govkb validate --strict`.
3. Add lifecycle/approval metadata parsing in a backward-compatible way.
4. Gate candidate auto-create on strict validation and explicit approval metadata.
5. Preserve normal validation and materialization behavior unless strict mode is requested.

