# GovKB Feature Spec Cookbook Adoption Validation

Last updated: 2026-04-25

## Checklist Results

| Gate | Status | Evidence |
|---|---|---|
| Phase order preserves source workflow intent. | PASS | `SPEC_COOKBOOK.MD` preserves intake, questions/decisions, review pack, reconciliation, KB update, scope lock, and handoff, with GovKB context preconditions added. |
| Single canonical feature folder path is used. | PASS | Prompts use `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/`. |
| `business-context.md` and `context.md` are required before substantive spec work. | PASS | `SPEC_COOKBOOK.MD`, `INTAKE_PROMPT.MD`, and references enforce this. |
| Reviewed snapshots remain immutable. | PASS | `SPEC_COOKBOOK.MD`, `REVIEW_DIFF_PROMPT.MD`, and `RECONCILIATION_PROMPT.MD` preserve the guardrail. |
| Tracker assumptions are adapted. | PASS | Tracker sync is generalized to tracker/reference status; no mandatory external tracker is assumed. |
| Handoff points to the GovKB engineering cookbook. | PASS | `HANDOFF_PROMPT.MD` and `SPEC_COOKBOOK.MD` point to `docs/COOKBOOK/COOKBOOK.MD`. |
| Feature-spec scripts are ported. | PASS | `docs/scripts/feature_spec/*.py` runs with GovKB feature paths, local-only tracker/reference handling, and no external tracker client imports. |
| No stale source-project paths, commands, or scripts remain in operational prompts/scripts. | PASS | Source-term scan found no source-project repo paths, tracker names, or script calls after adaptation. |
| Repo-local references exist. | PASS | `references/BUSINESS_CONTEXT_PRECONDITION.md` and `references/PROJECT_KB.md` were added. |
| Existing tests remain green. | PASS | `python3 -m unittest discover -s tests -v` passed: 64 tests. |

## Verification Commands

| Command | Working Dir | Result |
|---|---|---|
| Source-term scan for operational prompts and scripts | `/home/ev/code/govkb` | Passed; no source-project repo paths, tracker names, or script calls remain. |
| Script compile check | `/home/ev/code/govkb` | Passed: `PYTHONPYCACHEPREFIX=/tmp/govkb-pycache python3 -m py_compile docs/scripts/feature_spec/*.py`. |
| Disposable workflow smoke test | `/home/ev/code/govkb` | Passed: `run_feature_spec_workflow.py /tmp/govkb-feature-spec-script-test --repo-root /home/ev/code/govkb --json`. |
| Existing feature tracker dry-run | `/home/ev/code/govkb` | Passed: VS Code feature returns `trackerReady: true` with `not-configured` status and no writes. |
| `python3 -m unittest discover -s tests -v` | `/home/ev/code/govkb` | Passed: 64 tests. |

## Sample Dry-run

Sample feature:

```text
FeatureSlug: vscode-extension-public-distribution
```

Expected pre-engineering chain:

| Phase | Artifact |
|---|---|
| Business context | `business-context.md` |
| Implementation context | `context.md` |
| Intake | `spec-brief.md` |
| Questions/decisions | `open-questions.md`, `decision-log.md` |
| Scope lock | `scope-lock.md` |
| Handoff | `spec-handoff.md` |
| Engineering entry | `docs/COOKBOOK/COOKBOOK.MD` and `use-cases.md` |

This sample chain exists for the VS Code extension feature.

## Residual Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Scripts generate deterministic local artifacts. | Running the workflow with `--write` can refresh spec docs. | Review diffs before committing generated updates. |
| No repo-local assistant instruction file exists. | Future agents rely on session instructions and docs. | Add `AGENTS.md` later if a stable repo instruction surface is needed. |
| External tracker behavior is generic. | Public-launch tracking may need a specific integration later. | Treat tracker creation/wiring as explicit-confirmation work outside local spec flow. |

## Open TODOs

- TODO(Project owner): Decide whether GovKB should add repo-level `AGENTS.md`.
