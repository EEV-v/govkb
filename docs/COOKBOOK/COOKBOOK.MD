# GovKB Feature Development Cookbook

Complete workflow from business requirements to release artifacts for GovKB work.

This cookbook is adapted for the `govkb` repository. It preserves the source lifecycle while using GovKB's actual documentation structure, Python source layout, CLI command surface, and `unittest` test stack.

## Canonical Paths

| Item | Path |
|------|------|
| Cookbook prompts | `docs/COOKBOOK/` |
| Product docs | `docs/governed-skill-knowledge-framework/` |
| Feature folder | `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/` |
| Python package | `src/govkb/` |
| Development import shim | `govkb/__init__.py` |
| Tests | `tests/` |

Use `<FeatureSlug>` for the kebab-case feature folder and `<FeatureName>` for the human-readable title.

## Quick Reference

| Phase | Prompt | Output | Gate |
|-------|--------|--------|------|
| Pre | `PROJECT_ADOPTION_PROMPT.MD` | Adapted cookbook package | Only when porting this cookbook |
| 0 | Manual input | `business.md` | Scope and acceptance criteria are explicit |
| 1 | `CONTEXT_PROMPT.md` | `context.md` | Existing patterns and commands are grounded in repo evidence |
| 2 | `USE_CASES_FOCUSED_PROMPT.MD` | `use-cases.md` | 5-9 traceable scenarios, at least one smoke scenario |
| 3 | `POC_PROMPT.MD` | `requirements-catalog.md`, `poc-plan.md`, `poc-output.md`, rerun script | Assertions are rerunnable |
| 4 | `IMPL_PLAN_PROMPT.MD` | `implementation-plan.md` | Reuse-first plan with rollback and tests |
| 5 | `IMPL_PLAN_REVIEW_PROMPT.MD` | `review.md` | `Ready for Implementation: Yes` |
| 6 | `TEST_SCAFFOLD_PROMPT.MD` | Python test scaffold files | Files import and are runnable/skippable under unittest |
| 7 | `IMPLEMENT_PROMPT.MD` | Production code and tests | Local verification passes |
| 8 | `POC_PARITY_REVIEW_PROMPT.MD` | `poc-parity-review.md` | `Ready for Merge: Yes` |
| 9 | Manual | PR, merge, rollout | Review and verification evidence attached |
| 10a | `STAKEHOLDER-PRESENTATION-TEMPLATE.MD` | `presentation.md` | Business-readable summary |
| 10b | `RELEASE-NOTES-TEMPLATE.MD` | `release-notes.md` | User impact and verification recorded |
| 10c | `SIGN-OFF-TEMPLATE.MD` | `sign-off.md` | Sign-off request is concise |
| 11 | `ESTIMATE_PROMPT.MD` | `estimates.md` | Optional after implementation planning |

## Setup

```bash
cd /home/ev/code/govkb
FEATURE="your-feature-slug"
mkdir -p "docs/governed-skill-knowledge-framework/features/${FEATURE}"
```

Create or place `business.md` under:

```text
docs/governed-skill-knowledge-framework/features/<FeatureSlug>/business.md
```

If `spec-handoff.md`, `decision-log.md`, or `open-questions.md` already exist in the feature folder, treat them as upstream inputs for every engineering phase.

## GovKB Evidence Rules

- Use repo evidence first: `README.md`, `pyproject.toml`, `src/govkb/**`, `tests/**`, and existing docs under `docs/governed-skill-knowledge-framework/`.
- GovKB is a Python CLI/library project. Do not introduce framework assumptions from another stack unless the feature adds that stack.
- For tests, prefer existing patterns: `unittest.TestCase`, `tempfile.TemporaryDirectory`, `pathlib.Path`, `argparse.Namespace`, `unittest.mock.patch`, and direct calls into command functions.
- Keep raw session transcript content out of repo artifacts. If a feature needs session examples, use sanitized fixtures or synthetic JSONL snippets.
- If a feature touches assistant-local output, use disposable `CODEX_HOME` directories in tests.

## Core Commands

Run commands from `/home/ev/code/govkb` unless another working directory is explicitly stated.

```bash
python3 -m unittest discover -s tests -v
python3 -m govkb.cli --help
PYTHONPATH=src python3 -m govkb.cli --help
PYTHONPATH=src python3 -m govkb.cli validate <project-root>
PYTHONPATH=src python3 -m govkb.cli apply codex --project-root <project-root> --codex-home <temp-codex-home> --preview
```

Use `PYTHONPATH=src` when validating source-checkout command examples that must bypass the repo-root import shim.

## Cross-Project Adoption

If porting this cookbook again, run:

```text
@PROJECT_ADOPTION_PROMPT.MD
SourceProjectName: <name>
TargetProjectName: <name>
SourceCookbookPath: <path>
TargetProjectRoot: <path>
```

The adoption output must live under `docs/COOKBOOK/` and include `adoption-context.md`, `structure-map.md`, and `adoption-validation.md`.

## Phase 1-5: Planning And PoC

### Phase 1: Context

```text
@CONTEXT_PROMPT.md
FeatureSlug: <slug>
FeatureName: <name>
<attach business.md>
```

Output: `context.md`

Gate: existing code, docs, commands, risks, and open questions are evidence-backed.

### Phase 2: Use Cases

```text
@USE_CASES_FOCUSED_PROMPT.MD
FeatureSlug: <slug>
FeatureType: <CLI | Adapter | KnowledgeModel | Automation | VSCodeExtension | DocsWorkflow>
<attach business.md, context.md>
```

Output: `use-cases.md`

Gate: 5-9 scenarios, at least one `@smoke`, and traceability to requirements.

### Phase 3: PoC Package

