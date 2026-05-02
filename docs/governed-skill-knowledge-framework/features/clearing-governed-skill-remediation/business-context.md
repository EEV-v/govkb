# Clearing Governed Skill Remediation - Business Context

Last updated: 2026-05-01

## Business Purpose

Clearing is the proving case for GovKB governed skill quality gates. The current Clearing governed package is described as syntactically valid but semantically weak: an active `local-stack-workflow` capability was created from Corporate Actions-related evidence, contains generic memory, and includes paths that do not match the Clearing workspace root.

This feature turns strict validation output into a safe operational cleanup workflow. It is not a GovKB product feature implementation and should not change Clearing production code.

## Affected Workflow

1. GovKB strict validation runs against the Clearing governed package.
2. The maintainer reviews weak capability findings.
3. Candidate auto-create is disabled or constrained while remediation is active.
4. The maintainer chooses repair, rename/replace, deprecate, or demote.
5. Engineering applies only approved governed package changes in the owning Git repository.
6. Final strict validation confirms the package is clean or records explicit exceptions.

## Domain Terms

| Term | Meaning |
|---|---|
| Clearing governed package | The `.governed/` state used for Clearing project AI collaboration. |
| `local-stack-workflow` | The weak active capability called out by the split feature. |
| Remediation report | Reviewable evidence from strict validation and human assessment before file changes. |
| Demote | Move an active capability back to candidate/review state when evidence is insufficient. |
| Deprecate | Keep compatibility/history while removing routing or new learning. |
| Replace | Create a better domain-specific capability and retire the weak one. |

## Product And Process Precedent

- `governed-skill-quality-gates` provides the strict validation behavior this remediation depends on.
- `governed-skill-contract-and-migration` split Clearing remediation out as operational follow-up, not product MVP scope.
- GovKB product docs state assistant-local files are derived output and project knowledge belongs in repo-governed source.
- Existing candidate policy requires repeated evidence and review before activating new governed capabilities.

## Source-Backed Constraints

- Do not perform remediation before quality gates can identify weak package shape.
- Do not change Clearing production code.
- Do not query production systems.
- Preserve useful project-knowledge-steward memory unless strict validation identifies a concrete safety or correctness issue.
- Durable `.governed` changes must be written in the Git repository that owns Clearing project governance.

## Assumptions

- Engineering can prepare the remediation workflow before quality gates are implemented.
- Actual package mutation waits for strict validation output and maintainer approval.
- If the workspace being inspected is not the owning Git repo, the first output is a remediation report only.
- If `local-stack-workflow` is confirmed weak or wrong-domain, demotion or deprecation is safer than in-place repair.

## Open Context Gaps

- The actual Clearing workspace is not available in this local GovKB checkout, so implementation planning must verify the live path and repository owner before writing.
- The final remediation option depends on strict-validation findings and maintainer review.
- The list of mature existing Clearing skills to cross-reference remains deferred until broader migration work.

## Sources

- `docs/governed-skill-knowledge-framework/features/clearing-governed-skill-remediation/business.md` on 2026-05-01
- `docs/governed-skill-knowledge-framework/features/governed-skill-quality-gates/spec-handoff.md` on 2026-05-01
- `docs/governed-skill-knowledge-framework/features/governed-skill-contract-and-migration/business.md` on 2026-05-01
- `docs/governed-skill-knowledge-framework/business.md` on 2026-05-01
