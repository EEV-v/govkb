# Governed Skill Contract And Migration - Implementation Context

Last updated: 2026-05-01

## Objective

Define and implement a strict governed-skill package contract plus a safe path to convert existing local Codex skills into repo-owned GovKB capabilities.

## Source Artifacts

- User request: convert the Clearing GovKB state findings into a GovKB feature and define governed skill conventions, tooling locations, long-term memory rules, docs rules, and existing-skill conversion.
- Current product source: `docs/governed-skill-knowledge-framework/business.md`.
- Current feature workflow: `docs/COOKBOOK/COOKBOOK.MD`.
- Current capability contract loader: `src/govkb/core/contracts.py`.
- Current capability scaffold command: `src/govkb/commands/create_capability.py`.
- Current candidate staging and auto-create flow: `src/govkb/core/candidates.py`, `src/govkb/commands/candidates.py`.
- Current Codex materialization: `src/govkb/adapters/codex/materialize.py`.
- Current tests: `tests/test_init.py`, `tests/test_validate.py`, `tests/test_apply.py`, `tests/test_candidates.py`.

No repo-local `AGENTS.md`, `.github/copilot-instructions.md`, `CLAUDE.md`, or `.cursorrules` file was found in `/home/ev/code/govkb`; active session instructions apply.

## Existing Patterns

| Pattern Type | Existing Example | Location | Reuse? |
|---|---|---|---|
| Project package loading | `load_project_bundle` returns `ProjectBundle` plus `ValidationResult` | `src/govkb/core/contracts.py` | Extend validation, keep structured messages |
| Capability contract validation | `_load_capability_contract` checks required TOML tables and memory targets | `src/govkb/core/contracts.py` | Add strict package-quality checks outside the base parser |
| Capability scaffold | `run_create_capability` creates contract, instructions, memory, and init prompt | `src/govkb/commands/create_capability.py` | Reuse package creation pattern for conversion write |
| Candidate activation | `run_create_capability --from-candidate` marks candidates activated after package creation | `src/govkb/commands/create_capability.py` | Gate activation through strict validation |
| Candidate facts | `candidate-facts.toml` stores sectioned fact rows | `src/govkb/core/candidates.py` | Use as evidence, but validate before activation |
| Materialized skill naming | `materialized_skill_id(project_id, capability_id)` | `src/govkb/adapters/codex/materialize.py` | Preserve `govkb-<project>-<capability>` naming |
| Materialization copy | `_copy_tree` copies capability package assets into staged skill output | `src/govkb/adapters/codex/materialize.py` | Preserve `tools/` and adapter files automatically |
| Install-state tracking | `install_state_path`, `write_install_state` | `src/govkb/core/install_state.py` | Record converted capabilities through existing apply flow |
| CLI parser | `build_parser` adds top-level subcommands and nested subcommands | `src/govkb/cli.py` | Add `convert skill` and strict validation flag |
| Tests | `tempfile.TemporaryDirectory`, command function calls, direct assertions | `tests/test_apply.py`, `tests/test_candidates.py` | Reuse for conversion and strict validation tests |

## Proposed New Components

| Component | Purpose | Notes |
|---|---|---|
| `src/govkb/core/governed_skill.py` | Strict governed-skill package model and validation helpers | Keeps quality validation separate from TOML parsing |
| `src/govkb/core/skill_conversion.py` | Parse local Codex skills and produce conversion plans | Standard-library only; no PyYAML dependency unless added deliberately |
| `src/govkb/commands/convert.py` | CLI command for `govkb convert skill` | Preview-first with explicit `--write` for mutation |
| `tests/test_governed_skill_contract.py` | Strict validation unit tests | Covers package shape, naming, memory, paths, and tools |
| `tests/test_skill_conversion.py` | Existing skill conversion tests | Uses temp Codex homes and synthetic skills |
| `docs/governed-skill-knowledge-framework/features/governed-skill-contract-and-migration/poc-artifacts/governed-skill-package-contract.md` | Human-readable strict convention | Becomes reference for implementation and reviewers |

## Data Flow

1. Maintainer runs `govkb convert skill <source> --project-root <project> --preview`.
2. GovKB resolves `<source>` as either a filesystem path or a skill name under `<codex-home>/skills/`.
3. Converter reads `SKILL.md`, optional `references/`, optional `prompts/`, and optional helper assets.
4. Converter builds a `ConversionPlan` with target capability id, files to create, files to reject, safety warnings, and validation result.
5. Preview prints the plan without writing.
6. `--write` creates `.governed/capabilities/<capability-id>/` files, migration metadata, and safe copied tools.
7. Strict validation runs before success.
8. `govkb apply codex` materializes the governed capability back to assistant-local skill output.

## Domain Entities

- Governed skill package: one capability directory under `.governed/capabilities/<capability-id>/`.
- Capability contract: `capability.contract.toml` parsed into `CapabilityContract`.
- Memory target: `CapabilityTarget` with a relative path and allowed sections.
- Tool asset: optional helper script or fixture under `tools/`.
- Conversion source: existing local Codex skill directory.
- Conversion plan: inspectable record of target files, copied files, rejected files, warnings, and validation status.
- Migration metadata: governed package metadata that records source adapter, source path, conversion time, and status.

