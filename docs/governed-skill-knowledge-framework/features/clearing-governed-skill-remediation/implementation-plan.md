# Clearing Governed Skill Remediation - Implementation Plan

Last updated: 2026-05-02

## 0. Existing Code Inventory

| Category | Component | Location | Reuse Strategy |
|---|---|---|---|
| CLI parser | top-level commands | `src/govkb/cli.py` | Add additive `remediate project` command surface. |
| Remediation command | none | new `src/govkb/commands/remediate.py` | New file is justified because remediation reporting is separate from validation and candidate activation. |
| Remediation core | none | new `src/govkb/core/remediation.py` | New file holds read-only report model, recommendation mapping, rendering, and Git ownership checks. |
| Strict validation | package quality gate | `src/govkb/core/governed_skill.py` | Reuse activation-readiness validation instead of duplicating issue detection. |
| Project loading | governed bundle parser | `src/govkb/core/contracts.py` | Reuse bundle loading and validation messages. |
| Automation policy | auto-create manifest parser | `src/govkb/core/automation.py` | Reuse policy normalization for report visibility. |
| Candidate activation | strict auto-create gate | `src/govkb/commands/candidates.py`, `src/govkb/commands/create_capability.py` | Report documents existing approval and strict-activation constraint. |
| Existing tests | strict helper and command patterns | `tests/governed_skill_quality_gates_test_helper.py`, `tests/test_validate.py`, `tests/test_candidates.py` | Reuse temp dirs, direct command functions, and strict fixture patterns. |

## 0.5. Pre-flight Checklist

| Prerequisite | Status | Owner |
|---|---|---|
| Quality-gates implementation exists | Done | Engineering |
| Candidate auto-create strict activation gate exists | Done | Engineering |
| Clearing remediation spec handoff is ready | Done | Product/Engineering |
| Real Clearing checkout available for operational run | Blocked | Clearing maintainer |
| Full test-suite baseline clean | Blocked by unrelated existing failures | Engineering |

## 1. Scope And Boundaries

Implement a generic GovKB remediation report command that can be run against Clearing once its repository is available. The command is read-only by default. Optional report-file writing is limited to `.governed/reports/remediation/` and is blocked unless Git ownership of the governed package is verified.

Out of scope for this slice:

- editing Clearing production code
- rewriting `.governed/capabilities/**`
- demoting, deprecating, renaming, or repairing a capability automatically
- querying production systems
- bulk migrating Clearing skills

## 2. Requirements Mapping

| Requirement | Behavior | Location | New/Modify | Notes |
|---|---|---|---|---|
| REQ-CGSR-01 | Run strict validation in activation-readiness mode and include issue evidence. | `src/govkb/core/remediation.py` | New | Calls `validate_governed_skill_bundle(... activation_required=True)`. |
| REQ-CGSR-02 | Produce maintainer-reviewable plan before package changes. | core renderer, command output | New | Recommendations state approval required before writes. |
| REQ-CGSR-03 | Classify weak generic capability as demote/deprecate candidate. | core recommendation mapper | New | Maps `GSK-ID-002` to `demote-or-deprecate`. |
| REQ-CGSR-04 | Classify invalid paths as repair-after-approval. | core recommendation mapper | New | Maps `GSK-PATH-001` to `repair-paths-after-approval`. |
| REQ-CGSR-05 | Expose auto-create policy and strict activation constraint. | core report payload | New | Uses `automation_policy_from_manifest`. |
| REQ-CGSR-06 | Preserve strict-valid steward memory. | recommendation filtering | New | Recommendations are issue-driven, so clean capabilities are not flagged. |
| REQ-CGSR-07 | Include strict status and explicit issue list. | core report payload | New | JSON and markdown include strict status. |
| REQ-CGSR-08 | Gate durable report writes by Git ownership. | core Git helper, command | New | `--write-report` refuses non-Git/unowned roots. |
| REQ-CGSR-09 | Keep output safe for tools. | renderers | New | Uses strict issue messages and rule ids, not raw file content. |
| REQ-CGSR-10 | Avoid Clearing production changes. | command defaults and tests | New | Default writes nothing; optional report stays outside capabilities. |

## 3. Design

Add `govkb remediate project [project-root]`:

- `project-root` defaults to cwd
- `--write-report` writes the generated markdown report under `.governed/reports/remediation/`
- `--report-root <path>` overrides report directory for tests or operators
- `--json` emits machine-readable output

Core model:

- `GitOwnership`: project Git status, top-level path, governed ownership, dirty status, and blocker.
- `RemediationRecommendation`: capability id, option, severity, rationale, strict rule ids, locations, and approval requirement.
- `RemediationReport`: project paths, load warnings/errors, strict issues, auto-create policy, Git ownership, recommendations, write eligibility, and report path.

Recommendation mapping:

- `GSK-ID-002` -> `demote-or-deprecate`
- `GSK-PATH-001` -> `repair-paths-after-approval`
- `GSK-MEMORY-001` -> `repair-memory-after-approval`
- `GSK-SAFETY-001` -> `remove-unsafe-content`
- `GSK-LIFECYCLE-001` -> `approval-required`
- other strict errors -> `review-required`
- strict warnings -> `review-warning`

## 4. Integration Points

- `src/govkb/cli.py`: parser wiring for `remediate project`.
- `src/govkb/commands/remediate.py`: command argument handling, output selection, report-write errors.
- `src/govkb/core/remediation.py`: pure report construction, markdown/JSON payload rendering, Git ownership inspection, report write helper.
- `tests/test_clearing_governed_skill_remediation_use_cases.py`: traceable scenario coverage.
- `tests/test_clearing_governed_skill_remediation_smoke.py`: command smoke coverage.
- `tests/clearing_governed_skill_remediation_test_helper.py`: temp project fixtures.

