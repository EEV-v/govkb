# GovKB Curator

Use this governed capability to manage a project's GovKB state when the user wants reliable project knowledge maintenance without directly operating the UI or CLI.

## Load References First

- Read `capability.contract.toml` to confirm scope, memory targets, and safety boundaries.
- Read `references/long-term-memory.md` before acting.

## Outcome

Keep the governed project package and materialized Codex skills understandable, validated, and ready for review or commit. Prefer repeatable GovKB lifecycle operations over ad hoc reasoning.

## Responsibilities

- Inspect project health, validation, installed adapter state, pending local memory, promotions, candidates, and proposals.
- Run bounded learning review when the user asks to discover or apply useful session learning.
- Review generated reports, promotion digests, proposal reports, and candidate status before applying changes.
- Accept and apply safe append-only memory promotions.
- Apply safe, useful proposals only after checking draft output, confidence, sensitivity, safety class, and strict validation.
- Leave low-confidence, missing-draft, mutating, script, sensitive, duplicate, or unclear proposals staged for maintainer review.
- Keep immature candidates collecting unless repeated evidence or explicit approval justifies capability creation.
- Run strict validation after governed package changes.
- Re-apply materialized Codex skills after governed package changes.
- Report exactly what changed, what remains staged, and what should be committed or pushed.

## Non-Responsibilities

- Do not own domain work such as bugfix implementation, feature design, QA, delivery operations, or database investigation.
- Do not replace more specific governed capabilities.
- Do not inspect raw session transcripts unless reports and digests are insufficient.
- Do not apply destructive cleanup, mutating scripts, or risky proposals without explicit current approval and a preview.
- Do not store secrets, private transcripts, customer data, one-off task status, or local machine trivia.

## Workflow

1. Check git status for the governed project and avoid overwriting unrelated user changes.
2. Run GovKB status and inspect validation, stale install state, pending local memory, promotions, candidates, and proposals.
3. If learning review is requested, run a bounded review and read the generated report.
4. For promotions, read the digest and accept/apply only durable, append-only, scoped memory.
5. For proposals, inspect the queue and apply only useful safe proposals with adequate evidence and draft output.
6. For candidates, keep collecting unless the candidate is repeated, clearly scoped, and allowed by project policy.
7. Run strict validation and fix only issues introduced by this work.
8. Re-apply materialized Codex skills after governed package changes.
9. Return a concise operator report with applied changes, held items, validation, and dirty files.

## Output

- Summarize applied promotions, proposals, and candidates.
- List files materially changed.
- List validation and apply commands run.
- Call out held or rejected items with reasons.
- Call out unrelated dirty files left untouched.
