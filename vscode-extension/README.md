# GovKB VS Code Extension

Local VSIX proof for GovKB workflows.

## First Slice

- One-click setup for one trusted workspace.
- One-click apply through `govkb apply codex`.
- Status, capability, candidate, promotion, and report views backed by GovKB CLI data.
- Single Skill updates indicator backed by CLI status, comparing repo package revision, applied Codex state, and pending learned local memory.
- Memory review dry-run and apply runs with low-cost defaults and streamed output.
- Extension-triggered memory review uses a bounded default classifier timeout.
- Isolated promotion review lifecycle actions through `govkb promote --auto` and `govkb promotions`.
- Read-only startup refresh for the remembered project, so reopening the same folder shows current GovKB state without re-running setup or apply.
- Optional read-only monitoring refresh through `GovKB: Monitor Interval Seconds`.
- Default runtime discovery for GUI-launched VS Code sessions that do not inherit the shell PATH.

The extension is a thin orchestration layer. It delegates mutations to the GovKB CLI.
Promotion review state is recorded through GovKB sidecar metadata; normal project Git
commit, merge, and cleanup decisions stay outside the extension.

## Local Development

```bash
npm install
npm run compile
npm test
npm run test:host
npx @vscode/vsce package --no-dependencies
```

Usage notes live in `MANUAL.md`.

Marketplace publisher, final icon, and public branding are deferred until after local VSIX validation.