## 5. Application Logic

1. Resolve the project root and load the governed project bundle.
2. Collect base validation messages without failing report construction unless files cannot be parsed.
3. Run strict validation in activation-readiness mode for loaded capabilities.
4. Read automation policy from `.governed/project.toml`.
5. Inspect Git ownership with `git rev-parse --show-toplevel` and `git status --short`.
6. Group strict issues by capability root when possible.
7. Map grouped issues to recommendations and include issue-level locations.
8. Render human, markdown, or JSON output.
9. If `--write-report` is requested, refuse unless `.governed` is owned by the detected Git root, then write only the report file.

## 6. Data Consistency And Safety

Default execution writes nothing. `--write-report` writes only to `.governed/reports/remediation/` and never touches `.governed/capabilities/**`. The report does not include source file contents. It reports strict rule ids, safe strict messages, paths, policy settings, and recommendations. If the project is not inside a Git repository that owns `.governed`, durable report writing is blocked.

## 7. Testing Strategy

| Test Type | Location | Coverage |
|---|---|---|
| Use-case tests | `tests/test_clearing_governed_skill_remediation_use_cases.py` | Weak id, invalid path, auto-create policy, non-Git write refusal, JSON safety, recommendation mapping, steward preservation. |
| Smoke tests | `tests/test_clearing_governed_skill_remediation_smoke.py` | CLI command writes a report in a Git-owned temp project and help output includes the command. |
| Helper API | `tests/clearing_governed_skill_remediation_test_helper.py` | Fixture setup for strict-valid steward, weak workflow, automation policy, Git init, command capture. |
| Regression tests | existing strict/candidate tests | Verify quality-gates and auto-create behavior remain intact. |

## 8. Verification Commands

| Command | Working Dir | Purpose | Preconditions |
|---|---|---|---|
| `/Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m py_compile src/govkb/core/remediation.py src/govkb/commands/remediate.py src/govkb/cli.py tests/clearing_governed_skill_remediation_test_helper.py tests/test_clearing_governed_skill_remediation_use_cases.py tests/test_clearing_governed_skill_remediation_smoke.py` | `/Users/vasilevevgeny/code/govkb` | Syntax check touched files | Bundled Python 3.12 |
| `/Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_clearing_governed_skill_remediation_use_cases tests.test_clearing_governed_skill_remediation_smoke -v` | `/Users/vasilevevgeny/code/govkb` | Feature tests | None |
| `/Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_governed_skill_quality_gates_use_cases tests.test_governed_skill_quality_gates_smoke tests.test_candidates -v` | `/Users/vasilevevgeny/code/govkb` | Strict and candidate regression | None |
| `/Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m govkb.cli remediate project --help` | `/Users/vasilevevgeny/code/govkb` | CLI shape smoke | None |
| `/Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest discover -s tests -v` | `/Users/vasilevevgeny/code/govkb` | Final suite | Known unrelated baseline failures may remain |

## 9. Implementation Phases

### Phase 0 - Shape And Contracts

Scope:

Add remediation report dataclasses and CLI parser skeleton.

Files:

- `src/govkb/core/remediation.py`
- `src/govkb/commands/remediate.py`
- `src/govkb/cli.py`

Verify:

- `python3 -m govkb.cli remediate project --help`

Rollback:

- Remove parser wiring, command module, and core module.

### Phase 1 - Core Behavior

Scope:

Implement strict report construction, recommendation mapping, automation policy capture, Git ownership inspection, and renderers.

Files:

- `src/govkb/core/remediation.py`
- `tests/clearing_governed_skill_remediation_test_helper.py`
- `tests/test_clearing_governed_skill_remediation_use_cases.py`

Verify:

- `python3 -m unittest tests.test_clearing_governed_skill_remediation_use_cases -v`

Rollback:

- Remove core helper and feature tests.

### Phase 2 - Command Integration

Scope:

Implement human output, JSON output, `--write-report`, and write refusal behavior.

Files:

- `src/govkb/commands/remediate.py`
- `src/govkb/cli.py`
- `tests/test_clearing_governed_skill_remediation_smoke.py`

Verify:

- `python3 -m unittest tests.test_clearing_governed_skill_remediation_use_cases tests.test_clearing_governed_skill_remediation_smoke -v`

Rollback:

- Remove command integration while preserving core report model only if still useful.

### Phase 3 - Workflow Behavior

Scope:

Verify no capability package file is changed during report writing and feature behavior composes with strict/candidate gates.

Files:

- feature tests
- implementation summary

Verify:

- targeted remediation, strict, and candidate tests

Rollback:

- Revert report writing support if ownership behavior is too strict or too broad.

### Phase 4 - Docs

Scope:

Update implementation summary and PoC parity review.

Files:

- `docs/governed-skill-knowledge-framework/features/clearing-governed-skill-remediation/implementation-summary.md`
- `docs/governed-skill-knowledge-framework/features/clearing-governed-skill-remediation/poc-parity-review.md`

Verify:

- `git diff --check`

Rollback:

- Revert generated feature docs from this phase.

## 10. Rollback Plan

The command is additive and read-only by default. If report-file writing is risky, remove or hide `--write-report` while preserving stdout/JSON remediation planning. If recommendation mapping is too noisy, keep strict issues in the report and mark all recommendations as `review-required`.

## 11. Open Questions

- The real Clearing root must be supplied for operational remediation evidence.
- Actual capability mutation actions remain a follow-up after maintainer approval.

## 12. Ready Checklist

- Report generation is read-only by default.
- Strict validation evidence is included.
- Auto-create policy is visible and constrained by existing strict activation behavior.
- Durable report writes require Git ownership.
- Capability packages are not changed by the first slice.
- Tests use temp dirs and synthetic fixtures only.
