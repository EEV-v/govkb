# Governed Skill Contract And Migration - Implementation Plan

Last updated: 2026-05-01

## 0. Existing Code Inventory

| Category | Component | Location | Reuse Strategy |
|---|---|---|---|
| CLI parser | `build_parser` | `src/govkb/cli.py` | Add `validate --strict` and `convert skill` subcommand |
| Validation | `load_project_bundle`, `ValidationResult` | `src/govkb/core/contracts.py` | Keep TOML parsing stable; add strict package validation layer |
| Capability scaffolding | `run_create_capability` | `src/govkb/commands/create_capability.py` | Reuse file creation patterns for conversion write |
| Candidate auto-create | `run_candidates`, `run_create_capability --from-candidate` | `src/govkb/commands/candidates.py`, `src/govkb/commands/create_capability.py` | Gate activation through strict validation |
| Candidate model | candidate staging and facts | `src/govkb/core/candidates.py` | Reuse facts and draft contracts; add quality checks before activation |
| Codex materialization | `_copy_tree`, `_repo_skill_source`, `_render_wrapped_skill` | `src/govkb/adapters/codex/materialize.py` | Preserve governed `tools/` and optional adapter-specific `SKILL.md` |
| Memory scaffold | placeholder detection | `src/govkb/core/memory_scaffold.py` | Reuse to detect scaffold bullets in strict validation |
| Tests | command-function tests with temp dirs | `tests/test_apply.py`, `tests/test_candidates.py`, `tests/test_validate.py` | Add focused tests in same style |

## 0.5. Pre-flight Checklist

| Prerequisite | Status | Owner |
|---|---|---|
| Feature docs created through Phase 5 | Complete | Engineering |
| Strict package contract agreed | Complete as initial artifact | Engineering |
| Severity policy for strict validation | Open | Engineering |
| Migration metadata location | Open but non-blocking | Engineering |
| Clearing cleanup execution | Deferred | Project maintainer |

## 1. Scope And Boundaries

In scope:

- strict governed-skill package convention
- strict validation helpers
- `govkb validate --strict`
- preview-first `govkb convert skill`
- conversion write path
- candidate auto-create strict gate
- tests for validation, conversion, and materialization of tools

Out of scope:

- full migration of every installed local skill
- Claude or Copilot conversion
- automatic high-quality semantic rewriting of existing memory
- credentialed script execution
- direct cleanup of Clearing package artifacts in this feature branch

## 2. Requirements Mapping

| Requirement | Behavior | Location | New/Modify | Notes |
|---|---|---|---|---|
| REQ-GSCM-01 | Strict package shape | `src/govkb/core/governed_skill.py` | New | Validate required and optional locations |
| REQ-GSCM-02 | Naming checks | `src/govkb/core/governed_skill.py` | New | Warn/fail generic ids depending severity |
| REQ-GSCM-03 | Memory section and placeholder checks | `src/govkb/core/governed_skill.py` | New | Reuse scaffold detection |
| REQ-GSCM-04 | Command/path validation | `src/govkb/core/governed_skill.py` | New | Check backticked paths and configured roots |
| REQ-GSCM-05 | Tooling convention | `src/govkb/core/governed_skill.py`, materialization tests | New/Modify | Require `tools/README.md` when tools exist |
| REQ-GSCM-06 | Unsafe content checks | `src/govkb/core/governed_skill.py`, `src/govkb/core/skill_conversion.py` | New | Use secret/path patterns |
| REQ-GSCM-07 | Strict validation CLI | `src/govkb/commands/validate.py`, `src/govkb/cli.py` | Modify | Add `--strict` and optional JSON detail |
| REQ-GSCM-08 | Candidate auto-create gate | `src/govkb/commands/create_capability.py`, `src/govkb/commands/candidates.py` | Modify | Validate before `mark_candidate_activated` |
| REQ-GSCM-09 | Conversion preview | `src/govkb/commands/convert.py`, `src/govkb/core/skill_conversion.py` | New | Default non-mutating preview |
| REQ-GSCM-10 | Conversion write | `src/govkb/commands/convert.py` | New | Explicit `--write` only |
| REQ-GSCM-11 | Preserve safe assets | `src/govkb/core/skill_conversion.py` | New | Copy safe prompts/tools/fixtures |
| REQ-GSCM-12 | Migration metadata | `src/govkb/core/skill_conversion.py`, contract output | New | Use `[migration]` initially to match current parser |
| REQ-GSCM-13 | Materialization parity | `src/govkb/adapters/codex/materialize.py` tests | Modify tests first | Existing copy behavior likely sufficient |
| REQ-GSCM-14 | Machine-readable output | `src/govkb/commands/validate.py`, `src/govkb/commands/convert.py` | Modify/New | Shape similar to status/candidates JSON |
| REQ-GSCM-15 | Clearing remediation path | Docs and validation failures | Docs/Tests | Cleanup can be a follow-up task |

