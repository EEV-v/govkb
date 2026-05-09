# GovKB Usage Examples

These examples show how GovKB is intended to feel in real project use. They are deliberately more detailed than the customer presentation: each one includes the user prompt, CLI commands, expected artifacts, and the governance decision.

## Examples

| Example | What it proves |
|---|---|
| [Team Learning Loop](team-learning-loop.md) | A reusable lesson moves from one local Codex setup into repo-governed memory and then to another teammate. |
| [Unsafe Learning Rejection](unsafe-learning-rejection.md) | Non-append edits, local-only paths, and risky content stay out of durable governed memory. |
| [Clearing Governed Workflow](clearing-governed-workflow.md) | A real project capability can guide feature, bugfix, and support workflows without copying local assumptions into the repo. |
| [New Capability Candidate](new-capability-candidate.md) | Repeated unmatched work can become a reviewed capability instead of silently creating an active skill. |
| [Isolated Automation Review](isolated-automation-review.md) | Automated promotion creates a reviewable branch worktree without dirtying the active checkout. |

## Common Demo Setup

```bash
govkb validate --strict /path/to/project
govkb apply codex --project-root /path/to/project --codex-home "$CODEX_HOME"
```

In all examples, `.governed/` is the source of truth. Local Codex skills are derived outputs.
