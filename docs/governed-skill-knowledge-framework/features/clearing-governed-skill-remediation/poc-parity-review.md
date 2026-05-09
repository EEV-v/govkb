# Clearing Governed Skill Remediation - PoC Parity Review

Last updated: 2026-05-02

## Verdict

Ready for Merge: Yes

## Summary

The implementation matches the report-first PoC and accepted plan. It adds reusable remediation report behavior without editing `.governed/capabilities/**`, and durable report writes are blocked unless Git ownership of `.governed` is verified.

## Requirement Parity

| Requirement | PoC Assertion | Implementation Evidence | Result | Notes |
|---|---|---|---|---|
| REQ-CGSR-01 | Weak generic capability is detected by strict validation. | `build_remediation_report`, `test_uc_1_build_remediation_report_from_strict_validation` | Passed | Uses activation-readiness strict validation. |
| REQ-CGSR-02 | Report-first plan before package changes. | `test_uc_3_invalid_repo_paths_become_repair_actions_not_automatic_edits` | Passed | Capability file snapshot remains unchanged. |
| REQ-CGSR-03 | Weak generic active capability maps to demote/deprecate. | `remediation_option_for_rule`, `test_uc_2_prefer_demote_or_deprecate_for_weak_generic_capability` | Passed | `GSK-ID-002` maps to `demote-or-deprecate`. |
| REQ-CGSR-04 | Invalid paths are repair actions, not edits. | `test_uc_3_invalid_repo_paths_become_repair_actions_not_automatic_edits` | Passed | Maps `GSK-PATH-001` to `repair-paths-after-approval`. |
| REQ-CGSR-05 | Auto-create policy is visible and constrained. | `test_uc_4_candidate_auto_create_policy_is_visible_and_constrained` | Passed | JSON includes policy and strict activation requirement. |
| REQ-CGSR-06 | Useful steward memory remains available. | `test_uc_7_useful_project_knowledge_steward_memory_is_preserved` | Passed | Strict-valid steward receives no recommendation. |
| REQ-CGSR-07 | Strict status and issue list are explicit. | `RemediationReport.as_dict`, markdown renderer, use-case tests | Passed | Status, load messages, strict issues, and recommendations are emitted. |
| REQ-CGSR-08 | Durable writes require Git ownership. | `inspect_git_ownership`, `write_remediation_report`, UC-5/UC-6 tests | Passed | Non-Git roots and Git roots without `.governed` refuse report writes. |
| REQ-CGSR-09 | Output is safe for tools. | `test_uc_8_machine_readable_report_output_is_safe_for_tools` | Passed | Synthetic unsafe token is not emitted. |
| REQ-CGSR-10 | Clearing production code is untouched. | Command design and tests | Passed | Default writes nothing; optional write stays under `.governed/reports/remediation/`. |

## Scenario Parity

| Scenario | Test/Verification | Result | Notes |
|---|---|---|---|
| UC-1 | `test_uc_1_build_remediation_report_from_strict_validation` | Passed | Strict issue evidence present. |
| UC-2 | `test_uc_2_prefer_demote_or_deprecate_for_weak_generic_capability` | Passed | Weak id maps to demote/deprecate. |
| UC-3 | `test_uc_3_invalid_repo_paths_become_repair_actions_not_automatic_edits` | Passed | No capability file mutation. |
| UC-4 | `test_uc_4_candidate_auto_create_policy_is_visible_and_constrained` | Passed | Policy payload visible. |
| UC-5 | `test_uc_5_non_git_project_blocks_durable_report_write` | Passed | Durable write refused. |
| UC-5 | `test_uc_5_git_project_without_governed_root_blocks_report_write` | Passed | No `.governed` tree is created by mistake. |
| UC-6 | `test_smoke_git_owned_project_writes_report_only` | Passed | Markdown report written only. |
| UC-7 | `test_uc_7_useful_project_knowledge_steward_memory_is_preserved` | Passed | Steward not flagged. |
| UC-8 | `test_uc_8_machine_readable_report_output_is_safe_for_tools` | Passed | JSON safe. |
| UC-9 | `test_uc_9_strict_issue_category_maps_to_remediation_option` | Passed | Rule mapping table covered. |

## Command Evidence

| Command | Working Dir | Result | Evidence |
|---|---|---|---|
| `/Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m py_compile src/govkb/core/remediation.py src/govkb/commands/remediate.py src/govkb/cli.py tests/clearing_governed_skill_remediation_test_helper.py tests/test_clearing_governed_skill_remediation_use_cases.py tests/test_clearing_governed_skill_remediation_smoke.py` | `/Users/vasilevevgeny/code/govkb` | Passed | Syntax check. |
| `/Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_clearing_governed_skill_remediation_use_cases tests.test_clearing_governed_skill_remediation_smoke -v` | `/Users/vasilevevgeny/code/govkb` | Passed | 11 tests. |
| `/Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_governed_skill_quality_gates_use_cases tests.test_governed_skill_quality_gates_smoke tests.test_candidates -v` | `/Users/vasilevevgeny/code/govkb` | Passed | 30 regression tests. |
| `/Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m govkb.cli remediate project --help` | `/Users/vasilevevgeny/code/govkb` | Passed | Help includes `--write-report`, `--report-root`, and `--json`. |
| `docs/governed-skill-knowledge-framework/features/clearing-governed-skill-remediation/regenerate-poc-data.sh` | `/Users/vasilevevgeny/code/govkb` | Passed | 11 tests. |
| `git diff --check` | `/Users/vasilevevgeny/code/govkb` | Passed | No whitespace errors. |
| `/Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest discover -s tests -v` | `/Users/vasilevevgeny/code/govkb` | Failed | 9 known unrelated install/memory-review failures; remediation tests passed. |

## Deviations

| Deviation | Approved? | Reason | Follow-up |
|---|---|---|---|
| Real Clearing repository was not validated. | Yes | The local GovKB checkout does not include the Clearing owning repository. | Run `govkb remediate project /path/to/Clearing --write-report` when available. |
| Capability mutation actions were not implemented. | Yes | First remediation policy requires report and maintainer approval before package rewrites. | Add demote/deprecate/repair commands only after report review. |
| Rerun script uses a Python runtime fallback. | Yes | Local system `python3` is 3.9 and lacks `tomllib`. | Keep fallback until repo standardizes runtime invocation. |
| `--write-report` now also requires an existing `.governed` package. | Yes | Operational validation showed Git ownership alone should not create governed state in a non-governed Clearing subrepo. | Keep as a permanent safety guard. |

## Risks

- The real Clearing package may contain more issue categories than synthetic fixtures cover.
- The full suite remains blocked by unrelated install and memory-review baseline failures.

## Required Fixes Before Merge

None for this feature.

## Post-merge Follow-ups

- Generate and review the actual Clearing remediation report from the owning repository.
- Add approved package mutation workflow after the maintainer chooses demotion, deprecation, rename, replacement, or repair.
