# Memory Review Capability Evolution - PoC Plan

Last updated: 2026-05-28

## Mode

baseline-vs-candidate

The PoC proves current GovKB behavior and identifies the missing contracts needed for the candidate capability-evolution lane.

## Evidence Strategy

- Use source inspection under `/home/ev/code/govkb`.
- Use current CLI help for command-surface evidence.
- Use existing tests for memory-review wrapper, candidates JSON, and strict governed skill safety gates.
- Use synthetic/temp-dir test fixtures only; no raw Codex sessions, secrets, customer data, or user-home assistant state are required.
- Treat `.governed/**` as project source of truth and `$CODEX_HOME/**` memory-review output as derived evidence.

## Assertions

| Assertion | Method | Command/File | Expected Result |
|---|---|---|---|
| A1 Current CLI has no `govkb proposals` command. | CLI help | Working dir: `/home/ev/code/govkb`; `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli --help` | Help lists current commands and does not list `proposals`. |
| A2 Current memory-review schema has memory candidates and one semantic candidate, but no proposal array. | Source inspection | `src/govkb/adapters/codex/bin/codex-memory-review`, `schema_text()` | Schema requires `session_id`, `candidates`, and `semantic_candidate`; implementation must add a proposal array. |
| A3 Current memory-review report has no capability-evolution proposal section. | Source inspection and targeted test | `write_report()` in `src/govkb/adapters/codex/bin/codex-memory-review`; `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest tests.test_memory_review.MemoryReviewHelperTests.test_packaged_report_includes_review_contract -v` | Report currently covers applied, staged, candidate stage requests, auto-create, rejected, deferred, and failed rows. |
| A4 Current `govkb candidates` command is scoped to new capability candidates. | CLI help and source inspection | `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli candidates --help`; `src/govkb/commands/candidates.py`; `src/govkb/core/candidates.py` | Candidate actions are `stage`, `list`, and `auto-create-ready`; proposals should not overload this namespace. |
| A5 Strict validation and governed tool safety checks already exist for package-owned tools. | CLI help and tests | `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli validate --help`; `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest tests.test_governed_skill_quality_gates_use_cases -v` | `validate --strict` exists and tests cover credential safety, tool README, and mutating script dry-run/preview expectations. |
| A6 Memory-review wrapper already supports model/reasoning controls for higher-reasoning manual runs. | CLI help and tests | `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli review-memory --help`; `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest tests.test_review_memory_command -v` | Help and wrapper tests include `--codex-model`, `--codex-reasoning`, bounded session controls, inventory, and progress flags. |
| A7 There is no proposal storage/model implementation yet. | Source search | `rg -n "review-proposals|capability_evolution|proposals|proposal_type" src tests` | Matches are absent from production code; implementation needs new core and command modules. |
| A8 Existing candidate JSON and strict validation tests are a clean baseline for nearby behavior. | Targeted tests | `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest tests.test_review_memory_command tests.test_candidates_json tests.test_governed_skill_quality_gates_use_cases -v` | Targeted baseline passes before proposal implementation. |

## Data And Fixtures

Implementation should add only sanitized fixtures:

- Synthetic JSON classifier results with `capability_evolution_proposals`.
- Temp governed projects with `.governed/project.toml` and one or more existing capabilities.
- Proposal folders under temp `.governed/review-proposals/<proposal-id>/`.
- Proposed output files under temp `.governed/capabilities/<capability-id>/`.

No real session transcript, raw prompt, token, credential path, production evidence, customer identifier, or user-home `$CODEX_HOME` fixture is needed.

## Rerun Command

Working dir: `/home/ev/code/govkb`

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli --help
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli review-memory --help
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli candidates --help
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli validate --help
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest tests.test_review_memory_command tests.test_candidates_json tests.test_governed_skill_quality_gates_use_cases -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest tests.test_memory_review.MemoryReviewHelperTests.test_packaged_report_includes_review_contract -v
```

## Risks And Blockers

- Proposal apply will write governed package files; implementation needs path validation before any file write.
- Proposal staging touches repo-owned `.governed/**`; dry-run behavior must be explicit.
- If proposal metadata stores generated code bodies, validators must redact or reject transcript-like and secret-like content before persistence.
- The current memory-review scheduler is a script-like adapter file; care is needed to keep tests importable through the existing `SourceFileLoader` pattern.
- `govkb proposals apply` can run verification commands only after the command contract defines allowed cwd, timeout, and output behavior. The minimum safe slice can print the command and run strict validation first, then expand automated verification later.
