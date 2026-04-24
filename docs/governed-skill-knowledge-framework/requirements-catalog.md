# Requirements Catalog - Governed Skill Knowledge Framework PoC

Last updated: 2026-04-22

PoC scope: prove that existing local skills can be inventoried read-only, classified into migration tracks, and converted into first-wave contract candidates before production implementation starts.

| Catalog ID | Requirement Text | Source Section | In POC Scope | Assertion ID(s) | Evidence Artifact | Status |
|------------|------------------|----------------|--------------|-----------------|------------------|--------|
| REQ-TR-00 | Keep reusable framework source outside project repos in a separate shareable `govkb` repo/package that can be cloned, installed, tested, and reused. | Technical Requirements | No | N/A | N/A | Out of this migration-inventory PoC; covered by implementation Phase 0. |
| REQ-TR-01 | Introduce a repo-native governed package root at `<project-root>/.governed/`. | Technical Requirements | Partial | A-05 | `poc-artifacts/proposed-contracts/` | Contract candidates prove target shape; actual project scaffold remains implementation work. |
| REQ-TR-02 | Introduce capability contracts at `.governed/capabilities/<capability_id>/capability.contract.toml`. | Technical Requirements | Yes | A-05 | `poc-artifacts/proposed-contracts/*/capability.contract.toml` | Passed. |
| REQ-TR-03 | Keep project-only knowledge and references under the repo, not Codex overlays. | Technical Requirements | Partial | A-05, A-07 | `poc-artifacts/proposed-contracts/` | PoC writes only proposed repo-style artifacts; actual migration remains implementation work. |
| REQ-TR-04 | Add assistant adapter definitions under `.governed/adapters/<assistant>/`. | Technical Requirements | No | N/A | N/A | Out of this PoC; covered by implementation phase. |
| REQ-TR-05 | Add governed release/install manifests under `.governed/releases/<release_id>.toml`. | Technical Requirements | No | N/A | N/A | Out of this PoC; covered by implementation phase. |
| REQ-TR-06 | Use `govkb` as the CLI/app alias. | Technical Requirements | Partial | A-08 | `regenerate-poc-data.sh` | PoC uses feature-local script; real `govkb` packaging remains implementation work. |
| REQ-TR-07 | Remove central hardcoded skill routing such as `KEYWORD_SKILL_HINTS`. | Technical Requirements | Partial | A-02, A-05 | `poc-artifacts/skill-inventory.md` | PoC proves first-wave routing inputs can be derived from local skill metadata; scheduler integration remains implementation work. |
| REQ-TR-08 | Keep scheduler audit behavior for the first live adapter. | Technical Requirements | No | N/A | N/A | Out of this PoC; scheduler is not modified. |
| REQ-TR-09 | Preserve strict memory governance. | Technical Requirements | Partial | A-06 | `poc-artifacts/proposed-contracts/clearing-feature-estimator/capability.contract.toml` | Explicit-acceptance detection passed for estimator; full validator remains implementation work. |
| REQ-TR-10 | Project-only governed knowledge mutations target the repo package first. | Technical Requirements | Partial | A-07 | `poc-artifacts/summary.json` | PoC is read-only against source skills and writes only feature evidence. |
| REQ-TR-11 | Scheduled adapter resolves each session to the correct repo-governed package. | Technical Requirements | No | N/A | N/A | Out of this skill-inventory PoC; planned for adapter PoC/implementation. |
| REQ-TR-12 | Automated repo-first memory writes do not dirty active developer working tree. | Technical Requirements | Partial | A-07 | `poc/skill_inventory_dry_run.py` | PoC demonstrates read-only source handling; automation worktree remains implementation work. |
| REQ-TR-13 | Codex adapter discovers real session files if `session_index.jsonl` is incomplete. | Technical Requirements | No | N/A | N/A | Already proven in existing scheduler work; not part of this migration inventory PoC. |
| REQ-TR-14 | Preserve existing local Codex skill installs during migration. | Technical Requirements | Yes | A-01, A-04, A-07 | `poc-artifacts/skill-inventory.md` | Passed. All skills are classified; no source skill files are modified. |
| REQ-TR-15 | First implementation is ready for Claude/Copilot adapters. | Technical Requirements | No | N/A | N/A | Contract shape supports this later, but no runtime adapter proof in this PoC. |
| REQ-TR-16 | Existing skills classify into governed, adapter-local, or legacy tracks. | Technical Requirements | Yes | A-01, A-02, A-03, A-04 | `poc-artifacts/skill-inventory.md` | Passed. |
| REQ-TR-17 | Classify reusable learning from completed work as existing capability update, new capability candidate, project knowledge, or reject. | Technical Requirements | No | N/A | N/A | Out of this migration-inventory PoC; covered by Codex adapter implementation. |
| REQ-TR-18 | Auto-apply existing capability expertise only when target, section, confidence, and governance rules are satisfied. | Technical Requirements | Partial | A-06 | `poc-artifacts/proposed-contracts/clearing-feature-estimator/capability.contract.toml` | Governance shape is partially proven; live learning update validation remains implementation work. |
| REQ-TR-19 | Stage new governed capability candidates for explicit review rather than fully auto-creating them. | Technical Requirements | No | N/A | N/A | Requires learning classifier and candidate staging implementation. |
| REQ-TR-20 | Reports show learned, staged, rejected, promoted, and redistributable changes. | Technical Requirements | No | N/A | N/A | Existing report model is reused, but new learning-status fields are implementation work. |
| REQ-AI-00 | Reusable `govkb` framework repo/package can be cloned, installed, and used through `govkb init` to scaffold a project `.governed/` package. | Acceptance Intent | No | N/A | N/A | Out of this migration-inventory PoC; covered by implementation Phase 0. |
| REQ-AI-01 | Project-only governed knowledge lives in git and is not Codex-only overlay. | Acceptance Intent | Partial | A-05 | `poc-artifacts/proposed-contracts/` | Proposed contracts are repo-shaped; actual `.governed/` commit remains implementation work. |
| REQ-AI-02 | Framework discovers governed capabilities from contracts without hardcoded keyword map. | Acceptance Intent | Partial | A-02, A-05 | `poc-artifacts/proposed-contracts/` | Contract candidates exist for all memory-bearing first-wave skills. |
| REQ-AI-03 | New governed capability can participate without central script edits. | Acceptance Intent | Partial | A-05 | `poc-artifacts/proposed-contracts/` | PoC proves contract generation shape only. |
| REQ-AI-04 | Same package can define Codex and future assistants. | Acceptance Intent | No | N/A | N/A | Requires adapter manifest PoC. |
| REQ-AI-05 | `govkb apply codex` can apply repo release and record revision. | Acceptance Intent | No | N/A | N/A | Requires CLI implementation. |
| REQ-AI-06 | Project-local governance cannot be weakened by adapters. | Acceptance Intent | Partial | A-06 | `poc-artifacts/proposed-contracts/clearing-feature-estimator/capability.contract.toml` | Explicit-acceptance policy is captured in candidate contract. |
| REQ-AI-07 | Scheduled routing resolves repo or skips no-match sessions. | Acceptance Intent | No | N/A | N/A | Requires session metadata PoC. |
| REQ-AI-08 | Automated repo-first writes stay isolated until promotion. | Acceptance Intent | Partial | A-07 | `poc/skill_inventory_dry_run.py` | PoC is dry-run only; worktree isolation remains implementation work. |
| REQ-AI-09 | First live adapter produces reports, patches, and health signals. | Acceptance Intent | No | N/A | N/A | Existing scheduler already does this; not modified by this PoC. |
| REQ-AI-10 | Existing Codex skill installs keep working during migration. | Acceptance Intent | Yes | A-01, A-04, A-07 | `poc-artifacts/skill-inventory.md` | Passed. |
| REQ-AI-11 | Framework is documented enough for later skill creator override. | Acceptance Intent | Partial | A-05 | `poc-artifacts/proposed-contracts/` | Contract candidates clarify scaffolding inputs. |
| REQ-AI-12 | Existing local skills classify consistently into migration tracks. | Acceptance Intent | Yes | A-01, A-02, A-03, A-04, A-08 | `poc-artifacts/summary.json` | Passed. |
| REQ-AI-13 | A real work session can update an existing governed capability in the automation worktree with report evidence. | Acceptance Intent | No | N/A | N/A | Requires live Codex adapter integration. |
| REQ-AI-14 | Repeated unmatched work can stage a new governed capability candidate without central scheduler edits. | Acceptance Intent | No | N/A | N/A | Requires candidate detector implementation. |
| REQ-AI-15 | A promoted governed learning update can be applied by another local setup through `govkb apply codex`. | Acceptance Intent | No | N/A | N/A | Requires release/apply flow and second local setup fixture. |
