# GovKB Skill Inventory Dry Run

- Run at: `2026-04-21T20:46:00Z`
- Skills root: `/mnt/c/Users/Ev/.codex/skills`
- Skills scanned: `27`
- Governed capability now: `9`
- Legacy keep until migrated: `12`
- Adapter-local only: `6`
- Memory-bearing skills: `9`
- Generated contract candidates: `9`
- Validation status: `passed`

## Skill Classification

| Skill | Track | Memory | Explicit Acceptance | Reason |
|---|---|---:|---:|---|
| .system/imagegen | adapter-local only | no | no | system skill is assistant/runtime owned |
| .system/openai-docs | adapter-local only | no | no | system skill is assistant/runtime owned |
| .system/plugin-creator | adapter-local only | no | no | system skill is assistant/runtime owned |
| .system/skill-creator | adapter-local only | no | no | system skill is assistant/runtime owned |
| .system/skill-installer | adapter-local only | no | no | system skill is assistant/runtime owned |
| clearing-azure-monday-artifact-sync | legacy keep until migrated | no | no | project-specific skill without first-wave memory evidence<br>keep operationally available until contract parity is proven |
| clearing-bugfixer | governed capability now | yes | no | has durable memory file<br>project workflow knowledge keeper |
| clearing-db-audit-guard | legacy keep until migrated | no | no | project-specific skill without first-wave memory evidence<br>keep operationally available until contract parity is proven |
| clearing-devops-delivery | legacy keep until migrated | no | no | project-specific skill without first-wave memory evidence<br>keep operationally available until contract parity is proven |
| clearing-feature-cookbook | legacy keep until migrated | no | no | project-specific skill without first-wave memory evidence<br>keep operationally available until contract parity is proven |
| clearing-feature-estimator | governed capability now | yes | yes | has durable memory file<br>project workflow knowledge keeper |
| clearing-feature-question-manager | legacy keep until migrated | no | no | project-specific skill without first-wave memory evidence<br>keep operationally available until contract parity is proven |
| clearing-feature-review-diff | legacy keep until migrated | no | no | project-specific skill without first-wave memory evidence<br>keep operationally available until contract parity is proven<br>looks project-domain but has no durable memory file yet |
| clearing-feature-review-pack | legacy keep until migrated | no | no | project-specific skill without first-wave memory evidence<br>keep operationally available until contract parity is proven<br>looks project-domain but has no durable memory file yet |
| clearing-feature-spec-cookbook | legacy keep until migrated | no | no | project-specific skill without first-wave memory evidence<br>keep operationally available until contract parity is proven |
| clearing-feature-tracker-sync | legacy keep until migrated | no | no | project-specific skill without first-wave memory evidence<br>keep operationally available until contract parity is proven |
| clearing-keycloak-debug | legacy keep until migrated | no | no | project-specific skill without first-wave memory evidence<br>keep operationally available until contract parity is proven |
| clearing-master-reviewer | governed capability now | yes | no | has durable memory file<br>project workflow knowledge keeper |
| clearing-opensearch-log-query | legacy keep until migrated | no | no | project-specific skill without first-wave memory evidence<br>keep operationally available until contract parity is proven |
| clearing-prod-to-staging-replay | legacy keep until migrated | no | no | project-specific skill without first-wave memory evidence<br>keep operationally available until contract parity is proven |
| clearing-qa-on-staging | governed capability now | yes | no | has durable memory file<br>project workflow knowledge keeper |
| clearing-review-cashflow-reconciliation | governed capability now | yes | no | has durable memory file<br>reviewer capability with project-domain routing |
| clearing-review-corporate-actions-processing | governed capability now | yes | no | has durable memory file<br>reviewer capability with project-domain routing |
| clearing-review-internal-account-governance | governed capability now | yes | no | has durable memory file<br>reviewer capability with project-domain routing |
| clearing-review-security-master | governed capability now | yes | no | has durable memory file<br>reviewer capability with project-domain routing |
| clearing-review-transaction-lots-reconciliation | governed capability now | yes | no | has durable memory file<br>reviewer capability with project-domain routing |
| ev-style-writer | adapter-local only | no | no | not project-specific Clearing knowledge |

## Interpretation

- `governed capability now`: first-wave repo contract candidates.
- `legacy keep until migrated`: project-specific skills that should remain working until parity is proven.
- `adapter-local only`: assistant/runtime/personal helpers that should not become project source of truth.