## 3. Design

Add a strict validation layer that operates after base contracts load.

Suggested data model:

```python
@dataclass(frozen=True)
class StrictValidationIssue:
    severity: str
    rule_id: str
    location: str
    message: str

@dataclass(frozen=True)
class StrictValidationResult:
    issues: tuple[StrictValidationIssue, ...]
```

The strict validator should inspect each `CapabilityContract.capability_root` and check:

- required files exist
- memory target files exist
- memory sections match configured sections
- scaffold placeholder bullets are absent for activated or conversion-written packages
- capability id is lower kebab-case and not weakly generic without justification
- repo-relative paths exist or are explicitly marked planned
- local path and credential path patterns are absent
- secret/token-like strings are absent
- `tools/README.md` exists when `tools/scripts/` or `tools/fixtures/` exists
- mutating scripts document dry-run behavior

Add a conversion planner:

```python
@dataclass(frozen=True)
class SkillConversionPlan:
    source_path: Path
    target_capability_id: str
    target_root: Path
    files_to_write: tuple[PlannedFile, ...]
    rejected_items: tuple[RejectedItem, ...]
    warnings: tuple[str, ...]
```

`--preview` prints this plan. `--write` applies it, then runs strict validation.

## 4. Integration Points

- `src/govkb/cli.py`: add `convert` parser and `validate --strict`.
- `src/govkb/commands/validate.py`: call strict validator when requested.
- `src/govkb/commands/create_capability.py`: after candidate package creation and bootstrap, run strict validation before marking candidate activated.
- `src/govkb/commands/candidates.py`: ensure auto-create reports strict validation failures.
- `src/govkb/adapters/codex/materialize.py`: verify existing copy behavior includes `tools/`; adjust only if tests prove a gap.

## 5. Application Logic

Strict validation:

1. Load base bundle.
2. For each capability, inspect package root.
3. Build issues with stable rule ids.
4. Convert strict errors to command exit code 1.
5. Keep warning-only issues visible but non-fatal if severity policy chooses that.

Skill conversion:

1. Resolve source:
   - existing directory path, or
   - `<codex-home>/skills/<skill-name>`
2. Parse `SKILL.md`.
3. Derive capability id from `--capability-id`, source name, or frontmatter name.
4. Build target files:
   - `capability.contract.toml`
   - `instructions.md`
   - `references/long-term-memory.md`
   - `prompts/initialize-kb.md`
   - optional `adapters/codex/SKILL.md`
   - optional `tools/**`
5. Run safety filters.
6. Preview or write.
7. Validate strictly.

## 6. Data Consistency And Safety

- Source local skills are read-only inputs.
- Conversion write refuses to overwrite existing governed files unless an explicit update mode is added later.
- Tests use temp dirs and synthetic skills.
- Unsafe content is reported and not copied.
- Candidate activation is rolled back if strict validation fails.
- Existing materialized local skill fallback remains available through current migration support.

## 7. Testing Strategy

| Test Type | Location | Coverage |
|---|---|---|
| Strict validation unit tests | `tests/test_governed_skill_contract.py` | package shape, memory, paths, naming, tools, unsafe content |
| Conversion command tests | `tests/test_skill_conversion.py` | preview, write, skill-name resolution, safe scripts, unsafe rejection, rerun conflicts |
| Candidate gate tests | `tests/test_candidates.py` | auto-create refuses strict-invalid candidates |
| Materialization tests | `tests/test_apply.py` | converted tools are copied into Codex output |
| CLI help/JSON tests | `tests/test_validate.py`, new focused tests | `validate --strict`, `convert skill --json` |

## 8. Verification Commands

