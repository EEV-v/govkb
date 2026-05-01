# JSON CLI Contracts For VS Code Extension PoC

Last updated: 2026-04-25

These fixture contracts are implementation targets for the first engineering slice. They are intentionally small, deterministic, and free of user transcripts or secrets.

## Status Contract

Target command:

```bash
PYTHONPATH=src python3 -m govkb.cli status /tmp/govkb-poc/project --codex-home /tmp/govkb-poc/codex-home --json
```

Required fields:

- `schemaVersion`
- `projectRoot`
- `governedRoot`
- `project.id`
- `project.currentRelease`
- `validation.status`
- `validation.warnings`
- `validation.errors`
- `kbHealth.warnings`
- `kbHealth.suggestedRemediation`
- `capabilities[]`
- `adapters[]`
- `installState.codex`

The extension must consume this JSON rather than parsing the current human-formatted `govkb status` output.

## Candidates Contract

Target command:

```bash
PYTHONPATH=src python3 -m govkb.cli candidates list /tmp/govkb-poc/project --json
```

Required fields:

- `schemaVersion`
- `projectRoot`
- `candidates[].id`
- `candidates[].status`
- `candidates[].occurrences`
- `candidates[].suggestedCapabilityId`
- `candidates[].activationState`
- `candidates[].path`

The extension should preserve candidate paths for local inspection, but should not read or copy raw source session content into view state.

## Report Summary Contract

The first slice can parse memory-review report files locally after `govkb review-memory --dry-run` completes. The parser should expose aggregate data only:

- classifier model and reasoning
- failed, deferred, learned, and staged counts
- local report path
- raw transcript presence flag set to false for extension-owned summaries

If future GovKB adds a report-summary CLI command, it should return the same aggregate shape.

