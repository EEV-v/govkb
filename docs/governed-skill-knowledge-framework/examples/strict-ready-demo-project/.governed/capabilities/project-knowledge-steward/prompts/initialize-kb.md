# Initialize KB: Project Knowledge Steward

Use this prompt in an active assistant session after the strict-ready demo project is installed.

## Context

- Capability: `project-knowledge-steward`
- Contract: `.governed/capabilities/project-knowledge-steward/capability.contract.toml`
- Instructions: `.governed/capabilities/project-knowledge-steward/instructions.md`
- Memory: `.governed/capabilities/project-knowledge-steward/references/long-term-memory.md`

## Task

1. Read the project contract, capability instructions, and current memory.
2. Inspect only repository files directly needed to identify durable demo-project workflows.
3. Append minimal reusable memory entries when the evidence supports them.
4. Keep broad notes here only until a more specific governed capability exists.
5. Run `govkb validate --strict` for the project after changes.

## Governance

- Do not store secrets, bearer tokens, passwords, or copied credential values.
- Do not store local-only absolute paths.
- Do not store one-off task status, report output, or session narration.
- Prefer append-only memory changes unless a stored fact is clearly wrong.

## Output

- List memory bullets added or say `No KB update`.
- List repository files used as evidence.
- List validation command and result.

