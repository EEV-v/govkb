# Clearing Governed Skill Remediation - PoC Plan

## Mode

Fixture-validation.

## Evidence Strategy

Use synthetic temp projects that model the Clearing problem without requiring the real Clearing checkout. The PoC relies on existing strict validation behavior in `src/govkb/core/governed_skill.py`, project automation parsing in `src/govkb/core/automation.py`, and command-function testing patterns in `tests/governed_skill_quality_gates_test_helper.py`.

The real `/home/ev/code/Clearing` target remains an operational verification step after this reusable GovKB workflow exists.

## Assertions

| Assertion | Method | Command/File | Expected Result |
|---|---|---|---|
| A weak generic capability can be detected by strict validation. | Existing unit evidence | `/Users/vasilevevgeny/code/govkb/tests/test_governed_skill_quality_gates_use_cases.py` | `local-stack-workflow` without scope justification produces `GSK-ID-002`. |
| Remediation can be report-first. | Candidate implementation test | `tests/test_clearing_governed_skill_remediation_use_cases.py` | Building a report produces recommendations without changing capability files. |
| Candidate auto-create policy is available for reporting. | Existing code inspection and candidate test | `src/govkb/core/automation.py`, `src/govkb/commands/candidates.py` | Policy includes `auto_create_capabilities` and auto-create requires review approval plus strict activation. |
| Durable report writes can be gated by Git ownership. | Candidate implementation test | `tests/test_clearing_governed_skill_remediation_use_cases.py` | Non-Git roots refuse `--write-report`; Git-owned roots write only under `.governed/reports/remediation/`. |
| JSON output is safe for tools. | Candidate implementation test | `tests/test_clearing_governed_skill_remediation_use_cases.py` | JSON contains structured issues and recommendations without raw unsafe values. |

## Data And Fixtures

- Temp project roots created with `run_init`.
- Synthetic governed capabilities seeded through a feature test helper.
- Synthetic missing paths and token-like strings only; no raw sessions or local assistant state.
- Temp Git repositories for ownership-gated report-write tests.

## Rerun Command

From `/Users/vasilevevgeny/code/govkb`:

```bash
/Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_clearing_governed_skill_remediation_use_cases tests.test_clearing_governed_skill_remediation_smoke -v
```

## Risks And Blockers

- The real Clearing checkout is not present in this GovKB workspace, so operational validation against `/home/ev/code/Clearing` is blocked until that repository is available.
- Full `unittest discover` has unrelated baseline failures in install and memory-review tests; targeted remediation tests should still run cleanly.
