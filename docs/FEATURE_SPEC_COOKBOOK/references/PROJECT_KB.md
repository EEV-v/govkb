# GovKB Project KB

Use this knowledge base to ground `context.md` before drafting spec artifacts.

## Core Sources

- `README.md`
  - Repository purpose, current scope, and local development commands.
- `docs/README.md`
  - Documentation map.
- `docs/governed-skill-knowledge-framework/business.md`
  - Product scope, users, requirements, governance rules, CLI surface, acceptance criteria.
- `docs/governed-skill-knowledge-framework/implementation-plan.md`
  - Architecture, package boundaries, command workflows, migration rules, testing strategy.
- `docs/governed-skill-knowledge-framework/mvp-plus-test-plan.md`
  - Real validation workflows and low-cost classifier settings.
- `docs/governed-skill-knowledge-framework/features/*`
  - Neighboring feature intent, terminology, scope patterns, and precedent decisions.
- `src/govkb/**` and `tests/**`
  - Current code and test patterns.

## How To Use It

- Read the root docs first.
- Discover candidate neighboring feature specs with:

```bash
rg --files docs/governed-skill-knowledge-framework/features -g 'business.md'
```

- Read only the feature specs relevant to the current feature's domain, workflow, CLI surface, adapter behavior, packaging behavior, or UI.
- Prefer a few high-signal neighboring feature specs over loading many unrelated ones.
- Use these KB sources together with the current feature `business.md`, reviewed feedback files when present, and relevant current code to build `context.md`.

## Minimum Grounding Expectations

- Identify existing product entities, command contracts, APIs, storage, source-of-truth rules, and UI/packaging patterns from current code and documentation.
- Compare the current draft against established GovKB terms and nearby feature precedents.
- Turn unknowns into explicit assumptions or open questions instead of inferring behavior from one draft alone.

