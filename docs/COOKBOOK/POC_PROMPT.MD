ROLE
Principal engineer producing a rerunnable proof package for a GovKB feature.

GOAL
Create a PoC package that proves the planned behavior against current code, fixtures, docs, or sanitized sample data before implementation planning.

DOCUMENT CHAIN
- Inputs:
  - `business.md`
  - `context.md`
  - `use-cases.md`
  - relevant source files, docs, or sanitized fixtures
- Outputs under `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/`:
  - `requirements-catalog.md`
  - `poc-plan.md`
  - `poc-output.md`
  - `regenerate-poc-data.sh` when evidence must be rerun
- Next: `IMPL_PLAN_PROMPT.MD`

INPUT
- FeatureSlug: <kebab-case folder name>
- FeatureName: <human-readable title>
- PocMode: <baseline-vs-candidate | algorithm-comparison | parity-vs-current | fixture-validation>

DISCOVERY
- Identify current behavior from code and tests before proposing candidate behavior.
- Prefer direct evidence from `src/govkb/**`, `tests/**`, `README.md`, `pyproject.toml`, and current feature docs.
- For memory-review, candidate, or assistant-materialization features, use sanitized JSONL/session fixtures and disposable `CODEX_HOME` directories.
- If evidence depends on a real local assistant state, record it as a blocker unless it can be reproduced with temp dirs or sanitized fixtures.

OUTPUT 1: requirements-catalog.md

```markdown
# <FeatureName> - Requirements Catalog

| ID | Requirement | Source | PoC Assertion | Scenario(s) | Status |
|---|---|---|---|---|---|
```

Rules:
- Assign stable IDs such as `REQ-<SLUG>-01`.
- Every meaningful business requirement must be cataloged.
- Mark non-testable items as `Documentation Only` or `Blocked` with a reason.

OUTPUT 2: poc-plan.md

```markdown
# <FeatureName> - PoC Plan

## Mode

## Evidence Strategy

## Assertions

| Assertion | Method | Command/File | Expected Result |
|---|---|---|---|

## Data And Fixtures

## Rerun Command

## Risks And Blockers
```

Rules:
- Include exact working directory for every command.
- Use deterministic temp paths in examples, not user home state, unless the command is explicitly a local operational check.
- Do not use raw transcript content. Use synthetic or sanitized examples.

OUTPUT 3: poc-output.md

```markdown
# <FeatureName> - PoC Output

## Summary

## Assertion Results

| Assertion | Result | Evidence | Notes |
|---|---|---|---|

## Outliers

## Open Gaps

## Recommendation
```

Rules:
- Distinguish `Passed`, `Failed`, `Blocked`, and `Not Run`.
- Link or name local evidence files when created.
- If a command was not run, say why.

OUTPUT 4: regenerate-poc-data.sh

Create this file only when useful. It must be safe to rerun and should not touch user home state by default.

Preferred template:

```bash
#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../../.."
python3 -m unittest discover -s tests -v
```

QUALITY GATES
- Requirements, scenarios, and assertions are traceable.
- Evidence is rerunnable or the blocker is explicit.
- No external service or local assistant state is required without being called out.
- PoC output can feed implementation planning without guessing.

END
