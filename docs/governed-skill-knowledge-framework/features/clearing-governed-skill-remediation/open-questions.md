# Clearing Governed Skill Remediation - Open Questions

| ID | Question | Status | Owner | Notes |
|---|---|---|---|---|
| Q1 | Should `local-stack-workflow` be repaired, replaced, deprecated, or demoted? | Blocking | Clearing maintainer | Requires strict validation and human review. |
| Q2 | Should Clearing auto-create be disabled until quality gates are in place? | Blocking | Clearing maintainer | Current package has `auto_create_capabilities = true`. |
| Q3 | Which Git repository should own Clearing `.governed` state long term? | Blocking | Clearing maintainer | `/home/ev/code/Clearing` is a workspace, not a Git repo. |
| Q4 | Which existing mature Clearing skills should be referenced to avoid duplicate weak governed capabilities? | Deferred | Clearing/GovKB maintainers | Useful before broader migration. |
