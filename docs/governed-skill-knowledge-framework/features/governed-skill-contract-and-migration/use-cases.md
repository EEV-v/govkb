# Governed Skill Contract And Migration - Use Cases

Last updated: 2026-05-01

## Scope

This feature covers strict governed-skill package conventions, validation, and preview-first conversion of existing local Codex skills into governed GovKB capabilities.

## Actors

| Actor | Goal |
|---|---|
| Maintainer | Define and validate governed skills with predictable package quality |
| Engineer | Convert a useful existing Codex skill into `.governed/` without losing durable knowledge |
| Reviewer | Inspect conversion output, validation failures, and activation readiness |
| Automation | Refuse weak candidate activation when strict checks fail |

## Background

Given a GovKB project has a `.governed/` package
And assistant-local Codex skills are derived outputs, not source of truth
And strict validation rules are available for governed capability packages

## Scenarios

### UC-1: Strict governed package passes validation @smoke

Given a project capability has `capability.contract.toml`, `instructions.md`, `references/long-term-memory.md`, and `prompts/initialize-kb.md`
And its id is domain-specific lower kebab-case
And its memory sections match the contract
And referenced repo paths exist or are marked planned
When the maintainer runs `govkb validate <project-root> --strict`
Then validation succeeds
And the result identifies the package as strict-valid.

### UC-2: Existing Codex skill conversion previews without mutation @smoke

Given a local Codex skill has `SKILL.md` and `references/long-term-memory.md`
When the engineer runs `govkb convert skill <skill> --project-root <project-root> --codex-home <codex-home> --preview`
Then GovKB prints a conversion plan
And no files are written under `.governed/capabilities/`
And the plan lists the target capability id, target files, warnings, and validation status.

### UC-3: Existing Codex skill conversion writes a governed package @regression

Given a previewed local skill has durable instructions, memory, prompts, and one safe helper script
When the engineer reruns conversion with `--write`
Then GovKB creates `.governed/capabilities/<capability-id>/`
And copies the helper script under `tools/scripts/`
And creates or preserves `tools/README.md`
And writes migration metadata
And the new package passes strict validation.

### UC-4: Weak generic package is blocked from activation @regression

Given a candidate suggests a generic id such as `local-stack-workflow`
And its memory contains placeholder bullets or invalid repo paths
When candidate auto-create tries to activate the package
Then GovKB refuses activation
And the candidate remains reviewable
And the report lists exact validation failures.

### UC-5: Conversion rerun is idempotent or reports conflicts @regression

Given a converted capability already exists
When the engineer reruns the same conversion
Then GovKB either reports no changes
Or reports a clear conflict for changed target files
And it does not overwrite manually curated governed memory without explicit confirmation.

### UC-6: Unsafe local content is rejected @regression

Given an existing local skill contains raw transcript excerpts, token-like strings, local user-home paths, or credential-file paths
When conversion runs in preview or write mode
Then the unsafe content is not copied into governed memory
And the conversion plan reports each rejected item with a path and reason
And `--write` fails if required governed files would be unsafe.

### UC-7: Converted governed package materializes to Codex @regression

Given a converted package passes strict validation
When the maintainer runs `govkb apply codex --project-root <project-root> --codex-home <codex-home> --preview`
Then the materialization plan includes `govkb-<project-id>-<capability-id>`
And the assistant-local output includes governed instructions, references, prompts, and safe tools.

### UC-8: Validation output supports future UI and reports @regression

Given a governed package has strict-validation warnings or errors
When the maintainer runs `govkb validate <project-root> --strict --json`
Then the output includes machine-readable severity, rule id, location, and message
And no raw transcript or secret-like content is included in the output.

## Scenario Outlines

### UC-9: Capability id quality checks @regression

Given a capability id is `<capability_id>`
When strict validation evaluates naming
Then the result is `<expected>`

Examples:

| capability_id | expected |
|---|---|
| corporate-actions-alert-cleanup | pass |
| fix-dropcopy-ingest-resilience | pass |
| local-stack-workflow | warn-or-fail unless scope proves generic use |
| workflow-review | warn-or-fail unless scope proves generic use |

## Negative And Governance Cases

- Conversion must not mutate source local skills.
- Conversion must not copy secrets, token strings, raw transcripts, or credential-file paths.
- Auto-create must not mark strict-invalid candidates activated.
- Materialized assistant output must remain derived and replaceable.

## Traceability

| Requirement | Scenario(s) | Coverage |
|---|---|---|
| Governed package shape | UC-1, UC-3, UC-7 | Full |
| Naming and routing conventions | UC-1, UC-4, UC-9 | Full |
| Long-term memory conventions | UC-1, UC-4, UC-6 | Full |
| Tooling conventions | UC-3, UC-7 | Full |
| Strict validation | UC-1, UC-4, UC-8, UC-9 | Full |
| Existing skill conversion | UC-2, UC-3, UC-5, UC-6 | Full |
| Clearing remediation path | UC-4, UC-9 | Partial until Clearing cleanup is executed |

## Test Notes

| Scenario | Suggested Test Module | Notes |
|---|---|---|
| UC-1 | `tests/test_governed_skill_contract.py` | Use temp governed package |
| UC-2 | `tests/test_skill_conversion.py` | Assert preview writes nothing |
| UC-3 | `tests/test_skill_conversion.py` | Assert package files and strict pass |
| UC-4 | `tests/test_candidates.py` | Add strict-gated auto-create case |
| UC-5 | `tests/test_skill_conversion.py` | Rerun conversion against existing package |
| UC-6 | `tests/test_skill_conversion.py` | Synthetic unsafe local skill |
| UC-7 | `tests/test_apply.py` | Assert tools copied to materialized skill |
| UC-8 | `tests/test_validate.py` or `tests/test_status_json.py` | JSON validation shape |
| UC-9 | `tests/test_governed_skill_contract.py` | Table-driven id checks |
