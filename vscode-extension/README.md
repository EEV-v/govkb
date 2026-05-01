# GovKB VS Code Extension

Local VSIX proof for WSL/Linux GovKB workflows.

## First Slice

- One-click setup for one trusted workspace.
- One-click apply through `govkb apply codex`.
- Status, capability, candidate, and report views backed by GovKB CLI data.
- Memory review dry-run and apply runs with low-cost defaults and streamed output.

The extension is a thin orchestration layer. It delegates mutations to the GovKB CLI.

## Local Development

```bash
npm install
npm run compile
npm test
npx @vscode/vsce package --no-dependencies
```

Usage notes live in `MANUAL.md`.

Marketplace publisher, final icon, and public branding are deferred until after local VSIX validation.
