# Team Learning Loop

## Goal

Show that one teammate can learn a durable project fact during normal Codex work, a maintainer can promote it, and another teammate can receive it through `govkb apply codex`.

## Actors

| Actor | Role |
|---|---|
| Alice | Developer who discovers a reusable workflow lesson. |
| Maintainer | Reviews and commits governed knowledge updates. |
| Bob | Developer who receives the improved capability later. |

## Starting State

The project has a strict-valid `.governed/` package with an active `workflow-review` capability.

```bash
govkb validate --strict /repo/customer-demo
govkb apply codex --project-root /repo/customer-demo --codex-home /tmp/alice-codex
```

Expected result:

- Local Codex skill exists under `/tmp/alice-codex/skills/govkb-customer-demo-workflow-review`.
- Install state exists under `/tmp/alice-codex/memories/govkb/install-state/customer-demo--codex.json`.

## Alice Prompt

```text
Use $workflow-review. Review the rollout notes and update the customer demo workflow so future runs always capture smoke-test evidence before changing assistant setup.
```

Alice completes the task with Codex. During the session, the local governed memory gains one safe append-only bullet:

```markdown
- Capture customer-demo rollout evidence before changing assistant setup.
```

## Promotion

Manual maintainer promotion:

```bash
govkb promote /repo/customer-demo --assistant codex --codex-home /tmp/alice-codex
```

Expected result:

- The bullet is appended to `.governed/capabilities/workflow-review/references/long-term-memory.md`.
- A report is written under `.governed/reports/promotions/`.
- Git shows a normal reviewable diff.

## Redistribution

The maintainer commits the governed package update. Bob then applies the project package:

```bash
govkb apply codex --project-root /repo/customer-demo --codex-home /tmp/bob-codex
```

Expected result:

- Bob's materialized `workflow-review` skill includes the promoted lesson.
- Bob does not need Alice's local Codex files.
- The project repo remains the authority for the lesson.

## Success Criteria

- The lesson is repo-owned, not personal.
- The change is reviewable in Git.
- Another teammate receives the lesson through materialization only.
