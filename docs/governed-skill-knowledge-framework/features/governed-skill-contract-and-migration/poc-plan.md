# Governed Skill Contract And Migration - PoC Plan

## Mode

Baseline-vs-candidate.

## Evidence Strategy

Use current GovKB source and local Clearing package state to prove the gap, then define deterministic assertions for the target behavior. No raw session transcripts or user-home assistant state are required for implementation tests; conversion tests will use synthetic local skills in temp directories.

## Assertions

| Assertion | Method | Command/File | Expected Result |
|---|---|---|---|
| Current CLI has no skill conversion command | CLI help inspection | `python3 -m govkb.cli --help` | No `convert` command appears today |
| Current validation passes Clearing despite weak capability quality | CLI validation | `python3 -m govkb.cli validate /home/ev/code/Clearing` | Validation passes, proving strict quality checks are absent |
| Clearing weak package contains invalid project-relative build commands | File inspection | `/home/ev/code/Clearing/.governed/capabilities/local-stack-workflow/references/long-term-memory.md` | Memory contains `src/Etna.Clearing...` commands that do not exist from Clearing root |
| Current materialization already copies capability package trees | Source inspection | `src/govkb/adapters/codex/materialize.py` | `_copy_tree` can preserve `tools/` once governed packages contain it |
| Existing tests already support temp project and temp Codex home workflows | Test inspection | `tests/test_apply.py`, `tests/test_candidates.py` | Conversion and strict validation can use existing test style |
| Target contract is explicit enough to implement | Contract artifact | `poc-artifacts/governed-skill-package-contract.md` | Defines required files, optional tools, naming, memory, safety, and conversion rules |

## Data And Fixtures

Planned implementation fixtures:

- synthetic Codex skill with `SKILL.md`
- synthetic skill memory under `references/long-term-memory.md`
- synthetic safe script under `scripts/` or `tools/scripts/`
- synthetic unsafe skill containing token-like text and local paths
- temp governed project from `run_init`
- temp `CODEX_HOME`

## Rerun Command

From `/home/ev/code/govkb`:

```bash
python3 -m unittest discover -s tests -v
python3 -m govkb.cli --help
python3 -m govkb.cli validate /home/ev/code/Clearing
```

## Risks And Blockers

- The current Clearing project root is not a Git repo, so repo-native promotion evidence is weaker for that project.
- Strict validation could break existing packages if made default immediately.
- Some legacy skills may contain assistant-specific presentation that should stay adapter-local rather than governed.
- Conversion from freeform `SKILL.md` cannot guarantee perfect durable memory quality without reviewer inspection.
