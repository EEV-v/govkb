ROLE
Principal engineer writing a reuse-first implementation plan for a GovKB feature.

GOAL
Create `implementation-plan.md` that turns accepted requirements, use cases, and PoC evidence into a phased engineering plan with explicit tests, rollback, and repo evidence.

DOCUMENT CHAIN
- Inputs:
  - `business.md`
  - `context.md`
  - `use-cases.md`
  - `requirements-catalog.md`
  - `poc-plan.md`
  - `poc-output.md`
- Output:
  - `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/implementation-plan.md`
- Next:
  - `IMPL_PLAN_REVIEW_PROMPT.MD`

INPUT
- FeatureSlug: <kebab-case folder name>
- FeatureName: <human-readable title>
- CodebaseContext: govkb Python CLI/library, src-layout package, unittest tests

REQUIRED INVENTORY FIRST
Do not write the plan until these sections can be filled with concrete paths:

1. Existing code inventory
- CLI parser and command modules if command surface changes.
- Core modules under `src/govkb/core/` if parsing, contracts, project state, learning, or templates change.
- Adapter modules under `src/govkb/adapters/` if materialization or memory review changes.
- Tests under `tests/` that show the closest existing pattern.

2. Documentation inventory
- `README.md`
- `docs/README.md`
- relevant `docs/governed-skill-knowledge-framework/**` docs
- feature folder artifacts

3. Command inventory
- Build/help commands.
- Unit test commands.
- CLI preview/dry-run commands.
- Any manual verification commands.

4. Risk inventory
- Governance/security risks.
- Raw transcript or local-state leakage risks.
- Backward compatibility risks for existing `.governed` packages or local materialization.

OUTPUT FORMAT

```markdown
# <FeatureName> - Implementation Plan

Last updated: <YYYY-MM-DD>

## 0. Existing Code Inventory

| Category | Component | Location | Reuse Strategy |
|---|---|---|---|

## 0.5. Pre-flight Checklist

| Prerequisite | Status | Owner |
|---|---|---|

## 1. Scope And Boundaries

## 2. Requirements Mapping

| Requirement | Behavior | Location | New/Modify | Notes |
|---|---|---|---|---|

## 3. Design

## 4. Integration Points

## 5. Application Logic

## 6. Data Consistency And Safety

## 7. Testing Strategy

| Test Type | Location | Coverage |
|---|---|---|

## 8. Verification Commands

| Command | Working Dir | Purpose | Preconditions |
|---|---|---|---|

## 9. Implementation Phases

### Phase 0 - Shape And Contracts

Scope:

Files:

Verify:

Rollback:

### Phase 1 - Core Behavior

### Phase 2 - Command Or Adapter Integration

### Phase 3 - End-to-End Or Workflow Behavior

### Phase 4 - Docs, Packaging, Or Optional UI

## 10. Rollback Plan

## 11. Open Questions

## 12. Ready Checklist
```

PLAN RULES
- Prefer extending existing modules over adding new top-level packages.
- Justify every new file.
- Keep direct command-function tests for CLI behavior unless subprocess behavior itself is under test.
- Use temp dirs for project roots, Codex homes, fixtures, and generated files.
- Keep `.governed/**` as project source of truth and `$CODEX_HOME/**` as derived local output.
- Include `python3 -m unittest discover -s tests -v` as final verification unless impossible.
- Record exact rollback for each phase.

END
