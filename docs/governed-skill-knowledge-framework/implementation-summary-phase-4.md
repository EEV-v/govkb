# Governed Skill Knowledge Framework Implementation Summary: Phase 4

Last updated: 2026-04-22

## Scope delivered

Phase 4 created the first real repo-governed project package for Clearing, migrated the first two live capabilities into it, applied them into local Codex, and verified the daily memory-review runtime against real historical sessions.

Delivered repo surfaces:

- `/home/ev/code/Clearing/.governed/project.toml`
- `/home/ev/code/Clearing/.governed/releases/2026.04.23.toml`
- `/home/ev/code/Clearing/.governed/capabilities/clearing-feature-estimator/capability.contract.toml`
- `/home/ev/code/Clearing/.governed/capabilities/clearing-master-reviewer/capability.contract.toml`
- repo-copied source content for both migrated capabilities under:
  - `/home/ev/code/Clearing/.governed/capabilities/clearing-feature-estimator/`
  - `/home/ev/code/Clearing/.governed/capabilities/clearing-master-reviewer/`

Live runtime follow-up change:

- `/home/ev/.codex/bin/codex-memory-review`

## First governed project package

Created the first repo-owned governed package for this project:

- project id: `clearing`
- current release: `2026.04.23`
- first migrated capabilities:
  - `clearing-feature-estimator`
  - `clearing-master-reviewer`

Both contracts now carry governed routing metadata directly:

- aliases
- hints
- negative hints
- governed memory sections
- explicit-acceptance requirements
- migration fallback pointers to the existing local Codex skills

## Materialization result

Validated and applied the governed package with:

1. `python3 -m govkb.cli validate /home/ev/code/Clearing`
2. `python3 -m govkb.cli apply codex --project-root /home/ev/code/Clearing --preview`
3. `python3 -m govkb.cli apply codex --project-root /home/ev/code/Clearing`
4. `python3 -m govkb.cli status /home/ev/code/Clearing --codex-home /home/ev/.codex`

Result:

- repo validation passed
- local Codex install state recorded at:
  - `/home/ev/.codex/memories/govkb/install-state/clearing--codex.json`
- materialized capabilities: `2`
- release applied: `2026.04.23`
- revision applied: `workspace-2026-04-23-governed-first-wave`

One implementation defect was found during the first live apply:

- `Path.replace()` failed across devices when the staged temp directory lived under `/tmp`
- fixed in:
  - `/home/ev/code/Clearing/govkb/src/govkb/adapters/codex/materialize.py`
- behavior now uses `shutil.copytree(...)` for the final install step

## Live scheduler verification

The existing scheduled runtime was then exercised in `--dry-run` mode against real session files.

### Verified outcomes

1. Real implementation/review session routed through governed metadata and produced a staged `clearing-master-reviewer` lesson:
   - session file:
     - `/home/ev/.codex/sessions/2026/04/16/rollout-2026-04-16T16-56-07-019d9693-e415-73d0-ac02-5a93fd183e21.jsonl`
   - report:
     - `/home/ev/.codex/memories/codex-memory-review/reports/2026-04-22T215409Z-report.md`

2. Real direct review session explicitly selecting `$clearing-master-reviewer` routed correctly and produced governed review output:
   - compacted session file:
     - `/home/ev/.codex/sessions/2026/04/01/rollout-2026-04-01T22-16-16-019d4a79-992d-7880-a938-5a85abd7a40c.jsonl`
   - corrected post-fix report:
     - `/home/ev/.codex/memories/codex-memory-review/reports/2026-04-22T220856Z-report.md`

3. Real first-pass estimate session routed to `clearing-feature-estimator` and respected the explicit-acceptance gate:
   - session file:
     - `/home/ev/.codex/sessions/2026/03/25/rollout-2026-03-25T21-05-04-019d262b-e7ea-7d10-972b-aa8e46a47398.jsonl`
   - report:
     - `/home/ev/.codex/memories/codex-memory-review/reports/2026-04-22T220506Z-report.md`
   - staged memory outcome:
     - estimator lesson landed in `Staged`, not `Would Apply`, because the target skill requires explicit acceptance

### What the live reports proved

- governed install-state was loaded by the existing scheduled task
- governed aliases and hints were used to add migrated capabilities into prompt-target selection
- coexistence with legacy local skills still works
- explicit-acceptance rules still prevent auto-apply for estimator memory
- reports, staged patches, and applied patches still generate under the existing audit model

## Runtime defect found and fixed

While exercising a compacted session file, the report showed the wrong session id and timestamp.

Root cause:

- `parse_session_file()` walked all `session_meta` rows and kept the last one
- compacted sessions can contain an embedded earlier `session_meta`
- report metadata therefore drifted from the actual file/thread being processed

Fix applied in the live runtime:

- `/home/ev/.codex/bin/codex-memory-review`

Change:

- `parse_session_file()` now captures the first valid `session_meta` row and stops once both id and timestamp are found

Verification:

- direct parser check on the compacted file now returns:
  - session id: `019d4a79-992d-7880-a938-5a85abd7a40c`
  - updated_at: `2026-04-01T19:16:16.304Z`
- rerunning the dry-run produced a report that matches the file/thread id

## Observations from real usage

- The hybrid model behaves as intended:
  - migrated governed capabilities participate immediately
  - unmigrated domain reviewers still receive lessons from the same sessions when they are the best target
- Session classification is materially slower on long or compacted threads:
  - roughly 90 to 170 seconds for the single-session dry-runs used here
  - this is runtime cost, not correctness failure

## Next useful slice

- migrate 1 to 2 more real capabilities so governed routing covers a larger part of the current daily workload
- move more of the memory-review runtime logic out of the patched local script and into reusable package code
- add repo-worktree staging/promotion flow so governed updates can be proposed into the repo instead of only local skill memory
- prove second-local-setup redistribution from the repo package onto another Codex home
