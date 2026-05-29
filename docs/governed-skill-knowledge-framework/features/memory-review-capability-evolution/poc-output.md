# Memory Review Capability Evolution - PoC Output

Last updated: 2026-05-28

## Summary

The baseline confirms that GovKB has the right nearby pieces but not the capability-evolution lane itself.

Current behavior already supports:

- Bounded Codex memory review with model and reasoning controls.
- Memory candidate validation, report generation, progress events, and semantic new-capability candidates.
- Dedicated new-capability candidate storage and JSON summaries.
- Strict governed skill validation for tool folders, credential-like content, and mutating script safety.

Missing behavior:

- No `govkb proposals` command exists.
- No production proposal model or storage writer exists.
- The classifier schema has no `capability_evolution_proposals` array.
- The memory-review report has no distinct proposal section.
- There is no approved proposal apply path.

## Assertion Results

| Assertion | Result | Evidence | Notes |
|---|---|---|---|
| A1 Current CLI has no `govkb proposals` command. | Passed | `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli --help` exited 0. | Help lists `init`, `install`, `validate`, `remediate`, `init-kb`, `apply`, `status`, `capabilities`, `review-memory`, `candidates`, `convert`, `promote`, `promotions`, and `create`; no `proposals`. |
| A2 Current memory-review schema has memory candidates and one semantic candidate, but no proposal array. | Passed | Source inspection of `schema_text()` in `src/govkb/adapters/codex/bin/codex-memory-review`. | Required keys are `session_id`, `candidates`, and `semantic_candidate`. |
| A3 Current memory-review report has no capability-evolution proposal section. | Passed | Source inspection of `write_report()` plus targeted report-contract test. | Existing report sections cover memory and candidate flows only. |
| A4 Current `govkb candidates` command is scoped to new capability candidates. | Passed | `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli candidates --help` exited 0. | Candidate actions are `stage`, `list`, and `auto-create-ready`. |
| A5 Strict validation and governed tool safety checks already exist for package-owned tools. | Passed | `validate --help` exited 0; strict quality-gate use-case tests passed. | Reuse strict validation after proposal application. |
| A6 Memory-review wrapper already supports model/reasoning controls for higher-reasoning manual runs. | Passed | `review-memory --help` exited 0; `tests.test_review_memory_command` passed in the targeted baseline. | No new proposal-discovery flag is required by approved decisions. |
| A7 There is no proposal storage/model implementation yet. | Passed | `rg -n "review-proposals|capability_evolution|proposals|proposal_type" src tests` found no production proposal lane. | Feature docs mention the planned lane; code does not implement it yet. |
| A8 Existing candidate JSON and strict validation tests are a clean baseline for nearby behavior. | Passed | Targeted unittest command ran 15 tests in 0.070s and exited 0. | Covered review-memory wrapper, candidate JSON, and strict skill gates. |

## Command Results

Working dir for all commands: `/home/ev/code/govkb`

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli --help
exit 0; no proposals command listed
```

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli review-memory --help
exit 0; includes --codex-model, --codex-reasoning, --inventory-json, --progress-jsonl, --lookback-days, --max-sessions
```

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli candidates --help
exit 0; actions are stage, list, auto-create-ready
```

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli validate --help
exit 0; includes --strict and --json
```

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest tests.test_review_memory_command tests.test_candidates_json tests.test_governed_skill_quality_gates_use_cases -v
Ran 15 tests; OK
```

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest tests.test_memory_review.MemoryReviewHelperTests.test_packaged_report_includes_review_contract -v
Ran 1 test; OK
```

## Outliers

- The targeted quality-gate tests print temp project scaffold messages to stdout. This is existing test behavior and does not affect pass/fail status.
- Source search finds proposal wording in feature docs only, not production modules or tests.

## Open Gaps

- Add proposal schema and prompt language to the Codex memory-review adapter.
- Add proposal validation with target capability, type, output path, safety class, evidence summary, and sensitive-content checks.
- Add repo-owned proposal staging under `.governed/review-proposals/<proposal-id>/`.
- Add report and progress counts for capability-evolution proposals.
- Add `govkb proposals list`, `show`, and `apply`.
- Add tests that prove cron stages only and approved apply writes only bounded governed package files.

## Recommendation

Proceed to `implementation-plan.md`.

The first implementation should split cleanly into:

1. Proposal data model and storage.
2. Memory-review classifier/report integration.
3. `govkb proposals` list/show/apply command behavior.
4. Tests, docs, and validation wiring.
