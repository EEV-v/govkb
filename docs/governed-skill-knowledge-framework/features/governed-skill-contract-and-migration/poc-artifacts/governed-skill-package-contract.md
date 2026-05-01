# Governed Skill Package Contract

This document defines the target package convention for a GovKB governed skill.

## Canonical Package Root

```text
<project-root>/.governed/capabilities/<capability-id>/
```

`<capability-id>` must be lower kebab-case and should name the durable domain or workflow. It must not be a generic description of the capability mechanism unless the scope is truly generic.

## Required Files

```text
capability.contract.toml
instructions.md
prompts/initialize-kb.md
references/long-term-memory.md
```

`references/long-term-memory.md` is required when `[memory].enabled = true`.

## Optional Standard Files And Folders

```text
adapters/<assistant>/
docs/
tools/README.md
tools/scripts/
tools/fixtures/
```

### `adapters/<assistant>/`

Assistant-specific presentation files live here. For Codex, `adapters/codex/SKILL.md` may override the generated wrapper when the capability needs assistant-specific wording.

### `docs/`

Capability-owned runbooks, review notes, and extended reference docs live here. Durable short rules should still be summarized in `references/long-term-memory.md`.

### `tools/scripts/`

Reusable helper scripts owned by the capability live here.

Rules:

- scripts must not embed secrets
- mutating scripts must support `--dry-run` or `--preview`
- scripts must document required inputs
- scripts should write outputs under caller-provided paths or temp dirs by default
- scripts should avoid user-home state unless explicitly requested by the caller

### `tools/fixtures/`

Sanitized fixtures used by scripts or tests live here. Fixtures must not contain raw assistant transcripts, secrets, account identifiers, or local-only paths.

### `tools/README.md`

Required when `tools/scripts/` or `tools/fixtures/` exists.

It should explain:

- script purpose
- command examples
- working directory
- prerequisites
- mutation behavior
- safety flags
- output locations

## Contract Fields

`capability.contract.toml` must include:

```toml
contract_version = 1

[capability]
id = "<capability-id>"
name = "<Human Name>"
governed = true
description = "<When to use this capability>"

[routing]
aliases = ["$<capability-id>", "<capability-id>", "<human phrase>"]
hints = ["domain", "specific", "terms"]
negative_hints = ["codex-memory-review", "govkb install", "govkb apply", "report output", "cron schedule"]

[memory]
enabled = true
auto_apply_min_confidence = 0.85
requires_explicit_acceptance = false

[memory.targets.main]
path = "references/long-term-memory.md"
sections = [
  "Working Agreement",
  "Stable Workflows",
  "Commands And Verification",
  "Code And Docs Map",
  "Authority Rules",
]

[bootstrap]
profile = "workflow"
repo_roots = ["."]
authority_paths = []
seed_paths = []

[kb_health]
requires_verification_commands = true
requires_repo_map = true
required_sections = ["Working Agreement", "Stable Workflows", "Commands And Verification", "Code And Docs Map"]
```

## Memory Rules

`references/long-term-memory.md` must:

- contain the sections declared by the contract
- use durable, reusable, action-oriented bullets
- use repo-relative paths
- include correct working directories for commands when ambiguity exists
- avoid TODO/scaffold placeholder bullets after activation
- avoid raw transcripts, secrets, tokens, user-home paths, credential-file paths, exact incident ids, and one-off task status
- keep business-specific behavior only when reusable for future work

## Naming Rules

Good capability ids:

- `corporate-actions-alert-cleanup`
- `fix-dropcopy-ingest-resilience`
- `golden-security-master-review`
- `backend-local-stack-workflow`

Weak ids unless heavily justified:

- `local-stack-workflow`
- `workflow-review`
- `project-workflow`
- `governed-skill`

Materialized Codex skills use:

```text
govkb-<project-id>-<capability-id>
```

## Conversion Rules

When converting an existing Codex skill:

1. Read `SKILL.md`.
2. Parse `name` and `description` from frontmatter.
3. Map the body into `instructions.md` or `adapters/codex/SKILL.md`.
4. Copy `references/long-term-memory.md` only after safety checks.
5. Copy prompts into `prompts/` when they are reusable and safe.
6. Copy safe helper scripts into `tools/scripts/`.
7. Copy sanitized fixtures into `tools/fixtures/`.
8. Write migration metadata.
9. Run strict validation.
10. Require reviewer action for rejected or ambiguous content.
