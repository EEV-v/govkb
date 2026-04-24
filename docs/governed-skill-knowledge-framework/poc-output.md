# PoC Output - Governed Skill Knowledge Framework

Last updated: 2026-04-22

## 1. Scope And Run Metadata

This PoC is a migration inventory gate. It proves read-only skill classification and first-wave contract candidate generation; it does not prove adapter materialization, repo resolution, governed worktree isolation, live scheduler parity, or the self-improving learning loop.

| Field | Value |
|-------|-------|
| Run command | `./regenerate-poc-data.sh` |
| Run status | Passed |
| Latest run time | `2026-04-21T20:46:00Z` |
| Skills root | `/mnt/c/Users/Ev/.codex/skills` |
| Output directory | `poc-artifacts/` |
| Inventory hash | `cb782540cf1f2812863d4a5bdfd04f1bffcb7288b0b076e7691154830ba9fb67` |

## 2. Assertion Results Matrix

| Assertion ID | Requirement ID(s) | Scope Size | Pass | Fail | Status | Notes |
|--------------|-------------------|------------|------|------|--------|-------|
| A-01 | REQ-TR-14, REQ-TR-16, REQ-AI-10, REQ-AI-12 | 27 skills | 27 | 0 | Passed | Every discovered skill was classified exactly once. |
| A-02 | REQ-TR-07, REQ-TR-16, REQ-AI-02 | 9 memory-bearing skills | 9 | 0 | Passed | All memory-bearing skills became governed contract candidates. |
| A-03 | REQ-TR-16, REQ-AI-12 | 6 adapter-local skills | 6 | 0 | Passed | `.system/*` and `ev-style-writer` stayed adapter-local. |
| A-04 | REQ-TR-14, REQ-TR-16, REQ-AI-10 | 12 legacy skills | 12 | 0 | Passed | Non-memory Clearing skills remain safe under legacy fallback. |
| A-05 | REQ-TR-01, REQ-TR-02, REQ-TR-03, REQ-AI-01, REQ-AI-02, REQ-AI-03, REQ-AI-11 | 9 contract candidates | 9 | 0 | Passed | Proposed contract TOML files were generated under `poc-artifacts/proposed-contracts/`. |
| A-06 | REQ-TR-09, REQ-AI-06 | 1 approval-gated skill | 1 | 0 | Passed | `clearing-feature-estimator` preserved `requires_explicit_acceptance = true`. |
| A-07 | REQ-TR-10, REQ-TR-12, REQ-AI-08 | 1 source tree | 1 | 0 | Passed | Script writes only feature-local evidence and does not modify local skills. |
| A-08 | REQ-TR-06, REQ-AI-12 | 2 reruns | 2 | 0 | Passed | Rerun succeeded and inventory hash stayed stable. |

## 3. Key Metrics

| Metric | Value |
|--------|-------|
| Total skills scanned | 27 |
| Governed capability now | 9 |
| Legacy keep until migrated | 12 |
| Adapter-local only | 6 |
| Memory-bearing skills | 9 |
| Approval-gated skills | 1 |
| Generated contract candidates | 9 |
| Validation errors | 0 |

## 4. First-Wave Governed Candidates

| Capability | Reason |
|------------|--------|
| `clearing-bugfixer` | durable memory file + project workflow keeper |
| `clearing-feature-estimator` | durable memory file + explicit acceptance policy |
| `clearing-master-reviewer` | durable memory file + project workflow keeper |
| `clearing-qa-on-staging` | durable memory file + project workflow keeper |
| `clearing-review-cashflow-reconciliation` | durable memory file + reviewer capability |
| `clearing-review-corporate-actions-processing` | durable memory file + reviewer capability |
| `clearing-review-internal-account-governance` | durable memory file + reviewer capability |
| `clearing-review-security-master` | durable memory file + reviewer capability |
| `clearing-review-transaction-lots-reconciliation` | durable memory file + reviewer capability |

## 5. Legacy Keep Until Migrated

These remain operationally available and should not block repo-first rollout:

```text
clearing-azure-monday-artifact-sync
clearing-db-audit-guard
clearing-devops-delivery
clearing-feature-cookbook
clearing-feature-question-manager
clearing-feature-review-diff
clearing-feature-review-pack
clearing-feature-spec-cookbook
clearing-feature-tracker-sync
clearing-keycloak-debug
clearing-opensearch-log-query
clearing-prod-to-staging-replay
```

## 6. Adapter-Local Only

These should not become project source-of-truth capabilities:

```text
.system/imagegen
.system/openai-docs
.system/plugin-creator
.system/skill-creator
.system/skill-installer
ev-style-writer
```

## 7. Outliers And Boundary Cases

- `clearing-feature-review-diff` and `clearing-feature-review-pack` look project-domain but have no durable memory file yet. The PoC keeps them legacy until migration intent is explicit.
- Routing hints in generated contract candidates are mechanically derived and should be reviewed before production use.
- System skills are included only to prove they stay outside project-governed ownership.

## 8. Requirement Coverage Summary

| Coverage | Count | Meaning |
|----------|-------|---------|
| Yes | 5 | Fully proven by the dry-run inventory. |
| Partial | 14 | Shape or safety proven, implementation still required. |
| No | 18 | Outside this migration-inventory PoC. |

## 9. Recommendation And Next Actions

Recommendation: proceed to Phase 0 implementation, but keep it gated by this dry-run inventory.

Next actions:
1. Use the 9 generated contract candidates as the first migration input, not as final production contracts.
2. Implement `govkb validate` and contract schema checks before any materialization.
3. Keep the 12 legacy skills installed and unchanged until parity is proven.
4. Add an adapter-manifest PoC if we want proof for `govkb apply codex` before writing production materialization code.
