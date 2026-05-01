# Open Questions - VS Code Extension UI and Public Distribution

Last updated: 2026-04-25

| ID | Question | Status | Blocking | Owner | Source | Notes |
|---|---|---|---|---|---|---|
| Q1 | What exact runtime provisioning mechanism should support one-click setup: bundled wheel, downloaded package, embedded source, or guided local install action? | Resolved | No | Product/Engineering | business.md | First engineering slice uses `guidedInstall` plus explicit `govkb.command`/`pythonPath` settings. Missing runtime stops on one install action instead of silent download or bundling. |
| Q2 | What Marketplace publisher id, extension id, display name, icon, and branding should be used? | Deferred | No | Product | business.md | Blocks Marketplace publishing only. Local VSIX engineering can proceed with provisional package metadata and a TODO before public publish. |
| Q3 | Which platforms are launch-supported: WSL/Linux, macOS, Windows native, or all three? | Resolved | No | Product/Engineering | business-context.md | First engineering slice targets WSL/Linux path behavior. macOS and Windows native are deferred until after VSIX proof. |
| Q4 | Should memory-review apply mode be available in the first UI release, or should memory review stay dry-run while one-click apply only materializes governed packages? | Resolved | No | Product/Governance | business.md | First UI release exposes memory review as dry-run only. One-click apply materializes governed packages through `govkb apply codex`. |
| Q5 | Is telemetry allowed, and if yes, what minimal opt-in events are acceptable? | Resolved | No | Product/Security | business-context.md | No telemetry in the first release. Revisit only with an explicit privacy decision. |
| Q6 | Should scheduler setup and management remain CLI-only in the first extension release? | Resolved | No | Product/Engineering | business.md | Scheduler/cron management remains CLI-only for the first extension slice. |
| Q7 | How should multi-root workspaces behave when more than one folder has `.governed/`? | Resolved | No | Engineering | context.md | First release uses single selected workspace/project behavior and should stop on ambiguity with one selection action. |
| Q8 | Should the extension parse existing human CLI output or should GovKB add machine-readable JSON output for status/candidates/reports? | Resolved | No | Engineering | context.md | Engineering should add machine-readable JSON output for extension-facing status/candidates/report summaries before building durable views. |
