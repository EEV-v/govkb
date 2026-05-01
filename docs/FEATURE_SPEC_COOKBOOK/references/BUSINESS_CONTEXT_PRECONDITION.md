# GovKB Business Context Precondition

Use this before `context.md`, `spec-brief.md`, `open-questions.md`, `decision-log.md`, or `business-review-pack.md`.

## Goal

Produce `business-context.md` that grounds the feature in product and stakeholder context before spec analysis starts.

## Output

- `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/business-context.md`

## Source Priority

1. Current feature `business.md`
2. `README.md`
3. `docs/README.md`
4. `docs/governed-skill-knowledge-framework/business.md`
5. `docs/governed-skill-knowledge-framework/implementation-plan.md`
6. `docs/governed-skill-knowledge-framework/mvp-plus-test-plan.md`
7. Relevant neighboring feature folders under `docs/governed-skill-knowledge-framework/features/`
8. External sources only when local documentation is insufficient, ambiguous, or stale
   - official VS Code documentation for extension behavior
   - official Python packaging documentation when packaging behavior is in scope
   - official OpenAI/Codex documentation only when product/API behavior depends on it

## Rules

- Prefer project documentation before browsing.
- If external sources are used, record source name, link, and access date.
- Keep GovKB product conventions separate from external platform context.
- If project docs and external context disagree, create explicit assumptions or open questions.
- Do not copy external wording into canonical `business.md` automatically.
- Use business context to improve questions and decisions, not to bypass reviewed reconciliation.

## Minimum Contents

- business purpose and affected workflow
- domain/product terms needed to read the feature
- relevant product/process precedent from project docs
- external platform context when needed
- source-backed constraints, deadlines, or business rules
- explicit assumptions
- explicit open questions caused by missing, conflicting, or stale context
- source list with dates

