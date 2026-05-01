# VS Code Extension UI and Public Distribution - Spec Handoff

Last updated: 2026-04-25

## Handoff Status

Ready for engineering cookbook: Yes, for the locked first slice.

The first slice is local VSIX delivery for WSL/Linux with guided GovKB runtime setup, JSON CLI support for extension views, Workspace Trust gating, dry-run memory review, and one-click governed package materialization.

## Source Artifacts

| Artifact | Path |
|---|---|
| Business spec | `docs/governed-skill-knowledge-framework/features/vscode-extension-public-distribution/business.md` |
| Business context | `docs/governed-skill-knowledge-framework/features/vscode-extension-public-distribution/business-context.md` |
| Implementation context | `docs/governed-skill-knowledge-framework/features/vscode-extension-public-distribution/context.md` |
| Spec brief | `docs/governed-skill-knowledge-framework/features/vscode-extension-public-distribution/spec-brief.md` |
| Open questions | `docs/governed-skill-knowledge-framework/features/vscode-extension-public-distribution/open-questions.md` |
| Decision log | `docs/governed-skill-knowledge-framework/features/vscode-extension-public-distribution/decision-log.md` |
| Scope lock | `docs/governed-skill-knowledge-framework/features/vscode-extension-public-distribution/scope-lock.md` |

## Accepted Scope

- VS Code extension package under `vscode-extension/`.
- One-click setup for the selected trusted workspace.
- One-click apply for the selected trusted workspace.
- Command palette actions over existing GovKB CLI workflows.
- Status, capabilities, candidates, and reports views.
- Settings for GovKB runtime path, Codex home, classifier defaults, timeout, and dry-run behavior.
- Workspace Trust gating for local execution and mutations.
- JSON CLI output for extension-facing status/candidate/report data.
- Local `.vsix` packaging.
- Extension tests plus unchanged Python core test suite.

## Required Engineering Decisions Already Made

| Decision | Outcome |
|---|---|
| Core architecture | Extension calls GovKB CLI; Python GovKB remains core engine. |
| Source of truth | `.governed/` remains canonical; assistant-local files remain derived. |
| Runtime provisioning | First slice uses guided local install/configuration, not bundling or download. |
| Platform | WSL/Linux first. |
| Memory review | Dry-run only from UI. |
| One-click apply | Materializes governed packages through `govkb apply codex`. |
| Telemetry | None in first release. |
| Scheduler | CLI-only in first release. |
| Multi-root | Single selected workspace/project; ambiguity requires explicit selection. |
| UI data | Add JSON output in GovKB CLI for durable extension parsing. |

## Deferred Scope

- Marketplace publish and final public branding.
- macOS and Windows native support.
- Runtime bundling/download.
- Memory-review mutation UI.
- Scheduler management UI.
- Telemetry.
- VS Code Web support.
- Claude/Copilot adapter support.

## Engineering Cookbook Entry Point

Start with the GovKB feature cookbook at `docs/COOKBOOK/COOKBOOK.MD`.

Recommended next artifacts:

1. `use-cases.md`
2. `requirements-catalog.md`
3. `poc-plan.md`
4. `poc-output.md`
5. `implementation-plan.md`
6. `review.md`

## Initial PoC Focus

- Prove JSON CLI status/candidate/report output shape with Python tests.
- Prove extension command construction without shell interpolation.
- Prove Workspace Trust gates mutation commands.
- Prove one-click setup sequence stops on one runtime blocker when GovKB is unavailable.
- Prove one-click apply invokes `govkb apply codex` with project root and Codex home.
- Prove `.vsix` packaging can run locally.

## Required Verification Baseline

From `/home/ev/code/govkb`:

```bash
python3 -m unittest discover -s tests -v
```

For extension work, add target-specific Node/VS Code verification commands in `implementation-plan.md` after the package structure is chosen.

## Known Risks

| Risk | Mitigation |
|---|---|
| JSON CLI output is not implemented yet. | Treat as Phase 0 or Phase 1 prerequisite before durable views. |
| Guided install may still feel manual. | One-click setup must stop on exactly one concrete install/config action. |
| WSL/Linux-first behavior may leak assumptions into later platforms. | Keep path helpers isolated and record platform constraints. |
| Extension could accidentally become source of truth. | Mutate project/assistant state only through GovKB CLI. |
| Memory-review reports can contain sensitive local context. | Show summaries and file links; do not copy raw transcript content into extension state. |

## Workflow Notes

The adopted feature-spec orchestrator could not run directly before its GovKB adaptation was installed. The spec-cookbook gates were applied manually against the GovKB feature folder, and the source-specific tracker gate is treated as not applicable for local GovKB implementation.
