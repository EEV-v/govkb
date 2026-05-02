# Governed Skill Quality Gates - PoC Parity Review

Last updated: 2026-05-01

## Verdict

Ready for Merge: Yes

## Summary

Implemented behavior matches the accepted PoC and plan for the first engineering slice. Strict validation is available through the CLI, normal validation remains backward-compatible, and candidate auto-create now requires approved review metadata plus strict activation validation before activation and materialization.

## Requirement Parity

| Requirement | PoC Assertion | Implementation Evidence | Result | Notes |
|---|---|---|---|---|
| REQ-GSK-QG-01 | A1 | `govkb validate --strict` and strict issue objects in `src/govkb/core/governed_skill.py`; smoke CLI test asserts structured issue output. | Passed | `--json` also exposes `strictIssues`. |
| REQ-GSK-QG-02 | A4 | `tests/test_governed_skill_quality_gates_use_cases.py::test_uc_1_strict_validation_passes_complete_approved_package` | Passed | Temp package includes approval metadata. |
| REQ-GSK-QG-03 | A2, A4 | `test_uc_3_placeholder_memory_blocks_activation_readiness` | Passed | Placeholder bullets become `GSK-MEMORY-001` errors. |
| REQ-GSK-QG-04 | A2, A4 | `test_uc_4_invalid_project_references_block_activation_readiness` | Passed | Backticked missing paths become `GSK-PATH-001` errors. |
| REQ-GSK-QG-05 | A4 | `test_uc_5_credential_paths_and_token_like_content_are_rejected` | Passed | Reports rule and location without echoing token-like value. |
| REQ-GSK-QG-06 | A4 | `test_uc_6_package_owned_tools_require_visible_safety_documentation` | Passed | Tool scripts are read as text only. |
| REQ-GSK-QG-07 | A3 | `tests/test_candidates.py::test_auto_create_ready_skips_unapproved_candidate`; approved flow test still materializes after strict gate. | Passed | Candidate remains `ready-for-review` when unapproved. |
| REQ-GSK-QG-08 | A4 | `test_uc_8_generic_ids_require_justification_and_approval_before_activation` | Passed | Generic ids require scope justification during activation validation. |
| REQ-GSK-QG-09 | A2 | `test_uc_2_normal_validation_remains_backward_compatible`; existing validation tests pass. | Passed | Strict checks are opt-in except auto-create activation. |
| REQ-GSK-QG-10 | A4 | Generic-id strict rule covers weak synthetic `local-stack-workflow` shape. | Passed | Clearing cleanup remains out of scope. |

## Scenario Parity

| Scenario | Test/Verification | Result | Notes |
|---|---|---|---|
| UC-1 | `test_uc_1_strict_validation_passes_complete_approved_package` | Passed | Direct strict helper with `activation_required=True`. |
| UC-2 | `test_uc_2_normal_validation_remains_backward_compatible` | Passed | Normal command ignores strict-only problems. |
| UC-3 | `test_uc_3_placeholder_memory_blocks_activation_readiness` | Passed | Structured memory error. |
| UC-4 | `test_uc_4_invalid_project_references_block_activation_readiness` | Passed | Missing path error. |
| UC-5 | `test_uc_5_credential_paths_and_token_like_content_are_rejected` | Passed | Safe redacted issue message. |
| UC-6 | `test_uc_6_package_owned_tools_require_visible_safety_documentation` | Passed | Tool warnings without execution. |
| UC-7 | `test_auto_create_ready_skips_unapproved_candidate`; `test_auto_create_ready_creates_capability_and_materializes_codex` | Passed | Covers block and approved success path. |
| UC-8 | `test_uc_8_generic_ids_require_justification_and_approval_before_activation` | Passed | Generic id gate. |
| UC-9 | `test_uc_9_strict_issue_reporting_uses_stable_fields`; CLI smoke issue test | Passed | Stable `severity`, `ruleId`, `location`, `message`. |

## Command Evidence

| Command | Working Dir | Result | Evidence |
|---|---|---|---|
| `/Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m py_compile src/govkb/core/governed_skill.py src/govkb/core/contracts.py src/govkb/commands/validate.py src/govkb/commands/candidates.py src/govkb/commands/create_capability.py tests/governed_skill_quality_gates_test_helper.py tests/test_governed_skill_quality_gates_use_cases.py tests/test_governed_skill_quality_gates_smoke.py tests/test_candidates.py` | `/Users/vasilevevgeny/code/govkb` | Passed | Syntax check for touched Python files. |
| `/Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_governed_skill_quality_gates_use_cases tests.test_governed_skill_quality_gates_smoke -v` | `/Users/vasilevevgeny/code/govkb` | Passed | 10 quality-gates tests passed. |
| `/Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_validate tests.test_candidates -v` | `/Users/vasilevevgeny/code/govkb` | Passed | 22 validation/candidate tests passed. |
| `/Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m govkb.cli validate --help` | `/Users/vasilevevgeny/code/govkb` | Passed | Help shows `--strict` and `--json`. |
| `/Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest discover -s tests -v` | `/Users/vasilevevgeny/code/govkb` | Failed | 94 tests ran, 11 skipped, 9 unrelated existing failures in install/memory-review; quality-gates tests passed. |

## Deviations

| Deviation | Approved? | Reason | Follow-up |
|---|---|---|---|
| Direct TOML `[review]` metadata instead of public approval command | Yes | Plan review listed this as non-blocking for first slice. | Consider `govkb candidates approve` after workflow validation. |
| Path scanner only validates backticked path-like references | Yes | Avoids noisy prose false positives while still covering package-visible references. | Expand only after real project data shows missed issues. |

## Risks

- Full test discovery is not clean because of unrelated `test_install.py` and `test_memory_review.py` failures already observed before this feature implementation.
- Manual candidate approval metadata is functional but not ergonomic.

## Required Fixes Before Merge

None for this feature slice.

## Post-merge Follow-ups

- Add a public candidate approval command if direct review metadata is too manual.
- Decide later when strict validation should become the default for normal `govkb validate`.
