# Codex Skill Governed Conversion - Requirements Catalog

| ID | Requirement | Source | PoC Assertion | Scenario(s) | Status |
|---|---|---|---|---|---|
| REQ-CSGC-01 | Maintainer can preview conversion for one local Codex skill without writing files. | `business.md` acceptance criteria 1 | `govkb convert skill` default mode must leave `.governed/capabilities/` unchanged. | UC-1 | Candidate |
| REQ-CSGC-02 | Preview clearly shows target package, copied content, rejected content, manual-review content, and validation status. | `business.md` acceptance criteria 2 | Human and JSON preview output expose source, target, planned files, rejected files, manual review files, parity, and strict status. | UC-1, UC-9 | Candidate |
| REQ-CSGC-03 | Write mode creates a new governed capability package when preview is acceptable. | `business.md` acceptance criteria 3 | Explicit `--write` creates one new capability package. | UC-4 | Candidate |
| REQ-CSGC-04 | Write mode fails if the target package already exists. | `business.md` acceptance criteria 4 | Existing capability directory prevents writes. | UC-5 | Candidate |
| REQ-CSGC-05 | Source local skill remains unchanged. | `business.md` acceptance criteria 5, decision D4 | Compare source file content before and after preview/write/failure. | UC-1, UC-3, UC-5 | Candidate |
| REQ-CSGC-06 | Safe long-term memory, prompts, and helper scripts can be preserved in governed locations. | `business.md` acceptance criteria 6 | Safe source `references/`, `prompts/`, and tools copy to package locations. | UC-7 | Candidate |
| REQ-CSGC-07 | Unsafe content is rejected and not copied into repo-governed memory. | `business.md` acceptance criteria 7, decision D7 | Synthetic unsafe content produces rejected metadata and absent governed content. | UC-6, UC-9 | Candidate |
| REQ-CSGC-08 | Converted package passes strict validation before write succeeds. | `business.md` acceptance criteria 8, dependency on quality gates | Write runs `validate_governed_skill_package` and rolls back on strict errors. | UC-4 | Candidate |
| REQ-CSGC-09 | Converted package can be materialized with normal GovKB Codex apply. | `business.md` acceptance criteria 9 | `run_codex_apply` materializes the converted package from canonical `instructions.md`. | UC-8 | Candidate |
| REQ-CSGC-10 | Rollback path is clear. | `business.md` acceptance criteria 10 | Write success output names target package and remove/revert rollback guidance. | UC-4 | Candidate |

