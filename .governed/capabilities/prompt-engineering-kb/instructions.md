# Prompt Engineering KB

Use this governed capability when designing, auditing, rewriting, migrating, or debugging prompts for OpenAI, Anthropic/Claude, or another named LLM vendor, or when building production prompt templates, tool-use instructions, output contracts, or prompt evaluation rubrics.

## Load References First

- Read `references/long-term-memory.md` before acting. It is the governed prompt-engineering KB for this capability.
- If the user asks for "latest", "current", model-specific, or provider-specific guidance, refresh official vendor docs before making time-sensitive claims.
- If the user names a vendor that is not covered by the seeded OpenAI/Anthropic KB, do not extrapolate. Retrieve that vendor's official prompting, model, tool-use, structured-output, and safety docs first.

## Workflow

1. Identify the provider, model family, task contract, risk level, output format, allowed tools, and side effects.
2. Define success criteria and a small evaluation set before optimizing wording.
3. Start with the smallest prompt that preserves the product contract, then add structure only for observed failure modes.
4. Keep stable instructions separate from variable user input, retrieved context, and tool results.
5. Apply provider-specific guidance from the KB or refreshed official vendor docs. Treat cross-vendor rules as hypotheses until validated against that vendor's documentation and eval results.
6. Include output contracts, missing-evidence behavior, stop conditions, and tool-permission rules for production prompts.
7. Return the revised prompt with a concise diagnosis, provider-specific notes, and an eval plan.

## Governance

- Treat the KB as a governed source file. Local materialized skill edits are not durable.
- Keep official-source URLs in the KB source map and refresh them when adding vendor-specific or model-specific guidance.
- Do not store secrets, customer data, or private prompt transcripts in the KB.
