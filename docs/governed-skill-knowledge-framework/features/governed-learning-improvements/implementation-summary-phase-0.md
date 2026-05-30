# Governed Learning Improvements - Phase 0 Implementation Summary

Date: 2026-05-29

## Scope Implemented

Phase 0 adds a read-only proposal report for staged governed learning artifacts:

- `govkb proposals report [project_root]`
- `govkb proposals report [project_root] --json`

The report groups related staged proposals, keeps unrelated proposals separate, surfaces advisory quality warnings, and recommends the next review action per group.

Implemented warning coverage:

- Low-confidence proposals.
- Weak or missing verification evidence.
- Duplicate output paths.
- Script and wrapper proposals missing draft output behavior.
- Mutating scripts without visible `--dry-run` or `--preview` support.
- Script and wrapper proposals without focused syntax/help/unit verification evidence.

Implemented recommended actions:

- `merge-first` for related proposals that should be reconciled before promotion.
- `reject-duplicate` for related proposals targeting the same single output path.
- `inspect-safety` for script or wrapper proposals with safety warnings.
- `manual-review` for standalone proposals without stronger automated guidance.

## Consumer Check

The command was run against Clearing as a consumer project:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli proposals report /home/ev/code/Clearing --json
```

Observed result:

- Proposals: 10
- Groups: 9
- Warnings: 9
- Actions: 2 `inspect-safety`, 6 `manual-review`, 1 `merge-first`

The report grouped the two DVCA payout E2E runbook proposals together and left unrelated golden-lineage, mirror-stale-ref, split-source, and project-steward proposals separate.

## Verification

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest tests.test_governed_learning_improvements_use_cases tests.test_governed_learning_improvements_smoke tests.test_proposals -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -v
git diff --check
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli proposals report --help
```

Result:

- Focused tests passed.
- Full suite passed: 192 tests, 33 skipped scaffold tests.
- Diff whitespace check passed.
- CLI help resolved for the new command.

## Deferred

Phase 0 does not implement the later health report, maturity scoring, doctor command, self-noise filtering, or VS Code UI changes. Those remain documented future phases.
