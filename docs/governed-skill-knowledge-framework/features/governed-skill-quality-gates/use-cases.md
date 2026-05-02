# Governed Skill Quality Gates - Use Cases

Last updated: 2026-05-01

## Scope

Strict package-quality validation for governed skill packages, plus activation gating for candidate auto-create. Normal validation and existing materialization remain backward-compatible during the rollout.

## Actors

| Actor | Goal |
|---|---|
| Maintainer | See whether a governed capability package is structurally complete and activation-ready. |
| Reviewer | Approve only packages with clear scope, safe memory, and auditable lifecycle metadata. |
| Candidate automation | Create reviewable packages without silently activating weak governed skills. |
| Future conversion workflow | Rely on strict validation before writing converted local skills into `.governed`. |

## Background

Given a GovKB project with `.governed/project.toml`
And governed capabilities live under `.governed/capabilities/<capability-id>/`
And candidate packages live under `.governed/candidates/<candidate-id>/`
And normal `govkb validate` remains backward-compatible unless strict mode is requested

## Scenarios

### UC-1: Strict validation passes a complete approved package @smoke

Given a capability package with lower kebab-case id, required files, configured memory sections, safe repo-relative references, `prompts/initialize-kb.md`, and lifecycle approval metadata
When the maintainer runs `govkb validate --strict <project-root>`
Then validation exits successfully
And output reports strict validation passed
And each strict issue line, if any, includes severity, rule id, location, and message

### UC-2: Normal validation remains backward-compatible @smoke

Given an existing governed project whose capability package loads under the current contract parser but still contains strict-mode cleanup work
When the maintainer runs `govkb validate <project-root>` without `--strict`
Then base validation behavior is unchanged
And strict-only failures do not block existing materialization or delete local skills

### UC-3: Placeholder memory blocks activation readiness @regression

Given a capability package has `references/long-term-memory.md`
And memory sections contain TODO-style or scaffold placeholder bullets
When strict validation inspects the package
Then it reports an `error` for placeholder memory content
And the issue location identifies the memory file and section

### UC-4: Invalid project references block activation readiness @regression

Given governed memory or package docs contain repo-relative path references
When strict validation inspects the package
Then paths that do not exist are reported as errors unless clearly marked planned
And absolute paths or parent-traversal paths are reported as errors

### UC-5: Credential paths and token-like content are rejected @regression

Given governed memory or package docs mention local credential roots, private key files, `.env` files, token paths, or token-like strings
When strict validation inspects the package
Then each unsafe reference is reported as an `error`
And no raw secret value is copied into generated reports beyond the minimum safe issue context

### UC-6: Package-owned tools require visible safety documentation @regression

Given a capability package contains `tools/scripts/` or `tools/fixtures/`
When strict validation inspects the package
Then missing `tools/README.md` is reported
And mutating scripts without documented `--dry-run` or `--preview` behavior are reported
And validation never executes package-owned scripts

### UC-7: Candidate auto-create refuses strict-invalid packages @regression

Given project automation allows `candidates auto-create-ready`
And a ready candidate would generate a capability package that fails strict validation
When `govkb candidates auto-create-ready --project-root <project-root>` runs
Then the candidate remains reviewable and is not marked activated
And no Codex materialization is applied for that generated package
And output lists the strict validation reasons

### UC-8: Generic ids require justification and approval before activation @regression

Given a candidate proposes a weak generic capability id such as `local-stack-workflow`
When strict validation evaluates activation readiness
Then the package requires an explicit scope statement, at least two non-domain-specific use cases, and reviewer approval
And activation is blocked until both candidate metadata and capability metadata show approval

## Scenario Outlines

### UC-9: Strict issue reporting uses stable severity and rule ids @regression

Given a package has <problem>
When strict validation runs
Then it emits severity <severity>
And it emits rule id <rule_id>

Examples:

| problem | severity | rule_id |
|---|---|---|
| missing `instructions.md` | error | GSK-PACKAGE-001 |
| TODO placeholder memory | error | GSK-MEMORY-001 |
| missing `tools/README.md` | warning | GSK-TOOLS-001 |
| deprecated lifecycle state | info | GSK-LIFECYCLE-003 |

## Negative And Governance Cases

- Strict validation must not execute scripts under `tools/scripts/`.
- Strict validation must not require real local Codex home state.
- Strict validation must not mutate `.governed` packages or `$CODEX_HOME`.
- Candidate activation must be auditable before and after activation.
- Future conversion writes must be able to reuse the same strict validation result.

## Traceability

| Requirement | Scenario(s) | Coverage |
|---|---|---|
| Maintainer can run strict validation and see exact package-quality issues | UC-1, UC-3, UC-4, UC-5, UC-6, UC-9 | Covered |
| Complete domain-specific governed skill package passes strict validation | UC-1 | Covered |
| Placeholder memory fails strict activation readiness | UC-3, UC-7 | Covered |
| Invalid repo-relative command paths fail strict activation readiness | UC-4 | Covered |
| Local credential-file paths or token-like strings fail strict activation readiness | UC-5 | Covered |
| `tools/scripts/` without `tools/README.md` is reported | UC-6 | Covered |
| Candidate auto-create cannot mark strict-invalid package active | UC-7 | Covered |
| Generic capability ids require explicit justification and approval before activation | UC-8 | Covered |
| Existing projects can still use normal validation and materialization during rollout | UC-2 | Covered |
| Clearing weak `local-stack-workflow` shape can be flagged without cleanup scope | UC-8 | Covered as generic-id strict signal; Clearing cleanup remains out of scope |

## Test Notes

| Scenario | Suggested Test Module | Notes |
|---|---|---|
| UC-1 | `tests/test_governed_skill_quality_gates_smoke.py` | Build a temp project and complete strict-valid package fixture. |
| UC-2 | `tests/test_governed_skill_quality_gates_use_cases.py` | Assert `run_validate` without strict ignores strict-only package problems. |
| UC-3 | `tests/test_governed_skill_quality_gates_use_cases.py` | Use direct strict validation helper against placeholder memory. |
| UC-4 | `tests/test_governed_skill_quality_gates_use_cases.py` | Cover missing, absolute, and planned repo path references. |
| UC-5 | `tests/test_governed_skill_quality_gates_use_cases.py` | Cover credential path patterns and token-like indicators without storing real secrets. |
| UC-6 | `tests/test_governed_skill_quality_gates_use_cases.py` | Create tool folders and script text; assert scripts are not executed. |
| UC-7 | `tests/test_candidates.py` | Update auto-create tests to require strict validation and approval before activation. |
| UC-8 | `tests/test_governed_skill_quality_gates_use_cases.py` | Cover generic id with and without justification plus approval metadata. |
| UC-9 | `tests/test_governed_skill_quality_gates_smoke.py` | Assert strict issue serialization includes severity, rule id, location, and message. |
