# Initialize KB: Prompt Engineering KB

Use this prompt in an active assistant session when refreshing the governed prompt-engineering KB.

## Context

- Capability: `prompt-engineering-kb`
- Contract: `.governed/capabilities/prompt-engineering-kb/capability.contract.toml`
- Instructions: `.governed/capabilities/prompt-engineering-kb/instructions.md`
- Memory: `.governed/capabilities/prompt-engineering-kb/references/long-term-memory.md`
- Source policy: use official vendor documentation for provider-specific claims; OpenAI and Anthropic are seeded sources, not universal rules for every vendor.

## Task

1. Read the capability contract, instructions, and current KB.
2. Refresh official vendor docs when model-specific, "latest/current", or non-seeded-vendor guidance needs updating.
3. Update `references/long-term-memory.md` with durable prompting guidance, templates, checklists, and official source links.
4. Keep provider-specific claims scoped to the docs reviewed and record the review date.
5. Run `govkb validate` for the project after changes.

## Governance

- Do not store secrets, bearer tokens, API keys, passwords, or copied credential values.
- Do not store local-only absolute paths unless they are part of the governed repo contract.
- Do not store private prompt transcripts, customer data, or one-off session narration.
- Prefer targeted updates with source links; rewrite accepted KB only when the official docs or local convention changed.
- If source evidence is thin, leave the KB minimal and report that no durable update was made.

## Output

- List KB sections changed or say `No KB update`.
- List official vendor docs or repo files used as evidence.
- List validation command and result.
