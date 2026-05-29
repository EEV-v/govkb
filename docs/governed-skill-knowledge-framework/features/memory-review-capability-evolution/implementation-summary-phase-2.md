# Memory Review Capability Evolution - Implementation Summary Phase 2

## Completed

- Added public `govkb proposals list`, `govkb proposals show`, and `govkb proposals apply`.
- Added JSON output for `list` and `show`.
- Kept staging as an internal core operation, not a public CLI action.

## Files Changed

- `src/govkb/cli.py`
- `src/govkb/commands/proposals.py`
- `tests/test_proposals.py`
- `README.md`

## Verification

- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli proposals --help` passed.
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m govkb.cli proposals list --json .` passed.
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest tests.test_proposals -v` passed.

## Deviations From Plan

- Added JSON output immediately because the review noted it would be useful for future extension consumption.

## Next Phase

- Phase 3: memory-review classifier, report, progress, and staging integration.
