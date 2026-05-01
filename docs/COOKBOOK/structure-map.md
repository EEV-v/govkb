# GovKB Cookbook Structure Map

Last updated: 2026-04-25

## Prompt Mapping

| Source Prompt | Target Prompt | Changes | Reason | Evidence |
|---|---|---|---|---|
| `COOKBOOK.MD` | `docs/COOKBOOK/COOKBOOK.MD` | Replaced feature path, setup, test stack, commands, and rollout guidance. | GovKB uses Python CLI/library docs, not the source project structure. | `README.md`, `docs/README.md`, `pyproject.toml`, `tests/`. |
| `CONTEXT_PROMPT.md` | `docs/COOKBOOK/CONTEXT_PROMPT.md` | Added GovKB instruction, docs, code, and command discovery requirements. | Context must ground planning in actual repo modules. | `src/govkb/**`, `docs/governed-skill-knowledge-framework/**`. |
| `USE_CASES_FOCUSED_PROMPT.MD` | `docs/COOKBOOK/USE_CASES_FOCUSED_PROMPT.MD` | Adapted feature types and test notes to GovKB CLI/adapter/docs workflows. | Use cases should feed Python tests and governed package behavior. | `docs/governed-skill-knowledge-framework/business.md`. |
| `POC_PROMPT.MD` | `docs/COOKBOOK/POC_PROMPT.MD` | Replaced DB/bootstrap guidance with sanitized fixtures, temp dirs, and rerunnable Python evidence. | GovKB PoC evidence is usually filesystem, CLI, adapter, and report behavior. | `tests/test_candidates.py`, `tests/test_memory_review.py`. |
| `IMPL_PLAN_PROMPT.MD` | `docs/COOKBOOK/IMPL_PLAN_PROMPT.MD` | Reframed inventories around `src/govkb`, commands, adapters, and `unittest`. | Implementation plans need reusable Python module boundaries. | `src/govkb/cli.py`, `src/govkb/core/**`. |
| `IMPL_PLAN_REVIEW_PROMPT.MD` | `docs/COOKBOOK/IMPL_PLAN_REVIEW_PROMPT.MD` | Added GovKB-specific review gates for CLI contract, governance, temp dirs, and raw transcript safety. | Pre-implementation review must catch governance and command risks. | `business.md`, `mvp-plus-test-plan.md`. |
| `TEST_SCAFFOLD_PROMPT.MD` | `docs/COOKBOOK/TEST_SCAFFOLD_PROMPT.MD` | Replaced C# xUnit outputs with three Python `unittest` files. | GovKB's real test stack is Python stdlib `unittest`. | `tests/test_apply.py`, `tests/test_install.py`, `tests/test_init_kb.py`. |
| `IMPLEMENT_PROMPT.MD` | `docs/COOKBOOK/IMPLEMENT_PROMPT.MD` | Replaced build/test phases with Python core, command, adapter, workflow, and optional UI phases. | Implementation must follow current package boundaries. | `src/govkb/commands/**`, `src/govkb/adapters/**`. |
| `POC_PARITY_REVIEW_PROMPT.MD` | `docs/COOKBOOK/POC_PARITY_REVIEW_PROMPT.MD` | Added parity checks for tests, commands, governed source, and transcript safety. | Merge gate must prove PoC assertions survived implementation. | Existing docs and tests. |
| `STAKEHOLDER-PRESENTATION-TEMPLATE.MD` | `docs/COOKBOOK/STAKEHOLDER-PRESENTATION-TEMPLATE.MD` | Replaced source-specific rollout language with GovKB presentation sections. | Final artifact should be business-readable and repo-local. | Existing feature review materials. |
| `RELEASE-NOTES-TEMPLATE.MD` | `docs/COOKBOOK/RELEASE-NOTES-TEMPLATE.MD` | Removed external tracker URLs; added generic tracking and GovKB verification table. | No target tracker integration is defined in this repo. | No tracker docs found in GovKB. |
| `SIGN-OFF-TEMPLATE.MD` | `docs/COOKBOOK/SIGN-OFF-TEMPLATE.MD` | Replaced team-specific sign-off with generic GovKB sign-off request. | Avoid stale ownership and external assumptions. | `README.md`, feature docs. |
| `ESTIMATE_PROMPT.MD` | `docs/COOKBOOK/ESTIMATE_PROMPT.MD` | Adapted optional estimate prompt to GovKB phases. | Source folder contained this prompt and it should stay usable. | `implementation-plan.md` phase structure. |
| `PROJECT_ADOPTION_PROMPT.MD` | `docs/COOKBOOK/PROJECT_ADOPTION_PROMPT.MD` | Copied unchanged because it is generic and contains no source-project paths. | Future cookbook ports can reuse the adoption workflow. | Source prompt content. |

