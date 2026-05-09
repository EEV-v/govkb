# New Capability Candidate

## Goal

Show how repeated unmatched work becomes a candidate for maintainer review instead of an automatically active skill.

## Scenario

Three separate Codex sessions ask for release validation help:

```text
Prepare the release smoke-test checklist and signoff note.
```

```text
Review the release checklist and identify missing deployment evidence.
```

```text
Create the release validation summary for stakeholder approval.
```

No active governed capability specializes in release validation yet.

## Memory Review

The memory-review adapter sees repeated durable workflow signals and stages a candidate:

```bash
govkb review-memory \
  --assistant codex \
  --project-root /repo/customer-demo \
  --max-sessions 10
```

Expected candidate:

```text
.governed/candidates/release-validation-workflow/candidate.toml
```

Inspect candidates:

```bash
govkb candidates list /repo/customer-demo
govkb candidates list /repo/customer-demo --json
```

## Maintainer Review

The maintainer checks:

- Is this repeated enough to deserve a capability?
- Is the scope narrower than the project steward?
- Are routing hints precise?
- Are proposed facts grounded in repo artifacts?
- Does it avoid raw transcript or local-only assumptions?

The maintainer marks the candidate approved, then runs:

```bash
govkb candidates auto-create-ready \
  --project-root /repo/customer-demo \
  --assistant codex \
  --codex-home "$CODEX_HOME"
```

## Activation Gate

Expected behavior:

- Strict-invalid candidates do not become active capabilities.
- Approved and strict-valid candidates can become governed capability packages.
- The resulting capability is materialized only after it passes governance checks.

## Success Criteria

- New capabilities are reviewable.
- Repeated work does not silently mutate the assistant setup.
- Capability activation has a visible policy boundary.
