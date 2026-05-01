# Next Session Prompt: GovKB VS Code Extension UI/UX Improvements

Use this prompt in a fresh Codex session from `/home/ev/code/govkb`.

```text
We are working in the GovKB repository at /home/ev/code/govkb.

Task: improve the GovKB VS Code extension UI/UX for the existing local VSIX first slice.

Use $govkb-feature-cookbook only as workflow guidance. Do not restart the completed public-distribution feature from scratch. Treat the existing feature folder as upstream context:
- docs/governed-skill-knowledge-framework/features/vscode-extension-public-distribution/
- vscode-extension/
- src/govkb/commands/status.py
- src/govkb/commands/candidates.py
- tests/

Primary goal:
Make the extension easier and safer to use inside VS Code after install. Improve the user-facing UI states, command affordances, and troubleshooting path without expanding the first-slice scope beyond local WSL/Linux VSIX validation.

Important boundaries:
- Do not inspect assistant session internals or scheduler artifacts.
- Do not run memory review unless I explicitly ask for it.
- Do not change marketplace publisher, public branding, license, telemetry, or cross-platform support.
- Keep the extension a thin orchestration layer over the GovKB CLI.
- Do not copy raw assistant transcripts into repo docs, tests, fixtures, extension state, or output.
- Preserve existing JSON CLI contracts unless a required UI improvement proves an additive field is necessary.

Start by reading:
1. vscode-extension/MANUAL.md
2. vscode-extension/README.md
3. vscode-extension/package.json
4. vscode-extension/src/extension.ts
5. vscode-extension/src/views/*.ts
6. docs/governed-skill-knowledge-framework/features/vscode-extension-public-distribution/sign-off.md
7. docs/governed-skill-knowledge-framework/features/vscode-extension-public-distribution/release-notes.md

Then propose a short implementation plan and proceed with the changes.

Expected UI/UX improvements to evaluate and implement where practical:
- Make the GovKB sidebar more useful on first open: show actionable empty states instead of only "No reports loaded" style placeholders.
- Add visible running/progress feedback for long commands, especially setup, apply, and dry-run review.
- Prevent duplicate command runs where a command is already active.
- Make failure notifications actionable: open the GovKB output channel, run setup when apply is blocked by missing project setup, and refresh status when relevant.
- Add command buttons or view-title actions that map naturally to Status, Capabilities, Candidates, and Reports views.
- Improve report handling from the extension UI without exposing raw transcript content.
- Improve settings wording for runtime command, Python module mode, timeout, and session cap.
- Update MANUAL.md so a new user knows the shortest successful path after installing the VSIX.

Engineering expectations:
- Follow existing TypeScript style in vscode-extension/src.
- Prefer small helpers over broad refactors.
- Keep view rows deterministic and testable.
- Add or update Node tests under vscode-extension/src/test/suite for command construction, settings, flow behavior, and view row output.
- If Python CLI payloads change, add or update Python unittest coverage.

Verification before final response:
- npm test from vscode-extension/
- npm_config_cache=/tmp/govkb-npm-cache npx @vscode/vsce package --no-dependencies from vscode-extension/
- If Python CLI code changed: PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -v
- If the VSIX is rebuilt for local testing, install it with:
  code --remote wsl+Ubuntu-24.04 --install-extension /home/ev/code/govkb/vscode-extension/govkb-0.0.1.vsix --force

Final response should include:
- What UI/UX changed.
- Files changed.
- Verification commands and results.
- Any remaining first-slice limitations.
```

## Why This Prompt Should Stay Eligible For Future Project Learning

- It asks for product implementation work, not assistant-memory maintenance.
- It avoids known skip-trigger phrases and internal memory-tool filenames.
- It includes durable workflow signals: implementation plan, UI behavior, tests, and verification commands.
- It explicitly keeps local assistant-session artifacts out of scope.