## Artifact Mapping

| Source Artifact | Target Artifact | Path Pattern | Phase |
|---|---|---|---|
| `business.md` | `business.md` | `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/business.md` | 0 |
| `context.md` | `context.md` | `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/context.md` | 1 |
| `use-cases.md` | `use-cases.md` | `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/use-cases.md` | 2 |
| `requirements-catalog.md` | `requirements-catalog.md` | `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/requirements-catalog.md` | 3 |
| `poc-plan.md` | `poc-plan.md` | `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/poc-plan.md` | 3 |
| `poc-output.md` | `poc-output.md` | `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/poc-output.md` | 3 |
| rerun script | `regenerate-poc-data.sh` | `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/regenerate-poc-data.sh` | 3 |
| `implementation-plan.md` | `implementation-plan.md` | `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/implementation-plan.md` | 4 |
| `review.md` | `review.md` | `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/review.md` | 5 |
| use-case tests | Python use-case tests | `tests/test_<feature_slug>_use_cases.py` | 6 |
| smoke/E2E tests | Python smoke tests | `tests/test_<feature_slug>_smoke.py` | 6 |
| test helper | Python helper scaffold | `tests/<feature_slug>_test_helper.py` | 6 |
| `poc-parity-review.md` | `poc-parity-review.md` | `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/poc-parity-review.md` | 8 |
| `presentation.md` | `presentation.md` | `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/presentation.md` | 10a |
| `release-notes.md` | `release-notes.md` | `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/release-notes.md` | 10b |
| `sign-off.md` | `sign-off.md` | `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/sign-off.md` | 10c |
| `estimates.md` | `estimates.md` | `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/estimates.md` | Optional |

## Command Mapping

| Task | Source Command | Target Command | Working Dir | Preconditions |
|---|---|---|---|---|
| Full test suite | Source project test command | `python3 -m unittest discover -s tests -v` | `/home/ev/code/govkb` | Python 3.11+ available. |
| CLI help | Source project build/help command | `python3 -m govkb.cli --help` | `/home/ev/code/govkb` | Run from repo root. |
| Src-layout CLI help | N/A | `PYTHONPATH=src python3 -m govkb.cli --help` | `/home/ev/code/govkb` | Run from repo root. |
| Validate governed package | Source project validation command | `PYTHONPATH=src python3 -m govkb.cli validate <project-root>` | `/home/ev/code/govkb` | `<project-root>/.governed` exists. |
| Preview materialization | Source project integration verification | `PYTHONPATH=src python3 -m govkb.cli apply codex --project-root <project-root> --codex-home <temp-codex-home> --preview` | `/home/ev/code/govkb` | Initialized target project and temp Codex home. |
| Memory-review dry run | Source project end-to-end evidence command | `CODEX_HOME=<temp-codex-home> PYTHONPATH=src python3 -m govkb.cli review-memory --assistant codex --project-root <project-root> --dry-run --max-sessions 1 --classifier-codex-home ~/.codex --codex-model gpt-5.4-mini --codex-reasoning low --codex-timeout 180` | `/home/ev/code/govkb` | Nested classifier auth/config available. |

## Test Scaffold Mapping

| Source Element | Target Equivalent | Target File | Notes |
|---|---|---|---|
| Full scenario coverage tests | Python `unittest.TestCase`, one method per scenario or outline row | `tests/test_<feature_slug>_use_cases.py` | Preserve BDD step text through `record_step(...)`; scaffold-only tests may call `self.skipTest`. |
| Happy path E2E/manual exploration tests | Python smoke test with `tempfile.TemporaryDirectory` and disposable project/Codex roots | `tests/test_<feature_slug>_smoke.py` | Use one or two `@smoke` scenarios. |
| Helper API surface | Feature-specific Python helper with setup, seeding, execution, assertions, cleanup groups | `tests/<feature_slug>_test_helper.py` | No custom repo helper exists, so helper is generated per feature. |
| BDD step logger | `record_step(...)` list on feature helper | `tests/<feature_slug>_test_helper.py` | Target stack has no custom BDD logger; this preserves trace text without inventing framework dependencies. |
| Fixture collection attributes | Stdlib temp dirs, direct command function calls, `unittest.mock.patch` where needed | generated tests | Matches existing tests. |
| Smoke filtering | Run exact smoke module, e.g. `python3 -m unittest tests.test_<feature_slug>_smoke -v` | command | `unittest` has no marker system in this repo. |

