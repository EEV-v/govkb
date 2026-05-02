# Codex Skill Governed Conversion - Implementation Plan

Last updated: 2026-05-01

## 0. Existing Code Inventory

| Category | Component | Location | Reuse Strategy |
|---|---|---|---|
| CLI parser | top-level commands | `src/govkb/cli.py` | Add `convert skill` as an additive command. |
| Conversion command | none | new `src/govkb/commands/convert.py` | New file is justified because conversion orchestration is separate from apply/create. |
| Conversion planner | none | new `src/govkb/core/skill_conversion.py` | New file holds source resolution, classification, rendering, preview, and write helpers. |
| Contract model | migration fields | `src/govkb/core/contracts.py` | Reuse existing `[migration]` parse support and tolerate extra metadata. |
| Strict validation | package quality gate | `src/govkb/core/governed_skill.py` | Reuse write-time strict validation instead of duplicating rules. |
| Codex materialization | `instructions.md`, adapter override, migration fallback | `src/govkb/adapters/codex/materialize.py` | Converted packages can materialize normally from `instructions.md`. |
| Existing tests | apply/migration fallback | `tests/test_apply.py` | Add conversion tests and keep apply regression. |

## 0.5. Pre-flight Checklist

| Prerequisite | Status | Owner |
|---|---|---|
| Quality-gates implementation exists | Done | Engineering |
| Conversion spec handoff ready | Done | Product/Engineering |
| Use cases generated | Done | Engineering |
| PoC package generated | Done | Engineering |
| Full test-suite baseline clean | Blocked by unrelated existing failures | Engineering |

## 1. Scope And Boundaries

Implement one-skill Codex conversion with preview default and explicit write. Do not bulk convert, update existing governed packages, convert other assistants, execute helper scripts, or delete source local skills.

## 2. Requirements Mapping

| Requirement | Behavior | Location | New/Modify | Notes |
|---|---|---|---|---|
| REQ-CSGC-01 | Preview writes nothing. | `src/govkb/commands/convert.py`, `src/govkb/core/skill_conversion.py` | New | Default mode is preview unless `--write` is present. |
| REQ-CSGC-02 | Preview reports source, target, planned files, rejected/manual-review content, parity, and validation status. | command/core | New | Human and JSON output. |
| REQ-CSGC-03 | Write creates one new package. | core writer | New | Creates package directory atomically enough to remove on validation failure. |
| REQ-CSGC-04 | Existing target blocks write. | core writer | New | No update mode. |
| REQ-CSGC-05 | Source skill unchanged. | tests/core | New | All source reads are read-only. |
| REQ-CSGC-06 | Safe memory/prompts/tools preserved. | core classifier/writer | New | Copy safe source files into standard locations. |
| REQ-CSGC-07 | Unsafe content rejected and redacted. | core classifier/report | New | Reject whole unsafe file; report path/class/reason only. |
| REQ-CSGC-08 | Strict validation before success. | core writer | New | Roll back new package on strict errors. |
| REQ-CSGC-09 | Normal Codex apply materializes converted package. | existing apply + tests | Modify tests only | No materializer code change expected. |
| REQ-CSGC-10 | Rollback path clear. | command output | New | Print target directory removal/revert guidance. |

## 3. Design

Add `govkb convert skill <skill-or-path>`:

- `--project-root <path>` defaults to cwd
- `--codex-home <path>` resolves skill names under `<codex-home>/skills/`
- `--capability-id <id>` overrides default id
- `--write` enables mutation; absence means preview
- `--json` emits machine-readable output

Core model:

- `ConversionItem(path, classification, action, reason, destination)`
- `ConversionPlan(source_path, capability_id, package_path, planned_files, rejected_items, manual_review_items, parity_level, strict_status)`
- `ConversionWriteResult(plan, strict_issues, created_paths)`

Rendering:

- `SKILL.md` frontmatter/body becomes canonical `instructions.md`.
- Existing safe `references/long-term-memory.md` is used when present; otherwise generate required memory sections with non-placeholder bullets.
- Safe `prompts/**` copy to `prompts/**`.
- Safe source scripts/fixtures copy to `tools/scripts/**` or `tools/fixtures/**`; create `tools/README.md` when tools are copied.
- Unsafe files are rejected wholesale.
- Ambiguous files are manual-review only.

## 4. Integration Points

- `src/govkb/cli.py`: new `convert` command with `skill` subcommand.
- `src/govkb/commands/convert.py`: argument handling and output formatting.
- `src/govkb/core/skill_conversion.py`: read-only planning and write implementation.
- `src/govkb/core/governed_skill.py`: strict validation after rendering.
- `tests/test_skill_conversion.py`: focused unittest coverage.

