# Project Knowledge Steward

## Project Working Agreement

- Keep durable project knowledge in `.governed` so it can be reviewed, versioned, and redistributed to every Codex setup.

## Stable Workflows

- Run strict validation before materializing governed knowledge into assistant-local skills.
- Use the demo flow from `README.md` when showing first-run validation, apply, and status.

## Commands And Verification

- Run `govkb validate --strict` from the GovKB repository root before presenting this fixture.
- Run `govkb apply codex` with a disposable Codex home when demonstrating materialization.

## Repo Conventions

- Keep governed capability contracts, instructions, prompts, and memory under `.governed/capabilities`.
- Keep customer-demo evidence sanitized and free of local credentials or raw assistant transcripts.

## Code And Docs Map

- Use `README.md` as the demo-project entry point.
- Use `docs/README.md` for customer-owned documentation context.
- Use `src/README.md` and `tests/README.md` as stable source and verification placeholders for the demo fixture.

## Authority Rules

- Treat `.governed/capabilities/project-knowledge-steward/capability.contract.toml` as the source of truth for the demo steward capability.
- Prefer repo-governed memory over assistant-local memory after promotion review is complete.

## Candidate Skill Signals

- Stage repeated customer-demo workflows as governed candidates before adding new active capabilities.

