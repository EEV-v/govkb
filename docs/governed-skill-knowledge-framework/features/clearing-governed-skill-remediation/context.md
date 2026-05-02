# Clearing Governed Skill Remediation - Implementation Context

Last updated: 2026-05-01

## Existing Code Surface

| Area | Current Location | Observed Behavior |
|---|---|---|
| Strict validation dependency | `governed-skill-quality-gates` | Remediation should use strict validation findings instead of manual guessing. |
| Base validation CLI | `src/govkb/commands/validate.py` | Current validation loads contracts but does not yet enforce strict package quality. |
| Candidate auto-create | `src/govkb/commands/candidates.py`, `src/govkb/core/automation.py` | Auto-create is controlled by `.governed/project.toml` automation settings. |
| Capability lifecycle target | planned by quality gates | Lifecycle/approval state is not implemented yet, but remediation should consume it once available. |
| Clearing workspace | external to this checkout | `/home/ev/code/Clearing` and `/Users/vasilevevgeny/code/Clearing` were not available from this GovKB workspace during spec prep. |

## Current Gaps Against The Spec

- Quality gates are not implemented yet, so strict validation cannot currently produce the Clearing issue report.
- The actual Clearing governed package is not available in this local GovKB checkout for direct inspection.
- The owning Git repository for durable Clearing `.governed` state must be verified before mutation.
- The final option for `local-stack-workflow` depends on strict-validation findings and maintainer approval.

## Engineering Implications

- Start with an evidence-gathering phase, not file mutation.
- Run strict validation against the live Clearing project root once quality gates are implemented.
- Capture findings in a remediation report before changing `.governed`.
- Disable or constrain candidate auto-create while remediation is active.
- If the workspace is not a Git repository or not the owning repository, stop before writes and record the required owner/repo action.
- Prefer demotion or deprecation for a weak or wrong-domain active capability; only repair in place when strict validation and maintainer review confirm the id and scope are acceptable.
- Preserve useful project-knowledge-steward memory unless a concrete strict-validation finding says it is unsafe or incorrect.

## Recommended Test And Verification Focus

- strict validation flags the weak `local-stack-workflow` shape
- remediation report lists exact package issues and proposed option
- auto-create policy is disabled or constrained before cleanup changes
- no Clearing production code files are touched
- invalid commands and repo paths are corrected or removed only after approval
- final package validates under strict mode or records explicit exceptions

## Dependency Boundary

This spec is ready for engineering planning as an operational follow-up. Execution must wait until the quality-gates implementation can run strict validation against the live Clearing package.

## Verification Baseline

Run from the GovKB repo root after quality gates exist:

```bash
PYTHONPATH=src python3 -m govkb.cli validate /path/to/Clearing --strict
PYTHONPATH=src python3 -m govkb.cli candidates list /path/to/Clearing --json
PYTHONPATH=src python3 -m govkb.cli status /path/to/Clearing --json
```

Before writing remediation changes, verify the target is the owning Git repo:

```bash
git -C /path/to/Clearing rev-parse --show-toplevel
git -C /path/to/Clearing status --short
```

## Sources

- `docs/governed-skill-knowledge-framework/features/clearing-governed-skill-remediation/business.md`
- `docs/governed-skill-knowledge-framework/features/governed-skill-quality-gates/spec-handoff.md`
- `src/govkb/commands/validate.py`
- `src/govkb/commands/candidates.py`
- `src/govkb/core/automation.py`
