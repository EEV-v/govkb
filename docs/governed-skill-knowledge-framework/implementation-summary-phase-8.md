# Governed Skill Knowledge Framework Implementation Summary: Phase 8

Last updated: 2026-04-23

## Scope delivered

Phase 8 added git hygiene and a promotion digest around the auto-promote flow.

This answers the operational concern from Phase 7: auto-promotion is useful only if the resulting repo changes are visible and easy to review or commit.

## Behavior added

`govkb promote` now captures git status for `.governed` when the project is inside a Git worktree.

Captured fields:

- git root
- `.governed` status before promotion
- `.governed` status after promotion
- human-readable status message

When the project is not inside a Git worktree, promotion still runs and reports:

- `git unavailable: project root is not inside a git worktree`

This matches the current local Clearing workspace shape, where `/home/ev/code/Clearing` is not itself a Git repo root.

## Digest

When promotion has items to report, `govkb promote` now writes:

- timestamped report:
  - `.governed/reports/promotions/<timestamp>-promote-report.md`
- latest digest:
  - `.governed/reports/promotions/latest-promotion-digest.md`

The digest includes:

- mode and trigger
- report path
- promoted and rejected counts
- git status message
- changed `.governed` files
- promoted additions
- rejection reasons

## Files changed

Implementation:

- `/home/ev/code/Clearing/govkb/src/govkb/adapters/codex/promote.py`
- `/home/ev/code/Clearing/govkb/src/govkb/commands/promote.py`

Tests:

- `/home/ev/code/Clearing/govkb/tests/test_promote.py`

## Verification

Automated tests:

- command:
  - `python3 -m unittest discover -s tests -v`
- result:
  - passed
  - tests run: `13`

Covered behavior:

- append-only memory addition is promoted
- non-append memory change is rejected
- promotion report is written
- latest digest is written
- temp Git repo test confirms changed `.governed` files appear in the digest

Runtime checks:

- `python3 -m py_compile /home/ev/.codex/bin/codex-memory-review`
- `python3 -m govkb.cli promote /home/ev/code/Clearing --codex-home /home/ev/.codex --preview`

Current live promote preview result:

- promoted: `0`
- rejected: `0`
- git status: unavailable because `/home/ev/code/Clearing` is not inside a Git worktree
- no pending local governed memory changes need promotion

## Decision

The next useful step is new-capability candidate staging.

Reason:

- governed package materialization is done for all current memory-bearing Clearing skills
- auto-promote now closes the accepted-memory loop back into `.governed`
- git/digest visibility now makes automatic repo changes auditable
- the remaining core product promise is skill growth in number, not only expertise growth inside existing skills

Recommended next slice:

1. Detect repeated unmatched work patterns across memory-review reports or recent sessions.
2. Stage a new governed capability candidate under `.governed/candidates/<id>/`.
3. Include proposed routing hints, memory sections, source sessions, and why existing skills did not fit.
4. Keep candidate activation manual or review-gated.
5. Add `govkb create capability <id> --from-candidate <candidate-id>` or equivalent promotion path.

That completes the second half of the self-improving-project loop:

`existing skills gain expertise automatically; repeated new work proposes new governed skills for review.`
