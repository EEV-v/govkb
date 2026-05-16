# GovKB Agentic State Ownership

Last updated: 2026-05-16

This document defines which GovKB stores are authoritative, derived, generated, disposable, or test-only. It is the source-of-truth map for agentic-app state boundaries; command code and the VS Code extension should align to this map before adding new mutation paths.

GovKB reused architecture practices observed in `/Users/vasilevevgeny/code/caveman`, specifically source-of-truth maps, action registries, idempotent mutation flows, and dry-run tests. GovKB must not copy Caveman user-facing behavior, installer mechanics, hooks, prompt tone, or provider-specific runtime behavior.

## State Stores

| Store | Classification | Owner | Mutation Path | Notes |
|---|---|---|---|---|
| Project `.governed/**` | Authoritative repo source | Project Git repository | GovKB CLI commands under `src/govkb/commands/**` | Governed capability contracts, instructions, memory targets, candidates, reports, and project config live here when they are durable project knowledge. |
| `$CODEX_HOME/skills/govkb-*` | Derived assistant-local output | Codex adapter | `govkb apply codex`, `govkb install`, and rematerialization flows | These files are regenerated from `.governed/**` and should not be treated as source-of-truth. |
| `$CODEX_HOME/memories/govkb/install-state/*.json` | Derived adapter state | Codex adapter | Materialization flows | Records which repo revision was applied to a local assistant target. It can be rebuilt by applying governed content again. |
| `$CODEX_HOME/memories/govkb/projects/<project>/codex-memory-review/**` | Generated review artifacts | Memory review command | `govkb review-memory` | Review reports, patches, and state are generated evidence. Raw assistant transcript content must not be persisted in repo artifacts. |
| `$CODEX_HOME/memories/govkb/promotions/<project>/<run>.json` | Generated lifecycle audit metadata | Promotion lifecycle helpers | `govkb promotions mark-reviewed`, `apply`, `archive`, and `cleanup` | This sidecar record explains review, apply, archive, and cleanup decisions. Cleanup must preserve it. |
| `$CODEX_HOME/memories/govkb/worktrees/<project>/<run>` | Disposable review store | Promotion commands | `govkb promote --auto`, `govkb promotions cleanup` | Isolated worktrees support human review. Applied, archived, rejected, clean, or stale review worktrees can be removed after preview. |
| VS Code extension in-memory state | Derived UI state | Extension model/view code | Read-only refreshes plus CLI-backed flows | The extension guides users and invokes CLI commands. It must not become an authoritative state owner. |
| Temporary test directories | Disposable test state | Python and TypeScript tests | `tempfile.TemporaryDirectory`, fixture builders, fake runners | Tests must not depend on the user's real home directory, real Codex home, or raw assistant sessions. |

## Mutation Owners

| Mutation | Owning Module Or Command | Allowed Targets | UI Rule |
|---|---|---|---|
| Initialize governed package | `govkb init`, `govkb install` | Project `.governed/**` and optional derived Codex output | VS Code may invoke the CLI only after workspace trust. |
| Materialize governed skills | `govkb apply codex` | `$CODEX_HOME/skills/govkb-*`, install state, backups | VS Code may invoke the CLI; it must not write materialized files directly. |
| Review assistant memory | `govkb review-memory` | Assistant-local memory review reports, local memory targets, candidate packages, optional auto-promotion worktrees | VS Code may show progress and refresh derived views. |
| Promote local memory | `govkb promote` | Project `.governed/**` for manual promotion or isolated review worktrees for auto promotion | Auto promotion should keep the active project clean until review. |
| Review promotion lifecycle | `govkb promotions mark-reviewed` | Sidecar lifecycle metadata only | Git history and worktree files are unchanged. |
| Finalize accepted promotion | `govkb promotions apply` | Active project `.governed/**` and sidecar lifecycle metadata | The command copies reviewed files but never commits. |
| Archive promotion | `govkb promotions archive` | Sidecar lifecycle metadata only | Archiving is reversible by explicit metadata changes; it does not delete worktrees. |
| Cleanup promotion artifacts | `govkb promotions cleanup` | Eligible directories under computed promotions worktree root and preserved sidecar lifecycle metadata | Preview must be the default mental model; apply must be contained and idempotent. |
| Convert local skill | `govkb convert skill` | Project `.governed/capabilities/<id>/**` | The extension should select one discoverable source skill and reserve manual entry for explicit fallback. |
| Rename or merge governed skills | `govkb capabilities rename` and `merge` | Project `.governed/capabilities/**` | The extension may provide picker UI but mutation stays CLI-backed. |

## Cleanup Policy

Promotion cleanup is intentionally narrow. Preview mode must not delete files, write lifecycle metadata, or edit reports. Apply mode may remove only eligible worktree directories under the resolved promotions root for the current project and Codex home.

Eligible default cleanup states are `applied`, `archived`, `rejected`, `clean`, and stale worktrees that have no actionable governed changes. Ready or accepted review worktrees remain actionable and must not be deleted by the default cleanup path. Future targeted cleanup flags may remove actionable duplicates only with explicit user intent.

Cleanup apply must preserve `$CODEX_HOME/memories/govkb/promotions/<project>/<run>.json`. The preserved metadata should move to a terminal `cleaned` state and record a `cleanup` block with `cleanedAt`, `removedPaths`, and `reason`. Cleaned promotions are hidden from the default actionable promotion list because the review worktree no longer exists; the sidecar metadata remains the audit trail.

Cleanup must never mutate project `.governed/**`, materialized Codex skills, install state, or files outside the computed promotions worktree root.

## Test Isolation

Tests for mutation and cleanup behavior must create temporary project roots and temporary Codex homes. They should call command functions directly where possible, use `argparse.Namespace` for command arguments, and inspect JSON payloads instead of relying on the user's environment.

Tests that exercise deletion must seed synthetic worktrees under a temp `$CODEX_HOME/memories/govkb/worktrees/<project>/` root and verify both containment and sidecar metadata preservation. No test should use the real `/Users/vasilevevgeny/.codex` directory or raw session transcripts.
