# GovKB Feature Spec Cookbook Structure Map

Last updated: 2026-04-25

## Prompt Mapping

| Source Prompt | Target Prompt | Changes | Reason | Evidence |
|---|---|---|---|---|
| `SPEC_COOKBOOK.MD` | `docs/FEATURE_SPEC_COOKBOOK/SPEC_COOKBOOK.MD` | Added GovKB paths, `business-context.md`, `context.md`, generic tracker/reference status, and handoff into `docs/COOKBOOK/`. | GovKB needs spec convergence before engineering planning without source-project trackers. | `docs/governed-skill-knowledge-framework/**`, `docs/COOKBOOK/`. |
| `INTAKE_PROMPT.MD` | `docs/FEATURE_SPEC_COOKBOOK/INTAKE_PROMPT.MD` | Requires business/context preconditions and GovKB feature path. | Intake should not proceed from draft text alone. | Existing VS Code extension feature artifacts. |
| `TRACKER_SYNC_PROMPT.MD` | `docs/FEATURE_SPEC_COOKBOOK/TRACKER_SYNC_PROMPT.MD` | Generalized to tracker/reference sync. | No mandatory GovKB external tracker exists. | Repo has no tracker config. |
| `QUESTION_MANAGER_PROMPT.MD` | `docs/FEATURE_SPEC_COOKBOOK/QUESTION_MANAGER_PROMPT.MD` | Preserves ledgers and distinguishes first-slice from deferred public launch decisions. | Matches GovKB feature-spec needs. | `open-questions.md`, `decision-log.md` in VS Code feature. |
| `REVIEW_PACK_PROMPT.MD` | `docs/FEATURE_SPEC_COOKBOOK/REVIEW_PACK_PROMPT.MD` | Keeps tracker/reference and reconciliation gates separate; supports internal handoff wording. | GovKB may lock local scope before public send. | VS Code extension scope-lock/handoff. |
| `FINAL_REVIEW_PROMPT.MD` | `docs/FEATURE_SPEC_COOKBOOK/FINAL_REVIEW_PROMPT.MD` | Removed hard dependency on source-project orchestrator context. | GovKB has no adapted orchestrator script yet. | Manual handoff flow used in this repo. |
| `REVIEW_DIFF_PROMPT.MD` | `docs/FEATURE_SPEC_COOKBOOK/REVIEW_DIFF_PROMPT.MD` | Generalized feedback sources and classification. | Works for docs, comments, or reviewed returns. | `review-rounds/reconciliation-state.json`. |
| `RECONCILIATION_PROMPT.MD` | `docs/FEATURE_SPEC_COOKBOOK/RECONCILIATION_PROMPT.MD` | Keeps canonical update flags and adds no-change option. | Prevents blind `business.md` overwrites. | Source workflow guardrails. |
| `KB_MAINTENANCE_PROMPT.MD` | `docs/FEATURE_SPEC_COOKBOOK/KB_MAINTENANCE_PROMPT.MD` | Re-scoped shared KB to reusable GovKB lessons. | Avoids copying raw feature content. | `spec-knowledge-base.md`. |
| `SCOPE_LOCK_PROMPT.MD` | `docs/FEATURE_SPEC_COOKBOOK/SCOPE_LOCK_PROMPT.MD` | Allows named-slice scope lock with deferred public scope. | GovKB VSIX-first work needs slice-level handoff. | `scope-lock.md` for VS Code feature. |
| `HANDOFF_PROMPT.MD` | `docs/FEATURE_SPEC_COOKBOOK/HANDOFF_PROMPT.MD` | Points to GovKB engineering cookbook and source artifacts. | Completes pre-engineering handoff. | `spec-handoff.md`. |
| Review support prompts | `docs/FEATURE_SPEC_COOKBOOK/*_REVIEW_PROMPT.MD` | Updated to GovKB paths and generic tracker/reference checks. | Keeps review prompts usable in the target repo. | No source script paths remain. |
| Skill references | `docs/FEATURE_SPEC_COOKBOOK/references/*.md` | Added GovKB-specific business-context and project-KB references. | Source skill references lived outside the copied folder. | `README.md`, project docs, `src/govkb/**`, `tests/**`. |
| Feature-spec scripts | `docs/scripts/feature_spec/*.py` | Ported to GovKB paths, generic tracker/reference state, and local-only execution. | Lets the adopted prompt workflow run as a repo-local command set. | Disposable smoke test and existing VS Code feature tracker dry-run. |

