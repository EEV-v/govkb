# Governed Skill Quality Gates - Decision Log

| ID | Decision | Status | Owner | Rationale |
|---|---|---|---|---|
| D1 | Split existing-skill conversion out of the first slice. | Approved | Product | Quality gates must exist before conversion can be safe. |
| D2 | Keep normal `govkb validate` backward-compatible at first. | Approved | Product/Engineering | Existing projects may need cleanup before strict mode can become default. |
| D3 | Make strict validation mandatory for candidate activation. | Approved | Product/Governance | Prevents another weak auto-created active capability. |
| D4 | GovKB packages helper tools but does not execute them during validation or materialization. | Approved | Security/Governance | Avoids hidden script execution risk. |
| D5 | Unsafe content is not copied into governed memory. | Approved | Security/Governance | Reports may include redacted metadata and reasons only. |
| D6 | Clearing remediation is a follow-up operational feature, not the first product implementation slice. | Approved | Product | Clearing remains the proving case without expanding product scope. |
