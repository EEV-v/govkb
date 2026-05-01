# Spec Brief - VS Code Extension UI and Public Distribution

Last updated: 2026-04-25

## Objective

Create a VS Code extension that makes GovKB usable and distributable as an editor-native product with one-click setup and one-click apply for the open project, while keeping the Python GovKB core and repo-owned `.governed/` package as the authoritative implementation.

## Source Artifacts

- `business.md`
- `business-context.md`
- `context.md`
- `README.md`
- `pyproject.toml`
- `src/govkb/cli.py`
- `src/govkb/commands/install.py`
- `docs/governed-skill-knowledge-framework/business.md`
- `docs/governed-skill-knowledge-framework/implementation-plan.md`
- `docs/governed-skill-knowledge-framework/mvp-plus-test-plan.md`

## Problem Statement

The current CLI-first workflow proves GovKB core behavior, but it is not enough for public adoption. Users need one-click setup, one-click apply, visible project health, repeatable low-cost memory-review settings, report discovery, and candidate inspection inside the editor they already use.

## Scope Snapshot

- Add a VS Code extension package under the GovKB repo.
- Add one-click setup for the open project: detect/provision prerequisites, initialize `.governed`, apply Codex, bootstrap KB, validate, and show status.
- Add one-click apply for the open project: apply the governed package to Codex and refresh status.
- Register command palette actions over the existing CLI.
- Add GovKB status, capability, candidate, and report views.
- Add settings for command path, Codex home, classifier model, classifier reasoning, timeout, and dry-run behavior.
- Enforce Workspace Trust for trust-sensitive execution and mutation paths.
- Package a `.vsix` and prepare Marketplace metadata.
- Add extension tests plus keep Python tests green.

## Acceptance Snapshot

- Local `.vsix` installation works.
- One-click setup completes setup for a trusted open project or stops on one actionable blocker.
- One-click apply applies the open project's governed package without requiring users to enter CLI flags.
- Extension detects a GovKB project and GovKB runtime prerequisites.
- Trusted workspace can run install/init, validate, status, apply Codex, dry-run memory review, and candidate listing.
- Untrusted workspace blocks mutation and local execution actions.
- Low-cost classifier defaults are visible and used by memory-review dry-run.
- Views show health, capabilities, candidates, reports, and command output without raw transcript leakage.
- `@vscode/vsce` can package the extension.

## Review Readiness

- Public business review/tracker sync is deferred for Marketplace release.
- No feedback rounds exist yet.
- First engineering slice has scope lock and handoff.
- Current stage: ready for GovKB engineering cookbook.

## Current Open Questions

- Which runtime provisioning mechanism should make one-click setup work?
- What Marketplace publisher id and extension branding should be used?
- Which OS/path environments are supported at launch?
- Should first release expose memory-review mutation, or only one-click governed package apply plus dry-run memory review?
- Is telemetry allowed?
