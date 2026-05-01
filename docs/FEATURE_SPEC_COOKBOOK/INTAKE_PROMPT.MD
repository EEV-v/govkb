# Intake Prompt

Use this when a GovKB feature only has initial business material.

## Inputs

- `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/business.md`
- `business-context.md`
- `context.md`
- any reviewed `.docx.md` snapshots or normalized feedback files already in the feature folder
- optional PoC or discovery artifacts

## Output

- `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/spec-brief.md`

## Required Contents

- feature objective
- source artifacts
- problem statement
- scope snapshot
- acceptance snapshot
- current open questions
- current decisions
- review readiness
- tracker/reference status

## Rules

- Keep `business.md` canonical.
- Do not overwrite reviewed snapshots.
- Do not rewrite `business.md` just to fit cookbook style.
- Capture source artifacts, scope summary, open questions, decisions, and readiness for review or scope lock.
- If tracker linkage is not configured, say so explicitly; do not fabricate tracker ids.
- If `business-context.md` or `context.md` is missing, stop and create those first.

