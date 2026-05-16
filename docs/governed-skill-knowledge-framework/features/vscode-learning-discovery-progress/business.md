# VS Code Learning Discovery and Progress - Business Requirements

Last updated: 2026-05-10

## Problem

The VS Code extension currently makes GovKB learning feel inactive or broken after a new user applies GovKB to a real project. A project can have many historical Codex sessions, but the UI defaults to reviewing one recent session at a time, dry-run reports do not create `.governed/candidates`, and the Candidates view can show "No candidates found" without explaining whether sessions were discovered, skipped, deferred, already processed, matched existing capabilities, or blocked by classifier limits.

This creates a poor first-run experience: users cannot tell whether GovKB has no useful learning opportunities, has not scanned enough history, is still processing, or requires apply mode to stage candidates.

## Objective

Make learning discovery in the VS Code extension understandable, observable, and controllable for first-time and ongoing GovKB users while preserving GovKB's governance boundaries.

The extension should show what was discovered, what will be reviewed, what is being reviewed now, what the classifier concluded, and what action is needed next.

## Business Requirements

| ID | Requirement |
|---|---|
| LD-01 | After setup or apply, the user must see useful learning readiness, including installed capabilities and session inventory, not only an empty candidates list. |
| LD-02 | The extension must separate cheap session discovery from AI classification so users can inspect scope before paying time or model cost. |
| LD-03 | Users must be able to choose a bounded review scope, including date range and maximum sessions per batch. |
| LD-04 | Long-running review must expose live per-session progress: queued, prescreening, classifying, skipped, applied, staged, rejected, deferred, or failed. |
| LD-05 | Review output must explain why nothing visible was created: no durable signal, matched existing capability, dry-run only, already processed, classifier timeout, usage limit, missing executable, or governance rejection. |
| LD-06 | The UI must distinguish existing skill memory updates from new capability candidates. |
| LD-07 | The UI must make dry-run versus apply semantics explicit: dry-run writes reports and patch previews, while apply can update local memory and stage candidates. |
| LD-08 | Users must be able to open the latest report and relevant patch previews from the learning surface. |
| LD-09 | The extension must show safe structured classifier output such as target skill, lesson summary, confidence, validation decision, and semantic candidate summary without exposing raw session transcripts by default. |
| LD-10 | The feature must preserve governance boundaries: TypeScript extension code must not mutate `.governed/**` or `$CODEX_HOME/**` directly. Mutations continue through the GovKB CLI. |
| LD-11 | The feature must remain useful when a full backfill cannot finish in one run by showing batch progress and resumable next steps. |
| LD-12 | The feature should be cross-platform in behavior, with platform-specific runtime discovery handled by explicit settings or CLI discovery rather than hard-coded UX assumptions. |

## User Experience Target

First-time project flow:

1. User installs or enables GovKB for a project.
2. Status shows governed package state and applied Codex skills.
3. Learning view shows session inventory such as total project sessions, recent sessions, already reviewed sessions, and recommended batch scope.
4. User runs discovery without AI classification.
5. User starts a bounded dry-run batch.
6. UI shows live session progress and final report summary.
7. User reviews existing skill updates and new capability candidates separately.
8. User decides whether to run apply, promote learned memory, or increase lookback/batch size.

## Non-Goals

- Do not expose raw Codex session transcripts in the extension view by default.
- Do not implement direct TypeScript mutation of `.governed/**` or `$CODEX_HOME/**`.
- Do not automatically process all historical sessions without user-selected scope.
- Do not create candidates from dry-run alone unless the CLI explicitly supports a governed non-mutating candidate preview artifact.
- Do not hide classifier cost, timeout, quota, or connectivity failures behind a generic success state.

## Success Criteria

- A real project with many historical sessions does not appear empty after setup.
- A user can see session inventory before running AI classification.
- A user can run a bounded batch and understand exactly what happened for each reviewed session.
- "No candidates" means "no staged new capability candidates" and is not confused with "no learning happened."
- Reports, patches, skipped reasons, deferred reasons, and classifier decisions are visible from the extension.
- Existing extension tests and Python CLI tests remain green, with new coverage for discovery and progress behavior.

## Stakeholder Notes

- The Clearing project diagnostic that motivated this feature showed many historical sessions on disk but only a small recent selection under the default review window, plus a UI cap of one session per run.
- Dry-run reports can include useful "Would Apply" lessons for existing capabilities even when `.governed/candidates` remains empty.
- Long-running classifier calls may time out or be interrupted; users need progress and resumable batches rather than a hanging notification.