```text
@POC_PROMPT.MD
FeatureSlug: <slug>
PocMode: <baseline-vs-candidate | algorithm-comparison | parity-vs-current | fixture-validation>
<attach business.md, context.md, use-cases.md>
<attach relevant source files, fixtures, or sanitized sample data>
```

Outputs:

- `requirements-catalog.md`
- `poc-plan.md`
- `poc-output.md`
- `regenerate-poc-data.sh` when rerunnable evidence needs a script
- optional sanitized evidence artifacts

Gate: each requirement has at least one executable or inspectable assertion.

### Phase 4: Implementation Plan

```text
@IMPL_PLAN_PROMPT.MD
FeatureSlug: <slug>
<attach business.md, context.md, use-cases.md>
<attach requirements-catalog.md, poc-plan.md, poc-output.md>
CodebaseContext: govkb Python CLI/library, src-layout package, unittest tests
```

Output: `implementation-plan.md`

Gate: existing-code inventory is complete, new files are justified, phases have verification and rollback.

### Phase 5: Review

```text
@IMPL_PLAN_REVIEW_PROMPT.MD
FeatureSlug: <slug>
<attach implementation-plan.md, use-cases.md, requirements-catalog.md, poc-plan.md, poc-output.md>
<attach relevant source files>
```

Output: `review.md`

Gate: `Ready for Implementation: Yes`. If the answer is `No`, revise the plan and rerun review.

## Phase 6-8: Build And Parity

### Phase 6: Test Scaffolds

```text
@TEST_SCAFFOLD_PROMPT.MD
FeatureSlug: <slug>
FeatureName: <name>
<paste use-cases.md>
```

Outputs:

- `tests/test_<feature_slug>_use_cases.py`
- `tests/test_<feature_slug>_smoke.py`
- `tests/<feature_slug>_test_helper.py`

Verify:

```bash
python3 -m unittest tests.test_<feature_slug>_use_cases -v
python3 -m unittest tests.test_<feature_slug>_smoke -v
```

### Phase 7: Implement

```text
@IMPLEMENT_PROMPT.MD
FeatureSlug: <slug>
Phase: <0 | 1 | 2 | 3 | 4 | all>
<attach all planning and PoC documents>
```

| Phase | Focus | Verify |
|-------|-------|--------|
| 0 | Package shape, contracts, CLI args, docs | `python3 -m govkb.cli --help` |
| 1 | Core data model and parsing | targeted `python3 -m unittest tests.test_<module> -v` |
| 2 | Command behavior and adapters | targeted command tests with temp dirs |
| 3 | Memory-review/candidate flows | focused tests plus sanitized fixtures |
| 4 | Optional UI or packaging layer | target-specific tests plus core suite |

Required final verification:

```bash
python3 -m unittest discover -s tests -v
```

If the feature changes CLI commands, also run the relevant `PYTHONPATH=src python3 -m govkb.cli ...` command in preview/dry-run mode when possible.

### Phase 8: PoC Parity Review

```text
@POC_PARITY_REVIEW_PROMPT.MD
FeatureSlug: <slug>
<attach requirements-catalog.md, poc-plan.md, poc-output.md>
<attach implementation-plan.md, review.md>
<attach implementation summaries, test results, and refreshed PoC outputs>
```

Output: `poc-parity-review.md`

Gate: `Ready for Merge: Yes`.

## Phase 9: PR And Rollout

Use a PR summary shaped like:

```markdown
## <FeatureName>
Documents: business.md, use-cases.md, requirements-catalog.md, poc-output.md, implementation-plan.md, poc-parity-review.md
Changes: <by phase>
Use cases: UC-1 [x], UC-2 [x]
PoC parity: matched / exceptions approved
Testing: `python3 -m unittest discover -s tests -v`
Rollback: <specific revert or disable path>
```

For GovKB features, rollout usually means merging repo code/docs, then applying or validating a disposable target project only when the feature affects materialized assistant output.

## Phase 10: Finalization

### Stakeholder Presentation

```text
@STAKEHOLDER-PRESENTATION-TEMPLATE.MD
FeatureSlug: <slug>
<attach implementation-plan.md, use-cases.md, poc-output.md, poc-parity-review.md>
```

### Release Notes

```text
@RELEASE-NOTES-TEMPLATE.MD
FeatureSlug: <slug>
ReleaseDate: <YYYY-MM-DD>
<attach use-cases.md, presentation.md>
```

### Sign-off Request

```text
@SIGN-OFF-TEMPLATE.MD
<paste release-notes.md>
```

## Folder Shape

```text
docs/governed-skill-knowledge-framework/features/<FeatureSlug>/
├── business.md
├── business-context.md
├── context.md
├── use-cases.md
├── requirements-catalog.md
├── poc-plan.md
├── poc-output.md
├── regenerate-poc-data.sh
├── implementation-plan.md
├── review.md
├── poc-parity-review.md
├── presentation.md
├── release-notes.md
└── sign-off.md

tests/
├── test_<feature_slug>_use_cases.py
├── test_<feature_slug>_smoke.py
└── <feature_slug>_test_helper.py
```

## Common Failure Modes

| Problem | Fix |
|---------|-----|
| Feature folder uses a title instead of a slug | Rename to kebab-case and update references |
| Tests depend on real user home state | Move to `tempfile.TemporaryDirectory` and explicit `codex_home` |
| CLI examples omit working directory | Add cwd and command exactly |
| Prompt references unknown framework helpers | Replace with verified `unittest`/stdlib or mark TODO with owner |
| PoC uses raw session transcript | Replace with sanitized fixture or synthetic sample |

## Done Criteria

- All phase artifacts are in the canonical feature folder.
- Tests follow existing GovKB patterns.
- Commands include working directory and prerequisites.
- No source-project paths, frameworks, or tracker links remain.
- Final verification command and result are recorded.
