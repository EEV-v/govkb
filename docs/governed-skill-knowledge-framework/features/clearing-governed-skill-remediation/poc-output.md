# Clearing Governed Skill Remediation - PoC Output

## Summary

The PoC can proceed with synthetic project fixtures. Existing strict validation already detects the weak generic id shape needed for `local-stack-workflow`, and candidate auto-create is already constrained by review approval plus strict activation. The implementation gap is a reusable remediation report workflow that ties strict issues, policy state, Git ownership, and safe recommendations together.

## Assertion Results

| Assertion | Result | Evidence | Notes |
|---|---|---|---|
| A weak generic capability can be detected by strict validation. | Passed | `tests/test_governed_skill_quality_gates_use_cases.py::test_uc_8_generic_ids_require_justification_and_approval_before_activation` | Existing quality-gates implementation reports `GSK-ID-002`. |
| Remediation can be report-first. | Passed | `tests/test_clearing_governed_skill_remediation_use_cases.py` | Report generation produces recommendations without changing capability package files. |
| Candidate auto-create policy is available for reporting. | Passed | `src/govkb/core/automation.py`, `src/govkb/commands/candidates.py` | Auto-create policy parses from project manifest and activation now requires review approval plus strict validation. |
| Durable report writes can be gated by Git ownership. | Passed | `tests/test_clearing_governed_skill_remediation_use_cases.py`, `tests/test_clearing_governed_skill_remediation_smoke.py` | Non-Git roots refuse `--write-report`; Git-owned temp roots write only remediation reports. |
| JSON output is safe for tools. | Passed | `tests/test_clearing_governed_skill_remediation_use_cases.py` | JSON output includes structured issue/recommendation fields and excludes the synthetic unsafe token value. |

## Outliers

- The real Clearing package was not inspected because `/home/ev/code/Clearing` and `/Users/vasilevevgeny/code/Clearing` are not available from this workspace.
- The first slice should not implement package mutation actions such as demotion, deprecation, rename, or in-place repair.

## Open Gaps

- Real Clearing operational evidence remains blocked until the owning Clearing repository is available.
- Actual capability mutation actions remain deferred until the maintainer approves one report option.

## Recommendation

The report-first remediation workflow is implemented and ready for operational use against the real Clearing repository. Defer actual Clearing package rewrites until the maintainer reviews a generated report and approves a specific repair, demotion, deprecation, rename, or replacement path.