## Command Map

| Task | Command | Working Dir | Preconditions |
|---|---|---|---|
| Full test suite | `python3 -m unittest discover -s tests -v` | `/home/ev/code/govkb` | None |
| CLI help | `python3 -m govkb.cli --help` | `/home/ev/code/govkb` | Source checkout available |
| Validate project | `PYTHONPATH=src python3 -m govkb.cli validate <project-root>` | `/home/ev/code/govkb` | `<project-root>/.governed` exists |
| Strict validate project | `PYTHONPATH=src python3 -m govkb.cli validate <project-root> --strict` | `/home/ev/code/govkb` | New feature implemented |
| Preview conversion | `PYTHONPATH=src python3 -m govkb.cli convert skill <skill-or-path> --project-root <project-root> --codex-home <temp-codex-home> --preview` | `/home/ev/code/govkb` | New feature implemented |
| Write conversion | `PYTHONPATH=src python3 -m govkb.cli convert skill <skill-or-path> --project-root <project-root> --codex-home <temp-codex-home> --write` | `/home/ev/code/govkb` | Source skill is synthetic or approved |
| Preview materialization | `PYTHONPATH=src python3 -m govkb.cli apply codex --project-root <project-root> --codex-home <temp-codex-home> --preview` | `/home/ev/code/govkb` | Governed package validates |

## APIs And CLI Surface

Proposed CLI:

```text
govkb validate <project-root> [--strict] [--json]
govkb convert skill <skill-or-path> --project-root <project-root> [--codex-home <path>] [--capability-id <id>] [--preview | --write] [--json]
```

`--preview` is non-mutating. `--write` is explicit because conversion writes repo-owned governed files. `--json` should emit conversion plans and validation details for future UI use.

## Storage

- Source of truth: `<project-root>/.governed/capabilities/<capability-id>/`.
- Derived output: `<codex-home>/skills/govkb-<project-id>-<capability-id>/`.
- Optional governed tools: `<capability-root>/tools/scripts/`, `<capability-root>/tools/fixtures/`, `<capability-root>/tools/README.md`.
- Conversion metadata: `<capability-root>/migration.toml` or `[migration]` in `capability.contract.toml`; final file choice remains an implementation decision.

## Security And Governance

- Strict validation must reject or flag secrets, token-like values, raw transcript text, and local user-home paths.
- Conversion must never mutate the source local skill.
- Tests must use temp projects and temp Codex homes.
- Existing assistant-local files remain derived or legacy fallback output, not authoritative project state.
- Candidate auto-create must not bypass strict validation.

## Tests

- Unit tests for strict package validation:
  - valid package passes
  - generic id with weak scope fails or warns
  - missing memory target file fails
  - placeholder bullets fail for activated packages
  - invalid repo paths fail when not marked planned
  - local credential paths and secret patterns fail
  - tools without safety docs fail or warn
- Conversion tests:
  - preview emits plan and writes nothing
  - write creates valid governed package
  - skill name resolution uses `--codex-home`
  - safe scripts copy to `tools/scripts/`
  - unsafe content is rejected
  - rerun is idempotent or reports conflict clearly
- Integration tests:
  - converted capability materializes with `govkb apply codex`
  - candidate auto-create refuses strict-invalid packages

## Observability

- Validation result should include exact path, rule id, severity, and message.
- Conversion preview should list created, copied, skipped, and rejected files.
- Conversion write should print target capability path and validation status.
- Future reports can include strict-validation failures as health signals.

## Open Questions

| # | Question | Blocking? | Owner |
|---|---|---|---|
| Q1 | Should strict package checks be default errors or only enabled by `--strict` initially? | Yes | Engineering |
| Q2 | Should migration metadata live in `[migration]` inside `capability.contract.toml` or a separate `migration.toml`? | No | Engineering |
| Q3 | Should converted unsafe content be copied into a quarantine folder or only reported? | No | Engineering |

## Assumptions

| # | Assumption | Risk If Wrong |
|---|---|---|
| A1 | Standard-library parsing of simple Codex `SKILL.md` frontmatter is enough for migration. | Complex YAML frontmatter may need a parser dependency. |
| A2 | `tools/` copied by existing materialization is acceptable for Codex skills. | Adapter-specific filtering may be needed later. |
| A3 | Strict validation can start as opt-in to avoid breaking existing governed packages immediately. | Weak packages may continue passing default validation until projects opt in. |

## Traceability

| Context Section | business.md Source |
|---|---|
| Proposed New Components | Governed Skill Package Shape, Existing Skill Conversion |
| Data Flow | Existing Skill Conversion |
| Security And Governance | Strict Validation, Tooling Conventions |
| Tests | Acceptance Criteria |
| Open Questions | Strict Validation, Existing Skill Conversion |
