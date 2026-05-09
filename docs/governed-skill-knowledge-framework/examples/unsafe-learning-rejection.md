# Unsafe Learning Rejection

## Goal

Show that GovKB prefers missing a lesson over writing unsafe or noisy long-term memory.

## Setup

```bash
govkb apply codex --project-root /repo/customer-demo --codex-home /tmp/dev-codex
```

The local skill memory file is:

```text
/tmp/dev-codex/skills/govkb-customer-demo-workflow-review/references/long-term-memory.md
```

## Risky Local Changes

A local assistant session accidentally changes the memory heading and adds a local-only credential hint:

```diff
- # Workflow Review
+ # Workflow Review - Local Notes

 ## Working Agreement

+ - Use /Users/alice/.secrets/funding_creds.json for manual verification.
```

## Promotion Attempt

```bash
govkb promote /repo/customer-demo --assistant codex --codex-home /tmp/dev-codex
```

Expected result:

- Promotion exits with a rejection.
- The repo memory file is unchanged.
- The promotion report explains the rejected reason, such as preamble or heading mutation.
- The unsafe local path is not copied into `.governed/`.

## User-Facing Meaning

The assistant can experiment locally, but durable governed memory has a narrower contract:

- Append safe bullet lessons only.
- Keep configured sections stable.
- Do not store secrets, credential file names, local-only absolute paths, or production-only assumptions.
- Require maintainer review for anything beyond append-only memory.

## Success Criteria

- The active repo remains unchanged.
- The rejection is visible.
- The maintainer can fix or discard the local memory without silent knowledge drift.
