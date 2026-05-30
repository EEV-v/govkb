# Governed Learning Improvements - Phase 0 Implementation Summary

Date: 2026-05-30

## Scope Implemented

Phase 0 adds a read-only proposal report for staged governed learning artifacts:

- `govkb proposals report [project_root]`
- `govkb proposals report [project_root] --json`
- `govkb proposals review [project_root]`
- `govkb proposals review [project_root] --action inspect-safety`
- `govkb proposals review [project_root] --json`

The report groups related staged proposals, keeps unrelated proposals separate, surfaces advisory quality warnings, and recommends the next review action per group. The review command turns the same read-only data into maintainer-facing next steps with concrete `govkb proposals show` and, when appropriate, `govkb proposals apply` commands.

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
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli proposals review /home/ev/code/Clearing --action inspect-safety
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli proposals review /home/ev/code/Clearing --action merge-first
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli proposals review /home/ev/code/Clearing --action manual-review
```

Observed result:

- Proposals: 30
- Groups: 28
- Warnings: 16
- Actions: 4 `inspect-safety`, 2 `merge-first`, 22 `manual-review`, 0 `reject-duplicate`

The report grouped related realtime cashflow production verification proposals and the two DVCA payout E2E runbook proposals while leaving unrelated proposal groups separate.

## Verification

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest tests.test_governed_learning_improvements_use_cases tests.test_governed_learning_improvements_smoke tests.test_proposals -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -v
git diff --check
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli proposals report --help
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli proposals review /home/ev/code/Clearing --action inspect-safety
```

Result:

- Focused tests passed: 12 tests.
- Full suite passed: 194 tests, 33 skipped scaffold tests.
- Diff whitespace check passed.
- CLI help and Clearing consumer review commands resolved.

## Deferred

Phase 0 does not implement the later health report, maturity scoring, doctor command, self-noise filtering, or VS Code UI changes. Those remain documented future phases.
