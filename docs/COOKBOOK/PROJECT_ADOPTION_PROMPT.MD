ROLE
Principal systems engineer adapting this Feature Development Cookbook from one project to another while preserving workflow integrity.

GOAL
Produce a target-project cookbook package that preserves:
- Phase flow and intent
- Required documentation chain and folder structure
- Accurate test scaffold behavior for the target project's real test stack
- Compliance with target project chatbot instructions and documentation

DOCUMENT CHAIN
- **Input:**
  - Source cookbook folder (all prompts/templates)
  - Target project chatbot instructions and repository docs
  - Target project codebase patterns (especially tests)
- **Output:**
  - Adapted cookbook prompt set under `docs/COOKBOOK/` in the target project
  - Adoption mapping and validation artifacts
- **Next:**
  - Feature teams execute the adapted cookbook unchanged for new target-project features

ASSUMPTION
- The target project already contains a cookbook folder at `docs/COOKBOOK/`.

---

DISCOVERY PHASE (MANDATORY BEFORE ANY EDITS)

1) **Instruction inventory (highest priority)**
- Find and read target instruction files (examples):
  - `AGENTS.md` (repo root + parent roots)
  - `.github/copilot-instructions.md`
  - `.cursorrules`, `CLAUDE.md`, project-specific chatbot docs
- Record precedence and hard constraints.

2) **Documentation inventory**
- Read target project docs for:
  - Architecture and repo map
  - Contribution/testing workflows
  - Existing feature documentation structure
- Capture exact required doc filenames and locations.

3) **Code pattern inventory**
- Inspect representative target tests:
  - use-case style / behavior tests
  - end-to-end or integration smoke tests
  - helper/fixture/logger utilities
- Capture concrete patterns with file path evidence.

4) **Command inventory**
- Capture target commands with working directory and prerequisites:
  - build, restore/install, tests, lint/format
  - local environment bootstrapping and data seeding

No cookbook edits until all four inventories are complete.

---

MIGRATION SCOPE

Adapt the following source cookbook assets to target-project equivalents:
- `COOKBOOK.MD`
- `CONTEXT_PROMPT.md`
- `USE_CASES_FOCUSED_PROMPT.MD`
- `POC_PROMPT.MD`
- `IMPL_PLAN_PROMPT.MD`
- `IMPL_PLAN_REVIEW_PROMPT.MD`
- `TEST_SCAFFOLD_PROMPT.MD`
- `IMPLEMENT_PROMPT.MD`
- `POC_PARITY_REVIEW_PROMPT.MD`
- `STAKEHOLDER-PRESENTATION-TEMPLATE.MD`
- `RELEASE-NOTES-TEMPLATE.MD`
- `SIGN-OFF-TEMPLATE.MD`

Maintain the same lifecycle and phase intent unless target constraints require deviation.

---

STRUCTURE RULES (NON-NEGOTIABLE)

1) Preserve the required document chain (business -> context -> use-cases -> POC -> plan -> review -> test scaffold -> implement -> parity -> release docs).
2) Preserve a single canonical feature folder path pattern in all prompts.
3) Keep required artifact list explicit per phase (inputs, outputs, gates).
4) Keep documentation structure stable and navigable:
   - feature folder tree
   - prompt/template locations
   - test scaffold file locations
5) If target naming differs, provide a single mapping table and apply it consistently across all prompts.
6) No stale source-project paths, namespaces, frameworks, or commands in final prompts.

---

TEST_SCAFFOLD MIGRATION (CRITICAL)

For `TEST_SCAFFOLD_PROMPT.MD`, adapt with high precision:

1) **Output file mapping**
- Map source test outputs to actual target folders/modules/packages.
- Keep three-file intent where feasible:
  - full scenario coverage tests
  - happy-path E2E/manual-exploration tests
  - helper API surface scaffold

2) **Framework/fixture mapping**
- Replace source fixture/collection attributes with real target equivalents.
- Use existing target logger/step-reporting utilities; do not invent abstractions.

3) **Scenario traceability**
- Keep 1:1 mapping of scenario -> test method/spec.
- Preserve exact step text logging behavior where target stack allows.
- Keep `@smoke` style filtering intent for E2E selection (or target equivalent).

4) **Helper scaffold adaptation**
- Derive helper methods from test actions grouped by intent:
  setup, seeding, execution, assertions, cleanup.
- Use target-idiomatic types and async model.
- Keep method signatures scaffold-only unless target standard requires lightweight implementation stubs.

5) **Execution and exploration**
- Include target commands to run scaffold tests.
- Include local manual exploration instructions aligned with target environment tooling.

6) **Gap handling**
- If source behavior has no target equivalent, add explicit TODO with:
  - missing capability
  - impact/risk
  - suggested resolution owner

---

CHATBOT INSTRUCTION COMPLIANCE RULES

1) List discovered target instruction files and applied precedence.
2) Resolve conflicts by choosing stricter constraint and documenting the resolution.
3) Ensure every generated prompt uses commands/paths consistent with those instructions.
4) Never assume missing toolchain details; create TODOs instead of guessing.

---

REQUIRED OUTPUT ARTIFACTS

Create these adoption artifacts in `docs/COOKBOOK/` of the target project:

1) `adoption-context.md`
- Instruction inventory + precedence
- Documentation and code pattern evidence
- Key migration constraints

2) `structure-map.md`
- Prompt mapping
- Artifact mapping
- Command mapping with cwd and prerequisites

3) `adoption-validation.md`
- Checklist results
- Residual risks
- Open TODOs

4) Adapted prompt/template files
- Full target-project cookbook set (all files listed in Migration Scope)

---

REQUIRED TABLES

### Prompt Mapping
| Source Prompt | Target Prompt | Changes | Reason | Evidence |
|---------------|---------------|---------|--------|----------|

### Artifact Mapping
| Source Artifact | Target Artifact | Path Pattern | Phase |
|-----------------|-----------------|-------------|-------|

### Command Mapping
| Task | Source Command | Target Command | Working Dir | Preconditions |
|------|----------------|----------------|-------------|---------------|

### Test Scaffold Mapping
| Source Element | Target Equivalent | Target File | Notes |
|----------------|-------------------|-------------|-------|

---

QUALITY GATES (MUST PASS)

- [ ] All adapted prompts preserve phase order and required deliverables.
- [ ] `COOKBOOK.MD` references all prompt/template files that exist.
- [ ] Every command includes explicit working directory.
- [ ] Every referenced path exists or is marked TODO with owner.
- [ ] No stale source-project commands/paths/names remain unintentionally.
- [ ] `TEST_SCAFFOLD_PROMPT.MD` references only real target fixtures/helpers/utilities verified in repository.
- [ ] At least one sample `<FeatureName>` dry-run confirms end-to-end document chain consistency.

---

OUTPUT FORMAT

Return:
1) Discovery Summary
2) Migration Decisions (including instruction-conflict resolutions)
3) Files Created/Updated (absolute or repo-root paths)
4) Open TODOs/Blockers
5) Quality Gate Status

RULES
- Minimal, evidence-based edits
- Unknowns -> explicit TODO (no fabricated details)
- Keep prompts operational and copy/paste ready
- Adapt cookbook docs/prompts only (no feature implementation work)

END
