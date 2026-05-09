# Clearing Governed Workflow

## Goal

Show how a real project can use governed capabilities as working tools, not just documentation.

## Starting Point

The Clearing workspace has governed Codex capabilities materialized from `.governed/`:

- `govkb-clearing-clearing-feature-cookbook`
- `govkb-clearing-clearing-bugfix-cookbook`
- `govkb-clearing-clearing-level3-comment-writer`
- `govkb-clearing-clearing-level3-monday-matcher`

The maintainer validates and applies them:

```bash
govkb validate --strict /repo/Clearing
govkb apply codex --project-root /repo/Clearing --codex-home "$CODEX_HOME"
```

## Feature Planning Prompt

```text
Use $govkb-clearing-clearing-feature-cookbook.
Prepare the engineering-ready plan for adding a Clearing report export filter.
Ground the plan in existing Clearing docs and tests, and list the exact verification commands.
```

Expected behavior:

- Codex loads the governed feature cookbook references before planning.
- The plan follows Clearing feature artifacts rather than a generic planning template.
- The output names repo paths, test surfaces, rollout notes, and open questions.
- Durable lessons from the work can later be considered for governed memory.

## Bugfix Prompt

```text
Use $govkb-clearing-clearing-bugfix-cookbook.
Diagnose why the export filter fails for a settled account, produce a root-cause note, and propose the smallest fix with verification.
```

Expected behavior:

- The capability drives reproduction, diagnosis, fix planning, tests, and release-note shape.
- If the session discovers a reusable Clearing-specific verification command, it can be promoted as a memory bullet.
- Placeholder paths from legacy local skills must not become governed package paths.

## Support Comment Prompt

```text
Use $govkb-clearing-clearing-level3-comment-writer.
Write the business-readable Level 3 comment for the matched Azure work item without mentioning source code paths.
```

Expected behavior:

- The governed skill keeps stakeholder language separate from implementation detail.
- Ambiguous work item matching is delegated to the governed matcher capability.
- Sensitive local exports and credentials stay outside durable memory.

## Success Criteria

- The user prompt is short because the project capability carries the workflow.
- The same capability can be applied by another teammate.
- Strict validation and remediation keep the governed package reviewable.
- Learning is promoted only when it is durable, safe, and project-relevant.
