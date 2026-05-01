# VS Code Extension UI and Public Distribution - Scope Lock

Last updated: 2026-04-25

## Scope Status

Status: Locked for first engineering slice.

The first slice is a local VSIX proof for WSL/Linux users. It implements the VS Code extension as a thin orchestration layer over the existing GovKB CLI and adds core JSON output needed by the extension views.

## Locked Scope

- Add a VS Code extension package under `vscode-extension/`.
- Provide one-click setup for one selected trusted workspace:
  - detect GovKB runtime prerequisites
  - guide missing runtime setup through one install/configuration action
  - run `govkb install`
  - run `govkb init-kb --all`
  - run `govkb status`
- Provide one-click apply for one selected trusted workspace:
  - run `govkb apply codex --project-root <workspace>`
  - refresh status and report view state
- Add command palette actions for:
  - install/init
  - validate
  - status
  - apply Codex
  - memory-review dry-run
  - candidate listing
- Add GovKB status, capabilities, candidates, and reports views.
- Add extension settings for:
  - GovKB command path
  - Python path
  - Codex home
  - classifier model
  - classifier reasoning
  - review timeout
  - dry-run default
- Default memory-review dry-run settings to:
  - model: `gpt-5.4-mini`
  - reasoning: `low`
  - timeout: `180`
- Gate local execution and mutation paths behind VS Code Workspace Trust.
- Add machine-readable JSON output in GovKB CLI for extension-facing status, candidates, and report summaries.
- Add tests for command construction, trust gating, settings resolution, status/candidate/report parsing, and one-click orchestration.
- Package the extension as a local `.vsix`.

## Explicit Non-scope For First Slice

- Public Marketplace publish.
- Final publisher id, public extension id, icon, Marketplace banner, and public branding.
- Silent runtime download, bundled wheel, or embedded GovKB runtime.
- macOS and Windows native support.
- VS Code Web support.
- Scheduler/cron setup or management.
- Memory-review mutation/apply mode from the UI.
- Direct mutation of `.governed/` or `$CODEX_HOME` files by extension TypeScript code.
- Telemetry.
- Full Claude or Copilot adapter support.

## Deferred Items

| Item | Reason | Revisit Trigger |
|---|---|---|
| Marketplace publisher and branding | Needs product/public distribution decision. | Before public Marketplace release. |
| macOS support | Needs path and runtime validation outside WSL/Linux. | After VSIX WSL/Linux proof. |
| Windows native support | Needs Codex/GovKB path behavior and shell/runtime decisions. | After VSIX WSL/Linux proof. |
| Runtime bundling/download | Higher distribution and update complexity. | After guided setup proves UX gaps. |
| Memory-review mutation UI | Higher governance risk. | After dry-run UX and reports are validated. |
| Scheduler UI | Not needed for explicit first-use workflows. | After core setup/apply UX is stable. |
| Telemetry | Privacy posture not needed for first slice. | Before public telemetry proposal. |

## Resolved Questions

| Question | Resolution |
|---|---|
| Runtime provisioning | Use guided local install/configuration for first slice. |
| Launch platforms | WSL/Linux first. |
| Memory-review mutation | Dry-run only in first UI release. |
| Telemetry | None in first release. |
| Scheduler | CLI-only in first release. |
| Multi-root | Single selected workspace/project; stop on ambiguity. |
| Extension data source | Add JSON output to GovKB CLI instead of parsing human output for durable views. |

## Open Questions

No blocking questions remain for the first engineering slice.

## Open Decisions

No blocking decisions remain for the first engineering slice.

## Tracker Status

No external tracker has been configured for this GovKB feature. Tracker sync is not a blocker for local repository implementation. Public distribution tracking can be added before Marketplace release if needed.

## Handoff Eligibility

Engineering may proceed to the GovKB feature cookbook for use cases, PoC, implementation planning, review, scaffolding, and implementation.

