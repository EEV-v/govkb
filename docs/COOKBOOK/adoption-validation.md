# GovKB Cookbook Adoption Validation

Last updated: 2026-04-25

## Checklist Results

| Gate | Status | Evidence |
|---|---|---|
| All adapted prompts preserve phase order and required deliverables. | PASS | `COOKBOOK.MD` quick reference and each phase prompt preserve the chain from `business.md` to sign-off. |
| `COOKBOOK.MD` references all prompt/template files that exist. | PASS | References `PROJECT_ADOPTION`, `CONTEXT`, `USE_CASES`, `POC`, `IMPL_PLAN`, `IMPL_PLAN_REVIEW`, `TEST_SCAFFOLD`, `IMPLEMENT`, `POC_PARITY_REVIEW`, presentation, release notes, sign-off, and estimate prompt. |
| Every command includes explicit working directory. | PASS | Command tables in `COOKBOOK.MD`, `adoption-context.md`, and `structure-map.md` use `/home/ev/code/govkb`. |
| Every referenced path exists or is marked future feature output. | PASS | Existing roots verified: `docs/governed-skill-knowledge-framework/`, `src/govkb/`, `tests/`, `README.md`, `pyproject.toml`. Feature-specific files are documented as generated outputs. |
| No stale source-project commands, paths, namespaces, or frameworks remain unintentionally. | PASS | Operational prompts/templates scan clean; adoption provenance and mapping files intentionally name the source folder and replaced test framework. |
| `TEST_SCAFFOLD_PROMPT.MD` references only real target fixtures/helpers/utilities verified in repository. | PASS | Uses stdlib `unittest`, `tempfile`, `Path`, `argparse.Namespace`, `redirect_stdout`, and `unittest.mock.patch`; these are visible in current tests. |
| At least one sample dry-run confirms end-to-end document chain consistency. | PASS | See sample dry-run below. |

## Sample Dry-run

Sample input:

```text
FeatureSlug: sample-govkb-feature
FeatureName: Sample GovKB Feature
FeatureType: CLI
```

Expected document chain:

| Phase | Artifact |
|---|---|
| 0 | `docs/governed-skill-knowledge-framework/features/sample-govkb-feature/business.md` |
| 1 | `docs/governed-skill-knowledge-framework/features/sample-govkb-feature/context.md` |
| 2 | `docs/governed-skill-knowledge-framework/features/sample-govkb-feature/use-cases.md` |
| 3 | `docs/governed-skill-knowledge-framework/features/sample-govkb-feature/requirements-catalog.md`, `poc-plan.md`, `poc-output.md`, optional `regenerate-poc-data.sh` |
| 4 | `docs/governed-skill-knowledge-framework/features/sample-govkb-feature/implementation-plan.md` |
| 5 | `docs/governed-skill-knowledge-framework/features/sample-govkb-feature/review.md` |
| 6 | `tests/test_sample_govkb_feature_use_cases.py`, `tests/test_sample_govkb_feature_smoke.py`, `tests/sample_govkb_feature_test_helper.py` |
| 8 | `docs/governed-skill-knowledge-framework/features/sample-govkb-feature/poc-parity-review.md` |
| 10 | `presentation.md`, `release-notes.md`, `sign-off.md` |

The sample path mapping is internally consistent and aligns with existing repo layout.

## Verification Commands

| Command | Working Dir | Result |
|---|---|---|
| `python3 -m govkb.cli --help` | `/home/ev/code/govkb` | Passed during adoption discovery. |
| `PYTHONPATH=src python3 -m govkb.cli --help` | `/home/ev/code/govkb` | Passed during adoption discovery. |
| Source-term scan for stale project/framework references in operational prompts/templates | `/home/ev/code/govkb` | Passed after prompt adaptation. |
| `python3 -m unittest discover -s tests -v` | `/home/ev/code/govkb` | Passed: 64 tests. |

## Residual Risks

| Risk | Impact | Mitigation |
|---|---|---|
| No repo-local chatbot instruction file exists. | Future contributors may expect project-specific rules in a file. | Cookbook records active session instructions and repo conventions; add a repo instruction file later if desired. |
| Generated helper file under `tests/` is new per feature. | Feature authors must implement helper imports carefully. | Scaffold prompt keeps helper in `tests/<feature_slug>_test_helper.py` so `unittest discover -s tests` can import it. |
| Some future features may introduce a non-Python stack, such as a VS Code extension. | Cookbook defaults to Python tests may be incomplete for that stack. | Phase prompts require target-specific tests when a feature introduces another stack, while keeping core suite green. |

## Open TODOs

- TODO(Project owner): Decide whether GovKB should add a repo-level instruction file such as `AGENTS.md` for future assistant runs.
- TODO(Feature owner): For each future feature, fill actual tracker links in `release-notes.md` only if a tracker exists.