## 5. Application Logic

1. Resolve source:
   - direct directory path if it exists
   - otherwise `<codex-home>/skills/<skill-or-path>`
2. Read `SKILL.md`; derive skill name and description from frontmatter when present.
3. Build capability id from `--capability-id`, frontmatter name, or source directory name.
4. Classify source files:
   - `SKILL.md`: transformed to `instructions.md`
   - `references/**`: governed, unless unsafe
   - `prompts/**`: governed, unless unsafe
   - `tools/**`, `scripts/**`, `fixtures/**`: tool, unless unsafe
   - `agents/**`, adapter-specific files, unknown files: manual review
5. Preview:
   - render to a temp package and run approximate strict validation
   - print planned output and strict status
   - write nothing under project root
6. Write:
   - fail if package exists
   - render package
   - write redacted conversion report
   - run actual strict validation
   - remove package and fail if strict errors exist

## 6. Data Consistency And Safety

The source local skill is never opened for write. Preview never writes to project root or Codex home. Write mode only creates one new capability package and removes it on strict validation failure. Reports contain source-relative file paths and reasons, not unsafe values.

## 7. Testing Strategy

| Test Type | Location | Coverage |
|---|---|---|
| Command/core conversion tests | `tests/test_skill_conversion.py` | Preview, source resolution, write, existing target, unsafe rejection, direct path source, apply materialization. |
| Apply regression | `tests/test_apply.py` | Existing materialization behavior remains intact. |
| Strict regression | `tests/test_governed_skill_quality_gates_*` | Strict validator remains usable by conversion. |

## 8. Verification Commands

| Command | Working Dir | Purpose | Preconditions |
|---|---|---|---|
| `/Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_skill_conversion -v` | `/Users/vasilevevgeny/code/govkb` | Conversion feature tests | Bundled Python 3.12 |
| `/Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest tests.test_apply tests.test_governed_skill_quality_gates_use_cases tests.test_governed_skill_quality_gates_smoke -v` | `/Users/vasilevevgeny/code/govkb` | Apply and strict regression | Bundled Python 3.12 |
| `/Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m govkb.cli convert skill <skill> --project-root <project> --codex-home <codex-home>` | `/Users/vasilevevgeny/code/govkb` | Manual preview smoke | Temp project and skill |
| `/Users/vasilevevgeny/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest discover -s tests -v` | `/Users/vasilevevgeny/code/govkb` | Final suite | Known unrelated failures may remain |

## 9. Implementation Phases

### Phase 0 - Shape And Contracts

Scope:

Add CLI parser and conversion data model.

Files:

- `src/govkb/cli.py`
- `src/govkb/commands/convert.py`
- `src/govkb/core/skill_conversion.py`

Verify:

- `python -m govkb.cli convert skill --help`

Rollback:

- remove parser, command module, and core module

### Phase 1 - Core Behavior

Scope:

Implement source resolution, classification, rendering, preview, write, and strict validation.

Files:

- `src/govkb/core/skill_conversion.py`
- `tests/test_skill_conversion.py`

Verify:

- `python -m unittest tests.test_skill_conversion -v`

Rollback:

- remove conversion module and tests

### Phase 2 - Command Integration

Scope:

Wire command output, JSON payload, and rollback guidance.

Files:

- `src/govkb/commands/convert.py`
- `src/govkb/cli.py`
- `tests/test_skill_conversion.py`

Verify:

- preview/write command tests

Rollback:

- remove command integration while keeping core helpers only if useful

### Phase 3 - End-to-End Behavior

Scope:

Verify converted package materializes through normal Codex apply.

Files:

- `tests/test_skill_conversion.py`

Verify:

- conversion write plus `run_codex_apply`

Rollback:

- revert tests and any conversion behavior that does not meet apply contract

### Phase 4 - Docs

Scope:

Update implementation summary and PoC parity review.

Files:

- feature folder artifacts

Verify:

- `git diff --check`

Rollback:

- revert feature docs generated in this phase only

## 10. Rollback Plan

The command is additive and preview-only by default. If write behavior is risky, remove or hide `--write` while preserving preview/classification for review.

## 11. Open Questions

- Public approval/review workflow for converted packages remains outside this MVP.
- Update mode for existing governed packages remains deferred.

## 12. Ready Checklist

- Preview is default and non-mutating.
- Write is explicit and create-only.
- Source local skill is read-only.
- Unsafe content is rejected and redacted.
- Strict validation gates write success.
- Existing materializer can consume converted output.

