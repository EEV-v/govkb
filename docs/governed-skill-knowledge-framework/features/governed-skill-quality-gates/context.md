# Governed Skill Quality Gates - Implementation Context

Last updated: 2026-05-01

## Existing Code Surface

| Area | Current Location | Observed Behavior |
|---|---|---|
| CLI parser | `src/govkb/cli.py` | `govkb validate` has no strict flag yet. Candidate auto-create exists under `govkb candidates auto-create-ready`. |
| Base validation | `src/govkb/commands/validate.py`, `src/govkb/core/contracts.py` | Loads project, capability, adapter, and release TOML. Emits errors/warnings without severity or rule ids. |
| Capability contract model | `src/govkb/core/contracts.py` | `CapabilityContract` includes id, description, routing, memory targets, migration metadata, bootstrap config, and KB health config. It does not model lifecycle or approval state yet. |
| Capability scaffolding | `src/govkb/commands/create_capability.py` | Writes contract, instructions, long-term memory, and initialize prompt. Default scaffold contains TODO-style memory/instruction placeholders. |
| Candidate auto-create | `src/govkb/commands/candidates.py` | Creates capabilities from ready candidates when project automation policy allows it, then marks the candidate activated and materializes Codex output. It currently gates on base validation only. |
| Automation policy | `src/govkb/core/automation.py` | `auto_create_capabilities` defaults false; `auto_create_min_occurrences` defaults to 2. |
| Materialization | `src/govkb/adapters/codex/materialize.py` | Copies governed references/agents/prompts and supports migration fallback for legacy Codex skill sources. |
| KB health | `src/govkb/core/kb_bootstrap.py` | Detects placeholder-like memory content for bootstrap/health purposes, which can inform strict validation. |
| Tests | `tests/test_validate.py`, `tests/test_candidates.py`, `tests/test_apply.py` | Current coverage exercises base validation, candidate staging/activation, materialization, and migration fallback. |

## Current Gaps Against The Spec

- No strict validation module exists.
- `ValidationMessage` has only `location` and `message`; strict output needs severity and stable rule id.
- `govkb validate` has no `--strict` or JSON strict issue output.
- Capability contracts do not persist lifecycle state, approval state, reviewer, or approval timestamp.
- Candidate auto-create can mark a generated capability active after base validation even if memory/instructions contain weak placeholder content.
- Tooling conventions are not validated; there is no rule requiring `tools/README.md` when `tools/scripts/` or `tools/fixtures/` exists.
- Local credential path and token-like content checks are not centralized.
- Generic capability id checks exist only as candidate naming heuristics, not activation-readiness validation.

## Engineering Implications

- Add a strict validation layer that runs after `load_project_bundle`.
- Keep base validation backward-compatible and invoke strict checks only when requested or when candidate activation/conversion write requires them.
- Use structured strict issues with at least `severity`, `rule_id`, `location`, and `message`.
- Prefer a new core module, likely `src/govkb/core/governed_skill.py`, rather than expanding TOML parsing with package-quality logic.
- Add lifecycle/approval metadata to capability contracts or a companion package metadata file during implementation planning.
- Candidate auto-create must create/review packages without activation unless strict validation passes and approval metadata is present.
- Strict validation should inspect package files in addition to contract fields: `instructions.md`, `references/long-term-memory.md`, `prompts/initialize-kb.md`, optional `tools/`, and configured memory target files.

## Strict Validation Rule Inputs

The first implementation slice has source-backed rules for:

- package shape and required files
- lower kebab-case capability ids
- weak generic id justification and approval
- lifecycle and approval metadata
- placeholder memory/instruction content
- configured memory sections matching actual memory files
- repo-relative path references and planned-path exceptions
- forbidden local credential path patterns
- token-like or secret-like content indicators
- `tools/README.md` when tools exist
- mutating scripts documenting `--dry-run` or `--preview`

## Recommended Test Focus

- strict-valid package passes
- missing required files fail strict validation
- placeholder memory fails activation readiness
- missing configured memory sections fail
- absolute/local user-home paths fail unless explicitly marked runtime input
- credential path patterns fail
- token-like strings fail
- tools without `tools/README.md` are reported
- mutating scripts without preview/dry-run documentation are reported
- weak generic ids require justification and approved lifecycle metadata
- `govkb validate` remains backward-compatible without strict mode
- candidate auto-create refuses strict-invalid packages

## Readiness Assumptions

- No external tracker is configured for this local GovKB feature.
- The feature is ready for engineering handoff after scope lock because both prior blocking questions have been resolved in the feature spec.
- Codex skill conversion and Clearing remediation remain dependent follow-up features and should not be included in the first implementation plan.

## Verification Baseline

Run from the repo root:

```bash
PYTHONPYCACHEPREFIX=/tmp/govkb-pycache python3 -m py_compile docs/scripts/feature_spec/*.py
python3 -m unittest discover -s tests -v
python3 -m govkb.cli --help
PYTHONPATH=src python3 -m govkb.cli validate <project-root>
```

## Sources

- `src/govkb/cli.py`
- `src/govkb/commands/validate.py`
- `src/govkb/core/contracts.py`
- `src/govkb/commands/create_capability.py`
- `src/govkb/commands/candidates.py`
- `src/govkb/core/automation.py`
- `src/govkb/adapters/codex/materialize.py`
- `src/govkb/core/kb_bootstrap.py`
- `tests/test_validate.py`
- `tests/test_candidates.py`
- `tests/test_apply.py`
