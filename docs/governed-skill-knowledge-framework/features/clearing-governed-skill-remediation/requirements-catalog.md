# Clearing Governed Skill Remediation - Requirements Catalog

| ID | Requirement | Source | PoC Assertion | Scenario(s) | Status |
|---|---|---|---|---|---|
| REQ-CGSR-01 | Strict validation identifies the current weak Clearing governed package issues. | `business.md` acceptance criteria 1 | A synthetic `local-stack-workflow` package produces strict issues in remediation output. | UC-1, UC-2, UC-9 | Candidate |
| REQ-CGSR-02 | Maintainer has a reviewed remediation plan before files are changed. | `business.md` acceptance criteria 2, D4 | Report generation is default read-only and recommendations require approval before package rewrites. | UC-1, UC-3, UC-6 | Candidate |
| REQ-CGSR-03 | Weak generic active capability is classified for repair, replacement, deprecation, or demotion. | `business.md` acceptance criteria 3, D6 | `GSK-ID-002` maps to demote-or-deprecate recommendation. | UC-2, UC-9 | Candidate |
| REQ-CGSR-04 | Invalid commands and repo paths are identified for correction or removal. | `business.md` acceptance criteria 4 | `GSK-PATH-001` maps to path repair after approval without automatic edits. | UC-3, UC-9 | Candidate |
| REQ-CGSR-05 | Candidate auto-create no longer silently activates weak Clearing capabilities. | `business.md` acceptance criteria 5, D5 | Report exposes project automation policy and notes strict activation constraints. | UC-4 | Candidate |
| REQ-CGSR-06 | Useful durable Clearing memory remains available after remediation. | `business.md` acceptance criteria 6, D3 | Strict-valid `project-knowledge-steward` receives no remediation recommendation. | UC-7 | Candidate |
| REQ-CGSR-07 | Final Clearing package validates under strict mode or records explicit exceptions. | `business.md` acceptance criteria 7 | Report includes strict status and issue list that can serve as the exception baseline. | UC-1, UC-8 | Candidate |
| REQ-CGSR-08 | Durable Clearing `.governed` writes target the Git repository that owns project governance. | D7, `scope-lock.md` | `--write-report` is blocked for non-Git or unowned project roots. | UC-5, UC-6 | Candidate |
| REQ-CGSR-09 | Remediation output is safe for tools and does not leak unsafe local content. | Governance cases from `use-cases.md` | JSON/markdown output uses strict issue messages and recommendation text, not raw file content. | UC-8, UC-9 | Candidate |
| REQ-CGSR-10 | Clearing production code is not touched by the first remediation pass. | `business.md` out of scope | Command writes no files by default and optional report writes stay under `.governed/reports/`. | UC-3, UC-5, UC-6 | Candidate |
