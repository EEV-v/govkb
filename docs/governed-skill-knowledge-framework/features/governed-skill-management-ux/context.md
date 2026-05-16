# Governed Skill Management UX Context

## Existing Behavior

GovKB already supports governed project status, Codex materialization, local memory review, candidate activation, and automated promotion review. The CLI also has `govkb convert skill`, which can preview or write a strict-valid governed package from a local Codex skill. Before this feature, conversion was not visible in the VS Code extension, and governed capability rename or merge required manual filesystem edits.

## Relevant Code

- `src/govkb/core/skill_conversion.py` converts local Codex skills into governed packages.
- `src/govkb/commands/convert.py` exposes `govkb convert skill`.
- `src/govkb/core/contracts.py` loads governed capability contracts from `.governed/capabilities`.
- `src/govkb/commands/status.py` feeds the extension with project and capability summaries.
- `vscode-extension/src/views/capabilitiesView.ts` renders governed skills in VS Code.
- `vscode-extension/src/extension.ts` owns command registration and user prompts.

## Constraints

Governed skill management must keep source skills unchanged during conversion, preserve reviewable Git diffs, avoid auto-committing, and keep `.governed` validation passing after rename or merge. Merge operations should remove the source active capability only after target updates are written and validated.