## Artifact Mapping

| Source Artifact | Target Artifact | Path Pattern | Phase |
|---|---|---|---|
| `business.md` | `business.md` | `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/business.md` | Start |
| `business-context.md` | `business-context.md` | `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/business-context.md` | 0.0 |
| `context.md` | `context.md` | `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/context.md` | 0.1 |
| `spec-brief.md` | `spec-brief.md` | `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/spec-brief.md` | 0.2 |
| `open-questions.md` | `open-questions.md` | `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/open-questions.md` | 1 |
| `decision-log.md` | `decision-log.md` | `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/decision-log.md` | 1 |
| `business-review-pack.md` | `business-review-pack.md` | `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/business-review-pack.md` | 2 |
| `business-review-message.md` | `business-review-message.md` | `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/business-review-message.md` | 2 |
| reviewed source | reviewed/normalized source | `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/review-rounds/<label>-reviewed.docx.md` | 3 |
| changes | changes | `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/review-rounds/<label>-changes.md` | 3 |
| reconciliation | reconciliation | `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/review-rounds/<label>-reconciliation.md` | 3 |
| reconciliation state | reconciliation state | `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/review-rounds/reconciliation-state.json` | 3 |
| shared KB | shared KB | `docs/FEATURE_SPEC_COOKBOOK/spec-knowledge-base.md` | 4 |
| `scope-lock.md` | `scope-lock.md` | `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/scope-lock.md` | 5 |
| `spec-handoff.md` | `spec-handoff.md` | `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/spec-handoff.md` | 6 |

## Command Mapping

| Task | Source Command | Target Command | Working Dir | Preconditions |
|---|---|---|---|---|
| Run feature-spec workflow | Source-project script | `PYTHONDONTWRITEBYTECODE=1 python3 docs/scripts/feature_spec/run_feature_spec_workflow.py <FeatureSlug> --json` | `/home/ev/code/govkb` | Feature folder has `business.md`. |
| Record optional tracker/reference | Source tracker sync script | `PYTHONDONTWRITEBYTECODE=1 python3 docs/scripts/feature_spec/reconcile_feature_tracking.py <FeatureSlug> --tracker-label <Label> --tracker-id <ID> --tracker-url <URL> --write-artifacts --json` | `/home/ev/code/govkb` | A tracker/reference exists and should be written into local artifacts. |
| Discover feature business specs | Source feature-folder scan | `rg --files docs/governed-skill-knowledge-framework/features -g 'business.md'` | `/home/ev/code/govkb` | Feature folders exist. |
| Full verification baseline | Source project tests | `python3 -m unittest discover -s tests -v` | `/home/ev/code/govkb` | Python 3.11+ available. |
| CLI help baseline | Source project command | `python3 -m govkb.cli --help` | `/home/ev/code/govkb` | Run from repo root. |

## Handoff Mapping

| Spec Cookbook Gate | GovKB Engineering Cookbook Entry |
|---|---|
| `spec-handoff.md` exists and says ready | Start `docs/COOKBOOK/COOKBOOK.MD` |
| `scope-lock.md` names accepted slice | Generate `use-cases.md` for that slice |
| No blocking questions/open decisions | Generate PoC package and implementation plan |
| Deferred public/external scope is explicit | Keep implementation plan limited to accepted slice |
