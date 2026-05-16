# Agentic Architecture Refactoring - PoC Plan

## Mode

parity-vs-current

## Evidence Strategy

Use static repository inspection and existing test patterns to establish current behavior before implementation. The PoC does not mutate project state. It compares desired architecture practices against current GovKB locations and records the gap that the implementation plan must close.

## Assertions

| Assertion | Method | Command/File | Expected Result |
|---|---|---|---|
| Current GovKB has no consolidated agentic state ownership map. | Static docs inspection. | `README.md`, `docs/README.md`, `docs/governed-skill-knowledge-framework/**` | Existing docs describe product and features, but not one source/derived/disposable ownership map. |
| Current VS Code action metadata is spread across multiple files. | Static code inspection. | `vscode-extension/src/homeState.ts`, `vscode-extension/src/extension.ts`, `vscode-extension/package.json` | Same logical actions appear in multiple places with repeated labels and ids. |
| Current promotion lifecycle already has sidecar state that can be extended. | Static code inspection. | `src/govkb/core/promotion_lifecycle.py`, `src/govkb/commands/promotions.py` | States and metadata path helpers exist. |
| Current promotion cleanup command is absent. | CLI/code inspection. | `src/govkb/commands/promotions.py`, `src/govkb/cli.py` | Supported actions are list, show, mark-reviewed, apply, and archive. |
| Current tests have reusable dry-run/temp-dir patterns. | Static test inspection. | `tests/test_promotions.py`, `tests/test_skill_conversion.py`, `vscode-extension/src/test/suite/homeState.test.ts` | Temp project roots, Codex homes, git repos, and pure Home model tests exist. |
| Caveman patterns are safely reusable only as architecture practices. | External repo inspection. | `/Users/vasilevevgeny/code/caveman/CLAUDE.md`, `bin/install.js`, `bin/lib/settings.js`, `bin/lib/openclaw.js`, `tests/installer/e2e.dryrun.test.mjs` | Source-of-truth maps, registries, idempotency, marker blocks, and dry-run tests are reusable; tone/hooks/installer behavior are not. |

## Data And Fixtures

- No raw assistant sessions are needed.
- No real `CODEX_HOME` state is needed.
- Implementation tests should continue using `tempfile.TemporaryDirectory` for Python and synthetic fixture payloads for TypeScript.

## Rerun Command

No standalone regeneration script is required for the planning PoC. The evidence is static inspection of tracked source and docs. After implementation starts, the verification commands should be:

```bash
cd /Users/vasilevevgeny/code/govkb
PYTHONPATH=src python3 -m unittest discover -s tests -v
cd vscode-extension
npm test
```

## Risks And Blockers

- Cleanup semantics are resolved for implementation planning: preserve sidecar lifecycle metadata, mark it cleaned, and remove only eligible worktrees from the actionable list.
- A full action registry may require either manifest generation or parity tests; generating `package.json` would be a larger build-system change.
- Governed skill summaries need a storage decision: contract description, optional README, or a derived UI summary.
