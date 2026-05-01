# Governed Skill Contract And Migration - PoC Output

## Summary

The baseline confirms the feature is needed. GovKB can validate and materialize Clearing today, but validation does not catch weak capability naming, placeholder-like memory, invalid command paths, or local credential-file references in candidate facts. The CLI also has no existing `convert skill` command.

The implementation should add strict governed-skill validation, gate candidate activation through that validation, and add preview-first existing-skill conversion.

## Assertion Results

| Assertion | Result | Evidence | Notes |
|---|---|---|---|
| Current CLI has no skill conversion command | Passed | `python3 -m govkb.cli --help` inspected during feature planning | Existing commands are init, install, validate, init-kb, apply, status, review-memory, candidates, promote, create |
| Current validation passes Clearing despite weak capability quality | Passed | `python3 -m govkb.cli validate /home/ev/code/Clearing` returned validation passed | Shows current validation is not a strict quality gate |
| Clearing weak package contains invalid project-relative build commands | Passed | `local-stack-workflow` memory contains `dotnet build src/Etna.Clearing.ApiHost/...` while real paths are under `ETNAClearingService/src/...` | Strict validation should catch wrong repo paths |
| Current materialization already copies capability package trees | Passed | `src/govkb/adapters/codex/materialize.py` uses `_copy_tree` for capability package sources | `tools/` can be preserved without a new adapter concept |
| Existing tests support temp project and temp Codex home workflows | Passed | `tests/test_apply.py`, `tests/test_candidates.py` use `tempfile.TemporaryDirectory` and direct command calls | New tests can follow repo patterns |
| Target contract is explicit enough to implement | Passed | `poc-artifacts/governed-skill-package-contract.md` created | Contract covers shape, naming, memory, tooling, validation, and conversion |

## Outliers

- Existing GovKB package worktree is dirty with active extension and JSON CLI work. This feature should avoid depending on those changes except where JSON validation output is explicitly planned.
- The Clearing `.governed` package lives under a workspace that is not itself a Git repository, which limits promotion git status.

## Open Gaps

- Strict validation severity needs an implementation decision: default errors now, or opt-in `--strict` first.
- Migration metadata location needs a final decision: `[migration]` inside `capability.contract.toml` or a separate `migration.toml`.
- The implementation must define whether unsafe converted content is only reported or also preserved in a quarantine artifact.

## Recommendation

Proceed to implementation planning. Start with strict package validation and conversion preview data structures before writing any mutation logic. Gate candidate auto-create with strict validation after strict rules are test-backed.
