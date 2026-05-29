# Memory Review Capability Evolution - Requirements Catalog

| ID | Requirement | Source | PoC Assertion | Scenario(s) | Status |
|---|---|---|---|---|---|
| REQ-MRCE-01 | Memory review classifier schema represents capability-evolution proposals separately from memory lessons and semantic new-capability candidates. | `business.md` MVP Scope, Acceptance Criteria | A2, A3 | UC-1, UC-2, UC-3, UC-10 | Planned |
| REQ-MRCE-02 | A review run with no proposal opportunities behaves like the current memory-review flow. | `business.md` Acceptance Criteria | A2, A3, A8 | UC-1 | Planned |
| REQ-MRCE-03 | Valid proposal rows are staged under `.governed/review-proposals/<proposal-id>/`. | Approved Decision D1 | A1, A7 | UC-2, UC-3, UC-5, UC-6 | Planned |
| REQ-MRCE-04 | `.governed/candidates/<candidate-id>/` remains only for new governed capability candidates. | Approved Decision D1, D5 | A4 | UC-9, UC-10 | Planned |
| REQ-MRCE-05 | Proposal review UX is a dedicated `govkb proposals` command family with `list`, `show`, and `apply`. | Approved Decision D2 | A1, A4 | UC-6, UC-7 | Planned |
| REQ-MRCE-06 | Memory review always considers high-confidence capability-evolution opportunities; no separate discovery flag is required. | Approved Decision D3 | A6 | UC-2, UC-3 | Planned |
| REQ-MRCE-07 | Scheduled cron can stage proposals but cannot create executable files, rewrite instructions, or apply proposals. | Approved Decision D3, Safety Rules | A2, A3 | UC-5 | Planned |
| REQ-MRCE-08 | Proposal apply requires explicit approval metadata before writing files. | Approved Decision D4 | A5, A7 | UC-7, UC-8 | Planned |
| REQ-MRCE-09 | Approved output paths must stay under `.governed/capabilities/<capability-id>/`. | Safety Rules | A5, A7 | UC-2, UC-3, UC-7, UC-8 | Planned |
| REQ-MRCE-10 | The first implementation slice supports `script`, `wrapper`, `prompt`, `runbook`, and `instructions_update` proposals. | Approved Decision D5, Proposal Types | A7 | UC-3, UC-10 | Planned |
| REQ-MRCE-11 | Mutating script or wrapper proposals require `--dry-run`, `--preview`, or equivalent explicit confirmation behavior. | Safety Rules | A5, A7 | UC-8 | Planned |
| REQ-MRCE-12 | Proposal artifacts and reports must not contain raw transcripts, secrets, local credential paths, customer identifiers, or production evidence. | Out of Scope, Safety Rules | A5, A7 | UC-4, UC-6 | Planned |
| REQ-MRCE-13 | Memory review reports include a distinct capability-evolution section with count, target capability, type, path, safety profile, source session, and next action. | Acceptance Criteria, Context Observability | A3 | UC-1, UC-2, UC-4, UC-5 | Planned |
| REQ-MRCE-14 | Existing `govkb validate --strict` remains compatible and is reused after proposal application where package-owned tools or instructions are changed. | Acceptance Criteria, Context | A5 | UC-7, UC-8 | Planned |
| REQ-MRCE-15 | Maintainers can trace each staged proposal to the source review and source session without storing the raw session. | Desired Workflow, Acceptance Criteria | A3, A7 | UC-2, UC-5, UC-6 | Planned |
