# Governed Skill Knowledge Framework Implementation Summary: Phase 5

Last updated: 2026-04-23

## Scope delivered

Phase 5 expanded the real Clearing governed package from two capabilities to four and proved the repo package can be redistributed into a clean second Codex home.

Newly migrated capabilities:

- `clearing-review-internal-account-governance`
- `clearing-review-corporate-actions-processing`

Existing governed capabilities retained:

- `clearing-feature-estimator`
- `clearing-master-reviewer`

## Repo package changes

Added governed contracts:

- `/home/ev/code/Clearing/.governed/capabilities/clearing-review-internal-account-governance/capability.contract.toml`
- `/home/ev/code/Clearing/.governed/capabilities/clearing-review-corporate-actions-processing/capability.contract.toml`

Copied source content from the existing local Codex skills into the repo package:

- `SKILL.md`
- `agents/openai.yaml`
- `references/context-sources.md`
- `references/long-term-memory.md`

Updated release metadata:

- `/home/ev/code/Clearing/.governed/releases/2026.04.23.toml`
- revision: `workspace-2026-04-23-governed-second-wave`

## Verification

Package validation:

- command: `python3 -m govkb.cli validate /home/ev/code/Clearing`
- result: passed
- capabilities loaded: `4`

Framework tests:

- command: `python3 -m unittest discover -s tests -v`
- result: passed
- tests run: `10`

## Second-local setup proof

Created a clean Codex home under:

- `/tmp/govkb-clearing-second-local.FN1dQt`

Applied the repo package into that clean home:

- command: `python3 -m govkb.cli apply codex --project-root /home/ev/code/Clearing --codex-home /tmp/govkb-clearing-second-local.FN1dQt`
- materialized capabilities: `4`
- install state:
  - `/tmp/govkb-clearing-second-local.FN1dQt/memories/govkb/install-state/clearing--codex.json`

Verified second-local status:

- applied release: `2026.04.23`
- applied revision: `workspace-2026-04-23-governed-second-wave`
- materialized capabilities: `4`

Verified second-local scheduler discovery:

- command used `CODEX_HOME=/tmp/govkb-clearing-second-local.FN1dQt`
- result: memory-review discovered exactly `4` memory targets from the clean redistributed setup
- report written under the temp Codex home:
  - `/tmp/govkb-clearing-second-local.FN1dQt/memories/codex-memory-review/reports/2026-04-23T095838Z-report.md`

This proves a second local setup can receive the repo-owned governed package without relying on the original local `~/.codex/skills` state.

## Live Codex apply

Applied the second-wave release to the real local Codex home:

- command: `python3 -m govkb.cli apply codex --project-root /home/ev/code/Clearing`
- Codex home: `/home/ev/.codex`
- install state:
  - `/home/ev/.codex/memories/govkb/install-state/clearing--codex.json`
- materialized capabilities: `4`

Backups were created under:

- `/home/ev/.codex/memories/govkb/backups/clearing/codex/20260423T095936.488499Z/`

Live status now reports:

- applied release: `2026.04.23`
- applied revision: `workspace-2026-04-23-governed-second-wave`
- materialized capabilities: `4`

## Live scheduler check

Ran the existing live scheduled reviewer in dry-run mode against a known self-referential maintenance session:

- session file:
  - `/home/ev/.codex/sessions/2026/04/17/rollout-2026-04-17T20-31-38-019d9c7f-8fda-7692-8fc5-c51ecbfa8e1a.jsonl`
- report:
  - `/home/ev/.codex/memories/codex-memory-review/reports/2026-04-23T095952Z-report.md`

Result:

- discovered memory targets: `9`
- session correctly skipped as self-referential maintenance
- report and patches were written normally

The `9` target count is expected in hybrid mode: four capabilities now come from governed install state, while remaining unmigrated local skills still participate through legacy fallback.

## Remaining work

- migrate the remaining memory-bearing Clearing reviewer skills
- move live memory-review runtime logic into reusable `govkb` package code instead of keeping it mostly in the patched local script
- add repo-worktree staging/promotion so learned updates can be proposed back into `.governed` instead of staying only in local Codex skill memory
- add a first governed new-capability candidate flow for repeated unmatched work
