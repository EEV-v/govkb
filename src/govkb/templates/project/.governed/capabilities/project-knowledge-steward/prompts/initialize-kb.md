# Initialize KB: Project Knowledge Steward

Use this prompt in an active assistant session after the governed project is installed.

## Context

- Capability: `project-knowledge-steward`
- Contract: `.governed/capabilities/project-knowledge-steward/capability.contract.toml`
- Instructions: `.governed/capabilities/project-knowledge-steward/instructions.md`
- Memory: `.governed/capabilities/project-knowledge-steward/references/long-term-memory.md`
- Candidate evidence: none; initialize only from the current contract and repo facts.

## Task

1. Read the project contract, capability instructions, and current memory.
2. Inspect only repo files directly needed to identify stable project workflows, conventions, verification commands, and signals for future dedicated capabilities.
3. Append the minimal durable KB entries that will improve future sessions.
4. Keep broad notes here only until a more specific governed capability exists.
5. Run `govkb validate` for the project after changes.

## Governance

- Do not store secrets, bearer tokens, API keys, passwords, or copied credential values.
- Do not store local-only absolute paths unless they are part of the governed repo contract.
- Do not store one-off task status, report output, or session narration.
- Prefer append-only memory changes; do not rewrite accepted KB unless a fact is clearly wrong.
- If evidence is thin, leave the KB minimal and report that no durable update was made.

## Output

- List memory bullets added or say `No KB update`.
- List repo files used as evidence.
- List validation command and result.
