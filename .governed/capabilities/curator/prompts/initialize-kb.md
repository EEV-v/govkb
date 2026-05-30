# Initialize KB: GovKB Curator

Use this prompt after installing or refreshing the governed project.

## Context

- Capability: `curator`
- Contract: `.governed/capabilities/curator/capability.contract.toml`
- Instructions: `.governed/capabilities/curator/instructions.md`
- Memory: `.governed/capabilities/curator/references/long-term-memory.md`

## Outcome

Keep the curator memory focused on durable GovKB lifecycle operations for this project.

## Task

1. Read the contract, instructions, and current memory.
2. Inspect only GovKB lifecycle evidence needed for stable commands, safety rules, and state interpretation.
3. Append minimal durable entries when the project has a repeatable GovKB state-management rule not already present.
4. Do not add domain workflow details that belong to a specific governed capability.
5. Run strict validation after changes.

## Governance

- Do not store raw session transcripts, secrets, customer data, local machine trivia, or one-off task status.
- Keep proposal, promotion, candidate, validation, and apply rules distinct.
- Prefer short action-oriented bullets.

## Output

- List added memory bullets or say `No KB update`.
- List evidence files used.
- List validation command and result.