| Command | Working Dir | Purpose | Preconditions |
|---|---|---|---|
| `python3 -m unittest tests.test_governed_skill_contract -v` | `/home/ev/code/govkb` | Strict validation coverage | Tests implemented |
| `python3 -m unittest tests.test_skill_conversion -v` | `/home/ev/code/govkb` | Conversion coverage | Tests implemented |
| `python3 -m unittest tests.test_candidates -v` | `/home/ev/code/govkb` | Auto-create gate regression | Tests updated |
| `python3 -m unittest tests.test_apply -v` | `/home/ev/code/govkb` | Materialization regression | Tests updated |
| `python3 -m govkb.cli validate /tmp/demo --strict` | `/home/ev/code/govkb` | Strict CLI behavior | Temp project exists |
| `python3 -m govkb.cli convert skill sample --project-root /tmp/demo --codex-home /tmp/codex-home --preview` | `/home/ev/code/govkb` | Conversion preview | Synthetic skill exists |
| `python3 -m unittest discover -s tests -v` | `/home/ev/code/govkb` | Final regression | None |

## 9. Implementation Phases

### Phase 0 - Shape And Contracts

Scope:

- Add strict package contract docs and validator data structures.
- Add tests for valid/invalid package examples.

Files:

- `src/govkb/core/governed_skill.py`
- `tests/test_governed_skill_contract.py`

Verify:

- `python3 -m unittest tests.test_governed_skill_contract -v`

Rollback:

- Remove new module and test file.

### Phase 1 - Strict Validation CLI

Scope:

- Add `govkb validate --strict`.
- Add JSON issue shape if practical in this phase.

Files:

- `src/govkb/cli.py`
- `src/govkb/commands/validate.py`
- `tests/test_validate.py`

Verify:

- `python3 -m unittest tests.test_validate -v`
- `python3 -m govkb.cli validate <temp-project> --strict`

Rollback:

- Remove CLI flag and strict validator calls.

### Phase 2 - Skill Conversion Preview

Scope:

- Add conversion source resolver and conversion plan.
- Add `govkb convert skill ... --preview`.

Files:

- `src/govkb/core/skill_conversion.py`
- `src/govkb/commands/convert.py`
- `src/govkb/cli.py`
- `tests/test_skill_conversion.py`

Verify:

- `python3 -m unittest tests.test_skill_conversion -v`
- `python3 -m govkb.cli convert skill <synthetic> --project-root <temp> --codex-home <temp> --preview`

Rollback:

- Remove convert command and conversion module.

### Phase 3 - Conversion Write And Safety

Scope:

- Implement `--write`.
- Copy safe memory, prompts, scripts, and fixtures.
- Reject unsafe content.
- Run strict validation after write.

Files:

- `src/govkb/core/skill_conversion.py`
- `src/govkb/commands/convert.py`
- `tests/test_skill_conversion.py`

Verify:

- `python3 -m unittest tests.test_skill_conversion -v`

Rollback:

- Remove write path; preview remains possible if useful.

### Phase 4 - Candidate Gate And Materialization Regression

Scope:

- Gate candidate auto-create with strict validation.
- Add materialization tests for `tools/`.
- Adjust materialization only if tests prove tools are skipped.

Files:

- `src/govkb/commands/create_capability.py`
- `src/govkb/commands/candidates.py`
- `src/govkb/adapters/codex/materialize.py` if needed
- `tests/test_candidates.py`
- `tests/test_apply.py`

Verify:

- `python3 -m unittest tests.test_candidates tests.test_apply -v`
- `python3 -m unittest discover -s tests -v`

Rollback:

- Remove strict gate call and materialization adjustments.

## 10. Rollback Plan

- CLI additions can be reverted by removing parser branches and command module imports.
- Strict validation can be disabled by not passing `--strict` and by removing candidate-gate integration.
- Conversion writes only repo-local governed files; rollback is deleting the created capability folder from the target project.
- Existing `govkb apply codex` behavior remains unchanged unless materialization tests reveal a required tools copy fix.

## 11. Open Questions

- Should strict validation become default after existing packages are cleaned?
- Should migration metadata remain in `[migration]` or move to a separate file?
- Should conversion support an explicit update mode for existing governed packages in the first implementation?

## 12. Ready Checklist

- Requirements mapped: Yes
- Use cases mapped to tests: Yes
- PoC assertions recorded: Yes
- Safety rules explicit: Yes
- Rollback explicit: Yes
- Ready for review: Yes
