# Governed Skill Contract And Migration - Requirements Catalog

| ID | Requirement | Source | PoC Assertion | Scenario(s) | Status |
|---|---|---|---|---|---|
| REQ-GSCM-01 | Define a strict governed-skill package rooted at `.governed/capabilities/<capability-id>/`. | business.md Governed Skill Package Shape | Inspect current package loader and define target contract artifact. | UC-1, UC-3 | Planned |
| REQ-GSCM-02 | Enforce domain-specific lower kebab-case capability ids and materialized `govkb-<project>-<capability>` names. | business.md Naming And Routing Conventions | Compare current `materialized_skill_id` behavior and candidate naming failures. | UC-1, UC-4, UC-9 | Planned |
| REQ-GSCM-03 | Require memory sections to match the contract and reject placeholders after activation. | business.md Long-Term Memory And Knowledge Conventions | Inspect current `CapabilityTarget.sections` parsing and Clearing weak memory example. | UC-1, UC-4, UC-6 | Planned |
| REQ-GSCM-04 | Validate commands and repo paths in memory for correct project-relative references. | business.md Long-Term Memory And Knowledge Conventions | Show current validation passes a Clearing package with invalid `src/...` paths. | UC-1, UC-4 | Planned |
| REQ-GSCM-05 | Standardize `tools/scripts/`, `tools/fixtures/`, and `tools/README.md` for skill-owned tooling. | business.md Tooling Conventions | Define contract artifact and materialization expectation. | UC-3, UC-7 | Planned |
| REQ-GSCM-06 | Reject secrets, raw transcripts, local user-home paths, and credential-file paths from governed packages. | business.md Governed Skill Package Shape, Existing Skill Conversion | Use synthetic fixtures for unsafe content in planned tests. | UC-6, UC-8 | Planned |
| REQ-GSCM-07 | Add strict validation that reports exact package-quality failures. | business.md Strict Validation | Baseline shows current validation is TOML-shape only for these quality cases. | UC-1, UC-4, UC-8 | Planned |
| REQ-GSCM-08 | Gate candidate auto-create with strict validation. | business.md Strict Validation, Clearing Remediation Use Case | Current Clearing auto-create activated a weak package; target behavior refuses. | UC-4 | Planned |
| REQ-GSCM-09 | Provide preview-first conversion from existing Codex skill path or name. | business.md Existing Skill Conversion | Baseline CLI has no `convert` command; target CLI contract defined. | UC-2 | Planned |
| REQ-GSCM-10 | `--write` creates a governed capability package without mutating the source local skill. | business.md Existing Skill Conversion | Planned temp-dir conversion test. | UC-3, UC-5 | Planned |
| REQ-GSCM-11 | Conversion preserves safe durable instructions, memory, prompts, scripts, and fixtures. | business.md Existing Skill Conversion, Tooling Conventions | Planned synthetic skill with safe script. | UC-3, UC-7 | Planned |
| REQ-GSCM-12 | Conversion records migration metadata and reports approved differences. | business.md Existing Skill Conversion | Planned metadata assertion. | UC-3, UC-5 | Planned |
| REQ-GSCM-13 | Converted packages materialize back into Codex through existing apply flow. | business.md Acceptance Criteria | Extend `tests/test_apply.py` for tools and converted package output. | UC-7 | Planned |
| REQ-GSCM-14 | Validation output supports machine-readable UI/report use. | business.md Strict Validation | Extend JSON validation/status behavior. | UC-8 | Planned |
| REQ-GSCM-15 | Provide a Clearing remediation path for weak auto-created capabilities. | business.md Clearing Remediation Use Case | Document cleanup path; implementation can validate and block future repeats. | UC-4, UC-9 | Documentation Only until applied to Clearing |
