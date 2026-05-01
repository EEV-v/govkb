# Codex Skill Governed Conversion - Decision Log

| ID | Decision | Status | Owner | Rationale |
|---|---|---|---|---|
| D1 | Conversion depends on governed skill quality gates. | Approved | Product | Conversion needs strict package rules before writes are safe. |
| D2 | MVP converts one skill at a time. | Approved | Product | Avoids bulk migration risk. |
| D3 | MVP write mode creates new packages only. | Approved | Product/Engineering | Prevents accidental overwrite of curated governed memory. |
| D4 | Source local skills are never mutated. | Approved | Governance | Local assistant artifacts are inputs, not targets. |
| D5 | Conversion does not execute helper scripts. | Approved | Security/Governance | Script safety is reviewed, not trusted by execution. |
