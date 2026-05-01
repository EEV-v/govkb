ROLE
Principal reviewer evaluating a GovKB implementation plan before coding.

GOAL
Produce `review.md` with prioritized findings and a final `Ready for Implementation` decision.

DOCUMENT CHAIN
- Inputs:
  - `implementation-plan.md`
  - `use-cases.md`
  - `requirements-catalog.md`
  - `poc-plan.md`
  - `poc-output.md`
  - relevant source and test files
- Output:
  - `docs/governed-skill-knowledge-framework/features/<FeatureSlug>/review.md`
- Next:
  - If ready: `TEST_SCAFFOLD_PROMPT.MD` or `IMPLEMENT_PROMPT.MD`
  - If not ready: revise `implementation-plan.md` and rerun review

INPUT
- FeatureSlug: <kebab-case folder name>
- FeatureName: <human-readable title>

REVIEW CHECKS

| Area | Questions |
|---|---|
| Scope | Does the plan implement the accepted business scope without unrelated refactors? |
| Reuse | Does it extend existing GovKB modules and tests where practical? |
| CLI contract | Are argparse commands, flags, cwd, and preview/dry-run behavior explicit? |
| Governance | Does it preserve repo-owned `.governed` source and derived assistant-local outputs? |
| Safety | Does it avoid raw transcript leakage and user-home mutations in tests? |
| Tests | Are unit, command, and workflow tests mapped to scenarios and requirements? |
| Commands | Does every command include working directory and prerequisites? |
| Rollback | Can each phase be reverted or disabled cleanly? |
| PoC parity | Does the implementation plan preserve or explain all PoC assertions? |

OUTPUT FORMAT

```markdown
# <FeatureName> - Implementation Plan Review

Last updated: <YYYY-MM-DD>

## Verdict

Ready for Implementation: <Yes | No>

## Findings

| Priority | Area | Finding | Evidence | Recommendation |
|---|---|---|---|---|

## Gate Checklist

| Gate | Status | Evidence |
|---|---|---|
| Phase order preserved | PASS/WARN/FAIL | |
| Requirements mapped | PASS/WARN/FAIL | |
| PoC assertions carried forward | PASS/WARN/FAIL | |
| Tests are target-idiomatic | PASS/WARN/FAIL | |
| Commands are executable from stated cwd | PASS/WARN/FAIL | |
| Safety/governance constraints covered | PASS/WARN/FAIL | |
| Rollback is explicit | PASS/WARN/FAIL | |

## Required Revisions

## Non-blocking Recommendations

## Residual Risks
```

PRIORITY DEFINITIONS
- P0: plan can cause data loss, secret/raw transcript exposure, or wrong-source-of-truth mutation.
- P1: plan likely fails implementation, breaks public command behavior, or lacks necessary verification.
- P2: plan is workable but has avoidable maintenance, coverage, or clarity risk.
- P3: polish or minor documentation improvement.

RULES
- Findings first, ordered by severity.
- Cite exact files, docs, or plan sections.
- Do not approve if test scaffold paths, commands, or fixtures are invented.
- Do not approve if final verification is missing without a concrete reason.

END
