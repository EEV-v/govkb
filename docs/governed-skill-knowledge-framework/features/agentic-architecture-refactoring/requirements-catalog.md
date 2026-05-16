# Agentic Architecture Refactoring - Requirements Catalog

| ID | Requirement | Source | PoC Assertion | Scenario(s) | Status |
|---|---|---|---|---|---|
| REQ-AAR-01 | GovKB must have a maintained architecture ownership map. | `business.md` | Existing docs do not provide one consolidated ownership map; new artifact required. | UC-1 | Verified |
| REQ-AAR-02 | VS Code action metadata must be centralized where practical. | `business.md` | Current action labels and ids are spread across `homeState.ts`, `extension.ts`, and `package.json`. | UC-2, UC-9 | Verified |
| REQ-AAR-03 | Promotion lifecycle operations must be idempotent. | `business.md` | Existing lifecycle states exist; rerun semantics need explicit tests and no-op reporting. | UC-3, UC-9 | Verified |
| REQ-AAR-04 | GovKB must expose a cleanup path for stale or duplicate isolated promotion worktrees while preserving sidecar lifecycle audit metadata. | `business.md` | Promotion listing exists; cleanup command is not present in current command surface. | UC-4, UC-5 | Verified |
| REQ-AAR-05 | VS Code must mutate only through GovKB CLI-backed commands. | `business.md` | Current extension flows already call CLI-backed wrappers; new registry must preserve this. | UC-8 | Verified |
| REQ-AAR-06 | Conversion UX must use discoverable selections and hide already governed/materialized skills by default. | `business.md` | Current extension has filtering helpers; registry and view tests should preserve them. | UC-6 | Verified |
| REQ-AAR-07 | Governed skills must have user-facing summaries for UI display. | `business.md` | Capability payloads expose descriptions; summary placement needs UI and docs decision. | UC-7 | Verified |
| REQ-AAR-08 | Tests must cover dry-run/no-write, idempotency, duplicate/stale state, and local-state isolation. | `business.md` | Existing tests use temp dirs and dry-run patterns; new cases required. | UC-3, UC-4, UC-5, UC-8, UC-9 | Verified |
| REQ-AAR-09 | Refactoring must be phased and reversible. | `business.md` | Implementation plan must isolate docs, registry, lifecycle, UI, and tests by phase. | UC-1, UC-8 | Verified |
