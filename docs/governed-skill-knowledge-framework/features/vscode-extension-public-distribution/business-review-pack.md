# Business Review Pack - VS Code Extension UI and Public Distribution

Last updated: 2026-04-25

Status: Superseded for engineering handoff. Do not send externally without refreshing public-tracker and Marketplace decisions.

## Summary

GovKB currently works as a Python CLI and repo-native governed package. This feature proposes a VS Code extension that gives users one-click setup, one-click apply for the open project, editor-native status/candidate/report inspection, memory-review dry-runs, and public distribution.

The extension is intentionally thin. It should call the existing GovKB CLI rather than reimplement governance or classification logic in TypeScript.

## Proposed Scope

- One-click setup for the open project: detect/provision prerequisites, initialize `.governed`, apply Codex, bootstrap KB, validate, and show status.
- One-click apply for the open project: materialize the current governed package to Codex and refresh status without requiring CLI flags.
- VS Code command palette actions for install/init, validate, status, apply Codex, memory-review dry-run, candidate listing, and ready-candidate activation.
- Status bar plus GovKB views for project health, capabilities, candidates, and reports.
- Extension settings for GovKB command path, Codex home, classifier model, classifier reasoning, timeout, and dry-run defaults.
- Workspace Trust gating for local execution and mutation paths.
- `.vsix` packaging and Marketplace-ready metadata.
- Extension tests plus unchanged GovKB Python test expectations.

## Explicit Non-scope

- Rewriting GovKB core in TypeScript.
- Direct extension mutation of Codex skill files.
- VS Code Web support in the first release.
- Scheduler/cron management in the first release.
- Full Claude or Copilot adapter implementation.
- Marketplace publish before publisher, branding, license, and public README decisions are confirmed.

## Business Decisions Needed

| ID | Decision Needed | Current Recommendation |
|---|---|---|
| BD1 | Runtime provisioning mechanism | Resolved for first slice: guided local install/configuration, not bundling or download. |
| BD2 | Distribution sequence | Resolved for first slice: ship internal/local VSIX first, then Marketplace later. |
| BD3 | Branding | Deferred: confirm publisher id, extension id, display name, icon, and Marketplace copy before public publish. |
| BD4 | Launch platform matrix | Resolved for first slice: WSL/Linux first; macOS/Windows native later. |
| BD5 | Memory-review mutation level | Resolved for first slice: dry-run memory review only; one-click apply only materializes governed packages. |
| BD6 | Telemetry | Resolved for first slice: no telemetry. |
| BD7 | Extension-facing CLI data | Resolved for first slice: add machine-readable JSON output for status/candidates/report summaries. |

## Readiness Gates

- First-slice scope lock exists in `scope-lock.md`.
- First-slice engineering handoff exists in `spec-handoff.md`.
- Public Marketplace tracker/branding remains deferred and should be revisited before external/public send.
- Fresh final review was not run for external business send because this pack is not being sent externally.

## Acceptance Summary

The feature is accepted when a user can install the extension from VSIX, open a project in a trusted workspace, complete GovKB setup with one command/button, apply the governed package to Codex with one command/button, inspect status/candidates/reports, and package the extension for public Marketplace distribution without weakening governance boundaries.
