# VS Code Learning Discovery and Progress - Implementation Summary Phase 6

## Completed

- Fixed promotion review digests that mixed newly learned updates with already accepted but not-yet-applied updates.
- Stored promoted additions in promotion lifecycle metadata so accepted additions remain identifiable even after duplicate or superseded worktrees are archived.
- Split promotion digests into `New Additions To Review` and `Previously Accepted Carry-Forward`.
- Updated the current Clearing promotion digest for `20260512T202220000876Z` so the active review is readable immediately.

## Files Changed

- `src/govkb/adapters/codex/promote.py`
- `src/govkb/core/promotion_lifecycle.py`
- `tests/test_promote.py`

## Verification

- `PYTHONPATH=src /Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_promote tests.test_promotions -v`
