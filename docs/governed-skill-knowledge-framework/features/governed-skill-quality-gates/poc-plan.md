# Governed Skill Quality Gates - PoC Plan

## Mode

baseline-vs-candidate

## Evidence Strategy

Use repository code and targeted unit tests to prove the current baseline:

- `govkb validate` exists but has no strict flag.
- base validation already rejects contract-level path traversal.
- candidate auto-create currently activates ready candidates after base validation and Codex materialization.
- no strict validation module or structured strict issue type exists under `src/govkb`.

Candidate behavior will add strict validation as an opt-in project check and as a mandatory candidate activation gate.

## Assertions

| Assertion | Method | Command/File | Expected Result |
|---|---|---|---|
| A1: CLI has no strict validation flag today | CLI help plus source search | Working dir: `/Users/vasilevevgeny/code/govkb`; `/Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m govkb.cli --help`; `rg -n -e "--strict\|strict validation\|strict" src/govkb tests` | Help shows `validate` command but no strict option; strict references are unrelated existing text. |
| A2: base validation rejects configured unsafe relative paths | targeted unittest | Working dir: `/Users/vasilevevgeny/code/govkb`; `/Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_validate -v` | Existing tests pass and show contract-level path validation already works. |
| A3: candidate auto-create currently activates and materializes ready candidates | targeted unittest | Working dir: `/Users/vasilevevgeny/code/govkb`; `/Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_candidates.CandidateCommandTests.test_auto_create_ready_creates_capability_and_materializes_codex -v` | Existing test passes, proving current behavior activates after base validation only. |
| A4: strict scanner needs a new core surface | source inventory | `src/govkb/core/contracts.py`, `src/govkb/commands/validate.py`, `src/govkb/commands/candidates.py`, `src/govkb/core/kb_bootstrap.py` | Add a new focused strict validation module and keep base contract parsing backward-compatible. |

## Data And Fixtures

The PoC uses existing temp-dir `unittest` fixtures only. No raw assistant transcripts, real `$CODEX_HOME`, user-home files, or external services are required.

Candidate implementation tests should add synthetic temp projects with:

- strict-valid approved capability package
- missing required package files
- placeholder memory
- missing repo path references
- forbidden credential path patterns
- `tools/scripts/` without `tools/README.md`
- ready candidate with and without approval metadata

## Rerun Command

Working dir: `/Users/vasilevevgeny/code/govkb`

```bash
docs/governed-skill-knowledge-framework/features/governed-skill-quality-gates/regenerate-poc-data.sh
```

## Risks And Blockers

- System `/usr/bin/python3` is Python 3.9.6 in this environment and lacks `tomllib`; use the bundled Python 3.12 path above for verification.
- Full `unittest discover` has unrelated existing failures in memory-review and install-cron tests; targeted tests listed here pass.
- Approval metadata shape is not yet represented in contracts or candidates and must be added conservatively.

