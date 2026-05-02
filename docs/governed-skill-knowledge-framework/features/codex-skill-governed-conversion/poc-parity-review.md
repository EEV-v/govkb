# Codex Skill Governed Conversion - PoC Parity Review

Last updated: 2026-05-01

## Verdict

Ready for Merge: Yes

## Summary

Implemented behavior matches the accepted PoC and implementation plan. GovKB now has a preview-first `convert skill` workflow for one local Codex skill, explicit write mode, strict validation gating, redacted unsafe-content reporting, and normal Codex apply compatibility for converted packages.

## Requirement Parity

| Requirement | PoC Assertion | Implementation Evidence | Result | Notes |
|---|---|---|---|---|
| REQ-CSGC-01 | A1 | `tests/test_skill_conversion.py::test_preview_writes_no_files_and_reports_plan` | Passed | Preview leaves `.governed/capabilities/release-helper` absent. |
| REQ-CSGC-02 | A1 | Human output and `ConversionPlan.as_dict()` include source, target, planned, rejected, manual review, parity, and strict status. | Passed | JSON path covered by implementation shape; human preview covered by tests. |
| REQ-CSGC-03 | A2, A3 | `test_write_creates_strict_valid_package_and_apply_materializes_it` | Passed | Creates one new package with required files. |
| REQ-CSGC-04 | A1 | `test_write_fails_when_target_package_exists` | Passed | Existing marker file remains unchanged. |
| REQ-CSGC-05 | A1 | Preview/write tests compare source `SKILL.md` before and after. | Passed | Source local skill is read-only. |
| REQ-CSGC-06 | A2 | `test_write_creates_strict_valid_package_and_apply_materializes_it` | Passed | Safe memory, prompts, and scripts are preserved in governed locations. |
| REQ-CSGC-07 | A4 | `test_unsafe_content_is_rejected_and_report_is_redacted` | Passed | Unsafe source file is omitted and report excludes unsafe values. |
| REQ-CSGC-08 | A4 | Write path calls `validate_governed_skill_package`; test runs strict validation on resulting package. | Passed | Strict errors remove the package. |
| REQ-CSGC-09 | A2, A3 | `run_codex_apply` in conversion test materializes the converted capability. | Passed | Converted package materializes from repo instructions, not source fallback. |
| REQ-CSGC-10 | A1 | Write success output includes rollback guidance. | Passed | Human output names package removal/revert path. |

## Scenario Parity

| Scenario | Test/Verification | Result | Notes |
|---|---|---|---|
| UC-1 | `test_preview_writes_no_files_and_reports_plan` | Passed | Preview is non-mutating. |
| UC-2 | `test_source_name_resolves_from_codex_home` | Passed | Resolves under `<codex-home>/skills`. |
| UC-3 | `test_direct_source_path_outside_codex_home_is_accepted` | Passed | Direct path outside Codex home accepted. |
| UC-4 | `test_write_creates_strict_valid_package_and_apply_materializes_it` | Passed | Write creates strict-valid package. |
| UC-5 | `test_write_fails_when_target_package_exists` | Passed | Create-only guard. |
| UC-6 | `test_unsafe_content_is_rejected_and_report_is_redacted` | Passed | Rejected unsafe file is omitted and redacted. |
| UC-7 | `test_write_creates_strict_valid_package_and_apply_materializes_it` | Passed | Safe prompt and helper script copied; `tools/README.md` generated. |
| UC-8 | `test_write_creates_strict_valid_package_and_apply_materializes_it` | Passed | Normal apply materializes converted package. |
| UC-9 | `test_unsafe_content_is_rejected_and_report_is_redacted`; command output paths | Passed | Preview/write reporting is redacted; write report is package-local. |

## Command Evidence

| Command | Working Dir | Result | Evidence |
|---|---|---|---|
| `/Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m py_compile src/govkb/core/skill_conversion.py src/govkb/commands/convert.py src/govkb/cli.py tests/test_skill_conversion.py` | `/Users/vasilevevgeny/code/govkb` | Passed | Syntax check. |
| `/Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_skill_conversion -v` | `/Users/vasilevevgeny/code/govkb` | Passed | 6 tests passed. |
| `/Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_skill_conversion tests.test_apply tests.test_governed_skill_quality_gates_use_cases tests.test_governed_skill_quality_gates_smoke tests.test_candidates -v` | `/Users/vasilevevgeny/code/govkb` | Passed | 42 tests passed. |
| `/Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m govkb.cli convert skill --help` | `/Users/vasilevevgeny/code/govkb` | Passed | Help shows preview/write conversion options. |
| `docs/governed-skill-knowledge-framework/features/codex-skill-governed-conversion/regenerate-poc-data.sh` | `/Users/vasilevevgeny/code/govkb` | Passed | PoC checks rerun. |
| `/Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest discover -s tests -v` | `/Users/vasilevevgeny/code/govkb` | Failed | 100 tests ran, 11 skipped, 9 unrelated existing failures in install/memory-review; conversion tests passed. |

## Deviations

| Deviation | Approved? | Reason | Follow-up |
|---|---|---|---|
| Materialization fallback now requires `migration.status = "legacy-fallback"` | Yes | Prevents converted packages from copying source-local files, including rejected unsafe files, during apply. | Keep legacy fallback test coverage. |
| Preview strict validation is temp-rendered | Yes | Preview must not write project files; write-time strict validation is authoritative. | Label preview strict status as advisory if more CLI wording is added. |

## Risks

- MVP classifies unknown source files as manual review; real skill layouts may require follow-up copy rules.
- No update mode exists for converting into an existing governed package.
- Direct TOML metadata is used for conversion state; a richer review UI remains future work.

## Required Fixes Before Merge

None for this feature slice.

## Post-merge Follow-ups

- Add conversion update mode if maintainers need to refresh an existing governed package.
- Add a reviewer approval command/workflow for converted packages.
- Expand source layout classification after observing real skills.
