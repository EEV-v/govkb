# Final Review Prompt

Use this after `business-review-pack.md` and `business-review-message.md` are generated and before anything is sent externally.

## Goal

Run a quick independent second pass with only the relevant feature artifacts in scope. The purpose is to catch:

- stale asks
- pack/message drift
- contradictions with the canonical draft
- readiness wording that does not match the real workflow state
- avoidable stakeholder confusion

## Reviewer Input

Use a review context bundle when available. If no orchestrator bundle exists, review these files directly:

- Base artifacts:
  - `business.md`
  - `business-context.md`
  - `context.md`
  - `spec-brief.md`
  - `open-questions.md`
  - `decision-log.md`
- Final outbound artifacts:
  - `business-review-pack.md`
  - `business-review-message.md`
- Latest reconciled feedback round artifacts when available:
  - reviewed or normalized source
  - round diff
  - reconciliation file
- Workflow summary:
  - current stage
  - ready for business review?
  - ready for engineering handoff?
  - tracker/reference readiness
  - pending feedback status

## Review Checks

1. Do `business-review-pack.md` and `business-review-message.md` match canonical `business.md`?
2. Do blocking questions and decisions match the current ledgers?
3. Are asks concrete enough to answer without extra translation?
4. Is any wording stale, misleading, duplicated, or more final than the current stage allows?
5. Does the message summarize the pack without dropping an important ask?
6. If latest feedback was reconciled, does the pack reflect the reconciled state rather than raw feedback?
7. Is the pack safe to send now, or should it be refreshed/fixed first?

## Output Format

- `Findings`
  - severity: `high`, `medium`, or `low`
  - include file references
  - focus on send-readiness, not style nitpicks
- `What Looks Good`
- `Send Recommendation`
  - `Yes` or `No`
  - one-sentence reason

## Guardrails

- Treat this as a fast second-pass review, not a new scope-design exercise.
- Prefer catching mismatches and unclear asks over broad rewrites.
- If there are no blocking issues, say that clearly.

