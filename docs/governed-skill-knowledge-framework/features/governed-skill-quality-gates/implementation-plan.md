# Governed Skill Quality Gates - Implementation Plan

Last updated: 2026-05-01

## 0. Existing Code Inventory

| Category | Component | Location | Reuse Strategy |
|---|---|---|---|
| CLI parser | `govkb validate`, `govkb candidates auto-create-ready` | `src/govkb/cli.py` | Add `--strict` and optional `--json` to `validate`; leave normal invocation unchanged. |
| Validation command | project bundle reporting | `src/govkb/commands/validate.py` | Run strict validation only when requested and print structured issue lines. |
| Base contracts | `CapabilityContract`, `ValidationResult` | `src/govkb/core/contracts.py` | Keep base parsing compatible; add optional lifecycle/approval fields without requiring them in normal validation. |
| Strict package checks | none | new `src/govkb/core/governed_skill.py` | New file is justified because rules inspect package files and safety content, not just TOML schema. |
| Candidate activation | auto-create and manual create-from-candidate | `src/govkb/commands/candidates.py`, `src/govkb/commands/create_capability.py`, `src/govkb/core/candidates.py` | Gate `auto-create-ready` before activation; preserve manual create behavior except where explicit strict activation is requested internally. |
| Candidate metadata | `candidate.toml` writer/loader | `src/govkb/core/candidates.py` | Add optional `[review]` metadata and helper to detect approval. |
| Placeholder detection | KB bootstrap health | `src/govkb/core/kb_bootstrap.py` | Reuse or mirror existing placeholder patterns in strict validation so activation has deterministic errors. |
| Tests | validation and candidate workflows | `tests/test_validate.py`, `tests/test_candidates.py`, `tests/test_apply.py` | Add feature-specific unittest modules and update candidate auto-create expectations. |

## 0.5. Pre-flight Checklist

| Prerequisite | Status | Owner |
|---|---|---|
| Feature spec handoff is ready | Done | Product/Engineering |
| Use cases generated | Done | Engineering |
| PoC package generated | Done | Engineering |
| Targeted baseline tests pass | Done | Engineering |
| Full test-suite baseline is clean | Blocked by existing unrelated failures | Engineering |

## 1. Scope And Boundaries

Implement strict package validation and the first candidate auto-create gate. Do not convert local skills, remediate Clearing packages, execute package-owned scripts, or make strict mode the default normal validation path.

## 2. Requirements Mapping

| Requirement | Behavior | Location | New/Modify | Notes |
|---|---|---|---|---|
| REQ-GSK-QG-01 | `govkb validate --strict` prints strict issue severity, rule id, location, and message. | `src/govkb/cli.py`, `src/govkb/commands/validate.py`, `src/govkb/core/governed_skill.py` | Modify/New | `--json` can emit machine-readable strict issues for future tooling. |
| REQ-GSK-QG-02 | Complete approved package has no strict errors. | `src/govkb/core/governed_skill.py` | New | Tests create temp package fixture. |
| REQ-GSK-QG-03 | Placeholder memory/instructions are strict errors. | `src/govkb/core/governed_skill.py` | New | Use deterministic patterns from `kb_bootstrap.py`. |
| REQ-GSK-QG-04 | Bad package Markdown path references are strict errors. | `src/govkb/core/governed_skill.py` | New | Limit to backticked repo-relative paths to avoid broad prose false positives. |
| REQ-GSK-QG-05 | Credential paths and token-like content are strict errors. | `src/govkb/core/governed_skill.py` | New | Report pattern class and file location, not full secret value. |
| REQ-GSK-QG-06 | Tool folders require `tools/README.md`; mutating scripts need dry-run/preview docs. | `src/govkb/core/governed_skill.py` | New | Do not execute scripts. |
| REQ-GSK-QG-07 | Auto-create skips unapproved or strict-invalid candidates. | `src/govkb/commands/candidates.py`, `src/govkb/commands/create_capability.py` | Modify | Output skip reasons and leave candidates reviewable. |
| REQ-GSK-QG-08 | Generic ids require justification and approval. | `src/govkb/core/governed_skill.py`, `src/govkb/core/candidates.py` | New/Modify | Candidate approval is `[review]`; capability approval is `[lifecycle.approval]`. |
| REQ-GSK-QG-09 | Normal validation remains compatible. | `src/govkb/commands/validate.py`, tests | Modify | No strict checks unless flag is set. |
| REQ-GSK-QG-10 | Weak generic shape can be flagged without Clearing cleanup. | strict validation tests | New | Use synthetic `local-stack-workflow` fixture. |

## 3. Design

Add `src/govkb/core/governed_skill.py` with:

- `StrictIssue(severity, rule_id, location, message)`
- `StrictValidationResult(issues)` with `errors`, `warnings`, `infos`, and `ok`
- `validate_governed_skill_package(project_root, contract)` for one capability
- `validate_governed_skill_bundle(project_root, bundle, activation_required=False)` for commands

Lifecycle metadata remains optional for base parsing:

```toml
[lifecycle]
state = "draft" # draft | strict-valid | approved | active | rejected | deprecated
scope_justification = "..."

[lifecycle.approval]
status = "approved"
reviewer = "..."
approved_at = "2026-05-01T00:00:00Z"
```

Candidate review metadata is optional until activation:

```toml
[review]
status = "approved"
reviewer = "..."
approved_at = "2026-05-01T00:00:00Z"
notes = "..."
```

`auto-create-ready` checks candidate approval before creating the capability. When approved, the generated capability contract receives matching lifecycle approval metadata, then strict validation runs before candidate activation and Codex materialization.

## 4. Integration Points

