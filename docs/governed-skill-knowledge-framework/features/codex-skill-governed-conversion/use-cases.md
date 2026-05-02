# Codex Skill Governed Conversion - Use Cases

Last updated: 2026-05-01

## Scope

Preview-first conversion of one local Codex skill into one new GovKB governed capability package. The source local skill is read-only, write mode is explicit, and converted packages must pass strict validation before success.

## Actors

| Actor | Goal |
|---|---|
| Maintainer | Inspect a local Codex skill and decide whether it should become governed. |
| Reviewer | See copied, transformed, rejected, and manual-review content before accepting conversion. |
| GovKB CLI | Resolve a source skill, classify content, preview/write a package, and run strict validation. |
| Codex adapter | Materialize the converted governed package through normal `govkb apply codex`. |

## Background

Given a GovKB project with `.governed/`
And a local Codex skill exists either under `<codex-home>/skills/<skill-name>/` or at an explicitly provided directory path
And governed-skill strict validation is available
And conversion must not mutate the source local skill

## Scenarios

### UC-1: Preview one Codex skill without writing files @smoke

Given a local Codex skill directory with `SKILL.md`
And the target project has `.governed/`
When the maintainer runs `govkb convert skill <skill> --project-root <project-root> --codex-home <codex-home>`
Then GovKB prints a conversion preview
And the preview shows source skill path, proposed capability id, package path, planned files, rejected content, manual-review content, parity level, and validation status
And no files are created under `.governed/capabilities/`

### UC-2: Resolve source by skill name from Codex home @regression

Given `<codex-home>/skills/release-helper/SKILL.md` exists
When the maintainer previews `govkb convert skill release-helper --codex-home <codex-home>`
Then the source path resolves to `<codex-home>/skills/release-helper`
And the proposed capability id defaults to `release-helper`

### UC-3: Accept an explicit source path outside Codex home @regression

Given a local skill directory exists outside the configured Codex home
When the maintainer passes that directory path to `govkb convert skill`
Then GovKB accepts it as the source
And the source local skill is not copied into Codex home or mutated

### UC-4: Write creates a new strict-valid governed package @smoke

Given preview is acceptable
And no governed capability already exists at the target capability id
When the maintainer runs `govkb convert skill <skill> --write`
Then GovKB creates one new `.governed/capabilities/<capability-id>/` package
And the package includes `capability.contract.toml`, `instructions.md`, `references/long-term-memory.md`, `prompts/initialize-kb.md`, and migration metadata
And strict validation passes before the command exits successfully
And the command prints rollback guidance

### UC-5: Write fails when target package already exists @regression

Given `.governed/capabilities/<capability-id>/` already exists
When the maintainer runs conversion write mode for the same capability id
Then GovKB exits with an error
And the existing package is not modified
And the source local skill is not modified

### UC-6: Unsafe source content is rejected and redacted @regression

Given a source skill contains credential paths, token-like content, or local-only unsafe evidence
When conversion preview or write classifies the source files
Then unsafe content is not copied into governed memory, instructions, prompts, reports, or tools
And preview output identifies rejected source item paths and reasons without unsafe values
And write mode records only redacted rejected-item metadata in `docs/conversion-report.md`

### UC-7: Safe prompts, memory, and helper tools are preserved @regression

Given a source skill contains safe reference memory, reusable prompts, and helper scripts or fixtures
When conversion write mode succeeds
Then safe references are copied under `references/`
And safe prompts are copied under `prompts/`
And safe helper scripts or fixtures are copied under `tools/`
And `tools/README.md` documents purpose and safety when tools are present
And no helper script is executed

### UC-8: Converted package materializes through normal Codex apply @regression

Given conversion write mode created a governed capability package
When the maintainer runs `govkb apply codex --project-root <project-root> --codex-home <codex-home>`
Then the converted capability materializes as a GovKB-managed Codex skill
And the materialized skill uses the canonical governed instructions unless an adapter-specific `adapters/codex/SKILL.md` exists

## Scenario Outlines

### UC-9: Conversion output mode stays safe @regression

Given a conversion has <mode>
When source content contains rejected items
Then rejected-item metadata is reported in <destination>
And unsafe values are not present

Examples:

| mode | destination |
|---|---|
| preview | console or JSON output only |
| write | console or JSON output and `docs/conversion-report.md` |

## Negative And Governance Cases

- Conversion never executes source or package-owned scripts.
- Conversion never mutates the source local skill.
- Write mode never overwrites existing governed packages.
- Preview mode writes nothing.
- Unsafe values are not copied into governed memory or reports.
- Existing local Codex skills remain available until maintainers remove them separately.

## Traceability

| Requirement | Scenario(s) | Coverage |
|---|---|---|
| Maintainer can preview conversion without writing files | UC-1 | Covered |
| Preview shows target package, copied content, rejected content, manual review content, and validation status | UC-1, UC-9 | Covered |
| Write creates a new governed capability package when preview is acceptable | UC-4 | Covered |
| Write fails if target package already exists | UC-5 | Covered |
| Source local skill remains unchanged | UC-1, UC-3, UC-5 | Covered |
| Safe long-term memory, prompts, and helper scripts can be preserved | UC-7 | Covered |
| Unsafe content is rejected and not copied | UC-6, UC-9 | Covered |
| Converted package passes strict validation before write succeeds | UC-4 | Covered |
| Converted package can be materialized with normal GovKB Codex apply | UC-8 | Covered |
| Rollback path is clear | UC-4 | Covered |

## Test Notes

| Scenario | Suggested Test Module | Notes |
|---|---|---|
| UC-1 | `tests/test_skill_conversion.py` | Direct command-function preview with temp project and Codex home. |
| UC-2 | `tests/test_skill_conversion.py` | Resolve source by skill name under temp Codex home. |
| UC-3 | `tests/test_skill_conversion.py` | Pass direct source path outside Codex home. |
| UC-4 | `tests/test_skill_conversion.py` | Write package and run strict validation. |
| UC-5 | `tests/test_skill_conversion.py` | Existing target package remains unchanged. |
| UC-6 | `tests/test_skill_conversion.py` | Use synthetic unsafe strings; assert redacted report excludes values. |
| UC-7 | `tests/test_skill_conversion.py` | Assert prompts/tools copied and not executed. |
| UC-8 | `tests/test_skill_conversion.py`, `tests/test_apply.py` | Run `run_codex_apply` against converted package. |
| UC-9 | `tests/test_skill_conversion.py` | Compare preview and write reporting destinations. |

