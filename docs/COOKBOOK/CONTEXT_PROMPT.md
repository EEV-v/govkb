ROLE
Principal engineer producing implementation context for a GovKB feature.

GOAL
Create `context.md` from `business.md` so later phases can plan and implement against real repo structure rather than assumptions.

DOCUMENT CHAIN
- Input: `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/business.md`
- Optional inputs: `business-context.md`, `spec-brief.md`, `open-questions.md`, `decision-log.md`, `spec-handoff.md`
- Output: `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/context.md`
- Next: `USE_CASES_FOCUSED_PROMPT.MD`

INPUT
- FeatureSlug: <kebab-case folder name>
- FeatureName: <human-readable title>
- BusinessDocument: <business.md>

REQUIRED DISCOVERY
Inspect only enough code and docs to ground the feature:

1. Instruction and repo constraints
- Check for repo-local instruction files such as `AGENTS.md`, `.github/copilot-instructions.md`, `CLAUDE.md`, and `.cursorrules`.
- If none exist, state that no repo-local instruction file was found and apply the active session instructions.

2. Documentation map
- Read `README.md`.
- Read `docs/README.md`.
- Read relevant files under `docs/governed-skill-knowledge-framework/`.
- If the feature folder already has spec-phase docs, include them.

3. Code and test map
- Identify likely source modules under `src/govkb/`.
- Identify representative tests under `tests/`.
- Capture exact file paths and patterns that should be reused.

4. Command map
- Capture exact commands, working directory, and prerequisites.
- Include `python3 -m unittest discover -s tests -v` unless a narrower test command is enough for the phase.
- Include `PYTHONPATH=src python3 -m govkb.cli ...` examples for source-checkout CLI verification when relevant.

OUTPUT FORMAT
Write `context.md` with these sections:

```markdown
# <FeatureName> - Implementation Context

Last updated: <YYYY-MM-DD>

## Objective

## Source Artifacts

## Existing Patterns

| Pattern Type | Existing Example | Location | Reuse? |
|---|---|---|---|

## Proposed New Components

| Component | Purpose | Notes |
|---|---|---|

## Data Flow

## Domain Entities

## Command Map

| Task | Command | Working Dir | Preconditions |
|---|---|---|---|

## APIs And CLI Surface

## Storage

## Security And Governance

## Tests

## Observability

## Open Questions

| # | Question | Blocking? | Owner |
|---|---|---|---|

## Assumptions

| # | Assumption | Risk If Wrong |
|---|---|---|

## Traceability

| Context Section | business.md Source |
|---|---|
```

RULES
- Keep evidence path-based and concrete.
- Do not invent test helpers, fixtures, package names, commands, or docs.
- Unknowns become open questions or assumptions.
- Treat `.governed/**` as source of truth for governed packages and `$CODEX_HOME/**` as derived local output.
- Do not store raw assistant session transcript content in repo artifacts.
- Keep output concise enough to be useful as an engineering handoff.

END
