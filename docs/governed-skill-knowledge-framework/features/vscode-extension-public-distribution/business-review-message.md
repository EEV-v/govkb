# Business Review Message - VS Code Extension UI and Public Distribution

Status: Superseded for first engineering handoff. Do not send externally without refreshing public-tracker and Marketplace decisions.

Please review the draft scope for the GovKB VS Code extension and public distribution feature.

Main proposal: keep GovKB's Python CLI and `.governed/` package as the authoritative engine, and add a thin VS Code extension for one-click setup, one-click apply for the open project, validation, status, candidate/report inspection, low-cost memory-review dry-runs, VSIX packaging, and Marketplace readiness.

First-slice decisions now locked for engineering:

- Runtime provisioning: guided local install/configuration for the first slice.
- Distribution: local VSIX first; Marketplace publish later.
- Platform: WSL/Linux first.
- Memory review: dry-run only from UI.
- One-click apply: governed package materialization only.
- Telemetry: none.
- Extension views: add JSON CLI output for status/candidates/report summaries.

Engineering handoff artifacts are under `docs/governed-skill-knowledge-framework/features/vscode-extension-public-distribution/`.
