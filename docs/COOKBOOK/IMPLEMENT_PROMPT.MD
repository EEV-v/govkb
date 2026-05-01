ROLE
Senior engineer implementing a GovKB feature from approved artifacts.

GOAL
Implement production code, tests, and documentation phase by phase from `implementation-plan.md`, preserving GovKB's repo conventions and verification gates.

DOCUMENT CHAIN
- Required inputs:
  - `business.md`
  - `context.md`
  - `use-cases.md`
  - `requirements-catalog.md`
  - `poc-plan.md`
  - `poc-output.md`
  - `implementation-plan.md`
  - `review.md` with `Ready for Implementation: Yes`
- Optional inputs:
  - test scaffolds from `TEST_SCAFFOLD_PROMPT.MD`
  - `spec-handoff.md`, `decision-log.md`, `open-questions.md`
- Outputs:
  - production code under `src/govkb/**` or other planned paths
  - tests under `tests/**`
  - updated docs in the feature folder
- Next:
  - `POC_PARITY_REVIEW_PROMPT.MD`

INPUT
- FeatureSlug: <kebab-case folder name>
- Phase: <0 | 1 | 2 | 3 | 4 | all>

PRE-FLIGHT
- Read `review.md`. Stop if `Ready for Implementation` is not `Yes`.
- Check `git status --short` and avoid reverting unrelated user changes.
- Re-read touched files before editing.
- Keep edits scoped to the approved plan.

PHASE GUIDANCE

## Phase 0 - Shape And Contracts

Typical work:
- CLI argument shape, help text, docs, manifests, templates, or file layout.
- Validation scaffolding that later phases use.

Verify examples:

```bash
cd /home/ev/code/govkb
python3 -m govkb.cli --help
PYTHONPATH=src python3 -m govkb.cli --help
```

## Phase 1 - Core Behavior

Typical work:
- Pure helpers under `src/govkb/core/`.
- Contract parsing, ID handling, project package logic, template generation, candidate facts, or install-state behavior.

Test rules:
- Prefer focused unit tests.
- Use temp dirs for filesystem behavior.
- Avoid local user-home state.

## Phase 2 - Commands And Adapters

Typical work:
- `src/govkb/commands/**`
- `src/govkb/adapters/**`
- CLI orchestration and preview/dry-run behavior.

Test rules:
- Existing command tests usually call `run_*` functions with `argparse.Namespace`.
- Use `redirect_stdout` when output is part of behavior.
- Patch subprocess calls when testing command construction.

## Phase 3 - Workflow Behavior

Typical work:
- Memory-review, candidate lifecycle, promotion, install/apply flows, report generation, or cross-module integration.

Test rules:
- Use disposable project roots and `codex_home` paths.
- Keep raw transcript-like content out of repo fixtures.
- Assert install state, report paths, candidate status, or materialized skill files as appropriate.

## Phase 4 - Optional UI, Packaging, Or Docs

Typical work:
- Extension/package surfaces, public docs, release material, or specialized integration.

Test rules:
- Keep core suite green.
- Add target-specific verification only when the feature introduces that stack.

IMPLEMENTATION RULES
- Follow existing imports and module boundaries.
- Add comments only for non-obvious logic.
- Do not introduce dependencies without an explicit plan item.
- Do not mutate `$HOME` or the real user Codex home in tests.
- Keep `.governed/**` as canonical project source and assistant-local files as derived.
- Preserve backward compatibility for existing `.governed` fixtures unless the plan explicitly migrates them.

REQUIRED STATUS OUTPUT
After each implemented phase, update or create an implementation summary in the feature folder:

```markdown
# <FeatureName> - Implementation Summary Phase <N>

## Completed

## Files Changed

## Verification

## Deviations From Plan

## Next Phase
```

FINAL VERIFICATION

Run from `/home/ev/code/govkb`:

```bash
python3 -m unittest discover -s tests -v
```

Also run any feature-specific CLI preview/dry-run commands named in the plan.

FINAL RESPONSE REQUIREMENTS
- Summarize changed files by area.
- Report verification commands and results.
- Report any skipped commands with the reason.
- Name remaining blockers or TODOs.

END
