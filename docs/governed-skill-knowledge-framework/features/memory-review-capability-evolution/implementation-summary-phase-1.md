# Memory Review Capability Evolution - Implementation Summary Phase 1

## Completed

- Implemented proposal staging under `.governed/review-proposals/<proposal-id>/`.
- Implemented approval-gated proposal apply with bounded output paths under the target capability.
- Added safety checks for unsupported types, unsafe paths, sensitive content, raw-transcript indicators, mutating script behavior, and overwrite refusal.
- Reused strict validation against the target governed capability after apply.

## Files Changed

- `src/govkb/core/proposals.py`
- `tests/test_proposals.py`
- `tests/memory_review_capability_evolution_test_helper.py`

## Verification

- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest tests.test_proposals -v` passed.

## Deviations From Plan

- Strict validation is run for the target capability package after apply, rather than the whole project, to avoid unrelated strict findings blocking a bounded proposal apply.

## Next Phase

- Phase 2: public proposal command surface.
