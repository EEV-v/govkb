# Clearing Governed Skill Remediation - Use Cases

Last updated: 2026-05-02

## Scope

Report-first governed package remediation for a project such as Clearing. The first engineering slice runs strict validation, inspects candidate auto-create policy and Git ownership, and produces a maintainer-reviewable remediation report before any capability package files are changed.

## Actors

| Actor | Goal |
|---|---|
| Clearing maintainer | See strict-validation evidence and choose repair, replacement, deprecation, or demotion before package changes. |
| GovKB maintainer | Prove the remediation flow using reusable GovKB validation and reporting behavior. |
| GovKB CLI | Inspect one project root, classify remediation needs, and emit safe report output. |
| Reviewer | Verify that the report does not mutate Clearing package files or leak unsafe local content. |

## Background

Given a project root with a `.governed/` package
And governed-skill strict validation is available
And candidate auto-create is constrained by approval and strict activation gates
And durable `.governed` writes must target the Git repository that owns project governance

## Scenarios

### UC-1: Build remediation report from strict validation @smoke

Given a governed project contains a weak active capability such as `local-stack-workflow`
When the maintainer runs a remediation report command for the project
Then GovKB runs strict governed skill validation in activation-readiness mode
And the report lists strict issue severity, rule id, location, and safe message
And the report recommends maintainer approval before capability package files are changed

### UC-2: Prefer demotion or deprecation for weak generic active capability @regression

Given strict validation reports `GSK-ID-002` for `local-stack-workflow`
When GovKB builds remediation recommendations
Then the report classifies the capability as weak or wrong-domain until reviewed
And the recommended remediation option is demote or deprecate before repair in place

### UC-3: Invalid repo paths become repair actions, not automatic edits @regression

Given a governed capability memory file references a missing repo-relative path
When GovKB builds the remediation report
Then the report includes a path repair recommendation
And no governed capability file is rewritten
And the report states that invalid paths should be corrected or removed only after approval

### UC-4: Candidate auto-create policy is visible and constrained @regression

Given project automation enables candidate auto-create
When GovKB builds the remediation report
Then the report records the current auto-create setting and minimum occurrences
And it states that activation is constrained by review approval and strict validation
And it recommends disabling auto-create during manual remediation when maintainers want a freeze window

### UC-5: Unowned or non-Git project roots block durable report writes @regression

Given the inspected project root is not inside the Git repository that owns `.governed`
When the maintainer asks GovKB to write a remediation report under `.governed/reports/`
Then GovKB refuses the durable write
And the command output identifies the Git ownership blocker
And no report file is created under the project root

### UC-6: Owned Git project can write a report without changing capability packages @smoke

Given the inspected project root is inside the Git repository that owns `.governed`
When the maintainer asks GovKB to write the remediation report
Then GovKB creates a markdown report under `.governed/reports/remediation/`
And no files under `.governed/capabilities/` are created, removed, or rewritten
And the command prints the report path

### UC-7: Useful project-knowledge-steward memory is preserved @regression

Given the project has a useful `project-knowledge-steward` capability that passes strict validation
And another capability needs remediation
When GovKB builds the remediation report
Then the report does not recommend changing `project-knowledge-steward`
And the report states that useful durable memory remains available unless strict validation identifies a concrete issue

### UC-8: Machine-readable report output is safe for tools @regression

Given remediation output is requested as JSON
When GovKB builds the report
Then the JSON contains schema version, project root, strict issues, auto-create policy, Git ownership, recommendations, and write eligibility
And unsafe values from memory content are not included in issue messages or recommendation text

## Scenario Outlines

### UC-9: Strict issue category maps to remediation option @regression

Given strict validation reports <ruleId>
When GovKB builds remediation recommendations
Then the report suggests <option>

Examples:

| ruleId | option |
|---|---|
| GSK-ID-002 | demote-or-deprecate |
| GSK-PATH-001 | repair-paths-after-approval |
| GSK-MEMORY-001 | repair-memory-after-approval |
| GSK-SAFETY-001 | remove-unsafe-content |
| GSK-LIFECYCLE-001 | approval-required |

## Negative And Governance Cases

- Remediation report generation never changes Clearing production code.
- Default report generation writes no files.
- Durable `.governed/reports/` writes require verified Git ownership.
- Capability package files are not changed in this first engineering slice.
- Candidate auto-create remains constrained by the existing strict activation gate.
- Raw session transcripts, tokens, and credential path values are not copied into reports.

## Traceability

| Requirement | Scenario(s) | Coverage |
|---|---|---|
| Strict validation identifies weak Clearing governed package issues. | UC-1, UC-2, UC-9 | Covered |
| Maintainer has a reviewed remediation plan before files are changed. | UC-1, UC-3, UC-6 | Covered |
| Weak generic active capability is repaired, renamed/replaced, deprecated, or demoted after review. | UC-2, UC-9 | Covered as report recommendation for first pass |
| Invalid commands and repo paths are corrected or removed. | UC-3, UC-9 | Covered as report-first action, writes deferred |
| Candidate auto-create no longer silently activates weak Clearing capabilities. | UC-4 | Covered through policy visibility and existing strict activation gate |
| Useful durable Clearing memory remains available after remediation. | UC-7 | Covered |
| Final package validates under strict mode or has explicit exceptions. | UC-1, UC-8 | Covered as strict evidence and report status |
| Durable Clearing `.governed` writes target the owning Git repo. | UC-5, UC-6 | Covered |

## Test Notes

| Scenario | Suggested Test Module | Notes |
|---|---|---|
| UC-1 | `tests/test_clearing_governed_skill_remediation_use_cases.py` | Build synthetic weak package and inspect report model. |
| UC-2 | `tests/test_clearing_governed_skill_remediation_use_cases.py` | Assert `GSK-ID-002` maps to demote/deprecate. |
| UC-3 | `tests/test_clearing_governed_skill_remediation_use_cases.py` | Assert missing path is reported and capability file mtime/content remains unchanged. |
| UC-4 | `tests/test_clearing_governed_skill_remediation_use_cases.py` | Enable automation in temp project and inspect policy summary. |
| UC-5 | `tests/test_clearing_governed_skill_remediation_use_cases.py` | Non-Git temp project blocks `--write-report`. |
| UC-6 | `tests/test_clearing_governed_skill_remediation_smoke.py` | Git-owned temp project writes markdown report only. |
| UC-7 | `tests/test_clearing_governed_skill_remediation_use_cases.py` | Strict-valid steward produces no recommendation. |
| UC-8 | `tests/test_clearing_governed_skill_remediation_use_cases.py` | Direct command-function JSON output with synthetic unsafe value. |
| UC-9 | `tests/test_clearing_governed_skill_remediation_use_cases.py` | Table-driven mapping test for strict rule ids. |
