# GovKB Feature Spec Cookbook Adoption Context

Last updated: 2026-04-25

## Adoption Summary

The feature-spec cookbook from `/home/ev/code/Clearing/Clearing-docs/docs/FEATURE_SPEC_COOKBOOK` was copied into `docs/FEATURE_SPEC_COOKBOOK/` and adapted for GovKB.

The adopted workflow preserves the source lifecycle:

```text
business-context -> context -> spec-brief -> tracker/reference status -> open questions + decisions -> review pack -> final review -> feedback diff/reconciliation -> knowledge update -> scope lock -> spec handoff
```

## Instruction Inventory And Precedence

| Source | Status | Applied Precedence | Notes |
|---|---|---|---|
| Active Codex system/developer instructions | Found in current session | Highest | Governs file editing, sandboxing, and verification. |
| `/home/ev/code/govkb/AGENTS.md` | Not found | N/A | No repo-local override exists. |
| `/home/ev/code/govkb/.github/copilot-instructions.md` | Not found | N/A | No Copilot instruction file exists. |
| `/home/ev/code/govkb/CLAUDE.md` | Not found | N/A | No Claude instruction file exists. |
| `/home/ev/code/govkb/.cursorrules` | Not found | N/A | No Cursor instruction file exists. |

Conflict resolution: no target repo instruction conflicts were discovered. Active session instructions and existing GovKB conventions were applied.

## Documentation Inventory

| Document | Evidence | Adoption Impact |
|---|---|---|
| `README.md` | Defines GovKB as repo-native governed knowledge tooling and lists local dev commands. | Spec cookbook points to GovKB product docs and source-checkout verification. |
| `docs/README.md` | Provides docs map. | Added spec cookbook discoverability. |
| `docs/governed-skill-knowledge-framework/business.md` | Defines product scope, CLI surface, governance, and assistant-local derivation rules. | Business context and scope-lock prompts preserve `.governed` source of truth. |
| `docs/governed-skill-knowledge-framework/implementation-plan.md` | Defines implementation phases and package boundaries. | Handoff prompt points into `docs/COOKBOOK/` for engineering phases. |
| `docs/governed-skill-knowledge-framework/mvp-plus-test-plan.md` | Defines validation commands and low-cost classifier settings. | Context and handoff prompts require command grounding. |
| `docs/governed-skill-knowledge-framework/features/vscode-extension-public-distribution/` | Existing feature folder with spec artifacts and handoff. | Used as the local dry-run target for adoption. |

## Code And Workflow Inventory

| Pattern | Evidence | Adoption Impact |
|---|---|---|
| Python CLI package | `pyproject.toml`, `src/govkb/cli.py` | Spec context must capture command contracts and package boundaries. |
| Source layout and import shim | `src/govkb/**`, `govkb/__init__.py` | Commands distinguish repo-root execution from `PYTHONPATH=src` execution. |
| Test style | `tests/**` | Engineering handoff records `python3 -m unittest discover -s tests -v`. |
| Feature docs | `docs/governed-skill-knowledge-framework/features/*` | Canonical feature path is `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/`. |

## Key Migration Constraints

- Use `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/` as the single feature folder pattern.
- Require `business-context.md` and `context.md` before question, decision, or review-pack work.
- Keep `business.md` canonical; reviewed or normalized feedback inputs stay immutable.
- Generalize tracker sync to tracker/reference status because GovKB has no mandatory external tracker.
- Do not create external trackers without explicit confirmation.
- Treat local engineering readiness separately from public/external review readiness.
- Hand off to `docs/COOKBOOK/COOKBOOK.MD` only after `spec-handoff.md` exists.

