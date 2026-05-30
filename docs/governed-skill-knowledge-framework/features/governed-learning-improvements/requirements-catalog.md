# Governed Learning Improvements - Requirements Catalog

Last updated: 2026-05-30

| ID | Requirement | Source | PoC Assertion | Scenario(s) | Status |
|---|---|---|---|---|---|
| REQ-GLI-01 | Provide a read-only proposal review report that groups similar staged proposals. | AC1 | A-1 | UC-1 | Implemented in Phase 0 |
| REQ-GLI-02 | Show maintainer next actions for each proposal group. | AC1 | A-1 | UC-1 | Implemented in Phase 0 |
| REQ-GLI-03 | Score proposal quality without mutating proposal files. | AC4 | A-2 | UC-2 | Implemented in Phase 0 |
| REQ-GLI-04 | Provide one memory-review health report for a project. | AC2 | A-3 | UC-3 | Implemented in Phase 1 |
| REQ-GLI-05 | Filter obvious self-generated tails after a processed marker. | AC3 | A-4 | UC-4 | Planned for Phase 2 |
| REQ-GLI-06 | Preserve user-authored decisions in appended session tails. | AC3 | A-4 | UC-5 | Planned for Phase 2 |
| REQ-GLI-07 | Score capability maturity from governed artifacts and pending proposals. | AC5 | A-5 | UC-6 | Planned for Phase 3 |
| REQ-GLI-08 | Provide a VS Code/GovKB freshness check. | AC6 | A-6 | UC-7 | Implemented in Phase 4 |
| REQ-GLI-09 | Keep existing public commands backward compatible. | AC7 | A-7 | UC-1 through UC-7 | Passed in Phase 0-4 regression |

## Out Of Scope

| Item | Reason |
|---|---|
| Auto-apply proposal groups | Maintainer review and approval are a core safety boundary. |
| Live environment verification | This feature is about local governed workflow health and should not need credentials. |
| Clearing product code changes | Clearing is the first consumer, not the feature implementation owner. |
