# Isolated Automation Review

## Goal

Show the maintainer experience when automation promotes safe memory into an isolated worktree branch.

## Setup

The project has a committed `.governed/` package and a materialized Codex skill:

```bash
govkb validate --strict /repo/customer-demo
govkb apply codex --project-root /repo/customer-demo --codex-home "$CODEX_HOME"
git -C /repo/customer-demo status --short -- .governed
```

Expected active checkout status:

```text
```

## Automated Promotion

After memory review applies a safe local lesson, automation runs:

```bash
govkb promote /repo/customer-demo \
  --assistant codex \
  --codex-home "$CODEX_HOME" \
  --auto
```

Expected output includes:

```text
Auto isolation: created isolated git worktree for automated promotion review
Auto branch: codex/govkb-auto-promote/customer-demo/<run-id>
Auto worktree: $CODEX_HOME/memories/govkb/worktrees/customer-demo/<run-id>
```

The active checkout remains clean:

```bash
git -C /repo/customer-demo status --short -- .governed
```

## Review Surface

List isolated promotions:

```bash
govkb promotions list /repo/customer-demo --codex-home "$CODEX_HOME"
```

Expected shape:

```text
<run-id> state=ready-for-review changed=2 branch=codex/govkb-auto-promote/customer-demo/<run-id> worktree=...
```

Show the digest:

```bash
govkb promotions show <run-id> \
  --project-root /repo/customer-demo \
  --codex-home "$CODEX_HOME"
```

Expected review data:

- Branch name.
- Worktree path.
- Git status for `.governed/`.
- Latest promotion digest.
- Promoted additions.
- Rejections, if any.

Machine-readable output for UI or extension work:

```bash
govkb promotions list /repo/customer-demo --codex-home "$CODEX_HOME" --json
govkb promotions show <run-id> --project-root /repo/customer-demo --codex-home "$CODEX_HOME" --json
```

Record a GovKB lifecycle decision without changing Git history:

```bash
govkb promotions mark-reviewed <run-id> \
  --project-root /repo/customer-demo \
  --codex-home "$CODEX_HOME" \
  --decision accepted \
  --reviewer maintainer@example.local \
  --reason "Durable, scoped, and ready for normal repo review."
```

If the promotion is not useful:

```bash
govkb promotions mark-reviewed <run-id> \
  --project-root /repo/customer-demo \
  --codex-home "$CODEX_HOME" \
  --decision rejected \
  --reason "Too local to keep in governed memory."
```

Archive the GovKB lifecycle record after the team has handled it:

```bash
govkb promotions archive <run-id> \
  --project-root /repo/customer-demo \
  --codex-home "$CODEX_HOME" \
  --reason "Handled through normal repository process."
```

## Maintainer Decision

The maintainer can inspect the worktree like a normal Git checkout:

```bash
git -C "$CODEX_HOME/memories/govkb/worktrees/customer-demo/<run-id>" diff -- .governed
```

If accepted, the maintainer applies the `.governed/` changes through the team's normal Git process. GovKB lifecycle commands record review intent only; they do not commit, merge, cherry-pick, push, or change repository branch policy.

## Success Criteria

- Automation does real promotion work.
- The active developer checkout stays clean.
- The review artifact is discoverable with `govkb promotions list`.
- GovKB review decisions are recorded outside the Git worktree as sidecar lifecycle metadata.
- The maintainer can inspect a normal Git diff before accepting durable AI knowledge.
