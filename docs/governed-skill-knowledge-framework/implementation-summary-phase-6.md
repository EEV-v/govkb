# Governed Skill Knowledge Framework Implementation Summary: Phase 6

Last updated: 2026-04-23

## Scope delivered

Phase 6 applied the governed framework to all current memory-bearing Clearing skills.

The governed package now contains `9` memory-bearing capabilities:

- `clearing-bugfixer`
- `clearing-feature-estimator`
- `clearing-master-reviewer`
- `clearing-qa-on-staging`
- `clearing-review-cashflow-reconciliation`
- `clearing-review-corporate-actions-processing`
- `clearing-review-internal-account-governance`
- `clearing-review-security-master`
- `clearing-review-transaction-lots-reconciliation`

The non-memory utility skills are intentionally not part of this phase because the scheduled memory-review runtime only uses memory-bearing contracts today.

## Repo package changes

Added governed contracts and copied existing local skill source for the remaining five memory-bearing skills:

- `/home/ev/code/Clearing/.governed/capabilities/clearing-bugfixer/capability.contract.toml`
- `/home/ev/code/Clearing/.governed/capabilities/clearing-qa-on-staging/capability.contract.toml`
- `/home/ev/code/Clearing/.governed/capabilities/clearing-review-cashflow-reconciliation/capability.contract.toml`
- `/home/ev/code/Clearing/.governed/capabilities/clearing-review-security-master/capability.contract.toml`
- `/home/ev/code/Clearing/.governed/capabilities/clearing-review-transaction-lots-reconciliation/capability.contract.toml`

Updated release metadata:

- `/home/ev/code/Clearing/.governed/releases/2026.04.23.toml`
- revision: `workspace-2026-04-23-governed-all-memory-bearing`
- notes: `Governed Codex migration for all current memory-bearing Clearing skills.`

## Verification

Package validation:

- command: `python3 -m govkb.cli validate /home/ev/code/Clearing`
- result: passed
- capabilities loaded: `9`

Framework tests:

- command: `python3 -m unittest discover -s tests -v`
- result: passed
- tests run: `10`

Clean redistribution proof:

- temp Codex home:
  - `/tmp/govkb-clearing-all.cNQlLz`
- command:
  - `python3 -m govkb.cli apply codex --project-root /home/ev/code/Clearing --codex-home /tmp/govkb-clearing-all.cNQlLz`
- result:
  - materialized capabilities: `9`
  - applied revision: `workspace-2026-04-23-governed-all-memory-bearing`

Temp scheduler discovery proof:

- command used:
  - `CODEX_HOME=/tmp/govkb-clearing-all.cNQlLz python3 /home/ev/.codex/bin/codex-memory-review --dry-run --once --session-file /home/ev/.codex/sessions/2026/04/17/rollout-2026-04-17T20-31-38-019d9c7f-8fda-7692-8fc5-c51ecbfa8e1a.jsonl`
- result:
  - discovered memory targets: `9`
  - report written under the temp Codex home

## Live Codex apply

Applied the all-memory-bearing release to the real local Codex home:

- command:
  - `python3 -m govkb.cli apply codex --project-root /home/ev/code/Clearing`
- Codex home:
  - `/home/ev/.codex`
- install state:
  - `/home/ev/.codex/memories/govkb/install-state/clearing--codex.json`
- materialized capabilities:
  - `9`
- applied release:
  - `2026.04.23`
- applied revision:
  - `workspace-2026-04-23-governed-all-memory-bearing`

Backups were created under:

- `/home/ev/.codex/memories/govkb/backups/clearing/codex/20260423T100729.813779Z/`

## Live scheduler check

Ran the live memory-review runtime after the apply:

- report:
  - `/home/ev/.codex/memories/codex-memory-review/reports/2026-04-23T100753Z-report.md`
- result:
  - discovered memory targets: `9`
  - self-referential maintenance session was skipped correctly
  - reports and patches were written normally

At this point the scheduled task no longer depends on the hardcoded Clearing keyword map for the current memory-bearing skills. The governed repo package can recreate the same 9-target memory-review setup in another Codex home.

## Decision

The next implementation step should be repo promotion, not more migration.

Reason:

- the current milestone proves governed discovery, materialization, live scheduler compatibility, and second-local redistribution
- the remaining major product gap is that learned updates still land in local materialized Codex skill memory first
- the self-improving-project goal requires accepted learning to move back into `.governed` so the team can pull and apply it from git

Recommended next slice:

1. Implement `govkb promote` for local Codex memory deltas.
2. Compare local materialized skill memory files with repo `.governed` source memory files.
3. Stage safe repo patches under `.governed/capabilities/<id>/references/...`.
4. Preserve audit metadata linking promoted lines back to memory-review reports.
5. Keep estimator and other explicit-acceptance rules intact.
6. Re-run `govkb apply codex` after promotion so local generated state matches repo source.

After that slice, the loop becomes:

`real work session -> scheduled memory review -> local governed memory update/stage -> govkb promote -> repo commit -> teammate govkb apply codex`