- `run_validate(args)`: base validation first; strict validation only if `args.strict`.
- `run_candidates(args)`: `auto-create-ready` skips candidates without approval metadata; strict-invalid generated packages are rolled back and reported.
- `run_create_capability(args)`: supports internal `require_strict_activation` for auto-create; normal explicit scaffolding remains unchanged.
- `load_project_bundle`: parses lifecycle metadata if present and ignores absence during normal validation.

## 5. Application Logic

Strict validation rules:

- `GSK-PACKAGE-001`: required files missing.
- `GSK-ID-001`: capability id is not lower kebab-case.
- `GSK-ID-002`: generic id lacks justification or approval when activation is required.
- `GSK-LIFECYCLE-001`: lifecycle approval metadata missing when activation is required.
- `GSK-MEMORY-001`: memory target file missing, required section missing, or placeholder bullet present.
- `GSK-PATH-001`: backticked repo-relative package path is missing and not marked planned.
- `GSK-SAFETY-001`: forbidden credential path pattern or token-like content found.
- `GSK-TOOLS-001`: tools exist without `tools/README.md`.
- `GSK-TOOLS-002`: likely mutating script does not document `--dry-run` or `--preview`.

## 6. Data Consistency And Safety

Strict validation is read-only. Candidate auto-create may create a temporary package, but if strict activation validation fails the package directory is removed and the candidate stays reviewable. Reports must avoid echoing raw token-like strings; they can name the rule, file, and pattern class.

## 7. Testing Strategy

| Test Type | Location | Coverage |
|---|---|---|
| Strict validation unit/use-case tests | `tests/test_governed_skill_quality_gates_use_cases.py` | Missing files, placeholders, paths, credentials, tools, generic ids, normal validation compatibility. |
| Strict validation smoke tests | `tests/test_governed_skill_quality_gates_smoke.py` | Approved package passes and CLI strict output includes structured issue fields. |
| Feature helper | `tests/governed_skill_quality_gates_test_helper.py` | Temp project/package fixture builders. |
| Candidate workflow tests | `tests/test_candidates.py` | Auto-create skips unapproved candidates and activates approved strict-valid candidates. |
| Regression tests | existing `tests/test_validate.py`, `tests/test_apply.py` | Base validation and materialization remain intact. |

## 8. Verification Commands

| Command | Working Dir | Purpose | Preconditions |
|---|---|---|---|
| `/Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_governed_skill_quality_gates_use_cases tests.test_governed_skill_quality_gates_smoke -v` | `/Users/vasilevevgeny/code/govkb` | Feature tests | Bundled Python 3.12 available |
| `/Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_validate tests.test_candidates -v` | `/Users/vasilevevgeny/code/govkb` | Existing validation/candidate regression | Bundled Python 3.12 available |
| `/Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m govkb.cli validate --strict <temp-project-root>` | `/Users/vasilevevgeny/code/govkb` | CLI smoke | Temp project fixture exists |
| `/Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest discover -s tests -v` | `/Users/vasilevevgeny/code/govkb` | Final suite | Known unrelated failures may remain |

## 9. Implementation Phases

### Phase 0 - Shape And Contracts

Scope:

Add lifecycle metadata parsing and strict issue/result types.

Files:

- `src/govkb/core/contracts.py`
- `src/govkb/core/governed_skill.py`
- `tests/governed_skill_quality_gates_test_helper.py`

Verify:

- feature strict helper tests import and run

Rollback:

- remove new module, helper, and optional contract fields

### Phase 1 - Core Behavior

Scope:

Implement package shape, memory, path, safety, and tool rules.

Files:

- `src/govkb/core/governed_skill.py`
- `tests/test_governed_skill_quality_gates_use_cases.py`

Verify:

- `python -m unittest tests.test_governed_skill_quality_gates_use_cases -v`

Rollback:

- revert strict rule module and feature tests

### Phase 2 - Command Or Adapter Integration

Scope:

Add `govkb validate --strict` and structured output.

Files:

- `src/govkb/cli.py`
- `src/govkb/commands/validate.py`
- `tests/test_governed_skill_quality_gates_smoke.py`

Verify:

- CLI strict smoke test
- existing normal validate tests

Rollback:

- remove CLI flags and strict invocation

### Phase 3 - End-to-End Or Workflow Behavior

Scope:

Gate `candidates auto-create-ready` on approval and strict validation, preserving reviewable candidates on failure.

Files:

- `src/govkb/core/candidates.py`
- `src/govkb/commands/candidates.py`
- `src/govkb/commands/create_capability.py`
- `tests/test_candidates.py`

Verify:

- candidate auto-create tests

Rollback:

- restore previous auto-create path; strict CLI remains independently usable

### Phase 4 - Docs, Packaging, Or Optional UI

Scope:

Update docs and PoC parity review after implementation.

Files:

- feature folder artifacts

Verify:

- `git diff --check`
- targeted feature tests
- full discover if environment permits

Rollback:

- revert feature docs generated in this phase only

## 10. Rollback Plan

All production changes are additive behind `--strict` or the `auto-create-ready` activation path. If strict validation causes unexpected friction, disable the auto-create strict gate by reverting Phase 3 while keeping manual strict validation available for diagnostics.

## 11. Open Questions

- When strict validation becomes the default for normal `govkb validate` remains deferred.
- Deprecated routing behavior remains deferred and is not needed for this implementation.

## 12. Ready Checklist

- Requirements mapped to use cases and tests.
- Strict validation is read-only.
- Normal validation remains backward-compatible.
- Candidate auto-create has a concrete approval and strict validation gate.
- Package-owned scripts are inspected but never executed.
- Verification commands are concrete and local.

