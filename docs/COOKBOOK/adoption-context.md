# GovKB Cookbook Adoption Context

Last updated: 2026-04-25

## Adoption Summary

The feature cookbook from `/home/ev/code/Clearing/Clearing-docs/docs/COOKBOOK` was copied into `docs/COOKBOOK/` and adapted for the GovKB repository.

The adopted cookbook preserves the original lifecycle:

```text
business -> context -> use-cases -> PoC -> implementation plan -> review -> test scaffold -> implement -> parity review -> release artifacts
```

## Instruction Inventory And Precedence

| Source | Status | Applied Precedence | Notes |
|---|---|---|---|
| Active Codex system/developer instructions | Found in current session | Highest | Governs file editing, sandboxing, test execution, and response format. |
| `/home/ev/code/govkb/AGENTS.md` | Not found | N/A | No repo-local override exists. |
| `/home/ev/code/govkb/.github/copilot-instructions.md` | Not found | N/A | No Copilot instruction file exists. |
| `/home/ev/code/govkb/CLAUDE.md` | Not found | N/A | No Claude instruction file exists. |
| `/home/ev/code/govkb/.cursorrules` | Not found | N/A | No Cursor instruction file exists. |
| Sibling repo instruction files | Found outside target root | Ignored | Files under sibling repos are not ancestors of GovKB and were not applied. |

Conflict resolution: no target repo instruction conflicts were discovered. The active session instructions and the repository's existing conventions were applied.

## Documentation Inventory

| Document | Evidence | Adoption Impact |
|---|---|---|
| `README.md` | Lists product docs under `docs/governed-skill-knowledge-framework/` and local development commands. | Cookbook uses that docs folder as the canonical feature root. |
| `docs/README.md` | Identifies `governed-skill-knowledge-framework` as the product/spec doc location. | Cookbook feature artifacts live under that tree. |
| `docs/governed-skill-knowledge-framework/business.md` | Defines `.governed/`, CLI, Codex adapter, learning capture, audit, migration, and acceptance criteria. | Prompts preserve repo-owned governed package and derived assistant output rules. |
| `docs/governed-skill-knowledge-framework/implementation-plan.md` | Defines reusable `govkb` package, command surface, contract model, and phased delivery. | Implementation-plan prompt requires existing-code inventory and phased verification. |
| `docs/governed-skill-knowledge-framework/mvp-plus-test-plan.md` | Provides real validation commands with disposable project roots and `CODEX_HOME`. | Cookbook uses temp dirs and quota-safe/dry-run guidance for adapter features. |
| `docs/governed-skill-knowledge-framework/features/README.md` | Defines feature-level spec folders with `business.md` as the canonical draft. | Canonical feature path is `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/`. |
| `docs/governed-skill-knowledge-framework/features/vscode-extension-public-distribution/*` | Existing feature folder with `business.md`, `context.md`, `spec-brief.md`, and review materials. | Confirms feature-folder artifact style and naming. |

## Code Pattern Inventory

| Pattern | Evidence | Adoption Impact |
|---|---|---|
| Python src-layout package | `pyproject.toml`, `src/govkb/**`, `govkb/__init__.py` | Prompts reference `src/govkb/` and the repo-root import shim. |
| CLI parser and commands | `src/govkb/cli.py`, `src/govkb/commands/**` | Implementation prompts use argparse command modules and `run_*` function tests. |
| Unit tests with temp dirs | `tests/test_apply.py`, `tests/test_install.py`, `tests/test_init_kb.py` | Test scaffold prompt uses `unittest`, `tempfile`, `Path`, and disposable `codex_home`. |
| Command-output tests | `tests/test_install.py`, `tests/test_init_kb.py` | Prompts recommend `redirect_stdout` when stdout is behavior. |
| Subprocess command construction tests | `tests/test_review_memory_command.py` | Prompts require argument-array subprocess construction when subprocess behavior is tested. |
| Memory-review fixture behavior | `tests/test_memory_review.py`, `tests/test_candidates.py` | Prompts emphasize sanitized session fixtures and no raw transcript storage. |

## Command Inventory

| Task | Command | Working Dir | Preconditions |
|---|---|---|---|
| Full test suite | `python3 -m unittest discover -s tests -v` | `/home/ev/code/govkb` | Python 3.11+ available. |
| CLI help through repo shim | `python3 -m govkb.cli --help` | `/home/ev/code/govkb` | Run from repo root. |
| CLI help through src layout | `PYTHONPATH=src python3 -m govkb.cli --help` | `/home/ev/code/govkb` | Run from repo root. |
| Validate a target governed package | `PYTHONPATH=src python3 -m govkb.cli validate <project-root>` | `/home/ev/code/govkb` | `<project-root>/.governed` exists. |
| Preview Codex apply | `PYTHONPATH=src python3 -m govkb.cli apply codex --project-root <project-root> --codex-home <temp-codex-home> --preview` | `/home/ev/code/govkb` | Target project is initialized. |
| Memory-review dry run | `CODEX_HOME=<temp-codex-home> PYTHONPATH=src python3 -m govkb.cli review-memory --assistant codex --project-root <project-root> --dry-run --max-sessions 1 --classifier-codex-home ~/.codex --codex-model gpt-5.4-mini --codex-reasoning low --codex-timeout 180` | `/home/ev/code/govkb` | Nested Codex auth/config available in classifier home. |

## Key Migration Constraints

- Use `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/` as the single feature artifact path.
- Use Python `unittest` scaffolds under `tests/`; do not reference another project's C# test fixtures or Docker test harness.
- Keep `.governed/**` as canonical project source and `$CODEX_HOME/**` as derived local state.
- Use temp dirs for test project roots, Codex homes, reports, releases, and generated files.
- Keep raw assistant transcript content out of repo artifacts.
- Every command in prompts must include a working directory and prerequisites.

