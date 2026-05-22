# VS Code Guided Daily Workflow UI

## Stakeholder Need

GovKB users need the VS Code extension to feel like a daily operating surface instead of a collection of command labels and tree rows. A user should be able to open the GovKB sidebar and immediately understand what to do next: set up the project, apply governed skills, discover learning opportunities, review a batch, inspect generated updates, accept or reject a promotion, finalize accepted updates, commit changed files, or rematerialize Codex skills after commit.

The current tree-only UI exposes too many raw states, paths, worktrees, and command names. It also relies on text rows where familiar icons, primary actions, and guided pickers would be clearer. Users can see stale or duplicate promotion worktrees, already governed skills in conversion pickers, and applied promotions that still read as pending after commit. These states make the everyday flow hard to trust.

## Success Criteria

- The extension exposes one primary GovKB Home surface that answers "what should I do next?" for the selected project.
- The daily flow is explicit: refresh, discover, dry-run review, apply learning, inspect digest, accept or reject, finalize, commit, and apply Codex materialization.
- Tree views remain available as compact native summaries, but they do not act as the main workflow surface.
- Primary user actions use clear icons, labels, and state-specific availability rather than raw command lists.
- Promotion review is understandable without opening a separate worktree first; digest content, lifecycle state, and next action are visible from the UI.
- Governed skill management avoids manual typing when data is discoverable: conversion, rename, and merge use pickers with descriptions, validation previews, and explicit confirmation.
- Already governed or already materialized skills are hidden from conversion choices unless the user chooses a manual override.
- Finalized, duplicate, archived, or already committed promotion worktrees do not compete with current actionable work.
- The extension continues to use the GovKB CLI for project mutations; the UI must not directly mutate `.governed/**` or `$CODEX_HOME/**`.
- Long-running operations show progress, avoid duplicate execution, and leave useful output for troubleshooting.

## Non-Goals

- Replacing VS Code with a standalone desktop app.
- Showing raw Codex session transcripts in the UI.
- Automatically committing project changes.
- Building a full Git client inside GovKB.
- Removing existing CLI commands or tree views.

## User-Visible Outcomes

- A first-time user sees setup/apply guidance without needing to know command names.
- A regular user sees one primary next action and compact supporting counts.
- The primary action explains why it is recommended and what clicking it will do before the user runs it.
- A reviewer can accept, reject, finalize, and archive promotions from the extension without deciphering worktree paths first.
- A skill maintainer can convert one selected skill, rename a governed skill, or merge two governed skills through picker-driven flows.
- A user can tell when they are done: validation is ok, Codex skills are current, no learned updates are pending, and no promotion requires action.

## Daily Flow Wording Refinement

Everyday Home wording should stay business-readable. In particular, stale governed skills should say why apply is needed, such as "Repo governed skills changed since the last Codex install," and should say that clicking apply updates local Codex skills from `.governed` without committing repository files. Learning review should be presented as "Review learning updates" or "Preview review" rather than making "dry run" the main happy-path label; dry-run remains an implementation detail and an advanced command name.

## Constraints

- The extension targets the VS Code extension API declared by `vscode-extension/package.json`.
- Existing CLI contracts remain the authoritative mutation boundary.
- UI state derived from `govkb status`, `review-memory --inventory-json`, `promotions list --json`, `candidates list --json`, and report discovery is advisory and refreshable.
- Tests must use synthetic fixtures and temporary directories; no tests may depend on the user's real `$HOME`, real `CODEX_HOME`, or real Codex session history.
