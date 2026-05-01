# Combined Review Synthesis Prompt

Synthesize multiple independent reviews of the feature-spec cookbook and helper skills.

## Goal
Turn separate findings into one practical improvement plan.

## Synthesis Priorities
1. Identify repeated themes across reviewers.
2. Separate true must-fix issues from nice-to-have cleanup.
3. Prefer changes that improve repeated-loop usability, reduce ceremony, and increase reliability.
4. Preserve the parts of the workflow that clearly add value.

## Output Format
- `Consensus Must-Fix Issues`
- `Consensus Simplifications`
- `Conflicting Reviewer Opinions`
- `Recommended Next Patch Set`
- `What Should Stay Exactly As-Is`
- `Overall Judgment` on whether the workflow is already operationally useful

## Decision Lens
Choose improvements that make the workflow easier to run every week, not just easier to explain once.
