# Question Manager Review Prompt

Review the question/decision manager behavior for GovKB spec convergence.

## Inputs

- `docs/FEATURE_SPEC_COOKBOOK/QUESTION_MANAGER_PROMPT.MD`
- a feature folder containing `open-questions.md` and `decision-log.md`
- relevant `business.md`, `business-context.md`, `context.md`, and feedback artifacts

## Review Checks

1. Does it preserve existing ids, statuses, owners, and notes?
2. Does it avoid deleting unresolved rows when a later source is narrower?
3. Does it keep questions and decisions separate?
4. Does it identify first-slice decisions separately from deferred public-launch decisions?
5. Are new blockers reasonable and actionable?

## Output

- Findings
- Suggested ledger updates
- Residual risks

